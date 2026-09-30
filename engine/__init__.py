"""ATLAS — Motor analítico (Bloque 2).

API pública estable para el Bloque 3 (Backend). Integrar leyendo únicamente
``engine/contracts/ENGINE_CONTRACT_V1.md``; no depender de estructuras internas.

Uso mínimo:

    from engine import analyze_location, compare_locations

    result = analyze_location({"lat": 20.67, "lon": -101.35}, "building")
    payload = result.to_dict()

    cmp = compare_locations(
        {"lat": 20.67, "lon": -101.35},
        {"lat": 20.52, "lon": -100.81},
        "building",
    )

El motor funciona SIN Machine Learning. La ausencia de datos nunca se traduce
en "riesgo bajo" ni se generan puntuaciones globales o ganadores automáticos.
"""

from __future__ import annotations

from .comparison import compare_locations
from .schemas import (
    AnalysisResult,
    Category,
    ComparisonResult,
    Condition,
    ConditionStatus,
    ProjectType,
)
from .services import (
    ENGINE_VERSION,
    ContractDataSource,
    DataSource,
    FixtureDataSource,
    InvalidLocationError,
    InvalidProjectTypeError,
    analyze_location,
    default_data_source,
    list_layers,
    list_locations,
    list_sources,
    load_fixture,
    ml_status,
)

__version__ = "1.0.0-mvp"

__all__ = [
    "AnalysisResult",
    "Category",
    "ComparisonResult",
    "Condition",
    "ConditionStatus",
    "ContractDataSource",
    "DataSource",
    "ENGINE_VERSION",
    "FixtureDataSource",
    "InvalidLocationError",
    "InvalidProjectTypeError",
    "ProjectType",
    "__version__",
    "analyze_location",
    "compare_locations",
    "default_data_source",
    "list_layers",
    "list_locations",
    "list_sources",
    "load_fixture",
    "ml_status",
]
