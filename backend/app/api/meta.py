"""Identidad, cobertura y tipos de obra del MVP."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.adapters.engine_adapter import EngineAdapter, get_engine_adapter
from app.core.config import API_VERSION, PROJECT_TYPES, SUPPORTED_MUNICIPALITIES, SYSTEM_NAME
from app.services.catalog_service import ml_status

router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta(adapter: EngineAdapter = Depends(get_engine_adapter)) -> dict[str, Any]:
    status = ml_status(adapter)
    return {
        "system_name": SYSTEM_NAME,
        "version": API_VERSION,
        "supported_area": {
            "municipalities": list(SUPPORTED_MUNICIPALITIES),
            "state_coverage": "future",
            "note": (
                "El MVP cubre únicamente Irapuato y Celaya. "
                "Guanajuato completo es implementación futura."
            ),
        },
        "supported_municipalities": list(SUPPORTED_MUNICIPALITIES),
        "project_types": list(PROJECT_TYPES),
        "ml_status": status["status"],
    }
