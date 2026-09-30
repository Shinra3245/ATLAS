"""Analyzer de uso de suelo (factor territorial).

El uso de suelo actual requiere la capa vigente con geometría. Las series
históricas (Serie I) son ANTECEDENTE y no representan el estado actual; si la
lectura llega marcada como histórica, se conserva ese marco temporal.
"""

from __future__ import annotations

from typing import Optional

from ..schemas.enums import Category, ConditionStatus, TemporalContext
from ..services.data_source import FactorReading
from .base import BaseAnalyzer


class LandUseAnalyzer(BaseAnalyzer):
    factor = "land_use"
    label = "Uso de suelo"
    category = Category.TERRITORIAL_FACTOR
    default_temporal_context = TemporalContext.CURRENT
    missing_status = ConditionStatus.INSUFFICIENT_DATA
    data_key = "land_use"

    def _meaning(self, status, reading: Optional[FactorReading]) -> str:
        if status == ConditionStatus.DATA_AVAILABLE:
            temporal = reading.temporal_context if reading else None
            if temporal == TemporalContext.HISTORICAL:
                return (
                    "Clase de uso de suelo según serie HISTÓRICA; es antecedente de "
                    "cobertura, no el estado actual."
                )
            return "Clase de uso de suelo publicada para la unidad de análisis."
        return super()._meaning(status, reading)

    def _not_meaning(self, status, reading: Optional[FactorReading]) -> str:
        if (
            reading is not None
            and reading.temporal_context == TemporalContext.HISTORICAL
        ):
            return (
                "No representa el uso de suelo presente ni la clasificación oficial "
                "vigente; es un antecedente histórico."
            )
        return super()._not_meaning(status, reading)

    def _limitation_text(self, status, reading: Optional[FactorReading]) -> str:
        return (
            "La compatibilidad de uso de suelo definitiva depende del instrumento "
            "de planeación municipal vigente, no incluido en este factor."
        )
