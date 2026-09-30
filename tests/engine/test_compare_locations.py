"""Pruebas de ``compare_locations`` (comparación A/B, Bloque 2)."""

from __future__ import annotations

import pytest

from tests.engine.conftest import CELAYA, IRAPUATO, find_forbidden_keys, validate_json

from engine import compare_locations


def _factor(cmp_dict, factor):
    for f in cmp_dict["factors"]:
        if f["factor"] == factor:
            return f
    raise AssertionError(f"factor no comparado: {factor}")


def test_compare_uses_same_matrix(fixture_source):
    cmp = compare_locations(
        IRAPUATO, CELAYA, "building", data_source=fixture_source
    ).to_dict()
    factors = {f["factor"] for f in cmp["factors"]}
    assert {"flood_history", "faults", "slope", "land_use", "elevation"} <= factors


def test_compare_no_winner_no_score(fixture_source):
    cmp = compare_locations(
        IRAPUATO, CELAYA, "road", data_source=fixture_source
    ).to_dict()
    assert find_forbidden_keys(cmp) == set()
    assert "winner" not in cmp
    assert "best_location" not in cmp


def test_compare_detects_difference(fixture_source):
    cmp = compare_locations(
        IRAPUATO, CELAYA, "road", data_source=fixture_source
    ).to_dict()
    slope = _factor(cmp, "slope")
    assert slope["value_a"] == 14
    assert slope["value_b"] == 9
    assert slope["difference_detected"] is True
    assert slope["status_a"] == "DATA_AVAILABLE"
    assert slope["status_b"] == "PARTIAL_DATA"


def test_compare_a_complete_b_partial(fixture_source):
    cmp = compare_locations(
        IRAPUATO, CELAYA, "building", data_source=fixture_source
    ).to_dict()
    land_use = _factor(cmp, "land_use")
    assert land_use["value_a"] == "agricola"
    assert land_use["value_b"] is None
    assert land_use["condition_only_in"] == "A"
    assert land_use["more_data_available_at"] == "A"


def test_compare_side_by_side_fields(fixture_source):
    cmp = compare_locations(
        IRAPUATO, CELAYA, "building", data_source=fixture_source
    ).to_dict()
    slope = _factor(cmp, "slope")
    for key in (
        "value_a",
        "value_b",
        "coverage_a",
        "coverage_b",
        "source_a",
        "source_b",
        "observable_difference",
        "limitations",
    ):
        assert key in slope


@pytest.mark.parametrize("project_type", ["housing", "building", "road"])
def test_compare_all_project_types(fixture_source, project_type):
    cmp = compare_locations(
        IRAPUATO, CELAYA, project_type, data_source=fixture_source
    ).to_dict()
    assert cmp["project_type"] == project_type
    assert cmp["schema_version"] == "engine_result/v1"
    assert len(cmp["factors"]) > 0


def test_compare_determinism():
    c1 = compare_locations(IRAPUATO, CELAYA, "building").to_dict()
    c2 = compare_locations(IRAPUATO, CELAYA, "building").to_dict()
    assert c1 == c2


def test_compare_output_validates_against_schema(comparison_schema, fixture_source):
    cmp = compare_locations(
        IRAPUATO, CELAYA, "building", data_source=fixture_source
    ).to_dict()
    validate_json(cmp, comparison_schema)


def test_compare_real_output_validates_against_schema(comparison_schema):
    cmp = compare_locations(IRAPUATO, CELAYA, "building").to_dict()
    validate_json(cmp, comparison_schema)
