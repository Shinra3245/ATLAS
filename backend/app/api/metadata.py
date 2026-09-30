"""Fuentes y estado de ML publicados por el motor."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.adapters.engine_adapter import EngineAdapter, get_engine_adapter
from app.schemas.engine_results import ERROR_RESPONSES
from app.services.catalog_service import ml_status as read_ml_status
from app.services.catalog_service import sources as read_sources

router = APIRouter(tags=["metadata"])


@router.get("/sources", responses=ERROR_RESPONSES)
def sources(adapter: EngineAdapter = Depends(get_engine_adapter)) -> dict[str, Any]:
    return read_sources(adapter)


@router.get("/ml/status", responses=ERROR_RESPONSES)
def ml_status(adapter: EngineAdapter = Depends(get_engine_adapter)) -> dict[str, Any]:
    return read_ml_status(adapter)
