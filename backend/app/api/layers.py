"""Capas publicadas por el motor."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.adapters.engine_adapter import EngineAdapter, get_engine_adapter
from app.services.catalog_service import layers as list_layers

router = APIRouter(tags=["layers"])


@router.get("/layers")
def layers(adapter: EngineAdapter = Depends(get_engine_adapter)) -> dict[str, Any]:
    return list_layers(adapter)
