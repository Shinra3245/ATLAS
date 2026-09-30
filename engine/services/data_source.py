"""Fuentes de datos del motor.

REGLA DE CONSUMO (no negociable):
El motor SOLO consume datos de producción desde:
  - ``data/contracts/DATA_CONTRACT_V1.md``  (única fuente contractual)
  - ``data/processed/v1/``                  (productos reproducibles de Bloque 1)

Está PROHIBIDO leer ``data/incoming/**`` o ``data/raw/**`` como fuente de
producción (incluidos los XLSX). Este módulo nunca abre esos directorios.

Resolución territorial (DATA CONTRACT V1):
- La unidad de análisis es la LOCALIDAD censal (clave CVEGEO). No se aplican
  datos de localidad a una coordenada arbitraria: una coordenada se asocia a la
  localidad censal más cercana dentro del área soportada, y el municipio/clave
  provienen del registro documentado, NUNCA de cajas inventadas.
- Coordenadas en ``CRS_UNKNOWN``: no se reproyectan ni se declara EPSG:4326.

Para pruebas se usa ``FixtureDataSource``, cuyos datos están SIEMPRE marcados
como ``TEST_FIXTURE`` y jamás deben confundirse con datos reales.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from ..schemas.enums import (
    AnalysisUnit,
    AreaStatus,
    CoverageState,
    TemporalContext,
)
from ..schemas.location import ResolvedLocation
from ..schemas.source import Source
from ..utils.geo import distance_deg, is_finite_coord

#: Raíz del repositorio: services -> engine -> <root>.
REPO_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_V1_DIR = REPO_ROOT / "data" / "processed" / "v1"
DATA_CONTRACT_PATH = REPO_ROOT / "data" / "contracts" / "DATA_CONTRACT_V1.md"
ANALYSIS_UNITS_PATH = PROCESSED_V1_DIR / "analysis_units.json"
MUNICIPAL_CONTEXT_PATH = PROCESSED_V1_DIR / "municipal_context.json"
SOURCES_CATALOG_PATH = PROCESSED_V1_DIR / "sources_catalog.json"
LAYER_MANIFEST_PATH = PROCESSED_V1_DIR / "layer_manifest.json"
MANIFEST_PATH = PROCESSED_V1_DIR / "manifest.json"

#: Tolerancia numérica para distinguir coincidencia del punto publicado de una
#: asociación aproximada. No es un radio de cobertura ni un umbral de riesgo.
LOCALITY_MATCH_DEG = 1e-9
#: LÍMITE EFECTIVO de asociación (en grados): si la localidad censal más cercana
#: está más lejos que esto, la coordenada NO se asocia a ninguna localidad y se
#: reporta OUTSIDE_SUPPORTED_AREA. Evita "pegar" datos de una localidad a una
#: coordenada arbitraria y distante. ~0.05° ≈ 5.5 km.
LOCALITY_SUPPORT_DEG = 0.05


@dataclass(frozen=True)
class FactorReading:
    """Lectura cruda de un factor para una localidad.

    Representa lo que la FUENTE entrega, no una conclusión. El analyzer traduce
    esta lectura a un estado semántico y a una explicación.
    """

    factor: str
    value: Optional[Any]
    unit: Optional[str]
    coverage_state: CoverageState
    temporal_context: TemporalContext
    source: Optional[Source]
    coverage_detail: Optional[str] = None
    #: Señal de "condición cubierta pero no registrada" (p. ej. daño 2014 = 0).
    no_registered_condition: bool = False


@dataclass(frozen=True)
class LocalityResolution:
    """Resultado de resolver una coordenada/clave a una localidad soportada."""

    resolved: ResolvedLocation
    #: Registro subyacente de la localidad (o ``None`` si no hay match).
    record: Optional[dict[str, Any]]
    matched: bool
    distance_deg: Optional[float]


class DataSource(ABC):
    """Interfaz de acceso a datos territoriales para el motor."""

    version: str = "unknown"

    @abstractmethod
    def is_contract_available(self) -> bool: ...

    @abstractmethod
    def published_factors(self) -> set[str]: ...

    @abstractmethod
    def resolve(
        self, lat: float, lon: float, locality_id: Optional[str] = None
    ) -> LocalityResolution: ...

    @abstractmethod
    def read_factor(
        self, resolution: LocalityResolution, factor: str
    ) -> Optional[FactorReading]: ...

    def list_sources(self) -> list[dict[str, Any]]:
        return []

    def list_layers(self) -> list[dict[str, Any]]:
        return []

    def list_locations(self) -> list[dict[str, Any]]:
        return []

    def describe(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "version": self.version,
            "contract_available": self.is_contract_available(),
            "published_factors": sorted(self.published_factors()),
        }


# --------------------------------------------------------------------------- #
# Mapeo de factores del motor a campos reales del DATA CONTRACT V1.
# Solo se mapean factores SUSTENTADOS por el contrato. Los no mapeados quedan
# en el estado por defecto del analyzer (INSUFFICIENT/BLOCKED).
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FieldSpec:
    field: str
    unit: Optional[str]
    temporal: TemporalContext
    source_id: str = "core_geospatial"


#: Factores de paso directo (valor tal cual; DATA_AVAILABLE si no es nulo).
#: Los datos censales ITER 2020 se marcan REFERENCE_PERIOD (no ``current``):
#: describen el año 2020, no una observación de 2026.
CONTRACT_FIELD_MAP: dict[str, FieldSpec] = {
    "elevation": FieldSpec("altitude_m", "m", TemporalContext.REFERENCE_PERIOD),
    "population": FieldSpec("pobtot", "persons", TemporalContext.REFERENCE_PERIOD),
    "services_coverage": FieldSpec("cob_electrica", "ratio_0_1", TemporalContext.REFERENCE_PERIOD),
    "mobility": FieldSpec("dis_trans_2014", "category", TemporalContext.HISTORICAL),
    "hydrography_proximity": FieldSpec("dist_rio_arroyo_m", "m", TemporalContext.UNKNOWN),
    "road_proximity": FieldSpec("dist_carretera_m", "m", TemporalContext.UNKNOWN),
    "rail_proximity": FieldSpec("dist_via_ferrea_m", "m", TemporalContext.UNKNOWN),
    "industry_proximity": FieldSpec("dist_industria_m", "m", TemporalContext.UNKNOWN),
    "power_infrastructure_proximity": FieldSpec(
        "dist_linea_transmision_m", "m", TemporalContext.UNKNOWN
    ),
}

#: Campo de antecedente histórico de inundación (semántica especial 1/0/null).
FLOOD_FIELD = "riesgo_inundacion_2014"
FLOOD_SOURCE_ID = "core_geospatial"


@lru_cache(maxsize=8)
def _load_json(path_str: str) -> Any:
    path = Path(path_str)
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


class ContractDataSource(DataSource):
    """Fuente de producción: DATA CONTRACT v1 + ``data/processed/v1/``.

    Lee ``analysis_units.json`` (755 localidades), ``sources_catalog.json`` y
    ``layer_manifest.json``. Si el contrato no está publicado, opera en modo
    "sin datos": no publica factores y toda lectura devuelve ``None`` (ausencia
    de información), nunca "riesgo bajo".
    """

    def __init__(
        self,
        units_path: Path = ANALYSIS_UNITS_PATH,
        sources_path: Path = SOURCES_CATALOG_PATH,
        layers_path: Path = LAYER_MANIFEST_PATH,
        manifest_path: Path = MANIFEST_PATH,
        contract_path: Path = DATA_CONTRACT_PATH,
    ) -> None:
        self._units_path = units_path
        self._sources_path = sources_path
        self._layers_path = layers_path
        self._manifest_path = manifest_path
        self._contract_path = contract_path

        self._units: list[dict[str, Any]] = []
        self._index: dict[str, dict[str, Any]] = {}
        self._sources: dict[str, dict[str, Any]] = {}
        self._sources_list: list[dict[str, Any]] = []
        self._layers: list[dict[str, Any]] = []
        self._municipal_fields: dict[str, str] = {}
        self._municipal_values: dict[str, dict[str, Any]] = {}
        self._municipal_limitation = ""
        self.version = "no_contract"

        self._load()

    # ----------------------------------------------------------------- carga

    def _load(self) -> None:
        if not self._units_path.exists():
            return
        try:
            units = _load_json(str(self._units_path))
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(units, list):
            return
        self._units = units
        self._index = {str(r.get("id")): r for r in units if r.get("id") is not None}

        # Catálogos (best-effort).
        if self._sources_path.exists():
            try:
                cat = _load_json(str(self._sources_path))
                if isinstance(cat, list):
                    self._sources_list = cat
                    self._sources = {str(s.get("id")): s for s in cat if s.get("id")}
            except (json.JSONDecodeError, OSError):
                pass
        if self._layers_path.exists():
            try:
                layers = _load_json(str(self._layers_path))
                if isinstance(layers, list):
                    self._layers = layers
            except (json.JSONDecodeError, OSError):
                pass

        self._load_municipal_context()

        # Versión: preferir contract_version del manifiesto.
        self.version = self._compute_version()

    def _load_municipal_context(self) -> None:
        """Contexto municipal publicado aparte. No reescribe el maestro de 64 campos."""

        if not MUNICIPAL_CONTEXT_PATH.exists():
            return
        try:
            payload = _load_json(str(MUNICIPAL_CONTEXT_PATH))
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(payload, dict):
            return
        self._municipal_limitation = str(payload.get("limitation") or "")
        fields = payload.get("fields") or []
        if isinstance(fields, list):
            self._municipal_fields = {
                str(item["code"]): str(item["source_id"])
                for item in fields
                if isinstance(item, dict) and item.get("code") and item.get("source_id")
            }
        values = payload.get("values_by_id") or {}
        if isinstance(values, dict):
            self._municipal_values = values
        for source in payload.get("sources") or []:
            if not isinstance(source, dict) or not source.get("id"):
                continue
            source_id = str(source["id"])
            if source_id in self._sources:
                continue
            self._sources[source_id] = source
            self._sources_list.append(source)

    def _compute_version(self) -> str:
        if self._manifest_path.exists():
            try:
                man = _load_json(str(self._manifest_path))
                cv = man.get("contract_version")
                records = man.get("records")
                if cv:
                    return f"data_contract_{cv}_{records}"
            except (json.JSONDecodeError, OSError, AttributeError):
                pass
        return f"data_contract_units_{len(self._units)}"

    # -------------------------------------------------------------- interface

    def is_contract_available(self) -> bool:
        return bool(self._units)

    def published_factors(self) -> set[str]:
        if not self._units:
            return set()
        factors = set(CONTRACT_FIELD_MAP.keys())
        factors.add("flood_history")
        factors.update(self._municipal_fields)
        return factors

    def _build_source(self, source_id: str) -> Source:
        raw = self._sources.get(source_id)
        if not raw:
            return Source(id=source_id, name=source_id)
        # Se preserva la procedencia parcial de forma VISIBLE (no se oculta).
        verification = raw.get("verification_status", "UNKNOWN")
        coverage_note = raw.get("coverage_note")
        note = f"{verification}"
        if coverage_note:
            note = f"{verification}; {coverage_note}"
        return Source(
            id=str(raw.get("id", source_id)),
            name=str(raw.get("name", source_id)),
            institution=raw.get("institution"),
            dataset=raw.get("dataset"),
            date_or_version=raw.get("date_or_version"),
            coverage_note=note,
            is_test_fixture=False,
        )

    def _nearest(self, lat: float, lon: float) -> tuple[Optional[dict[str, Any]], Optional[float]]:
        best: Optional[dict[str, Any]] = None
        best_d: Optional[float] = None
        for r in self._units:
            rlat, rlon = r.get("latitude"), r.get("longitude")
            if not is_finite_coord(rlat, rlon):
                continue
            d = distance_deg(lat, lon, rlat, rlon)
            if best_d is None or d < best_d:
                best, best_d = r, d
        return best, best_d

    def _resolved_from_record(
        self, rec: dict[str, Any], lat: float, lon: float, distance: float
    ) -> ResolvedLocation:
        notes: list[str] = [
            "Coordenadas del contrato en CRS_UNKNOWN; no reproyectadas.",
        ]
        if distance > LOCALITY_MATCH_DEG:
            notes.append(
                "La coordenada se asoció a la localidad censal más cercana "
                f"(id {rec.get('id')}); no coincide con su punto publicado. "
                "Los datos describen la localidad, no una medición del predio."
            )
        return ResolvedLocation(
            lat=lat,
            lon=lon,
            municipality=rec.get("municipality"),
            area_status=AreaStatus.SUPPORTED,
            analysis_unit=AnalysisUnit.LOCALITY,
            locality_id=str(rec.get("id")) if rec.get("id") is not None else None,
            label=rec.get("locality"),
            notes=notes,
        )

    def resolve(
        self, lat: float, lon: float, locality_id: Optional[str] = None
    ) -> LocalityResolution:
        if not self._units:
            resolved = ResolvedLocation(
                lat=lat,
                lon=lon,
                municipality=None,
                area_status=AreaStatus.OUTSIDE_SUPPORTED_AREA,
                analysis_unit=AnalysisUnit.UNDETERMINED,
                notes=["DATA CONTRACT V1 no disponible; sin datos de producción."],
            )
            return LocalityResolution(resolved, None, matched=False, distance_deg=None)

        # Resolución por clave de localidad, si se provee.
        if locality_id is not None:
            rec = self._index.get(str(locality_id))
            if rec is not None:
                rlat, rlon = rec.get("latitude", lat), rec.get("longitude", lon)
                resolved = self._resolved_from_record(rec, rlat, rlon, 0.0)
                return LocalityResolution(resolved, rec, matched=True, distance_deg=0.0)
            resolved = ResolvedLocation(
                lat=lat,
                lon=lon,
                municipality=None,
                area_status=AreaStatus.OUTSIDE_SUPPORTED_AREA,
                analysis_unit=AnalysisUnit.UNDETERMINED,
                notes=[f"locality_id no reconocido en el DATA CONTRACT: {locality_id}."],
            )
            return LocalityResolution(resolved, None, matched=False, distance_deg=None)

        # Resolución por coordenada: localidad censal más cercana, SOLO si está
        # dentro del límite efectivo de asociación. Una coordenada distante de
        # cualquier localidad NO hereda los datos de la más cercana.
        rec, dist = self._nearest(lat, lon)
        if rec is not None and dist is not None and dist <= LOCALITY_SUPPORT_DEG:
            resolved = self._resolved_from_record(rec, lat, lon, dist)
            return LocalityResolution(resolved, rec, matched=True, distance_deg=dist)

        notes = [
            "Fuera del área soportada por el MVP (solo Irapuato y Celaya). "
            "Guanajuato estatal es implementación futura."
        ]
        if dist is not None:
            notes.append(
                f"La localidad censal más cercana está a {dist:.4f}° "
                f"(> límite de asociación {LOCALITY_SUPPORT_DEG}°); no se asocian "
                "sus datos a esta coordenada."
            )
        resolved = ResolvedLocation(
            lat=lat,
            lon=lon,
            municipality=None,
            area_status=AreaStatus.OUTSIDE_SUPPORTED_AREA,
            analysis_unit=AnalysisUnit.UNDETERMINED,
            notes=notes,
        )
        return LocalityResolution(resolved, None, matched=False, distance_deg=dist)

    def read_factor(
        self, resolution: LocalityResolution, factor: str
    ) -> Optional[FactorReading]:
        rec = resolution.record
        if rec is None:
            return None

        if factor == "flood_history":
            raw = rec.get(FLOOD_FIELD)
            if raw is None:
                return None  # null -> INSUFFICIENT (analyzer)
            damaged = int(raw) == 1
            return FactorReading(
                factor=factor,
                value=bool(damaged),
                unit=None,
                coverage_state=CoverageState.AVAILABLE,
                temporal_context=TemporalContext.HISTORICAL,
                source=self._build_source(FLOOD_SOURCE_ID),
                coverage_detail="Antecedente censal 2014 a nivel localidad.",
                no_registered_condition=not damaged,
            )

        source_id = self._municipal_fields.get(factor)
        if source_id is not None:
            locality_id = str(rec.get("id"))
            raw = (self._municipal_values.get(locality_id) or {}).get(factor)
            if raw is None:
                return None
            return FactorReading(
                factor=factor,
                value=raw,
                unit=None,
                coverage_state=CoverageState.PARTIAL,
                temporal_context=TemporalContext.UNKNOWN,
                source=self._build_source(source_id),
                coverage_detail=self._municipal_limitation or None,
            )

        spec = CONTRACT_FIELD_MAP.get(factor)
        if spec is None:
            return None
        raw = rec.get(spec.field)
        if raw is None:
            return None
        return FactorReading(
            factor=factor,
            value=raw,
            unit=spec.unit,
            coverage_state=CoverageState.AVAILABLE,
            temporal_context=spec.temporal,
            source=self._build_source(spec.source_id),
            coverage_detail=None,
        )

    # ------------------------------------------------------------- catálogos

    def list_sources(self) -> list[dict[str, Any]]:
        # Se devuelve tal cual, preservando UNKNOWN/PENDING y provenance parcial.
        return list(self._sources_list)

    def list_layers(self) -> list[dict[str, Any]]:
        return list(self._layers)

    def list_locations(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for r in self._units:
            out.append(
                {
                    "id": str(r.get("id")),
                    "municipality": r.get("municipality"),
                    "municipality_code": r.get("municipality_code"),
                    "locality": r.get("locality"),
                    "locality_code": r.get("locality_code"),
                    "latitude": r.get("latitude"),
                    "longitude": r.get("longitude"),
                    "altitude_m": r.get("altitude_m"),
                    "coordinate_crs": r.get("coordinate_crs", "CRS_UNKNOWN"),
                }
            )
        return out


class FixtureDataSource(DataSource):
    """Fuente de PRUEBA. Todos sus datos son ``TEST_FIXTURE``."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._version = str(payload.get("fixture_version", "test_fixture"))
        self.version = f"fixture_{self._version}"
        self._localities: list[dict[str, Any]] = list(payload.get("localities", []))
        self._index: dict[str, dict[str, Any]] = {
            str(loc.get("locality_id")): loc
            for loc in self._localities
            if loc.get("locality_id") is not None
        }
        self._published: set[str] = set()
        for loc in self._localities:
            self._published.update((loc.get("factors") or {}).keys())

    def is_contract_available(self) -> bool:
        return True

    def published_factors(self) -> set[str]:
        return set(self._published)

    def _nearest(self, lat: float, lon: float):
        best = None
        best_d = None
        for loc in self._localities:
            if not is_finite_coord(loc.get("lat"), loc.get("lon")):
                continue
            d = distance_deg(lat, lon, loc["lat"], loc["lon"])
            radius = float(loc.get("match_radius_deg", LOCALITY_SUPPORT_DEG))
            if d <= radius and (best_d is None or d < best_d):
                best, best_d = loc, d
        return best, best_d

    def resolve(
        self, lat: float, lon: float, locality_id: Optional[str] = None
    ) -> LocalityResolution:
        rec = None
        dist = None
        if locality_id is not None:
            rec = self._index.get(str(locality_id))
            dist = 0.0 if rec else None
        if rec is None:
            rec, dist = self._nearest(lat, lon)
        if rec is not None:
            resolved = ResolvedLocation(
                lat=lat,
                lon=lon,
                municipality=rec.get("municipality"),
                area_status=AreaStatus.SUPPORTED,
                analysis_unit=AnalysisUnit.LOCALITY,
                locality_id=str(rec.get("locality_id")) if rec.get("locality_id") else None,
                label=rec.get("locality") or rec.get("locality_id"),
                notes=["TEST_FIXTURE: datos simulados de prueba."],
            )
            return LocalityResolution(resolved, rec, matched=True, distance_deg=dist)
        resolved = ResolvedLocation(
            lat=lat,
            lon=lon,
            municipality=None,
            area_status=AreaStatus.OUTSIDE_SUPPORTED_AREA,
            analysis_unit=AnalysisUnit.UNDETERMINED,
            notes=["Fuera del área del fixture de prueba."],
        )
        return LocalityResolution(resolved, None, matched=False, distance_deg=None)

    def read_factor(
        self, resolution: LocalityResolution, factor: str
    ) -> Optional[FactorReading]:
        rec = resolution.record
        if rec is None:
            return None
        raw = (rec.get("factors") or {}).get(factor)
        if raw is None:
            return None
        sp = raw.get("source") or {}
        source = Source.test_fixture(
            id=str(sp.get("id", f"fixture:{factor}")),
            name=str(sp.get("name", factor)),
            institution=sp.get("institution"),
            dataset=sp.get("dataset"),
            date_or_version=sp.get("date_or_version"),
            coverage_note=sp.get("coverage_note"),
        )
        return FactorReading(
            factor=factor,
            value=raw.get("value"),
            unit=raw.get("unit"),
            coverage_state=CoverageState(raw.get("coverage_state", "available")),
            temporal_context=TemporalContext(raw.get("temporal_context", "current")),
            source=source,
            coverage_detail=raw.get("coverage_detail"),
            no_registered_condition=bool(raw.get("no_registered_condition", False)),
        )

    def list_locations(self) -> list[dict[str, Any]]:
        return [
            {
                "id": str(loc.get("locality_id")),
                "municipality": loc.get("municipality"),
                "locality": loc.get("locality"),
                "latitude": loc.get("lat"),
                "longitude": loc.get("lon"),
                "is_test_fixture": True,
            }
            for loc in self._localities
        ]


def load_fixture(path: str | Path) -> FixtureDataSource:
    """Carga un fixture JSON marcado TEST_FIXTURE desde disco."""

    with Path(path).open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return FixtureDataSource(payload)


def default_data_source() -> DataSource:
    """Fuente de producción por defecto (DATA CONTRACT)."""

    return ContractDataSource()
