"""Pruebas de integración con datos REALES del DATA CONTRACT V1.

Estas pruebas consumen `data/processed/v1/analysis_units.json` a través de la
fuente de producción por defecto (ContractDataSource). Verifican que el motor
lee valores reales, respeta la clave/municipio documentados e interpreta la
semántica histórica correctamente.
"""

from __future__ import annotations

from tests.engine.conftest import (
    CELAYA_FLOOD_ZERO,
    IRAPUATO,
    LOS_AGUIRRE,
    all_conditions,
    condition_by_factor,
    validate_json,
)

from engine import (
    analyze_location,
    compare_locations,
    list_layers,
    list_locations,
    list_sources,
    ml_status,
)


def test_real_contract_available():
    from engine import default_data_source

    ds = default_data_source()
    assert ds.is_contract_available() is True
    assert "flood_history" in ds.published_factors()


def test_real_flood_damage_reported_is_available():
    # Los Aguirre (110070078): riesgo_inundacion_2014 = 1 (con daño).
    result = analyze_location(LOS_AGUIRRE, "housing").to_dict()
    flood = condition_by_factor(result, "flood_history")
    assert flood["status"] == "DATA_AVAILABLE"
    assert flood["value"] is True
    assert flood["temporal_context"] == "historical"
    assert flood["source"]["is_test_fixture"] is False
    assert result["ml"]["experiment"]["locality"]["recorded"] == "con_dano"


def test_real_flood_no_damage_is_no_registered():
    # 110070079 (Celaya, lat<20.40): riesgo_inundacion_2014 = 0 (sin daño).
    result = analyze_location(CELAYA_FLOOD_ZERO, "housing").to_dict()
    assert result["location"]["area_status"] == "supported"  # localidad antes rechazada
    assert result["location"]["municipality"] == "Celaya"
    flood = condition_by_factor(result, "flood_history")
    assert flood["status"] == "NO_REGISTERED_CONDITION"
    assert flood["value"] is False
    # Sin daño 2014 NO es "seguro".
    assert "seguro" in flood["explanation"]["not_meaning"].lower()
    assert result["ml"]["experiment"]["locality"]["recorded"] == "sin_dano"


def test_real_flood_null_is_insufficient():
    # Cabecera Irapuato (110170001): riesgo_inundacion_2014 = null.
    result = analyze_location(IRAPUATO, "housing").to_dict()
    flood = condition_by_factor(result, "flood_history")
    assert flood["status"] == "INSUFFICIENT_DATA"
    assert flood["value"] is None


def test_real_elevation_is_census_altitude():
    result = analyze_location(LOS_AGUIRRE, "building").to_dict()
    elevation = condition_by_factor(result, "elevation")
    assert elevation["status"] == "DATA_AVAILABLE"
    assert elevation["value"] == 1761
    assert elevation["unit"] == "m"
    # No debe presentarse como DEM/pendiente.
    assert "dem" in elevation["explanation"]["not_meaning"].lower()


def test_real_context_distances_available():
    result = analyze_location(LOS_AGUIRRE, "road").to_dict()
    road = condition_by_factor(result, "road_proximity")
    assert road["status"] == "DATA_AVAILABLE"
    assert road["value"] == 30.1
    assert road["category"] == "context"


def test_real_slope_blocked_no_dem():
    result = analyze_location(LOS_AGUIRRE, "building").to_dict()
    slope = condition_by_factor(result, "slope")
    assert slope["status"] == "BLOCKED_DATA_VALIDATION"


def test_real_precipitation_context_only_insufficient():
    result = analyze_location(LOS_AGUIRRE, "housing").to_dict()
    precip = condition_by_factor(result, "precipitation")
    assert precip["status"] == "INSUFFICIENT_DATA"
    assert "estación" in precip["explanation"]["meaning"].lower()


def test_real_sources_provenance_partial_visible():
    result = analyze_location(LOS_AGUIRRE, "housing").to_dict()
    assert result["sources"], "debe haber al menos una fuente real"
    core = [s for s in result["sources"] if s["id"] == "core_geospatial"]
    assert core, "core_geospatial debe estar presente"
    assert "PARTIAL" in (core[0]["coverage_note"] or "")


def test_real_output_validates_against_schema(analysis_schema):
    result = analyze_location(LOS_AGUIRRE, "building").to_dict()
    validate_json(result, analysis_schema)


def test_real_15_low_celaya_localities_supported():
    low = [x for x in list_locations() if x["municipality"] == "Celaya" and x["latitude"] < 20.40]
    assert len(low) >= 15
    for loc in low:
        result = analyze_location({"lat": loc["latitude"], "lon": loc["longitude"]}, "housing").to_dict()
        assert result["location"]["area_status"] == "supported"
        assert result["location"]["municipality"] == "Celaya"


def test_real_compare_two_localities(comparison_schema):
    cmp = compare_locations(LOS_AGUIRRE, IRAPUATO, "building").to_dict()
    validate_json(cmp, comparison_schema)
    flood = next(f for f in cmp["factors"] if f["factor"] == "flood_history")
    # A (Los Aguirre) tiene antecedente; B (Irapuato cabecera) es null.
    assert flood["value_a"] is True
    assert flood["condition_only_in"] == "A"


def test_catalogs_real():
    sources = list_sources()
    assert len(sources) == 14
    source_ids = {item["id"] for item in sources}
    assert "riesgos_naturales_localidades" in source_ids
    assert len(list_layers()) >= 40
    assert len(list_locations()) == 755
    status = ml_status()
    assert status["enabled"] is True
    assert status["status"] == "HISTORICAL_EXPERIMENT"


def test_locations_carry_cvegeo_and_crs_unknown():
    locs = list_locations()
    sample = locs[0]
    assert len(sample["id"]) == 9  # CVEGEO
    assert sample["coordinate_crs"] == "CRS_UNKNOWN"


# --------------------------------------------------------------------------- #
# Regresión: 3 pendientes de Bloque 2 reportados tras la integración.
# --------------------------------------------------------------------------- #

# Coordenada arbitraria lejos de cualquier localidad (~0.20° de la más cercana).
FAR_ARBITRARY = {"lat": 20.90, "lon": -101.00}


def test_distant_coordinate_is_not_associated_to_a_locality():
    """Pendiente 1: la asociación geográfica no debe ser permisiva.

    Una coordenada distante (> límite efectivo de 0.05°) NO hereda los datos de
    la localidad más cercana; se reporta fuera del área soportada.
    """
    result = analyze_location(FAR_ARBITRARY, "housing").to_dict()
    assert result["location"]["area_status"] == "outside_supported_area"
    assert result["location"]["locality_id"] in (None,)
    assert result["conditions"] == []
    assert result["territorial_factors"] == []
    assert result["context"] == []
    # Debe explicitar por qué (distancia al centroide más cercano).
    joined = " ".join(result["location"]["notes"]).lower()
    assert "límite de asociación" in joined or "área soportada" in joined


def test_near_coordinate_still_resolves():
    """El límite no debe rechazar puntos legítimos cercanos a una localidad."""
    result = analyze_location(LOS_AGUIRRE, "housing").to_dict()
    assert result["location"]["area_status"] == "supported"
    assert result["location"]["locality_id"] == "110070078"


def test_near_but_distinct_coordinate_explains_locality_resolution():
    point = {**LOS_AGUIRRE, 'lat': LOS_AGUIRRE['lat'] + 0.001}
    result = analyze_location(point, 'housing').to_dict()
    assert result['location']['area_status'] == 'supported'
    assert result['location']['locality_id'] == '110070078'
    notes = ' '.join(result['location']['notes']).lower()
    assert 'no coincide' in notes
    assert 'predio' in notes


def test_exact_locality_coordinate_does_not_claim_approximate_resolution():
    result = analyze_location(LOS_AGUIRRE, 'housing').to_dict()
    assert not any('no coincide' in note for note in result['location']['notes'])
    assert result["location"]["locality_id"] == "110070078"


def test_same_coordinates_different_localities_have_distinct_ids():
    """Pendiente 2: no debe haber colisión de identificadores.

    Dos localidades distintas solicitadas con LAS MISMAS coordenadas de entrada
    (resueltas por clave) entregan datos distintos y deben tener analysis_id
    distintos.
    """
    same_coords = {"lat": 20.6, "lon": -100.9}
    a = analyze_location({**same_coords, "locality_id": "110070078"}, "housing").to_dict()
    b = analyze_location({**same_coords, "locality_id": "110070079"}, "housing").to_dict()
    assert a["location"]["locality_id"] != b["location"]["locality_id"]
    assert a["analysis_id"] != b["analysis_id"]


def test_census_factors_are_reference_period_not_current():
    """Pendiente 3: población/servicios/altitud 2020 no son observaciones 2026."""
    result = analyze_location(LOS_AGUIRRE, "building").to_dict()
    for factor in ("population", "services_coverage", "elevation"):
        cond = condition_by_factor(result, factor)
        assert cond["temporal_context"] == "reference_period", factor
        assert cond["temporal_context"] != "current", factor
        # Debe ser inequívoco en las limitaciones legibles.
        assert any("2020" in lim for lim in cond["limitations"]), factor
    # El antecedente de inundación sigue siendo histórico, no reference_period.
    assert condition_by_factor(result, "flood_history")["temporal_context"] == "historical"


def test_compare_same_locality_is_flagged():
    """Señal same_locality para que Backend rechace comparar una localidad consigo misma."""
    cmp = compare_locations(
        {"lat": 0.0, "lon": 0.0, "locality_id": "110070078"},
        {"lat": 5.0, "lon": 5.0, "locality_id": "110070078"},
        "housing",
    ).to_dict()
    assert cmp["same_locality"] is True
    assert any("misma localidad" in n.lower() for n in cmp["notes"])


def test_compare_distinct_localities_not_flagged():
    cmp = compare_locations(LOS_AGUIRRE, CELAYA_FLOOD_ZERO, "housing").to_dict()
    assert cmp["same_locality"] is False
