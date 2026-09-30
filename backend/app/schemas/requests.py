"""Solicitudes de análisis y comparación."""

from __future__ import annotations

import math
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core.config import PROJECT_TYPES


class LocationIn(BaseModel):
    """Coordenada en grados decimales. El municipio lo resuelve el motor."""

    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    locality_id: Optional[str] = None
    label: Optional[str] = None

    @field_validator("lat", "lon")
    @classmethod
    def finite_coordinate(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("la coordenada debe ser un número finito")
        return value


class AnalyzeRequest(BaseModel):
    project_type: str = Field(..., pattern="^(" + "|".join(PROJECT_TYPES) + ")$")
    location: LocationIn


class CompareRequest(BaseModel):
    project_type: str = Field(..., pattern="^(" + "|".join(PROJECT_TYPES) + ")$")
    location_a: LocationIn
    location_b: LocationIn
