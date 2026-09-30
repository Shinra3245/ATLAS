"""Traduce llamadas de la API al motor, sin recalcular condiciones.

Si `analyze_location` o `compare_locations` no existen, la operación falla con
`EngineUnavailableError`. No hay resultados de reserva.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Optional

from app.adapters.contract_validation import validate_engine_payload
from app.core.config import DEFAULT_ML_REASON, DEFAULT_ML_STATUS
from app.core.errors import EngineContractError, EngineUnavailableError

#: Claves que el backend tiene prohibido publicar, aunque el motor las emita.
FORBIDDEN_KEYS = frozenset(
    {
        "winner",
        "best_location",
        "global_risk",
        "global_risk_score",
        "risk_percentage",
        "safety_percentage",
        "safety_score",
        "feasibility_percentage",
        "feasibility_score",
        "overall_risk_percent",
        "risk_score",
    }
)

_ENTRY_MODULES = (
    "engine",
    "engine.services.analyze",
    "engine.comparison.compare",
)


def ensure_repo_root() -> Path:
    """Añade la raíz del repositorio a `sys.path` para importar `engine`."""

    repo = Path(__file__).resolve().parents[3]
    root = str(repo)
    if root not in sys.path:
        sys.path.insert(0, root)
    return repo


def _import_engine(module_name: str) -> Any:
    ensure_repo_root()
    return importlib.import_module(module_name)


def _find_callable(name: str) -> Optional[Any]:
    for module_name in _ENTRY_MODULES:
        try:
            module = _import_engine(module_name)
        except ModuleNotFoundError:
            continue
        candidate = getattr(module, name, None)
        if callable(candidate):
            return candidate
    return None


def _reject_forbidden(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_KEYS:
                raise EngineContractError(f"clave prohibida: {key}")
            _reject_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden(item)


def _as_payload(result: Any, kind: Optional[str] = None) -> dict[str, Any]:
    if hasattr(result, "to_dict") and callable(result.to_dict):
        payload = result.to_dict()
    else:
        serialization = _import_engine("engine.schemas")
        payload = serialization.to_jsonable(result)
    if not isinstance(payload, dict):
        raise EngineContractError("el motor no devolvió un objeto")
    _reject_forbidden(payload)
    if kind is not None:
        validate_engine_payload(payload, kind)
    return payload


class EngineAdapter:
    """Puente de solo lectura hacia el Bloque 2."""

    def resolve_municipality(
        self, lat: float, lon: float, locality_id: Optional[str] = None
    ) -> Optional[str]:
        """Municipio resuelto por el motor; la clave explícita tiene prioridad."""

        try:
            module = _import_engine("engine.services.data_source")
        except ModuleNotFoundError as exc:
            raise EngineUnavailableError(
                "el motor no publica resolución geográfica"
            ) from exc
        resolution = module.default_data_source().resolve(lat, lon, locality_id=locality_id)
        location = resolution.resolved
        status = location.area_status
        status_value = status.value if hasattr(status, "value") else str(status)
        if status_value != "supported":
            return None
        municipality = location.municipality
        return str(municipality) if municipality else None

    def analyze(
        self,
        project_type: str,
        lat: float,
        lon: float,
        locality_id: Optional[str] = None,
        label: Optional[str] = None,
    ) -> dict[str, Any]:
        function = _find_callable("analyze_location")
        if function is None:
            raise EngineUnavailableError("analyze_location no está publicado")
        schemas = _import_engine("engine.schemas")
        location = schemas.Location(
            lat=lat,
            lon=lon,
            locality_id=locality_id,
            label=label,
        )
        try:
            result = function(location, schemas.ProjectType(project_type))
        except TypeError as exc:
            raise EngineContractError(
                "analyze_location no acepta (Location, ProjectType)"
            ) from exc
        return _as_payload(result, "analysis")

    def compare(
        self,
        project_type: str,
        lat_a: float,
        lon_a: float,
        lat_b: float,
        lon_b: float,
        locality_id_a: Optional[str] = None,
        label_a: Optional[str] = None,
        locality_id_b: Optional[str] = None,
        label_b: Optional[str] = None,
    ) -> dict[str, Any]:
        function = _find_callable("compare_locations")
        if function is None:
            raise EngineUnavailableError("compare_locations no está publicado")
        schemas = _import_engine("engine.schemas")
        project = schemas.ProjectType(project_type)
        location_a = schemas.Location(
            lat=lat_a,
            lon=lon_a,
            locality_id=locality_id_a,
            label=label_a,
        )
        location_b = schemas.Location(
            lat=lat_b,
            lon=lon_b,
            locality_id=locality_id_b,
            label=label_b,
        )
        try:
            result = function(location_a, location_b, project)
        except TypeError as exc:
            raise EngineContractError(
                "compare_locations no acepta (Location, Location, ProjectType)"
            ) from exc
        return _as_payload(result, "comparison")

    def list_sources(self) -> Optional[list[Any]]:
        return self._optional_catalog("list_sources")

    def list_layers(self) -> Optional[list[Any]]:
        return self._optional_catalog("list_layers")

    def list_locations(self) -> Optional[list[Any]]:
        return self._optional_catalog("list_locations")

    def ml_status(self) -> dict[str, Any]:
        function = _find_callable("ml_status")
        if function is not None:
            try:
                return _as_payload(function())
            except EngineContractError:
                raise
            except TypeError as exc:
                raise EngineContractError(
                    "ml_status no acepta una llamada sin argumentos"
                ) from exc
        try:
            module = _import_engine("engine.services.ml_info")
        except ModuleNotFoundError:
            return {
                "enabled": False,
                "status": DEFAULT_ML_STATUS,
                "reason": DEFAULT_ML_REASON,
            }
        info = getattr(module, "disabled_ml_info", None)
        if not callable(info):
            return {
                "enabled": False,
                "status": DEFAULT_ML_STATUS,
                "reason": DEFAULT_ML_REASON,
            }
        return _as_payload(info())

    def _optional_catalog(self, name: str) -> Optional[list[Any]]:
        function = _find_callable(name)
        if function is None:
            return None
        try:
            raw = function()
        except TypeError as exc:
            raise EngineContractError(f"{name} no acepta una llamada sin argumentos") from exc
        if raw is None:
            return None
        if not isinstance(raw, list):
            raise EngineContractError(f"{name} no devolvió una lista")
        return raw


def get_engine_adapter() -> EngineAdapter:
    return EngineAdapter()
