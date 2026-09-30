"""Analyzer de fallas/fracturas geológicas (amenaza).

Requiere una capa geológica con geometría (pendiente en Bloque 1). Sin ese
dato, el estado es INSUFFICIENT_DATA: nunca se asume ausencia de fallas.
"""

from __future__ import annotations

from typing import Optional

from ..schemas.enums import Category, ConditionStatus, TemporalContext
from ..services.data_source import FactorReading
from .base import BaseAnalyzer


class FaultsAnalyzer(BaseAnalyzer):
    factor = "faults"
    label = "Fallas / fracturas geológicas"
    category = Category.HAZARD
    default_temporal_context = TemporalContext.CURRENT
    missing_status = ConditionStatus.INSUFFICIENT_DATA
    data_key = "faults"

    def _meaning(self, status, reading: Optional[FactorReading]) -> str:
        if status == ConditionStatus.DATA_AVAILABLE:
            return "La capa geológica indica presencia/proximidad de fallas o fracturas."
        if status == ConditionStatus.NO_REGISTERED_CONDITION:
            return "La capa geológica no registra fallas/fracturas en la cobertura."
        return super()._meaning(status, reading)

    def _limitation_text(self, status, reading: Optional[FactorReading]) -> str:
        return (
            "La caracterización geológica-estructural definitiva requiere estudio "
            "geotécnico específico; este factor es de apoyo preliminar."
        )
