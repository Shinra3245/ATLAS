"""Catálogos opcionales para el Backend (Bloque 3).

Exponen fuentes, capas (atributos por localidad) y localidades reales del DATA
CONTRACT V1, además del estado de ML. NO autentican procedencia: trasladan las
marcas SOURCE_PROVENANCE_PARTIAL / UNKNOWN / PENDING tal como las publica
Bloque 1, sin ocultarlas.
"""

from __future__ import annotations

from typing import Any, Optional

from .data_source import DataSource, default_data_source
from .ml_info import disabled_ml_info


def list_sources(data_source: Optional[DataSource] = None) -> list[dict[str, Any]]:
    """Catálogo de fuentes recibidas (con provenance parcial visible)."""

    source = data_source if data_source is not None else default_data_source()
    return source.list_sources()


def list_layers(data_source: Optional[DataSource] = None) -> list[dict[str, Any]]:
    """Inventario de variables por localidad (no capas de geometría continua)."""

    source = data_source if data_source is not None else default_data_source()
    return source.list_layers()


def list_locations(data_source: Optional[DataSource] = None) -> list[dict[str, Any]]:
    """Localidades soportadas (clave CVEGEO, municipio, coordenadas CRS_UNKNOWN)."""

    source = data_source if data_source is not None else default_data_source()
    return source.list_locations()


def ml_status() -> dict[str, Any]:
    """Estado del módulo ML (deshabilitado). Valores de ``MLStatus``."""

    info = disabled_ml_info()
    return {
        "enabled": info.enabled,
        "status": info.status.value,
        "reason": info.reason,
    }
