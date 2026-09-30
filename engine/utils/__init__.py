"""Utilidades transversales del motor (geo, ids)."""

from __future__ import annotations

from .geo import (
    BoundingBox,
    bbox_from_points,
    distance_deg,
    is_finite_coord,
)
from .ids import analysis_id, comparison_id

__all__ = [
    "BoundingBox",
    "analysis_id",
    "bbox_from_points",
    "comparison_id",
    "distance_deg",
    "is_finite_coord",
]
