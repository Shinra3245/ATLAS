"""Registro de analyzers del motor.

El orden es estable y determinista. Los factores NÚCLEO (amenazas y factores
territoriales) van primero; el contexto después. Este registro es la única
fuente de verdad sobre qué factores existen y en qué orden se reportan.
"""

from __future__ import annotations

from .base import BaseAnalyzer
from .context import ContextAnalyzer, context_analyzers
from .elevation import ElevationAnalyzer
from .faults import FaultsAnalyzer
from .flood import FloodHistoryAnalyzer
from .landslide import LandslideAnalyzer
from .landuse import LandUseAnalyzer
from .slope import SlopeAnalyzer

#: Analyzers de factores núcleo (amenazas + factores territoriales), en orden.
CORE_ANALYZERS: list[BaseAnalyzer] = [
    FloodHistoryAnalyzer(),
    FaultsAnalyzer(),
    LandslideAnalyzer(),
    SlopeAnalyzer(),
    LandUseAnalyzer(),
    ElevationAnalyzer(),
]


def all_analyzers() -> list[BaseAnalyzer]:
    """Lista completa y ordenada de analyzers (núcleo + contexto)."""

    return [*CORE_ANALYZERS, *context_analyzers()]


__all__ = [
    "BaseAnalyzer",
    "CORE_ANALYZERS",
    "ContextAnalyzer",
    "ElevationAnalyzer",
    "FaultsAnalyzer",
    "FloodHistoryAnalyzer",
    "LandUseAnalyzer",
    "LandslideAnalyzer",
    "SlopeAnalyzer",
    "all_analyzers",
    "context_analyzers",
]
