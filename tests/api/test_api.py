"""Contrato HTTP del Bloque 3. El doble de motor solo vive en estas pruebas."""

from __future__ import annotations

from app.adapters import engine_adapter
from tests.api.conftest import CELAYA, IRAPUATO, assert_no_forbidden

ANALYZE = {"project_type": "building", "location": IRAPUATO}
COMPARE = {
    "project_type": "building",
    "location_a": IRAPUATO,
    "location_b": CELAYA,
}


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_meta_covers_only_irapuato_and_celaya(client):
    response = client.get("/api/meta")
    assert response.status_code == 200
    body = response.json()
    assert body["system_name"] == "ATLAS"
    assert body["version"]
    assert body["supported_municipalities"] == ["Irapuato", "Celaya"]
    assert body["supported_area"]["state_coverage"] == "future"
    assert body["project_types"] == ["housing", "building", "road"]
    assert body["ml_status"] == "DISABLED_PENDING_TARGET_VALIDATION"


def test_ml_status_starts_disabled(client):
    response = client.get("/api/ml/status")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is False
    assert body["status"] == "DISABLED_PENDING_TARGET_VALIDATION"


def test_sources_and_layers_come_from_the_engine(client):
    sources = client.get("/api/sources")
    layers = client.get("/api/layers")
    locations = client.get("/api/locations")
    assert sources.status_code == 200
    published = sources.json()["sources"]
    assert published
    assert all(item.get("id") and item.get("name") for item in published)
    assert all(item.get("is_test_fixture") is not True for item in published)
    assert layers.json()["layers"]
    assert len(locations.json()["locations"]) == 755


def test_unknown_location_is_404(client):
    response = client.get("/api/locations/no-existe")
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


def test_location_filter_outside_mvp_is_422(client):
    response = client.get("/api/locations", params={"municipality": "León"})
    assert response.status_code == 422
    assert response.json()["error"] == "OUTSIDE_SUPPORTED_AREA"


def test_analyze_valid_preserves_engine_status(fixture_client):
    with fixture_client("available") as client:
        response = client.post("/api/analyze", json=ANALYZE)
    assert response.status_code == 200
    body = response.json()
    assert body["conditions"][0]["status"] == "DATA_AVAILABLE"
    assert body["project_type"] == "building"
    assert body["sources"][0]["is_test_fixture"] is True
    assert_no_forbidden(body)


def test_compare_valid_has_no_winner(fixture_client):
    with fixture_client("available") as client:
        response = client.post("/api/compare", json=COMPARE)
    assert response.status_code == 200
    body = response.json()
    assert body["project_type"] == "building"
    assert body["factors"][0]["status_a"] == "DATA_AVAILABLE"
    assert_no_forbidden(body)


def test_invalid_coordinates(client):
    response = client.post(
        "/api/analyze",
        json={"project_type": "building", "location": {"lat": 95, "lon": -101.354}},
    )
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_invalid_project_type(client):
    response = client.post(
        "/api/analyze",
        json={"project_type": "airport", "location": IRAPUATO},
    )
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"


def test_malformed_json_is_400(client):
    response = client.post(
        "/api/analyze",
        content=b"{",
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "BAD_REQUEST"


def test_outside_supported_area_does_not_analyze(fixture_client):
    with fixture_client("available") as client:
        response = client.post(
            "/api/analyze",
            json={
                "project_type": "road",
                "location": {"lat": 21.019, "lon": -101.257},
            },
        )
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "OUTSIDE_SUPPORTED_AREA"
    assert "conditions" not in body
    assert_no_forbidden(body)


def test_partial_data_is_not_rewritten(fixture_client):
    with fixture_client("partial") as client:
        response = client.post("/api/analyze", json=ANALYZE)
    body = response.json()
    assert response.status_code == 200
    assert body["conditions"][0]["status"] == "PARTIAL_DATA"
    assert body["conditions"][0]["status"] != "LOW_RISK"
    assert_no_forbidden(body)


def test_insufficient_data_is_not_low_risk(fixture_client):
    with fixture_client("insufficient") as client:
        response = client.post("/api/analyze", json=ANALYZE)
    body = response.json()
    assert response.status_code == 200
    assert body["conditions"][0]["status"] == "INSUFFICIENT_DATA"
    assert "LOW_RISK" not in response.text
    assert "SAFE" not in response.text
    assert_no_forbidden(body)


def test_engine_unavailable(client, monkeypatch):
    monkeypatch.setattr(engine_adapter, "_find_callable", lambda _name: None)
    response = client.post("/api/analyze", json=ANALYZE)
    assert response.status_code == 503
    assert response.json()["error"] == "ENGINE_UNAVAILABLE"
    compared = client.post("/api/compare", json=COMPARE)
    assert compared.status_code == 503
    assert compared.json()["error"] == "ENGINE_UNAVAILABLE"


def test_real_engine_analyze_preserves_data_status(client):
    response = client.post("/api/analyze", json=ANALYZE)
    assert response.status_code == 200
    body = response.json()
    statuses = [
        item["status"]
        for item in body["conditions"] + body["territorial_factors"] + body["context"]
    ]
    assert "INSUFFICIENT_DATA" in statuses
    assert "LOW_RISK" not in statuses
    assert "SAFE" not in statuses
    assert body["ml"]["enabled"] is False
    assert body["ml"]["status"] == "DISABLED_PENDING_TARGET_VALIDATION"
    assert_no_forbidden(body)


def test_real_engine_exposes_municipal_context(client):
    response = client.post("/api/analyze", json=ANALYZE)
    assert response.status_code == 200
    body = response.json()
    context = {item["factor"]: item for item in body["context"]}
    flood = context["gp_inundac_mun_context"]
    assert flood["status"] == "PARTIAL_DATA"
    assert flood["value"]
    assert "medición" in flood["explanation"]["not_meaning"].casefold() or "medicion" in flood["explanation"]["not_meaning"].casefold()
    assert "localidad" in flood["explanation"]["meaning"].casefold()
    sources = client.get("/api/sources")
    source_ids = {item["id"] for item in sources.json()["sources"]}
    assert "riesgos_naturales_localidades" in source_ids
    assert_no_forbidden(body)


def test_real_engine_compare_has_no_winner(client):
    response = client.post("/api/compare", json=COMPARE)
    assert response.status_code == 200
    body = response.json()
    assert body["factors"]
    assert "INSUFFICIENT_DATA" in {item["status_a"] for item in body["factors"]}
    assert_no_forbidden(body)


def test_real_engine_analyze_is_deterministic(client):
    first = client.post("/api/analyze", json=ANALYZE).json()
    second = client.post("/api/analyze", json=ANALYZE).json()
    assert first == second


def test_same_location_is_rejected(fixture_client):
    with fixture_client("available") as client:
        response = client.post(
            "/api/compare",
            json={
                "project_type": "housing",
                "location_a": IRAPUATO,
                "location_b": IRAPUATO,
            },
        )
    assert response.status_code == 422
    assert response.json()["error"] == "SAME_LOCATION"


def test_repeated_analyze_is_identical(fixture_client):
    with fixture_client("available") as client:
        first = client.post("/api/analyze", json=ANALYZE).json()
        second = client.post("/api/analyze", json=ANALYZE).json()
    assert first == second
    assert_no_forbidden(first)


def test_compare_forwards_locality_identity(client):
    response = client.post(
        "/api/compare",
        json={
            "project_type": "building",
            "location_a": {
                "lat": 20.67280138888889,
                "lon": -101.34811694444444,
                "locality_id": "110170001",
                "label": "Irapuato",
            },
            "location_b": {
                "lat": 20.521523888888886,
                "lon": -100.81357305555555,
                "locality_id": "110070001",
                "label": "Celaya",
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["location_a"]["locality_id"] == "110170001"
    assert body["location_a"]["label"] == "Irapuato"
    assert body["location_b"]["locality_id"] == "110070001"
    assert body["location_b"]["label"] == "Celaya"


def test_non_finite_latitude_is_a_validation_error(client):
    response = client.post(
        "/api/analyze",
        content=b'{"project_type":"building","location":{"lat":1e309,"lon":-101.354}}',
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert body["details"][0]["input"] == "non_finite"


def test_incomplete_engine_payload_is_rejected(client, monkeypatch):
    def fake_find(name: str):
        if name == "analyze_location":
            return lambda location, project_type: {"analysis_id": "an_incomplete"}
        return None

    monkeypatch.setattr(engine_adapter, "_find_callable", fake_find)
    response = client.post("/api/analyze", json=ANALYZE)
    assert response.status_code == 500
    assert response.json()["error"] == "ENGINE_CONTRACT_VIOLATION"


def test_unknown_schema_version_and_risk_score_are_rejected(client, monkeypatch):
    def fake_find(name: str):
        if name == "analyze_location":
            return lambda location, project_type: {
                "schema_version": "engine_result/v9",
                "risk_score": 99,
            }
        return None

    monkeypatch.setattr(engine_adapter, "_find_callable", fake_find)
    response = client.post("/api/analyze", json=ANALYZE)
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "ENGINE_CONTRACT_VIOLATION"
    assert "risk_score" not in body


def test_openapi_documents_analysis_and_errors(client):
    spec = client.get("/openapi.json").json()
    schemas = spec["components"]["schemas"]
    assert "analysis_id" in schemas["AnalysisResultOut"]["properties"]
    assert "conditions" in schemas["AnalysisResultOut"]["properties"]
    assert "locality_id" in schemas["ResolvedLocationOut"]["properties"]
    assert "factors" in schemas["ComparisonResultOut"]["properties"]
    analyze = spec["paths"]["/api/analyze"]["post"]["responses"]
    compare = spec["paths"]["/api/compare"]["post"]["responses"]
    for code in ("400", "404", "422", "500", "503"):
        assert code in analyze
        assert code in compare
    request_schema = spec["paths"]["/api/compare"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    assert request_schema


def test_forbidden_engine_keys_are_not_published(client, monkeypatch):
    def fake_find(name: str):
        if name == "analyze_location":
            return lambda location, project_type: {"winner": "A", "global_risk": 1}
        return None

    monkeypatch.setattr(engine_adapter, "_find_callable", fake_find)
    response = client.post("/api/analyze", json=ANALYZE)
    assert response.status_code == 500
    body = response.json()
    assert body["error"] == "ENGINE_CONTRACT_VIOLATION"
    assert "winner" not in body


# --------------------------------------------------------------------------- #
# Regresión: pendientes funcionales de Bloque 3 (búsqueda, clave, comparación).
# --------------------------------------------------------------------------- #


def test_search_by_municipality_name_returns_results(client):
    """Buscar 'Irapuato' debe encontrar localidades (filtra por campo real)."""
    response = client.get("/api/locations", params={"query": "Irapuato"})
    assert response.status_code == 200
    found = response.json()["locations"]
    assert len(found) > 0
    assert all(item.get("municipality") == "Irapuato" for item in found)


def test_search_by_locality_name_returns_results(client):
    """Buscar por el nombre de la localidad (campo `locality`) también funciona."""
    response = client.get("/api/locations", params={"query": "celaya"})
    assert response.status_code == 200
    assert len(response.json()["locations"]) > 0


def test_unknown_locality_id_in_analyze_is_404(client):
    """Un locality_id inexistente es un error de cliente (404), no 'fuera de alcance'."""
    response = client.post(
        "/api/analyze",
        json={
            "project_type": "building",
            "location": {**IRAPUATO, "locality_id": "999999999"},
        },
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


def test_unknown_locality_id_in_compare_is_404(client):
    response = client.post(
        "/api/compare",
        json={
            "project_type": "building",
            "location_a": {**IRAPUATO, "locality_id": "110170001"},
            "location_b": {**CELAYA, "locality_id": "999999999"},
        },
    )
    assert response.status_code == 404
    assert response.json()["error"] == "NOT_FOUND"


def test_compare_same_locality_via_distinct_coordinates_is_rejected(client):
    """Distinta coordenada pero MISMA localidad censal ⇒ 422 SAME_LOCATION."""
    response = client.post(
        "/api/compare",
        json={
            "project_type": "building",
            "location_a": {**IRAPUATO, "locality_id": "110170001"},
            "location_b": {**CELAYA, "locality_id": "110170001"},
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "SAME_LOCATION"


def test_analyze_explicit_locality_uses_canonical_coordinates(client):
    response = client.post('/api/analyze', json={
        'project_type': 'housing',
        'location': {'lat': 0, 'lon': 0, 'locality_id': '110070078'},
    })
    assert response.status_code == 200
    location = response.json()['location']
    assert location['locality_id'] == '110070078'
    assert location['municipality'] == 'Celaya'
    assert location['lat'] != 0 and location['lon'] != 0


def test_compare_distinct_keys_with_identical_auxiliary_coordinates(client):
    response = client.post('/api/compare', json={
        'project_type': 'road',
        'location_a': {'lat': 0, 'lon': 0, 'locality_id': '110070078'},
        'location_b': {'lat': 0, 'lon': 0, 'locality_id': '110170001'},
    })
    assert response.status_code == 200
    body = response.json()
    assert body['location_a']['locality_id'] == '110070078'
    assert body['location_b']['locality_id'] == '110170001'
    assert body['location_a']['municipality'] == 'Celaya'
    assert body['location_b']['municipality'] == 'Irapuato'
    assert_no_forbidden(body)


def test_compare_key_and_coordinate_resolve_before_identity_check(client):
    response = client.post('/api/compare', json={
        'project_type': 'building',
        'location_a': {**IRAPUATO, 'locality_id': '110070078'},
        'location_b': IRAPUATO,
    })
    assert response.status_code == 200
    assert response.json()['location_a']['locality_id'] == '110070078'
    assert response.json()['location_b']['locality_id'] == '110170001'


def test_same_key_with_identical_auxiliary_coordinates_is_rejected(client):
    location = {'lat': 0, 'lon': 0, 'locality_id': '110070078'}
    response = client.post('/api/compare', json={
        'project_type': 'building', 'location_a': location, 'location_b': location,
    })
    assert response.status_code == 422
    assert response.json()['error'] == 'SAME_LOCATION'
