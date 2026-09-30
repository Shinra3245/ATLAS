"""Garantía obligatoria del Plan Maestro (punto 7 y QA de los 10 puntos).

Una capa espacial del núcleo que NO existe o no está validada:
- NUNCA se representa como `DATA_AVAILABLE` (dato disponible del sitio).
- NUNCA se traduce a "riesgo bajo", "seguro" ni a un estado fuera del enum.
- NUNCA se sustituye por un indicador municipal (los `*_mun_context` son
  contexto, no la amenaza del predio).
- El antecedente censal de inundación 2014 permanece histórico, no amenaza
  actual.

Estas pruebas fallan si alguien intenta "cerrar" el punto 7 haciendo pasar un
faltante por dato disponible o convirtiendo un indicador municipal en amenaza.
"""

from __future__ import annotations

import json

from conftest import (
    CELAYA,
    IRAPUATO,
    LOS_AGUIRRE,
    all_conditions,
    condition_by_factor,
)

from engine import analyze_location
from engine.schemas.enums import ConditionStatus

VALID_STATUSES = {s.value for s in ConditionStatus}

#: Capacidades espaciales del núcleo SIN capa validada en V1 (PENDING_LAYERS.md).
#: Ninguna puede aparecer como dato disponible del predio.
CORE_SPATIAL_PENDING = ("slope", "faults", "landslide_susceptibility", "land_use")
PENDING_ALLOWED = {
    "BLOCKED_DATA_VALIDATION",
    "INSUFFICIENT_DATA",
    "OUTSIDE_SUPPORTED_AREA",
}

SAMPLES = (IRAPUATO, CELAYA, LOS_AGUIRRE)


def test_pending_core_layers_never_data_available():
    for loc in SAMPLES:
        result = analyze_location(loc, "housing").to_dict()
        for factor in CORE_SPATIAL_PENDING:
            cond = condition_by_factor(result, factor)
            assert cond["status"] != "DATA_AVAILABLE", (factor, loc, cond["status"])
            assert cond["status"] != "PARTIAL_DATA", (factor, loc, cond["status"])
            assert cond["status"] in PENDING_ALLOWED, (factor, cond["status"])


def test_no_factor_uses_a_safe_or_low_risk_label():
    forbidden = ("LOW_RISK", "NO_RISK", "RIESGO_BAJO", "SIN_RIESGO", "IS_SAFE")
    for loc in SAMPLES:
        result = analyze_location(loc, "building").to_dict()
        blob = json.dumps(result, ensure_ascii=False)
        for token in forbidden:
            assert token not in blob, (token, loc)
        for cond in all_conditions(result):
            # Todo estado publicado es uno de los 6 estados del contrato.
            assert cond["status"] in VALID_STATUSES, cond["status"]


def test_flood_is_historical_never_current_hazard():
    result = analyze_location(LOS_AGUIRRE, "housing").to_dict()
    flood = condition_by_factor(result, "flood_history")
    assert flood["category"] == "hazard_history"
    assert flood["temporal_context"] == "historical"
    # No debe existir un factor de inundación "actual" con dato disponible del sitio.
    for cond in all_conditions(result):
        if "inund" in cond["factor"] or ("flood" in cond["factor"] and cond["factor"] != "flood_history"):
            assert cond["status"] != "DATA_AVAILABLE", cond["factor"]
            # Un peligro municipal de inundación es contexto, no amenaza del predio.
            assert cond["category"] in ("context",), cond["factor"]


def test_municipal_indicators_are_context_never_hazard():
    result = analyze_location(LOS_AGUIRRE, "housing").to_dict()
    municipal = [c for c in all_conditions(result) if c["factor"].endswith("_mun_context")]
    assert municipal, "el análisis debe incluir indicadores municipales"
    for cond in municipal:
        assert cond["category"] == "context", cond["factor"]
        # Un indicador municipal repetido por localidad no es dato del predio.
        assert cond["status"] in {"PARTIAL_DATA", "INSUFFICIENT_DATA"}, (
            cond["factor"],
            cond["status"],
        )
    # En particular, peligros municipales que coinciden temáticamente con capas
    # faltantes NO se presentan como la amenaza del sitio.
    for factor in ("gp_inundac_mun_context", "susceplad_mun_context", "gp_sismico_mun_context"):
        cond = condition_by_factor(result, factor)
        assert cond["category"] == "context", factor


def test_insufficient_factor_keeps_null_value_not_zero():
    """INSUFFICIENT_DATA no se convierte en 0/False (que se leería como sin condición)."""
    result = analyze_location(IRAPUATO, "housing").to_dict()
    for factor in ("faults", "landslide_susceptibility", "land_use"):
        cond = condition_by_factor(result, factor)
        if cond["status"] == "INSUFFICIENT_DATA":
            assert cond["value"] is None, (factor, cond["value"])


def test_slope_is_blocked_not_derived_from_census_altitude():
    """La altitud censal (elevation) no habilita `slope`: sigue bloqueada."""
    result = analyze_location(LOS_AGUIRRE, "building").to_dict()
    elevation = condition_by_factor(result, "elevation")
    slope = condition_by_factor(result, "slope")
    assert elevation["status"] == "DATA_AVAILABLE"  # altitud censal auxiliar
    assert slope["status"] == "BLOCKED_DATA_VALIDATION"  # no se deriva del punto
