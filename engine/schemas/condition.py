"""Modelo de una condición/factor analizado y su explicación."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .enums import (
    Category,
    ConditionStatus,
    CoverageState,
    Priority,
    TemporalContext,
)
from .source import Source


@dataclass(frozen=True)
class Coverage:
    """Cobertura espacial del dato para la unidad analizada."""

    state: CoverageState
    detail: Optional[str] = None


@dataclass(frozen=True)
class Explanation:
    """Explicabilidad estructurada.

    Responde de forma trazable a las preguntas obligatorias del proyecto:
    - ``found``       -> ¿Qué se encontró?
    - ``data_origin`` -> ¿Qué dato lo produjo / de dónde salió?
    - ``operation``   -> ¿Cómo se obtuvo / qué operación se realizó?
    - ``meaning``     -> ¿Qué significa?
    - ``not_meaning`` -> ¿Qué NO significa?
    - ``limitation``  -> ¿Qué limitación tiene?
    """

    found: str
    data_origin: str
    operation: str
    meaning: str
    not_meaning: str
    limitation: str


@dataclass(frozen=True)
class Condition:
    """Una condición/factor/contexto evaluado por el motor.

    Un mismo ``Condition`` sirve para amenazas, factores territoriales y
    contexto; la categoría lo distingue. El ``value`` es el DATO BRUTO y NO
    cambia con el tipo de obra: solo cambian ``priority``, ``explanation`` y
    ``review_items``.
    """

    #: Código estable del factor (p. ej. "flood_history", "slope").
    factor: str
    #: Etiqueta legible.
    label: str
    #: Clasificación semántica (amenaza/histórico/factor/contexto/derivado).
    category: Category
    #: Estado del dato (disponible/parcial/insuficiente/no registrado/...).
    status: ConditionStatus
    #: Cobertura espacial del dato.
    coverage: Coverage
    #: Marco temporal (actual/histórico/...). Clave para no confundir 2014 con hoy.
    temporal_context: TemporalContext
    #: Explicabilidad estructurada.
    explanation: Explanation
    #: Valor bruto del dato (numérico, texto o None si no hay dato).
    value: Optional[Any] = None
    #: Unidad del valor, cuando aplica (p. ej. "%", "m").
    unit: Optional[str] = None
    #: Fuente/procedencia del dato, si existe.
    source: Optional[Source] = None
    #: Limitaciones específicas de esta condición.
    limitations: list[str] = field(default_factory=list)
    #: Prioridad de lectura según el tipo de obra (fijada por contextualización).
    priority: Priority = Priority.CONTEXTUAL
    #: Aspectos que podrían requerir revisión (nunca dictámenes legales).
    review_items: list[str] = field(default_factory=list)
