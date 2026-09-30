"""Catálogos publicados por el motor. Vacío si el contrato aún no los trae."""

from __future__ import annotations

from typing import Any, Optional

from app.adapters.engine_adapter import EngineAdapter, _as_payload
from app.core.config import CATALOG_UNPUBLISHED, SUPPORTED_MUNICIPALITIES
from app.core.errors import APIError, EngineContractError


def _json_item(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        from app.adapters.engine_adapter import _reject_forbidden

        _reject_forbidden(item)
        return item
    return _as_payload(item)


def _public_sources(raw: Optional[list[Any]]) -> tuple[list[dict[str, Any]], str | None]:
    if raw is None:
        return [], CATALOG_UNPUBLISHED
    published: list[dict[str, Any]] = []
    for item in raw:
        data = _json_item(item)
        if data.get("is_test_fixture") is True:
            continue
        published.append(data)
    if not published:
        return [], CATALOG_UNPUBLISHED
    return published, None


def sources(adapter: EngineAdapter) -> dict[str, Any]:
    items, limitation = _public_sources(adapter.list_sources())
    body: dict[str, Any] = {"sources": items}
    if limitation:
        body["limitation"] = limitation
    return body


def layers(adapter: EngineAdapter) -> dict[str, Any]:
    raw = adapter.list_layers()
    if not raw:
        return {"layers": [], "limitation": CATALOG_UNPUBLISHED}
    return {"layers": [_json_item(item) for item in raw]}


def locations(
    adapter: EngineAdapter,
    municipality: Optional[str],
    query: Optional[str],
) -> dict[str, Any]:
    if municipality is not None and municipality not in SUPPORTED_MUNICIPALITIES:
        raise APIError(
            status_code=422,
            error="OUTSIDE_SUPPORTED_AREA",
            message=(
                "El catálogo de localidades solo cubre Irapuato y Celaya. "
                "Guanajuato estatal está planificado como expansión futura."
            ),
            details={"supported_municipalities": list(SUPPORTED_MUNICIPALITIES)},
        )
    raw = adapter.list_locations()
    body: dict[str, Any] = {
        "locations": [],
        "municipality": municipality,
        "query": query,
    }
    if not raw:
        body["limitation"] = CATALOG_UNPUBLISHED
        return body
    needle = query.casefold() if query else None
    selected: list[dict[str, Any]] = []
    for item in raw:
        data = _json_item(item)
        if municipality is not None and data.get("municipality") != municipality:
            continue
        if needle is not None:
            haystack = " ".join(
                str(data.get(field) or "")
                for field in ("id", "locality", "municipality", "label", "name")
            ).casefold()
            if needle not in haystack:
                continue
        selected.append(data)
    body["locations"] = selected
    return body


def location_by_id(adapter: EngineAdapter, location_id: str) -> dict[str, Any]:
    raw = adapter.list_locations()
    if raw:
        for item in raw:
            data = _json_item(item)
            if str(data.get("id")) == location_id:
                return data
    raise APIError(
        status_code=404,
        error="NOT_FOUND",
        message="No existe una localidad publicada con ese identificador.",
        details={"id": location_id},
    )


def ml_status(adapter: EngineAdapter) -> dict[str, Any]:
    payload = adapter.ml_status()
    if "status" not in payload or "enabled" not in payload:
        raise EngineContractError("ml_status no incluye enabled y status")
    return payload

