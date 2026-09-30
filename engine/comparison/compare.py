"""Comparación A/B con la MISMA matriz de análisis.

``compare_locations`` NO usa un motor distinto: llama a ``analyze_location`` para
A y para B con el mismo ``project_type`` y alinea los factores lado a lado.

PROHIBIDO por contrato devolver ``winner``, ``best_location``, ``safety_score``,
``global_risk_score``, ``feasibility_score`` o cualquier ranking absoluto. La
comparación solo describe diferencias observables y disponibilidad de datos.
"""

from __future__ import annotations

from typing import Any, Optional, Union

from ..schemas.condition import Condition
from ..schemas.enums import AreaStatus, ConditionStatus, ProjectType
from ..schemas.result import (
    ENGINE_RESULT_SCHEMA_VERSION,
    AnalysisResult,
    ComparisonResult,
    FactorComparison,
)
from ..services.analyze import (
    ENGINE_VERSION,
    LocationInput,
    ProjectTypeInput,
    _normalize_location,
    _normalize_project_type,
    analyze_location,
)
from ..services.data_source import DataSource
from ..utils.ids import comparison_id

#: Riqueza relativa de un estado (para "dónde hay más dato"). No es riesgo.
_STATUS_RANK = {
    ConditionStatus.DATA_AVAILABLE: 3,
    ConditionStatus.PARTIAL_DATA: 2,
    ConditionStatus.NO_REGISTERED_CONDITION: 1,
    ConditionStatus.BLOCKED_DATA_VALIDATION: 0,
    ConditionStatus.INSUFFICIENT_DATA: 0,
    ConditionStatus.OUTSIDE_SUPPORTED_AREA: 0,
}

_HAS_VALUE = {ConditionStatus.DATA_AVAILABLE, ConditionStatus.PARTIAL_DATA}


def _index_conditions(result: AnalysisResult) -> dict[str, Condition]:
    index: dict[str, Condition] = {}
    for group in (result.conditions, result.territorial_factors, result.context):
        for cond in group:
            index[cond.factor] = cond
    return index


def _ordered_factors(
    result_a: AnalysisResult, result_b: AnalysisResult
) -> list[str]:
    order: list[str] = []
    for result in (result_a, result_b):
        for group in (result.conditions, result.territorial_factors, result.context):
            for cond in group:
                if cond.factor not in order:
                    order.append(cond.factor)
    return order


def _source_name(cond: Optional[Condition]) -> Optional[str]:
    if cond is None or cond.source is None:
        return None
    return cond.source.name


def _fmt(value: Optional[Any], unit: Optional[str]) -> str:
    if value is None:
        return "sin dato"
    return f"{value} {unit}".strip() if unit else f"{value}"


def _compare_factor(
    factor: str, a: Optional[Condition], b: Optional[Condition]
) -> FactorComparison:
    label = (a or b).label  # type: ignore[union-attr]
    category = (a or b).category.value  # type: ignore[union-attr]
    unit = (a and a.unit) or (b and b.unit)

    status_a = a.status if a else ConditionStatus.INSUFFICIENT_DATA
    status_b = b.status if b else ConditionStatus.INSUFFICIENT_DATA
    value_a = a.value if a else None
    value_b = b.value if b else None
    a_has = status_a in _HAS_VALUE and value_a is not None
    b_has = status_b in _HAS_VALUE and value_b is not None

    difference_detected = bool(a_has and b_has and value_a != value_b)

    condition_only_in: Optional[str] = None
    if a_has and not b_has:
        condition_only_in = "A"
    elif b_has and not a_has:
        condition_only_in = "B"

    rank_a = _STATUS_RANK.get(status_a, 0)
    rank_b = _STATUS_RANK.get(status_b, 0)
    if rank_a > rank_b:
        more_data_available_at: Optional[str] = "A"
    elif rank_b > rank_a:
        more_data_available_at = "B"
    else:
        more_data_available_at = None

    if a_has and b_has:
        if difference_detected:
            observable = f"Diferencia observable: A = {_fmt(value_a, unit)}, B = {_fmt(value_b, unit)}."
        else:
            observable = f"Sin diferencia observable en el valor (A = B = {_fmt(value_a, unit)})."
    elif condition_only_in:
        present = "A" if condition_only_in == "A" else "B"
        observable = (
            f"Dato disponible solo en {present}; el otro lado no tiene dato "
            "comparable (no interpretar como mejor/peor)."
        )
    else:
        observable = (
            "Sin dato comparable en A ni B para este factor "
            f"(A: {status_a.value}, B: {status_b.value})."
        )

    limitations: list[str] = []
    for cond in (a, b):
        if cond is not None:
            for lim in cond.limitations:
                if lim not in limitations:
                    limitations.append(lim)

    return FactorComparison(
        factor=factor,
        label=label,
        category=category,
        unit=unit,
        value_a=value_a,
        value_b=value_b,
        status_a=status_a.value,
        status_b=status_b.value,
        coverage_a=(a.coverage.state.value if a else "missing"),
        coverage_b=(b.coverage.state.value if b else "missing"),
        source_a=_source_name(a),
        source_b=_source_name(b),
        observable_difference=observable,
        difference_detected=difference_detected,
        more_data_available_at=more_data_available_at,
        condition_only_in=condition_only_in,
        limitations=limitations,
    )


def compare_locations(
    location_a: LocationInput,
    location_b: LocationInput,
    project_type: ProjectTypeInput,
    data_source: Optional[DataSource] = None,
    data_source_b: Optional[DataSource] = None,
) -> ComparisonResult:
    """Compara A y B bajo los MISMOS criterios y tipo de obra.

    Ambas ubicaciones se analizan con ``analyze_location``; el resultado alinea
    cada factor lado a lado sin declarar ganador ni puntuación global.
    """

    pt = _normalize_project_type(project_type)
    loc_a = _normalize_location(location_a)
    loc_b = _normalize_location(location_b)

    result_a = analyze_location(loc_a, pt, data_source=data_source)
    result_b = analyze_location(
        loc_b, pt, data_source=data_source_b if data_source_b is not None else data_source
    )

    index_a = _index_conditions(result_a)
    index_b = _index_conditions(result_b)

    factors = [
        _compare_factor(factor, index_a.get(factor), index_b.get(factor))
        for factor in _ordered_factors(result_a, result_b)
    ]

    notes: list[str] = [
        "La comparación usa la misma matriz de factores para A y B.",
        "No se declara un ganador ni una puntuación global; solo diferencias "
        "observables y disponibilidad de datos.",
    ]
    for label, result in (("A", result_a), ("B", result_b)):
        if result.location.area_status == AreaStatus.OUTSIDE_SUPPORTED_AREA:
            notes.append(
                f"La ubicación {label} está fuera del área soportada (Irapuato/Celaya)."
            )

    # Señal de identidad: si A y B resuelven a la MISMA localidad censal, la
    # comparación es trivial (mismos datos). Se expone para que el consumidor
    # (Backend) pueda rechazar o advertir; el motor no falla por ello.
    loc_id_a = result_a.location.locality_id
    loc_id_b = result_b.location.locality_id
    same_locality = bool(loc_id_a is not None and loc_id_a == loc_id_b)
    if same_locality:
        notes.append(
            "A y B resuelven a la MISMA localidad censal "
            f"({loc_id_a}); no hay comparación efectiva entre localidades distintas."
        )

    limitations = [
        "Comparación preliminar de apoyo; no sustituye estudios técnicos.",
        "La ausencia de información en un lado no implica menor riesgo en el otro.",
    ]

    # ID determinista basado en coordenadas, tipo de obra y la IDENTIDAD de
    # ambos análisis (que ya incluyen la localidad resuelta de cada lado).
    cid = comparison_id(
        loc_a.lat,
        loc_a.lon,
        loc_b.lat,
        loc_b.lon,
        pt.value,
        f"{result_a.analysis_id}:{result_b.analysis_id}",
    )

    return ComparisonResult(
        comparison_id=cid,
        schema_version=ENGINE_RESULT_SCHEMA_VERSION,
        engine_version=ENGINE_VERSION,
        project_type=pt.value,
        location_a=result_a.location,
        location_b=result_b.location,
        factors=factors,
        coverage_a=result_a.coverage,
        coverage_b=result_b.coverage,
        limitations=limitations,
        notes=notes,
        same_locality=same_locality,
    )
