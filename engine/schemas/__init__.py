"""Esquemas y tipos del motor analítico (contratos internos de Bloque 2).

Reexporta los tipos públicos que forman parte del ENGINE CONTRACT v1.
"""

from __future__ import annotations

from .condition import Condition, Coverage, Explanation
from .enums import (
    AnalysisUnit,
    AreaStatus,
    Category,
    ConditionStatus,
    CoverageState,
    MLStatus,
    Priority,
    ProjectType,
    TemporalContext,
)
from .location import Location, ResolvedLocation
from .result import (
    DISCLAIMER,
    ENGINE_RESULT_SCHEMA_VERSION,
    AnalysisResult,
    ComparisonResult,
    CoverageSummary,
    FactorComparison,
    MLInfo,
)
from .serialization import to_jsonable
from .source import Source

__all__ = [
    "AnalysisResult",
    "AnalysisUnit",
    "AreaStatus",
    "Category",
    "ComparisonResult",
    "Condition",
    "ConditionStatus",
    "Coverage",
    "CoverageState",
    "CoverageSummary",
    "DISCLAIMER",
    "ENGINE_RESULT_SCHEMA_VERSION",
    "Explanation",
    "FactorComparison",
    "Location",
    "MLInfo",
    "MLStatus",
    "Priority",
    "ProjectType",
    "ResolvedLocation",
    "Source",
    "TemporalContext",
    "to_jsonable",
]
