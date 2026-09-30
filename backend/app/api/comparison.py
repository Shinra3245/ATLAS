"""Comparación A/B con el mismo tipo de obra. No elige un ganador."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.adapters.engine_adapter import EngineAdapter, get_engine_adapter
from app.schemas.engine_results import ERROR_RESPONSES, ComparisonResultOut
from app.schemas.requests import CompareRequest
from app.services.analysis_service import compare as run_compare

router = APIRouter(tags=["comparison"])


@router.post(
    "/compare",
    response_model=ComparisonResultOut,
    responses=ERROR_RESPONSES,
)
def compare(
    body: CompareRequest,
    adapter: EngineAdapter = Depends(get_engine_adapter),
) -> dict[str, Any]:
    return run_compare(body, adapter)
