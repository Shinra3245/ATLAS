"""Pruebas de ``analyze_location`` (motor analítico, Bloque 2)."""

from __future__ import annotations

import pytest

from tests.engine.conftest import (
    CELAYA,
    IRAPUATO,
    OUTSIDE,
    all_conditions,
    condition_by_factor,
    find_forbidden_keys,
    validate_json,
)

from engine import analyze_location


# --------------------------------------------------------------- área soportada


def test_irapuato_is_supported():
    result = analyze_location(IRAPUATO, "building").to_dict()
    assert result["location"]["municipality"] == "Irapuato"
    assert result["location"]["area_status"] == "supported"
    assert result["location"]["analysis_unit"] == "locality"
    assert result["location"]["locality_id"] == "110170001"


def test_celaya_is_supported():
    result = analyze_location(CELAYA, "housing").to_dict()
    assert result["location"]["municipality"] == "Celaya"
    assert result["location"]["area_status"] == "supported"
    assert result["location"]["locality_id"] == "110070001"


def test_outside_supported_area():
    result = analyze_location(OUTSIDE, "road").to_dict()
    assert result["location"]["area_status"] == "outside_supported_area"
    assert result["location"]["municipality"] is None
    assert result["conditions"] == []
    assert result["territorial_factors"] == []
    assert any("no significa" in lim.lower() for lim in result["limitations"])


def test_resolve_by_locality_id():
    result = analyze_location({"lat": 0.0, "lon": 0.0, "locality_id": "110070078"}, "housing").to_dict()
    assert result["location"]["municipality"] == "Celaya"
    assert result["location"]["label"] == "Los Aguirre"


# ------------------------------------------------------------------- estados


def test_data_available_status(fixture_source):
    result = analyze_location(IRAPUATO, "building", data_source=fixture_source).to_dict()
    slope = condition_by_factor(result, "slope")
    assert slope["status"] == "DATA_AVAILABLE"
    assert slope["value"] == 14
    assert slope["unit"] == "%"
    assert slope["source"]["is_test_fixture"] is True


def test_partial_data_status(fixture_source):
    result = analyze_location(CELAYA, "road", data_source=fixture_source).to_dict()
    slope = condition_by_factor(result, "slope")
    assert slope["status"] == "PARTIAL_DATA"
    assert slope["coverage"]["state"] == "partial"


def test_null_value_with_partial_coverage_is_insufficient(fixture_source):
    # Regresión: un valor null con cobertura parcial NO es PARTIAL_DATA.
    from engine import FixtureDataSource

    payload = {
        "fixture_version": "test-null-partial",
        "localities": [
            {
                "locality_id": "T1",
                "municipality": "Irapuato",
                "locality": "T1",
                "lat": 20.674,
                "lon": -101.349,
                "match_radius_deg": 0.05,
                "factors": {
                    "population": {
                        "value": None,
                        "coverage_state": "partial",
                        "temporal_context": "current",
                    }
                },
            }
        ],
    }
    ds = FixtureDataSource(payload)
    result = analyze_location(IRAPUATO, "housing", data_source=ds).to_dict()
    pop = condition_by_factor(result, "population")
    assert pop["value"] is None
    assert pop["status"] == "INSUFFICIENT_DATA"


def test_factor_without_contract_field_is_insufficient():
    # land_use no tiene campo en el DATA CONTRACT V1 -> información insuficiente.
    result = analyze_location(IRAPUATO, "housing").to_dict()
    land_use = condition_by_factor(result, "land_use")
    assert land_use["status"] == "INSUFFICIENT_DATA"


def test_insufficient_data_is_not_low_risk():
    result = analyze_location(IRAPUATO, "housing").to_dict()
    faults = condition_by_factor(result, "faults")
    assert faults["status"] == "INSUFFICIENT_DATA"
    assert "riesgo bajo" in faults["explanation"]["not_meaning"].lower()


def test_slope_blocked_pending_dem():
    result = analyze_location(IRAPUATO, "building").to_dict()
    slope = condition_by_factor(result, "slope")
    assert slope["status"] == "BLOCKED_DATA_VALIDATION"


def test_no_registered_condition(fixture_source):
    result = analyze_location(CELAYA, "housing", data_source=fixture_source).to_dict()
    flood = condition_by_factor(result, "flood_history")
    assert flood["status"] == "NO_REGISTERED_CONDITION"
    assert "seguro" in flood["explanation"]["not_meaning"].lower()


# -------------------------------------------------------------- dato histórico


def test_flood_history_is_historical(fixture_source):
    result = analyze_location(IRAPUATO, "housing", data_source=fixture_source).to_dict()
    flood = condition_by_factor(result, "flood_history")
    assert flood["category"] == "hazard_history"
    assert flood["temporal_context"] == "historical"
    assert "2014" in flood["explanation"]["not_meaning"]
    assert "actual" in flood["explanation"]["not_meaning"].lower()


# --------------------------------------------------- tipo de obra no altera dato


@pytest.mark.parametrize("project_type", ["housing", "building", "road"])
def test_project_type_does_not_change_raw_value(fixture_source, project_type):
    result = analyze_location(
        IRAPUATO, project_type, data_source=fixture_source
    ).to_dict()
    slope = condition_by_factor(result, "slope")
    assert slope["value"] == 14
    assert slope["unit"] == "%"


def test_project_type_changes_priority(fixture_source):
    housing = analyze_location(IRAPUATO, "housing", data_source=fixture_source).to_dict()
    building = analyze_location(IRAPUATO, "building", data_source=fixture_source).to_dict()
    assert condition_by_factor(housing, "faults")["priority"] == "secondary"
    assert condition_by_factor(building, "faults")["priority"] == "primary"
    # Mismo dato bruto pese al distinto énfasis.
    assert condition_by_factor(housing, "slope")["value"] == condition_by_factor(building, "slope")["value"] == 14


# ---------------------------------------------------------------- proyectos


@pytest.mark.parametrize("project_type", ["housing", "building", "road"])
def test_all_project_types_produce_result(project_type):
    result = analyze_location(IRAPUATO, project_type).to_dict()
    assert result["project_type"] == project_type
    assert result["schema_version"] == "engine_result/v1"
    assert len(all_conditions(result)) > 0


# ------------------------------------------------------------------- ML / claves


def test_historical_experiment_is_visible_without_a_score():
    result = analyze_location(IRAPUATO, "building").to_dict()
    ml = result["ml"]
    assert ml["enabled"] is True
    assert ml["status"] == "HISTORICAL_EXPERIMENT"
    assert ml["experiment"]["validation"]["useful_for_a_decision"] is False
    assert ml["experiment"]["locality"]["recorded"] == "sin_dato"
    assert "probabilidad" not in ml["experiment"]["locality"]["reading"].lower()


def test_no_forbidden_keys(fixture_source):
    result = analyze_location(IRAPUATO, "building", data_source=fixture_source).to_dict()
    assert find_forbidden_keys(result) == set()


# ------------------------------------------------------------------ determinismo


def test_determinism_same_input_same_output():
    r1 = analyze_location(IRAPUATO, "building").to_dict()
    r2 = analyze_location(IRAPUATO, "building").to_dict()
    assert r1 == r2


def test_explainability_fields_present(fixture_source):
    result = analyze_location(IRAPUATO, "building", data_source=fixture_source).to_dict()
    for cond in all_conditions(result):
        exp = cond["explanation"]
        for field in ("found", "data_origin", "operation", "meaning", "not_meaning", "limitation"):
            assert exp[field], f"explicación incompleta en {cond['factor']}: {field}"


# ------------------------------------------------------------------- errores


def test_invalid_project_type_raises():
    from engine import InvalidProjectTypeError

    with pytest.raises(InvalidProjectTypeError):
        analyze_location(IRAPUATO, "bridge")


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_coordinates_rejected(bad):
    from engine import InvalidLocationError

    with pytest.raises(InvalidLocationError):
        analyze_location({"lat": bad, "lon": -101.3}, "housing")


@pytest.mark.parametrize('point', [
    {'lat': 91, 'lon': 0}, {'lat': -91, 'lon': 0},
    {'lat': 0, 'lon': 181}, {'lat': 0, 'lon': -181},
])
def test_global_coordinate_bounds_are_checked_even_with_explicit_id(point):
    from engine import InvalidLocationError
    with pytest.raises(InvalidLocationError):
        analyze_location({**point, 'locality_id': '110070078'}, 'housing')


# ------------------------------------------------------------ validación schema


def test_output_validates_against_schema(analysis_schema, fixture_source):
    result = analyze_location(IRAPUATO, "building", data_source=fixture_source).to_dict()
    validate_json(result, analysis_schema)


def test_real_output_validates_against_schema(analysis_schema):
    result = analyze_location(IRAPUATO, "building").to_dict()
    validate_json(result, analysis_schema)
