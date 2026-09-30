"""Cálculo de cobertura de datos.

La cobertura es un CONTEO de estados de dato (cuántos factores disponibles,
parciales, insuficientes, etc.). NO es un porcentaje de riesgo ni de seguridad.
Deliberadamente no se calcula ningún índice agregado interpretable como
"nivel de seguridad".
"""

from __future__ import annotations

from typing import Iterable

from ..schemas.condition import Condition
from ..schemas.enums import ConditionStatus
from ..schemas.result import CoverageSummary


def compute_coverage(conditions: Iterable[Condition]) -> CoverageSummary:
    """Agrega los estados de un conjunto de condiciones en un resumen contable."""

    conditions = list(conditions)
    counts = {
        ConditionStatus.DATA_AVAILABLE: 0,
        ConditionStatus.PARTIAL_DATA: 0,
        ConditionStatus.INSUFFICIENT_DATA: 0,
        ConditionStatus.NO_REGISTERED_CONDITION: 0,
        ConditionStatus.BLOCKED_DATA_VALIDATION: 0,
    }
    by_category: dict[str, dict[str, int]] = {}

    for cond in conditions:
        if cond.status in counts:
            counts[cond.status] += 1
        cat = cond.category.value
        bucket = by_category.setdefault(cat, {})
        bucket[cond.status.value] = bucket.get(cond.status.value, 0) + 1

    return CoverageSummary(
        expected=len(conditions),
        data_available=counts[ConditionStatus.DATA_AVAILABLE],
        partial_data=counts[ConditionStatus.PARTIAL_DATA],
        insufficient_data=counts[ConditionStatus.INSUFFICIENT_DATA],
        no_registered_condition=counts[ConditionStatus.NO_REGISTERED_CONDITION],
        blocked_data_validation=counts[ConditionStatus.BLOCKED_DATA_VALIDATION],
        by_category=by_category,
    )
