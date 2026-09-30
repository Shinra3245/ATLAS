"""Localidades publicadas por el motor."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query

from app.adapters.engine_adapter import EngineAdapter, get_engine_adapter
from app.schemas.engine_results import ERROR_RESPONSES
from app.services import catalog_service

router = APIRouter(tags=["locations"])


@router.get("/locations", responses=ERROR_RESPONSES)
def locations(
    municipality: Optional[str] = Query(default=None),
    query: Optional[str] = Query(default=None),
    adapter: EngineAdapter = Depends(get_engine_adapter),
) -> dict[str, Any]:
    return catalog_service.locations(adapter, municipality, query)


@router.get("/locations/{location_id}", responses=ERROR_RESPONSES)
def location_by_id(
    location_id: str,
    adapter: EngineAdapter = Depends(get_engine_adapter),
) -> dict[str, Any]:
    return catalog_service.location_by_id(adapter, location_id)
