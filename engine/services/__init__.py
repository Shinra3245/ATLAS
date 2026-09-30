"""Servicios del motor: orquestación, fuentes de datos, cobertura, contexto."""

from __future__ import annotations

from .analyze import (
    ENGINE_VERSION,
    InvalidLocationError,
    InvalidProjectTypeError,
    analyze_location,
)
from .catalog import list_layers, list_locations, list_sources, ml_status
from .contextualize import contextualize
from .coverage import compute_coverage
from .data_source import (
    ContractDataSource,
    DataSource,
    FactorReading,
    FixtureDataSource,
    LocalityResolution,
    default_data_source,
    load_fixture,
)
from .ml_info import disabled_ml_info

__all__ = [
    "ContractDataSource",
    "DataSource",
    "ENGINE_VERSION",
    "FactorReading",
    "FixtureDataSource",
    "InvalidLocationError",
    "InvalidProjectTypeError",
    "LocalityResolution",
    "analyze_location",
    "compute_coverage",
    "contextualize",
    "default_data_source",
    "disabled_ml_info",
    "list_layers",
    "list_locations",
    "list_sources",
    "load_fixture",
    "ml_status",
]
