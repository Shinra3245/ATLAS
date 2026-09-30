"""Analyzers de CONTEXTO territorial.

Estos factores (hidrología, vialidad, ferrocarril, industria, electricidad,
población, servicios, movilidad, agricultura, vegetación, precipitación...) son
CONTEXTO o infraestructura. NUNCA se convierten automáticamente en amenaza ni
en penalización de riesgo. Solo aportan lectura territorial cuando su
significado es defendible.

Se implementa un ``ContextAnalyzer`` genérico configurable para no duplicar
lógica, y una fábrica ``context_analyzers()`` con el conjunto del MVP.
"""

from __future__ import annotations

from typing import Optional

from ..schemas.enums import Category, ConditionStatus, TemporalContext
from ..services.data_source import FactorReading
from .base import BaseAnalyzer


class ContextAnalyzer(BaseAnalyzer):
    """Analyzer genérico para un factor de contexto territorial."""

    category = Category.CONTEXT

    def __init__(
        self,
        factor: str,
        label: str,
        *,
        unit: Optional[str] = None,
        temporal_context: TemporalContext = TemporalContext.CURRENT,
        missing_status: ConditionStatus = ConditionStatus.INSUFFICIENT_DATA,
        meaning_available: Optional[str] = None,
        missing_meaning: Optional[str] = None,
    ) -> None:
        self.factor = factor
        self.label = label
        self.unit = unit
        self.default_temporal_context = temporal_context
        self.missing_status = missing_status
        self.data_key = factor
        self._meaning_available = meaning_available
        self._missing_meaning = missing_meaning

    def _meaning(self, status, reading: Optional[FactorReading]) -> str:
        if status == ConditionStatus.DATA_AVAILABLE and self._meaning_available:
            return self._meaning_available
        if (
            status
            in (
                ConditionStatus.INSUFFICIENT_DATA,
                ConditionStatus.BLOCKED_DATA_VALIDATION,
            )
            and self._missing_meaning
        ):
            return self._missing_meaning
        return super()._meaning(status, reading)

    def _not_meaning(self, status, reading: Optional[FactorReading]) -> str:
        # Refuerzo del guardarraíl: contexto != amenaza.
        base = (
            "Es una variable de contexto/infraestructura; no es una amenaza ni un "
            "nivel de riesgo por sí misma."
        )
        parent = super()._not_meaning(status, reading)
        if status in (
            ConditionStatus.DATA_AVAILABLE,
            ConditionStatus.PARTIAL_DATA,
            ConditionStatus.NO_REGISTERED_CONDITION,
        ):
            return base
        return f"{base} {parent}"

    def _limitation_text(self, status, reading: Optional[FactorReading]) -> str:
        return (
            "Variable de contexto territorial; su uso como factor explicativo "
            "requiere una interpretación con significado defendible."
        )


def _base_context_analyzers() -> list[ContextAnalyzer]:
    """Conjunto de analyzers de contexto del MVP."""

    return [
        ContextAnalyzer(
            "hydrography_proximity",
            "Proximidad a hidrografía (río/canal/cuerpo de agua)",
            unit="m",
            meaning_available=(
                "Distancia a rasgos hidrográficos; contexto para lectura de "
                "inundación cuando exista la capa espacial."
            ),
        ),
        ContextAnalyzer(
            "road_proximity",
            "Proximidad a red carretera/vial",
            unit="m",
        ),
        ContextAnalyzer(
            "rail_proximity",
            "Proximidad a red ferroviaria",
            unit="m",
        ),
        ContextAnalyzer(
            "industry_proximity",
            "Proximidad a industria",
            unit="m",
        ),
        ContextAnalyzer(
            "power_infrastructure_proximity",
            "Proximidad a infraestructura eléctrica",
            unit="m",
        ),
        ContextAnalyzer(
            "population",
            "Población (contexto de demanda)",
        ),
        ContextAnalyzer(
            "services_coverage",
            "Cobertura de servicios (eléctrica/drenaje)",
            unit="%",
        ),
        ContextAnalyzer(
            "mobility",
            "Movilidad / accesibilidad",
        ),
        ContextAnalyzer(
            "agriculture_vegetation",
            "Agricultura / vegetación",
        ),
        # Clima 2024-2026: publicado por estación (una por municipio), CONTEXT_ONLY.
        # No es unible a la localidad por cercanía (DATA CONTRACT V1); a nivel de
        # localidad no hay dato utilizable.
        ContextAnalyzer(
            "precipitation",
            "Precipitación (clima 2024–2026, por estación)",
            unit="mm",
            temporal_context=TemporalContext.CURRENT,
            missing_status=ConditionStatus.INSUFFICIENT_DATA,
            missing_meaning=(
                "Existe una serie mensual de precipitación 2024–2026, pero es de "
                "estación (una por municipio), CONTEXT_ONLY, y el DATA CONTRACT V1 "
                "no permite unirla a la localidad por cercanía. Sin dato a nivel "
                "de la unidad de análisis."
            ),
        ),
    ]


def context_analyzers() -> list[ContextAnalyzer]:
    """Conjunto de analyzers de contexto del MVP, más el contexto municipal."""

    from .municipal import municipal_context_analyzers

    return [*_base_context_analyzers(), *municipal_context_analyzers()]
