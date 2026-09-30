"""Análisis de una ubicación. El cuerpo de éxito es el JSON del motor."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.adapters.engine_adapter import EngineAdapter, get_engine_adapter
from app.schemas.engine_results import ERROR_RESPONSES, AnalysisResultOut
from app.schemas.requests import AnalyzeRequest
from app.services.analysis_service import analyze as run_analyze

router = APIRouter(tags=["analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResultOut,
    responses=ERROR_RESPONSES,
)
def analyze(
    body: AnalyzeRequest,
    adapter: EngineAdapter = Depends(get_engine_adapter),
) -> dict[str, Any]:
    return run_analyze(body, adapter)
