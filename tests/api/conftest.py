"""Prepara imports y un cliente HTTP en proceso."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
for path in (str(ROOT), str(BACKEND)):
    if path not in sys.path:
        sys.path.insert(0, path)

from app.adapters.engine_adapter import get_engine_adapter  # noqa: E402
from app.main import app  # noqa: E402
from tests.api.engine_double import FixtureEngineAdapter  # noqa: E402

IRAPUATO = {"lat": 20.676, "lon": -101.354}
CELAYA = {"lat": 20.523, "lon": -100.815}
FORBIDDEN_KEYS = {
    "winner",
    "best_location",
    "global_risk",
    "global_risk_score",
    "risk_percentage",
    "safety_percentage",
    "safety_score",
    "feasibility_percentage",
    "feasibility_score",
    "overall_risk_percent",
}


def assert_no_forbidden(value: object) -> None:
    if isinstance(value, dict):
        assert FORBIDDEN_KEYS.isdisjoint(value)
        for item in value.values():
            assert_no_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            assert_no_forbidden(item)


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def fixture_client():
    def _make(mode: str = "available") -> TestClient:
        app.dependency_overrides[get_engine_adapter] = lambda: FixtureEngineAdapter(mode)
        return TestClient(app)

    yield _make
    app.dependency_overrides.clear()
