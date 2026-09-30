"""Modelos de resultado del motor: análisis individual y comparación A/B."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .condition import Condition
from .enums import MLStatus
from .location import ResolvedLocation
from .serialization import to_jsonable
from .source import Source

#: Versión del esquema de resultado. Forma parte del ENGINE CONTRACT v1.
ENGINE_RESULT_SCHEMA_VERSION = "engine_result/v1"

#: Advertencia de alcance obligatoria en toda salida.
DISCLAIMER = (
    "Evaluación territorial preliminar. ATLAS no emite permisos ni dictámenes "
    "estructurales, no declara una zona como segura y no sustituye estudios "
    "técnicos. La ausencia de información no equivale a ausencia de riesgo."
)


@dataclass(frozen=True)
class CoverageSummary:
    """Resumen agregado de cobertura de datos del análisis.

    Es un CONTEO de estados de dato, NO un porcentaje de riesgo/seguridad.
    """

    expected: int
    data_available: int
    partial_data: int
    insufficient_data: int
    no_registered_condition: int
    blocked_data_validation: int
    by_category: dict[str, dict[str, int]] = field(default_factory=dict)


@dataclass(frozen=True)
class MLInfo:
    """Estado del módulo ML en el resultado (complementario y apagado)."""

    enabled: bool
    status: MLStatus
    reason: str


@dataclass(frozen=True)
class AnalysisResult:
    """Resultado de ``analyze_location`` para una ubicación y tipo de obra.

    Deliberadamente NO contiene: puntuación global de riesgo/seguridad,
    puntuación de factibilidad ni ganador. Esas claves están prohibidas.
    """

    analysis_id: str
    schema_version: str
    engine_version: str
    project_type: str
    location: ResolvedLocation
    #: Amenazas y antecedentes históricos de amenaza.
    conditions: list[Condition]
    #: Factores territoriales medibles (pendiente, uso de suelo, elevación...).
    territorial_factors: list[Condition]
    #: Contexto territorial (infraestructura, accesibilidad, población...).
    context: list[Condition]
    coverage: CoverageSummary
    sources: list[Source]
    limitations: list[str]
    review_items: list[str]
    ml: MLInfo
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict[str, Any]:
        """Devuelve la representación JSON-compatible y determinista."""

        return to_jsonable(self)


@dataclass(frozen=True)
class FactorComparison:
    """Comparación lado a lado de un factor entre A y B.

    No calcula "mejor" ni "peor"; solo describe la diferencia observable.
    """

    factor: str
    label: str
    category: str
    unit: Optional[str]
    value_a: Optional[Any]
    value_b: Optional[Any]
    status_a: str
    status_b: str
    coverage_a: str
    coverage_b: str
    source_a: Optional[str]
    source_b: Optional[str]
    #: Descripción textual y neutra de la diferencia (o su ausencia).
    observable_difference: str
    #: True solo si ambos lados tienen dato comparable y difieren.
    difference_detected: bool
    #: "A", "B" o None: en cuál hay más disponibilidad de dato.
    more_data_available_at: Optional[str]
    #: "A", "B" o None: si la condición solo aparece con dato en un lado.
    condition_only_in: Optional[str]
    limitations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComparisonResult:
    """Resultado de ``compare_locations`` (A vs. B) con la MISMA matriz.

    Prohibido por contrato: ``winner``, ``best_location``, ``safety_score``,
    ``global_risk_score``, ``feasibility_score`` o cualquier ranking absoluto.
    """

    comparison_id: str
    schema_version: str
    engine_version: str
    project_type: str
    location_a: ResolvedLocation
    location_b: ResolvedLocation
    factors: list[FactorComparison]
    coverage_a: CoverageSummary
    coverage_b: CoverageSummary
    limitations: list[str]
    notes: list[str]
    #: True si A y B resuelven a la MISMA localidad censal (comparación trivial).
    #: Señal para el consumidor; el motor no falla por comparar una localidad
    #: consigo misma, pero lo declara de forma explícita.
    same_locality: bool = False
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict[str, Any]:
        """Devuelve la representación JSON-compatible y determinista."""

        return to_jsonable(self)
