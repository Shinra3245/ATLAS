"""Analyzer de elevación (variable auxiliar).

La elevación disponible en el DATA CONTRACT V1 es la ALTITUD CENSAL de la
localidad (ITER 2020), no un DEM. Es una variable AUXILIAR: apoya la lectura de
otros factores y no es una amenaza por sí misma. NO debe usarse para derivar
pendiente (eso requiere un DEM validado, pendiente en Bloque 1).
"""

from __future__ import annotations

from typing import Optional

from ..schemas.enums import Category, ConditionStatus, TemporalContext
from ..services.data_source import FactorReading
from .base import BaseAnalyzer


class ElevationAnalyzer(BaseAnalyzer):
    factor = "elevation"
    label = "Elevación (altitud censal, auxiliar)"
    category = Category.TERRITORIAL_FACTOR
    unit = "m"
    default_temporal_context = TemporalContext.REFERENCE_PERIOD
    missing_status = ConditionStatus.INSUFFICIENT_DATA
    data_key = "elevation"

    def _meaning(self, status, reading: Optional[FactorReading]) -> str:
        if status == ConditionStatus.DATA_AVAILABLE:
            val = reading.value if reading else None
            return (
                f"Altitud censal de la localidad de {val} m (ITER 2020), variable "
                "auxiliar de terreno."
            )
        return super()._meaning(status, reading)

    def _not_meaning(self, status, reading: Optional[FactorReading]) -> str:
        return (
            "La altitud censal no es un DEM ni la elevación precisa del predio, y "
            "no debe usarse para derivar pendiente. Por sí sola no es una amenaza."
        )

    def _limitation_text(self, status, reading: Optional[FactorReading]) -> str:
        return (
            "Altitud censal de la localidad (ITER 2020) a nivel de punto; no "
            "equivale a un modelo digital de elevación ni a la cota del predio."
        )
