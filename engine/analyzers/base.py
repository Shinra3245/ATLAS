"""Analyzer base: traduce lecturas crudas a condiciones explicables.

Todos los analyzers comparten la lógica de:
- pedir el factor a la fuente de datos;
- derivar un ESTADO semántico (nunca una conclusión de riesgo);
- construir una explicación estructurada que responde las preguntas
  obligatorias de explicabilidad.

Los guardarraíles críticos viven aquí como texto por defecto de
``not_meaning`` para cada estado, de modo que ningún analyzer pueda,
por omisión, convertir ausencia de datos en "riesgo bajo".
"""

from __future__ import annotations

from abc import ABC
from typing import Optional

from ..schemas.condition import Condition, Coverage, Explanation
from ..schemas.enums import (
    Category,
    ConditionStatus,
    CoverageState,
    Priority,
    TemporalContext,
)
from ..services.data_source import DataSource, FactorReading, LocalityResolution


class BaseAnalyzer(ABC):
    """Clase base de un analyzer de factor."""

    factor: str = "unknown"
    label: str = "Factor"
    category: Category = Category.TERRITORIAL_FACTOR
    unit: Optional[str] = None
    default_temporal_context: TemporalContext = TemporalContext.CURRENT
    #: Estado cuando NO hay dato alguno para el factor.
    missing_status: ConditionStatus = ConditionStatus.INSUFFICIENT_DATA
    #: Clave de datos solicitada a la fuente (por defecto == factor).
    data_key: Optional[str] = None

    # ------------------------------------------------------------------ API

    def key(self) -> str:
        return self.data_key or self.factor

    def analyze(
        self, data_source: DataSource, resolution: LocalityResolution
    ) -> Condition:
        reading = data_source.read_factor(resolution, self.key())
        if reading is None:
            return self._build_missing()
        status = self._status_from_reading(reading)
        return self._build_present(reading, status)

    # --------------------------------------------------------------- status

    def _status_from_reading(self, reading: FactorReading) -> ConditionStatus:
        # Un valor no utilizable (None) nunca es "dato disponible" ni "parcial":
        # aunque la cobertura declarada sea parcial, sin valor no hay dato.
        if reading.no_registered_condition:
            return ConditionStatus.NO_REGISTERED_CONDITION
        if reading.value is None:
            return self.missing_status
        if reading.coverage_state == CoverageState.MISSING:
            return self.missing_status
        if reading.coverage_state == CoverageState.PARTIAL:
            return ConditionStatus.PARTIAL_DATA
        return ConditionStatus.DATA_AVAILABLE

    # ----------------------------------------------------------- construction

    def _build_present(
        self, reading: FactorReading, status: ConditionStatus
    ) -> Condition:
        coverage = Coverage(state=reading.coverage_state, detail=reading.coverage_detail)
        return Condition(
            factor=self.factor,
            label=self.label,
            category=self.category,
            status=status,
            coverage=coverage,
            temporal_context=reading.temporal_context,
            explanation=self._explanation(status, reading),
            value=reading.value,
            unit=reading.unit if reading.unit is not None else self.unit,
            source=reading.source,
            limitations=self._limitations(status, reading),
            priority=Priority.CONTEXTUAL,
            review_items=[],
        )

    def _build_missing(self) -> Condition:
        status = self.missing_status
        coverage = Coverage(state=CoverageState.MISSING, detail=self._missing_detail())
        return Condition(
            factor=self.factor,
            label=self.label,
            category=self.category,
            status=status,
            coverage=coverage,
            temporal_context=TemporalContext.NOT_APPLICABLE,
            explanation=self._explanation(status, None),
            value=None,
            unit=self.unit,
            source=None,
            limitations=self._limitations(status, None),
            priority=Priority.CONTEXTUAL,
            review_items=[],
        )

    # --------------------------------------------------------- explicabilidad

    def _explanation(
        self, status: ConditionStatus, reading: Optional[FactorReading]
    ) -> Explanation:
        return Explanation(
            found=self._found(status, reading),
            data_origin=self._data_origin(status, reading),
            operation=self._operation(status, reading),
            meaning=self._meaning(status, reading),
            not_meaning=self._not_meaning(status, reading),
            limitation=self._limitation_text(status, reading),
        )

    # Hooks con valores por defecto; los analyzers concretos afinan el texto.

    def _found(self, status: ConditionStatus, reading: Optional[FactorReading]) -> str:
        if reading is not None and status in (
            ConditionStatus.DATA_AVAILABLE,
            ConditionStatus.PARTIAL_DATA,
        ):
            unit = f" {reading.unit}" if reading.unit else ""
            return f"{self.label}: {reading.value}{unit}."
        if status == ConditionStatus.NO_REGISTERED_CONDITION:
            return f"{self.label}: la fuente no registra la condición en su cobertura."
        if status == ConditionStatus.BLOCKED_DATA_VALIDATION:
            return f"{self.label}: dataset candidato pendiente de validación por Bloque 1."
        return f"{self.label}: sin información suficiente."

    def _data_origin(
        self, status: ConditionStatus, reading: Optional[FactorReading]
    ) -> str:
        if reading is not None and reading.source is not None:
            src = reading.source
            parts = [src.name]
            if src.date_or_version:
                parts.append(f"({src.date_or_version})")
            return " ".join(parts)
        return "Sin fuente disponible en el DATA CONTRACT actual."

    def _operation(
        self, status: ConditionStatus, reading: Optional[FactorReading]
    ) -> str:
        if status in (ConditionStatus.DATA_AVAILABLE, ConditionStatus.PARTIAL_DATA):
            return (
                "Lectura directa del valor publicado para la unidad de análisis, "
                "sin transformación adicional."
            )
        if status == ConditionStatus.NO_REGISTERED_CONDITION:
            return "Verificación de cobertura de la fuente sin registro del evento."
        return "No se realizó ninguna operación por falta de dato utilizable."

    def _meaning(
        self, status: ConditionStatus, reading: Optional[FactorReading]
    ) -> str:
        # Por defecto genérico; los analyzers concretos lo especializan.
        if status == ConditionStatus.DATA_AVAILABLE:
            return f"Se dispone del valor de {self.label.lower()} para la unidad."
        if status == ConditionStatus.PARTIAL_DATA:
            return (
                f"Se dispone de {self.label.lower()} con cobertura parcial; "
                "leer con cautela."
            )
        if status == ConditionStatus.NO_REGISTERED_CONDITION:
            return "La fuente cubre la zona y no registra la condición."
        if status == ConditionStatus.BLOCKED_DATA_VALIDATION:
            return "Hay un dataset candidato aún no validado ni publicado."
        return "No hay información suficiente para pronunciarse."

    def _not_meaning(
        self, status: ConditionStatus, reading: Optional[FactorReading]
    ) -> str:
        # GUARDARRAÍLES CRÍTICOS: no derivar seguridad/riesgo de la ausencia.
        if status == ConditionStatus.INSUFFICIENT_DATA:
            return (
                "No significa riesgo bajo ni ausencia del factor; significa que "
                "no hay información suficiente."
            )
        if status == ConditionStatus.NO_REGISTERED_CONDITION:
            return (
                "No significa que el sitio sea seguro; significa que la fuente no "
                "registró la condición dentro de su cobertura."
            )
        if status == ConditionStatus.BLOCKED_DATA_VALIDATION:
            return (
                "No significa ausencia del factor; el dataset candidato aún no está "
                "validado ni publicado por Bloque 1."
            )
        if status == ConditionStatus.PARTIAL_DATA:
            return (
                "No representa a toda la unidad de análisis; la cobertura es parcial."
            )
        return "No constituye un dictamen técnico ni una medición certificada."

    def _limitation_text(
        self, status: ConditionStatus, reading: Optional[FactorReading]
    ) -> str:
        return (
            "Evaluación preliminar de apoyo; no sustituye estudios técnicos ni "
            "levantamientos de campo."
        )

    def _limitations(
        self, status: ConditionStatus, reading: Optional[FactorReading]
    ) -> list[str]:
        limitations = [self._limitation_text(status, reading)]
        if status == ConditionStatus.PARTIAL_DATA:
            limitations.append("Cobertura parcial: el valor puede no generalizarse.")
        if reading is not None and (
            reading.temporal_context == TemporalContext.REFERENCE_PERIOD
        ):
            limitations.append(
                "Dato de un período de referencia fechado (censo 2020); no es una "
                "observación actual (2026) y puede haber cambiado."
            )
        return limitations

    def _missing_detail(self) -> str:
        if self.missing_status == ConditionStatus.BLOCKED_DATA_VALIDATION:
            return "Dataset candidato pendiente de validación/publicación por Bloque 1."
        return "El DATA CONTRACT no publica este factor con cobertura para la unidad."
