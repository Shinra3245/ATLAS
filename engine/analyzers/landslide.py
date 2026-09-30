"""Analyzer de susceptibilidad de laderas / deslizamientos (amenaza).

Requiere una capa de susceptibilidad con geometría (pendiente en Bloque 1).
Sin ese dato, INSUFFICIENT_DATA; no se infiere estabilidad.
"""

from __future__ import annotations

from typing import Optional

from ..schemas.enums import Category, ConditionStatus, TemporalContext
from ..services.data_source import FactorReading
from .base import BaseAnalyzer


class LandslideAnalyzer(BaseAnalyzer):
    factor = "landslide_susceptibility"
    label = "Susceptibilidad de laderas / deslizamientos"
    category = Category.HAZARD
    default_temporal_context = TemporalContext.CURRENT
    missing_status = ConditionStatus.INSUFFICIENT_DATA
    data_key = "landslide_susceptibility"

    def _meaning(self, status, reading: Optional[FactorReading]) -> str:
        if status == ConditionStatus.DATA_AVAILABLE:
            return "La capa de susceptibilidad reporta un nivel para la unidad de análisis."
        if status == ConditionStatus.NO_REGISTERED_CONDITION:
            return "La capa de susceptibilidad no registra la condición en la cobertura."
        return super()._meaning(status, reading)

    def _limitation_text(self, status, reading: Optional[FactorReading]) -> str:
        return (
            "La susceptibilidad de laderas depende de pendiente, litología y "
            "humedad; requiere DEM adecuado y validación específica."
        )
