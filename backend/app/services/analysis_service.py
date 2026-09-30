"""Validación de cobertura y reenvío al motor."""

from __future__ import annotations

from app.adapters.engine_adapter import EngineAdapter
from app.core.config import OUTSIDE_AREA_MESSAGE, SUPPORTED_MUNICIPALITIES
from app.core.errors import APIError
from app.schemas.requests import AnalyzeRequest, CompareRequest, LocationIn


def _outside(which: str | None = None) -> APIError:
    details: dict[str, object] = {
        "supported_municipalities": list(SUPPORTED_MUNICIPALITIES),
    }
    if which is not None:
        details["location"] = which
    return APIError(
        status_code=422,
        error="OUTSIDE_SUPPORTED_AREA",
        message=OUTSIDE_AREA_MESSAGE,
        details=details,
    )


def _same_point(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> bool:
    return (round(lat_a, 6), round(lon_a, 6)) == (round(lat_b, 6), round(lon_b, 6))


def _municipality(adapter: EngineAdapter, location: LocationIn) -> str | None:
    if location.locality_id is not None:
        return adapter.resolve_municipality(location.lat, location.lon, locality_id=location.locality_id)
    return adapter.resolve_municipality(location.lat, location.lon)


def _ensure_known_locality(adapter: EngineAdapter, locality_id: str, which: str | None = None) -> None:
    """Si se pide una clave de localidad explícita, debe existir en el catálogo.

    Una clave inexistente es un error del cliente (404), no una ubicación "fuera
    de alcance". Si el catálogo aún no está publicado, no se puede validar y se
    omite la comprobación (el motor decidirá).
    """
    raw = adapter.list_locations()
    if not raw:
        return
    known = {str(item.get("id")) for item in raw if isinstance(item, dict)}
    if str(locality_id) not in known:
        details: dict[str, object] = {"locality_id": locality_id}
        if which is not None:
            details["location"] = which
        raise APIError(
            status_code=404,
            error="NOT_FOUND",
            message="No existe una localidad publicada con ese identificador.",
            details=details,
        )


def analyze(body: AnalyzeRequest, adapter: EngineAdapter) -> dict:
    if body.location.locality_id is not None:
        _ensure_known_locality(adapter, body.location.locality_id)
    municipality = _municipality(adapter, body.location)
    if municipality is None:
        raise _outside()
    return adapter.analyze(
        project_type=body.project_type,
        lat=body.location.lat,
        lon=body.location.lon,
        locality_id=body.location.locality_id,
        label=body.location.label,
    )


def compare(body: CompareRequest, adapter: EngineAdapter) -> dict:
    if body.location_a.locality_id is not None:
        _ensure_known_locality(adapter, body.location_a.locality_id, "location_a")
    if body.location_b.locality_id is not None:
        _ensure_known_locality(adapter, body.location_b.locality_id, "location_b")
    if _municipality(adapter, body.location_a) is None:
        raise _outside("location_a")
    if _municipality(adapter, body.location_b) is None:
        raise _outside("location_b")
    # Si hay clave explícita, el motor compara identidades resueltas. Dos claves
    # distintas pueden llevar las mismas coordenadas auxiliares en la solicitud.
    if body.location_a.locality_id is None and body.location_b.locality_id is None and _same_point(
        body.location_a.lat,
        body.location_a.lon,
        body.location_b.lat,
        body.location_b.lon,
    ):
        raise APIError(
            status_code=422,
            error="SAME_LOCATION",
            message="La comparación requiere dos coordenadas distintas.",
        )
    result = adapter.compare(
        project_type=body.project_type,
        lat_a=body.location_a.lat,
        lon_a=body.location_a.lon,
        lat_b=body.location_b.lat,
        lon_b=body.location_b.lon,
        locality_id_a=body.location_a.locality_id,
        label_a=body.location_a.label,
        locality_id_b=body.location_b.locality_id,
        label_b=body.location_b.label,
    )
    # El motor declara si ambas coordenadas resolvieron a la MISMA localidad
    # censal (aunque las coordenadas de entrada difieran). Comparar una localidad
    # consigo misma no es una comparación efectiva entre sitios distintos.
    if result.get("same_locality") is True:
        raise APIError(
            status_code=422,
            error="SAME_LOCATION",
            message=(
                "Ambas ubicaciones corresponden a la misma localidad censal; "
                "la comparación requiere dos localidades distintas."
            ),
        )
    return result
