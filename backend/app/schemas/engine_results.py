"""Modelos de respuesta alineados al ENGINE CONTRACT v1, para OpenAPI."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Any] = None


class ExplanationOut(BaseModel):
    found: str
    data_origin: str
    operation: str
    meaning: str
    not_meaning: str
    limitation: str


class CoverageOut(BaseModel):
    state: str
    detail: Optional[str] = None


class SourceOut(BaseModel):
    id: str
    name: str
    institution: Optional[str] = None
    dataset: Optional[str] = None
    date_or_version: Optional[str] = None
    coverage_note: Optional[str] = None
    is_test_fixture: bool


class ConditionOut(BaseModel):
    factor: str
    label: str
    category: str
    status: str
    coverage: CoverageOut
    temporal_context: str
    explanation: ExplanationOut
    value: Any = None
    unit: Optional[str] = None
    source: Optional[SourceOut] = None
    limitations: list[str]
    priority: str
    review_items: list[str]


class ResolvedLocationOut(BaseModel):
    lat: float
    lon: float
    municipality: Optional[str] = None
    area_status: str
    analysis_unit: str
    locality_id: Optional[str] = None
    label: Optional[str] = None
    notes: list[str]


class CoverageSummaryOut(BaseModel):
    expected: int
    data_available: int
    partial_data: int
    insufficient_data: int
    no_registered_condition: int
    blocked_data_validation: int
    by_category: dict[str, Any]


class MLOut(BaseModel):
    enabled: bool
    status: str
    reason: str


class AnalysisResultOut(BaseModel):
    analysis_id: str
    schema_version: str = Field(examples=["engine_result/v1"])
    engine_version: str
    project_type: str
    location: ResolvedLocationOut
    conditions: list[ConditionOut]
    territorial_factors: list[ConditionOut]
    context: list[ConditionOut]
    coverage: CoverageSummaryOut
    sources: list[SourceOut]
    limitations: list[str]
    review_items: list[str]
    ml: MLOut
    disclaimer: str


class FactorComparisonOut(BaseModel):
    factor: str
    label: str
    category: str
    unit: Optional[str] = None
    value_a: Any = None
    value_b: Any = None
    status_a: str
    status_b: str
    coverage_a: str
    coverage_b: str
    source_a: Optional[str] = None
    source_b: Optional[str] = None
    observable_difference: str
    difference_detected: bool
    more_data_available_at: Optional[str] = None
    condition_only_in: Optional[str] = None
    limitations: list[str]


class ComparisonResultOut(BaseModel):
    comparison_id: str
    schema_version: str = Field(examples=["engine_result/v1"])
    engine_version: str
    project_type: str
    location_a: ResolvedLocationOut
    location_b: ResolvedLocationOut
    factors: list[FactorComparisonOut]
    coverage_a: CoverageSummaryOut
    coverage_b: CoverageSummaryOut
    limitations: list[str]
    notes: list[str]
    disclaimer: str


ERROR_RESPONSES: dict[int, dict[str, Any]] = {
    400: {"model": ErrorResponse, "description": "El cuerpo no es JSON válido."},
    404: {"model": ErrorResponse, "description": "No existe el recurso publicado."},
    422: {
        "model": ErrorResponse,
        "description": "Validación, coordenada fuera de Irapuato/Celaya o ubicaciones idénticas.",
    },
    500: {
        "model": ErrorResponse,
        "description": "Error interno o salida del motor que no cumple el ENGINE CONTRACT.",
    },
    503: {"model": ErrorResponse, "description": "El motor no publica la operación pedida."},
}
