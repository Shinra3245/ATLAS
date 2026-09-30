"""Modelo de ubicación de entrada y su resolución territorial."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .enums import AnalysisUnit, AreaStatus


@dataclass(frozen=True)
class Location:
    """Ubicación de entrada para ``analyze_location``.

    El motor solo requiere ``lat``/``lon``. El municipio y la unidad de análisis
    se resuelven internamente contra el área soportada (Irapuato/Celaya).
    """

    lat: float
    lon: float
    #: Identificador opcional de localidad si el llamador ya lo conoce
    #: (p. ej. clave del dataset maestro). Nunca se inventa.
    locality_id: Optional[str] = None
    #: Etiqueta opcional legible provista por el llamador.
    label: Optional[str] = None


@dataclass(frozen=True)
class ResolvedLocation:
    """Ubicación ya resuelta contra el soporte geográfico del MVP."""

    lat: float
    lon: float
    municipality: Optional[str]
    area_status: AreaStatus
    analysis_unit: AnalysisUnit
    locality_id: Optional[str] = None
    label: Optional[str] = None
    notes: list[str] = field(default_factory=list)
