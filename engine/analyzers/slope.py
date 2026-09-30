"""Analyzer de pendiente (factor territorial).

La pendiente se deriva de un DEM/MDS. Existe un dataset candidato de terreno/DEM
en poder de Bloque 1, pero mientras el DATA CONTRACT no lo publique como
disponible, el estado por defecto es BLOCKED_DATA_VALIDATION (no INSUFFICIENT):
el dato existe como candidato pero aún no está validado.

Cuando el DATA CONTRACT publique ``slope`` con cobertura, el valor bruto (p. ej.
14 %) se leerá tal cual y NO cambiará con el tipo de obra.
"""

from __future__ import annotations

from typing import Optional

from ..schemas.enums import Category, ConditionStatus, TemporalContext
from ..services.data_source import FactorReading
from .base import BaseAnalyzer


class SlopeAnalyzer(BaseAnalyzer):
    factor = "slope"
    label = "Pendiente del terreno"
    category = Category.TERRITORIAL_FACTOR
    unit = "%"
    default_temporal_context = TemporalContext.CURRENT
    missing_status = ConditionStatus.BLOCKED_DATA_VALIDATION
    data_key = "slope"

    def _meaning(self, status, reading: Optional[FactorReading]) -> str:
        if status == ConditionStatus.DATA_AVAILABLE:
            val = reading.value if reading else None
            return (
                f"Pendiente media aproximada de {val}% derivada del DEM para la "
                "unidad de análisis."
            )
        if status == ConditionStatus.BLOCKED_DATA_VALIDATION:
            return (
                "Existe un dataset candidato de terreno/DEM, pero la pendiente aún "
                "no está validada ni publicada por el DATA CONTRACT."
            )
        return super()._meaning(status, reading)

    def _limitation_text(self, status, reading: Optional[FactorReading]) -> str:
        return (
            "La pendiente depende de la resolución del DEM; un valor puntual no "
            "captura microtopografía. Requiere DEM homogéneo validado."
        )
