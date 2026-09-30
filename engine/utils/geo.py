"""Utilidades geográficas para la resolución territorial.

IMPORTANTE: el soporte geográfico del MVP se deriva de las localidades REALES
publicadas por el DATA CONTRACT (clave CVEGEO y municipio documentados), no de
cajas inventadas. Este módulo solo aporta primitivas (caja envolvente y
distancia) que las fuentes de datos usan para construir su propia área
soportada a partir de sus localidades.

Las coordenadas del contrato están en `CRS_UNKNOWN`; NO se reproyectan. La
distancia en grados se usa únicamente para asociar una coordenada a la localidad
censal más cercana, nunca para medir en metros.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class BoundingBox:
    """Caja geográfica [lat_min, lat_max] x [lon_min, lon_max]."""

    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float

    def contains(self, lat: float, lon: float) -> bool:
        return (
            self.lat_min <= lat <= self.lat_max
            and self.lon_min <= lon <= self.lon_max
        )

    def expanded(self, margin_deg: float) -> "BoundingBox":
        return BoundingBox(
            lat_min=self.lat_min - margin_deg,
            lat_max=self.lat_max + margin_deg,
            lon_min=self.lon_min - margin_deg,
            lon_max=self.lon_max + margin_deg,
        )


def bbox_from_points(points: Iterable[tuple[float, float]]) -> Optional[BoundingBox]:
    """Construye la caja envolvente de una secuencia de (lat, lon)."""

    lats: list[float] = []
    lons: list[float] = []
    for lat, lon in points:
        if is_finite_coord(lat, lon):
            lats.append(lat)
            lons.append(lon)
    if not lats:
        return None
    return BoundingBox(min(lats), max(lats), min(lons), max(lons))


def distance_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia euclidiana en grados (solo para asociar a la localidad cercana)."""

    return math.hypot(lat1 - lat2, lon1 - lon2)


def is_finite_coord(lat: float, lon: float) -> bool:
    """True si ambas coordenadas son números finitos (no NaN/Inf)."""

    try:
        return math.isfinite(float(lat)) and math.isfinite(float(lon))
    except (TypeError, ValueError):
        return False
