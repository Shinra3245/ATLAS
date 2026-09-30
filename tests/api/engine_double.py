"""Doble de motor SOLO para pruebas de la API.

No es el motor analítico. Cada fuente lleva la marca TEST_FIXTURE.
No calcula riesgo, ganador ni porcentajes.
"""

from __future__ import annotations

from typing import Any, Optional

from app.core.config import DEFAULT_ML_REASON, DEFAULT_ML_STATUS
from app.core.errors import EngineUnavailableError
from engine.schemas import (
    ENGINE_RESULT_SCHEMA_VERSION,
    AnalysisResult,
    AnalysisUnit,
    AreaStatus,
    Category,
    ComparisonResult,
    Condition,
    ConditionStatus,
    Coverage,
    CoverageState,
    CoverageSummary,
    Explanation,
    FactorComparison,
    MLInfo,
    MLStatus,
    Priority,
    ResolvedLocation,
    Source,
    TemporalContext,
)


def _coverage_state(status: ConditionStatus) -> CoverageState:
    if status is ConditionStatus.PARTIAL_DATA:
        return CoverageState.PARTIAL
    if status is ConditionStatus.DATA_AVAILABLE:
        return CoverageState.AVAILABLE
    return CoverageState.MISSING


def _condition(status: ConditionStatus) -> Condition:
    return Condition(
        factor="test_factor",
        label="TEST_FIXTURE factor",
        category=Category.TERRITORIAL_FACTOR,
        status=status,
        coverage=Coverage(
            state=_coverage_state(status),
            detail="TEST_FIXTURE",
        ),
        temporal_context=TemporalContext.CURRENT,
        explanation=Explanation(
            found="TEST_FIXTURE",
            data_origin="TEST_FIXTURE",
            operation="Doble de prueba de la API. No es un cálculo del motor.",
            meaning="Estado de dato simulado para comprobar que la API lo conserva.",
            not_meaning="No significa riesgo bajo, seguridad ni factibilidad.",
            limitation="Dato simulado. No proviene de una fuente real.",
        ),
        value=None,
        unit=None,
        source=Source.test_fixture("fixture:test_factor", "factor de prueba"),
        limitations=["TEST_FIXTURE"],
        priority=Priority.CONTEXTUAL,
        review_items=[],
    )


def _summary(status: ConditionStatus) -> CoverageSummary:
    return CoverageSummary(
        expected=1,
        data_available=1 if status is ConditionStatus.DATA_AVAILABLE else 0,
        partial_data=1 if status is ConditionStatus.PARTIAL_DATA else 0,
        insufficient_data=1 if status is ConditionStatus.INSUFFICIENT_DATA else 0,
        no_registered_condition=0,
        blocked_data_validation=0,
    )


def _resolved(
    lat: float,
    lon: float,
    municipality: str,
    locality_id: Optional[str] = None,
    label: Optional[str] = None,
) -> ResolvedLocation:
    return ResolvedLocation(
        lat=lat,
        lon=lon,
        municipality=municipality,
        area_status=AreaStatus.SUPPORTED,
        analysis_unit=AnalysisUnit.UNDETERMINED,
        locality_id=locality_id,
        label=label,
        notes=["TEST_FIXTURE"],
    )


class FixtureEngineAdapter:
    """Sustituye al adapter real dentro de TestClient."""

    def __init__(self, mode: str = "available") -> None:
        self.mode = mode

    def resolve_municipality(self, lat: float, lon: float, locality_id: Optional[str] = None) -> Optional[str]:
        from engine.services.data_source import default_data_source

        resolution = default_data_source().resolve(lat, lon, locality_id=locality_id)
        status = resolution.resolved.area_status
        status_value = status.value if hasattr(status, "value") else str(status)
        if status_value != "supported":
            return None
        return resolution.resolved.municipality

    def analyze(
        self,
        project_type: str,
        lat: float,
        lon: float,
        locality_id: Optional[str] = None,
        label: Optional[str] = None,
    ) -> dict[str, Any]:
        if self.mode == "unavailable":
            raise EngineUnavailableError("analyze_location no está publicado")
        status = {
            "partial": ConditionStatus.PARTIAL_DATA,
            "insufficient": ConditionStatus.INSUFFICIENT_DATA,
        }.get(self.mode, ConditionStatus.DATA_AVAILABLE)
        municipality = self.resolve_municipality(lat, lon) or "Irapuato"
        result = AnalysisResult(
            analysis_id="an_test_fixture",
            schema_version=ENGINE_RESULT_SCHEMA_VERSION,
            engine_version="test-double",
            project_type=project_type,
            location=_resolved(lat, lon, municipality),
            conditions=[_condition(status)],
            territorial_factors=[],
            context=[],
            coverage=_summary(status),
            sources=[Source.test_fixture("fixture:analysis", "análisis de prueba")],
            limitations=["TEST_FIXTURE. Este cuerpo no es un resultado del motor real."],
            review_items=[],
            ml=MLInfo(
                enabled=False,
                status=MLStatus.DISABLED_PENDING_TARGET_VALIDATION,
                reason="TEST_FIXTURE",
            ),
        )
        return result.to_dict()

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
        if self.mode == "unavailable":
            raise EngineUnavailableError("compare_locations no está publicado")
        status = ConditionStatus.DATA_AVAILABLE
        factor = FactorComparison(
            factor="test_factor",
            label="TEST_FIXTURE factor",
            category=Category.TERRITORIAL_FACTOR.value,
            unit=None,
            value_a=None,
            value_b=None,
            status_a=status.value,
            status_b=status.value,
            coverage_a=CoverageState.AVAILABLE.value,
            coverage_b=CoverageState.AVAILABLE.value,
            source_a="fixture:test_factor",
            source_b="fixture:test_factor",
            observable_difference="TEST_FIXTURE: no hay diferencia calculada.",
            difference_detected=False,
            more_data_available_at=None,
            condition_only_in=None,
            limitations=["TEST_FIXTURE"],
        )
        result = ComparisonResult(
            comparison_id="cmp_test_fixture",
            schema_version=ENGINE_RESULT_SCHEMA_VERSION,
            engine_version="test-double",
            project_type=project_type,
            location_a=_resolved(lat_a, lon_a, "Irapuato", locality_id_a, label_a),
            location_b=_resolved(lat_b, lon_b, "Celaya", locality_id_b, label_b),
            factors=[factor],
            coverage_a=_summary(status),
            coverage_b=_summary(status),
            limitations=["TEST_FIXTURE. Esta comparación no elige un ganador."],
            notes=["TEST_FIXTURE"],
        )
        return result.to_dict()

    def list_sources(self) -> None:
        return None

    def list_layers(self) -> None:
        return None

    def list_locations(self) -> None:
        return None

    def ml_status(self) -> dict[str, Any]:
        return {
            "enabled": False,
            "status": DEFAULT_ML_STATUS,
            "reason": DEFAULT_ML_REASON,
        }
