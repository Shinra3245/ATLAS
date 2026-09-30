"""Orquestador central: ``analyze_location``.

Ejecuta la misma matriz de analyzers para cualquier localidad soportada,
contextualiza por tipo de obra sin alterar el dato bruto, agrega cobertura,
fuentes, limitaciones y aspectos a revisar, y produce un ``AnalysisResult``
determinista y explicable.

La resolución territorial es responsabilidad de la fuente de datos (clave y
municipio documentados del DATA CONTRACT), no de cajas geográficas inventadas.
"""

from __future__ import annotations

import math
from typing import Any, Optional, Union

from ..analyzers import all_analyzers
from ..schemas.condition import Condition
from ..schemas.enums import AreaStatus, Category, Priority, ProjectType
from ..schemas.location import Location
from ..schemas.result import (
    ENGINE_RESULT_SCHEMA_VERSION,
    AnalysisResult,
    CoverageSummary,
)
from ..schemas.source import Source
from ..utils.ids import analysis_id
from .contextualize import contextualize
from .coverage import compute_coverage
from .data_source import (
    DataSource,
    FixtureDataSource,
    LocalityResolution,
    default_data_source,
)
from .ml_info import disabled_ml_info, historical_experiment_info

#: Versión del motor. Forma parte del contrato y de la trazabilidad.
ENGINE_VERSION = "engine/1.0.0-mvp"

LocationInput = Union[Location, dict[str, Any]]
ProjectTypeInput = Union[ProjectType, str]


class InvalidProjectTypeError(ValueError):
    """El tipo de obra no es uno de: housing, building, road."""


class InvalidLocationError(ValueError):
    """La ubicación de entrada no tiene lat/lon válidos y finitos."""


def _normalize_project_type(project_type: ProjectTypeInput) -> ProjectType:
    if isinstance(project_type, ProjectType):
        return project_type
    try:
        return ProjectType(str(project_type).strip().lower())
    except ValueError as exc:  # pragma: no cover - mensaje explícito
        valid = ", ".join(pt.value for pt in ProjectType)
        raise InvalidProjectTypeError(
            f"project_type inválido: {project_type!r}. Válidos: {valid}."
        ) from exc


def _normalize_location(location: LocationInput) -> Location:
    if isinstance(location, Location):
        lat, lon = location.lat, location.lon
        locality_id = location.locality_id
        label = location.label
    elif isinstance(location, dict):
        try:
            lat = float(location["lat"])
            lon = float(location["lon"])
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidLocationError(
                "La ubicación requiere 'lat' y 'lon' numéricos."
            ) from exc
        locality_id = location.get("locality_id")
        label = location.get("label")
    else:
        raise InvalidLocationError(
            "location debe ser Location o dict con 'lat'/'lon'."
        )

    # Rechazo estricto de NaN/Inf: garantiza JSON serializable de forma estricta.
    if not (math.isfinite(lat) and math.isfinite(lon)):
        raise InvalidLocationError(
            "Las coordenadas deben ser números finitos (no NaN ni Infinito)."
        )
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise InvalidLocationError("Latitud fuera de -90..90 o longitud fuera de -180..180.")
    return Location(lat=lat, lon=lon, locality_id=locality_id, label=label)


def _dedup_sources(conditions: list[Condition]) -> list[Source]:
    seen: dict[str, Source] = {}
    order: list[str] = []
    for cond in conditions:
        if cond.source is not None and cond.source.id not in seen:
            seen[cond.source.id] = cond.source
            order.append(cond.source.id)
    return [seen[i] for i in order]


def _aggregate_review_items(conditions: list[Condition]) -> list[str]:
    ordered: list[str] = []
    for target in (Priority.PRIMARY, Priority.SECONDARY, Priority.CONTEXTUAL):
        for cond in conditions:
            if cond.priority != target:
                continue
            for item in cond.review_items:
                if item not in ordered:
                    ordered.append(item)
    return ordered


def _base_limitations(
    data_source: DataSource, conditions: list[Condition]
) -> list[str]:
    limitations = [
        "Cobertura limitada a Irapuato y Celaya.",
        "La ausencia de información no equivale a ausencia de riesgo.",
        "Unidad de análisis: localidad censal; no se aplica a un predio o "
        "coordenada arbitraria.",
    ]
    uses_real = any(
        cond.source is not None and not cond.source.is_test_fixture
        for cond in conditions
    )
    if isinstance(data_source, FixtureDataSource):
        limitations.append(
            "Ejecución sobre TEST_FIXTURE: los datos son simulados de prueba y no "
            "deben confundirse con datos reales."
        )
    elif not data_source.is_contract_available():
        limitations.append(
            "DATA CONTRACT v1 no disponible: no hay datos de producción; los "
            "factores se reportan como información insuficiente o bloqueada."
        )
    elif uses_real:
        limitations.append(
            "Procedencia de fuentes parcial (SOURCE_PROVENANCE_PARTIAL): "
            "atribuciones declaradas por los libros recibidos, no verificadas de "
            "forma independiente."
        )
    return limitations


def analyze_location(
    location: LocationInput,
    project_type: ProjectTypeInput,
    data_source: Optional[DataSource] = None,
) -> AnalysisResult:
    """Analiza una localidad para un tipo de obra.

    Args:
        location: ``Location`` o ``{"lat": ..., "lon": ..., "locality_id"?: ...}``.
        project_type: ``"housing"``/``"building"``/``"road"`` o ``ProjectType``.
        data_source: fuente de datos; por defecto la de producción (DATA CONTRACT).

    Returns:
        ``AnalysisResult`` determinista y serializable con ``to_dict()``.
    """

    pt = _normalize_project_type(project_type)
    loc = _normalize_location(location)
    source = data_source if data_source is not None else default_data_source()

    resolution: LocalityResolution = source.resolve(loc.lat, loc.lon, loc.locality_id)
    resolved = resolution.resolved

    aid = analysis_id(
        loc.lat, loc.lon, pt.value, source.version, resolved.locality_id
    )

    # Fuera del área soportada (o localidad no reconocida): sin factores.
    if resolved.area_status == AreaStatus.OUTSIDE_SUPPORTED_AREA:
        empty_coverage = CoverageSummary(
            expected=0,
            data_available=0,
            partial_data=0,
            insufficient_data=0,
            no_registered_condition=0,
            blocked_data_validation=0,
            by_category={},
        )
        return AnalysisResult(
            analysis_id=aid,
            schema_version=ENGINE_RESULT_SCHEMA_VERSION,
            engine_version=ENGINE_VERSION,
            project_type=pt.value,
            location=resolved,
            conditions=[],
            territorial_factors=[],
            context=[],
            coverage=empty_coverage,
            sources=[],
            limitations=[
                "Ubicación fuera del área de cobertura (Irapuato/Celaya).",
                "OUTSIDE_SUPPORTED_AREA no significa ausencia de riesgo; significa "
                "que ATLAS no cubre esa zona.",
            ],
            review_items=[
                "Seleccionar una localidad dentro de Irapuato o Celaya para analizar."
            ],
            ml=disabled_ml_info(),
        )

    # Ejecutar la matriz completa de analyzers y contextualizar por tipo de obra.
    raw_conditions = [a.analyze(source, resolution) for a in all_analyzers()]
    conditions_all = [contextualize(c, pt) for c in raw_conditions]

    hazards = [
        c
        for c in conditions_all
        if c.category in (Category.HAZARD, Category.HAZARD_HISTORY, Category.DERIVED)
    ]
    territorial = [
        c for c in conditions_all if c.category == Category.TERRITORIAL_FACTOR
    ]
    context = [c for c in conditions_all if c.category == Category.CONTEXT]

    coverage = compute_coverage(conditions_all)
    sources = _dedup_sources(conditions_all)
    review_items = _aggregate_review_items(conditions_all)
    limitations = _base_limitations(source, conditions_all)

    return AnalysisResult(
        analysis_id=aid,
        schema_version=ENGINE_RESULT_SCHEMA_VERSION,
        engine_version=ENGINE_VERSION,
        project_type=pt.value,
        location=resolved,
        conditions=hazards,
        territorial_factors=territorial,
        context=context,
        coverage=coverage,
        sources=sources,
        limitations=limitations,
        review_items=review_items,
        ml=historical_experiment_info(resolution.record),
    )
