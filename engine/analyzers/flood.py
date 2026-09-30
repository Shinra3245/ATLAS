"""Analyzer de antecedente histórico de inundación.

El único dato disponible en el dataset maestro es un indicador CENSAL de
inundación de 2014. Por tanto se trata como ``hazard_history`` con marco
temporal ``historical`` y NUNCA se presenta como riesgo actual 2026.

La inundación como amenaza ACTUAL requiere una capa espacial moderna con
geometría y fecha (pendiente en Bloque 1); mientras no exista, el factor de
inundación actual permanece como información insuficiente.
"""

from __future__ import annotations

from typing import Optional

from ..schemas.enums import Category, ConditionStatus, CoverageState, TemporalContext
from ..services.data_source import FactorReading
from .base import BaseAnalyzer


class FloodHistoryAnalyzer(BaseAnalyzer):
    factor = "flood_history"
    label = "Antecedente histórico de inundación (censo 2014)"
    category = Category.HAZARD_HISTORY
    default_temporal_context = TemporalContext.HISTORICAL
    missing_status = ConditionStatus.INSUFFICIENT_DATA
    data_key = "flood_history"

    def _status_from_reading(self, reading: FactorReading) -> ConditionStatus:
        # Defensa semántica: un antecedente "sin daño" (False/0) es una condición
        # cubierta pero NO registrada; jamás debe leerse como daño reportado.
        if reading.value is None and not reading.no_registered_condition:
            return self.missing_status
        if reading.no_registered_condition or reading.value in (False, 0, "0"):
            return ConditionStatus.NO_REGISTERED_CONDITION
        if reading.coverage_state == CoverageState.PARTIAL:
            return ConditionStatus.PARTIAL_DATA
        return ConditionStatus.DATA_AVAILABLE

    def _meaning(self, status, reading: Optional[FactorReading]) -> str:
        if status == ConditionStatus.DATA_AVAILABLE:
            return (
                "La localidad reportó antecedente de inundación en el registro "
                "censal de 2014. Es un dato histórico de referencia."
            )
        if status == ConditionStatus.NO_REGISTERED_CONDITION:
            return (
                "El registro censal de 2014 no marcó antecedente de inundación "
                "para la localidad."
            )
        return super()._meaning(status, reading)

    def _not_meaning(self, status, reading: Optional[FactorReading]) -> str:
        base = (
            "No representa el riesgo de inundación actual (2026): es un "
            "antecedente histórico de 2014, no una capa espacial vigente."
        )
        if status == ConditionStatus.NO_REGISTERED_CONDITION:
            return (
                base
                + " Que no se registrara en 2014 no significa que el sitio sea seguro hoy."
            )
        if status == ConditionStatus.INSUFFICIENT_DATA:
            return (
                "No significa riesgo bajo; no hay antecedente histórico utilizable "
                "para esta unidad y no existe aún capa de inundación actual."
            )
        return base

    def _limitation_text(self, status, reading: Optional[FactorReading]) -> str:
        return (
            "Indicador histórico censal 2014 a nivel localidad; no es cartografía "
            "de inundación ni representa el estado hidrológico presente."
        )
