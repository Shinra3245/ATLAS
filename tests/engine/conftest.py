"""Configuración de pruebas del motor (Bloque 2).

Agrega la raíz del repositorio a ``sys.path`` para poder ``import engine`` sin
instalar el paquete, y expone utilidades/fixtures comunes (incluida la
validación de salidas contra los JSON Schema publicados).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "atlas_test_fixture.json"

CONTRACTS_DIR = REPO_ROOT / "engine" / "contracts"
ANALYSIS_SCHEMA_PATH = CONTRACTS_DIR / "engine_result.schema.json"
COMPARISON_SCHEMA_PATH = CONTRACTS_DIR / "engine_comparison.schema.json"

# Coordenadas/localidades REALES del DATA CONTRACT V1 (analysis_units.json).
IRAPUATO = {"lat": 20.67280138888889, "lon": -101.34811694444444}  # id 110170001, flood null
CELAYA = {"lat": 20.521523888888886, "lon": -100.81357305555555}  # id 110070001, flood null
LOS_AGUIRRE = {"lat": 20.61018638888889, "lon": -100.88004638888889}  # id 110070078, flood=1
CELAYA_FLOOD_ZERO = {"lat": 20.38450222222222, "lon": -100.75242916666667}  # id 110070079, flood=0, lat<20.40
OUTSIDE = {"lat": 19.4326, "lon": -99.1332}  # Ciudad de México (fuera del MVP)


@pytest.fixture()
def fixture_source():
    """Fuente de datos TEST_FIXTURE compartida (Irapuato completo, Celaya parcial)."""

    from engine import load_fixture

    return load_fixture(FIXTURE_PATH)


@pytest.fixture(scope="session")
def analysis_schema():
    with ANALYSIS_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def comparison_schema():
    with COMPARISON_SCHEMA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_json(instance, schema) -> None:
    """Valida ``instance`` contra ``schema`` (lanza si no cumple)."""

    import jsonschema

    jsonschema.validate(instance=instance, schema=schema)


FORBIDDEN_KEYS = {
    "overall_risk_percent",
    "global_risk_score",
    "safety_score",
    "feasibility_score",
    "winner",
    "best_location",
    "risk_score",
    "overall_risk",
    "ranking",
}


def find_forbidden_keys(obj) -> set[str]:
    """Busca recursivamente claves prohibidas en cualquier nivel del resultado."""

    found: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in FORBIDDEN_KEYS:
                found.add(key)
            found |= find_forbidden_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            found |= find_forbidden_keys(item)
    return found


def all_conditions(result_dict) -> list[dict]:
    """Devuelve todas las condiciones (amenazas + factores + contexto)."""

    return [
        *result_dict["conditions"],
        *result_dict["territorial_factors"],
        *result_dict["context"],
    ]


def condition_by_factor(result_dict, factor: str) -> dict:
    for cond in all_conditions(result_dict):
        if cond["factor"] == factor:
            return cond
    raise AssertionError(f"factor no encontrado: {factor}")
