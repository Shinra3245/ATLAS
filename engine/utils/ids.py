"""Identificadores deterministas.

El motor es reproducible: la misma entrada produce el mismo resultado. Por eso
los identificadores se derivan por hash de la entrada canónica, sin relojes ni
aleatoriedad.
"""

from __future__ import annotations

import hashlib


def _round_coord(value: float) -> str:
    """Normaliza una coordenada a 6 decimales para un hash estable."""

    return f"{value:.6f}"


def analysis_id(
    lat: float,
    lon: float,
    project_type: str,
    data_version: str,
    locality_id: str | None = None,
) -> str:
    """ID determinista de un análisis individual.

    Incluye la IDENTIDAD de la localidad resuelta: dos consultas con las mismas
    coordenadas pero distinta localidad (p. ej. resueltas por ``locality_id``)
    entregan datos distintos y por tanto deben tener identificadores distintos.
    """

    raw = "|".join(
        [
            "analysis",
            _round_coord(lat),
            _round_coord(lon),
            locality_id or "-",
            project_type,
            data_version,
        ]
    )
    return "an_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def comparison_id(
    lat_a: float,
    lon_a: float,
    lat_b: float,
    lon_b: float,
    project_type: str,
    data_version: str,
) -> str:
    """ID determinista de una comparación A/B."""

    raw = "|".join(
        [
            "comparison",
            _round_coord(lat_a),
            _round_coord(lon_a),
            _round_coord(lat_b),
            _round_coord(lon_b),
            project_type,
            data_version,
        ]
    )
    return "cmp_" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
