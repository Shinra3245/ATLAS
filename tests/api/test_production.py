"""Regresiones del despliegue: datos, sesión y entrega web/API en un origen."""
import hashlib
import io
import tarfile
import time

import pytest
from fastapi.testclient import TestClient

from app.core import auth, production
from app.core.errors import APIError
from app.main import create_app
from scripts.deploy.data_bundle import ROOT, install, pack, verify_data


@pytest.fixture
def deployed(monkeypatch, tmp_path):
    monkeypatch.setenv("ATLAS_ENV", "production")
    monkeypatch.setenv("ATLAS_FIREBASE_PROJECT_ID", "atlas-test")
    monkeypatch.setenv("ATLAS_STATIC_DIR", str(tmp_path))
    (tmp_path / "index.html").write_text("<!doctype html><title>ATLAS</title>")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/app-123.js").write_text("console.log('ATLAS')")
    with TestClient(create_app()) as client:
        yield client


def test_web_and_data_ready_share_origin(deployed):
    assert deployed.get("/").status_code == 200
    assert deployed.get("/api/ready").json()["records"] == 755
    assert len(deployed.get("/api/locations").json()["locations"]) == 755
    assert deployed.get("/api/not-real").status_code == 404
    assert deployed.get("/.env").status_code == 404
    assert deployed.get("/assets/app-123.js").headers["cache-control"].endswith("immutable")
    assert deployed.get("/").headers["cache-control"] == "no-store"


@pytest.mark.parametrize("path", ["analyze", "analyze/", "compare", "assistant"])
def test_writes_need_session(deployed, path):
    response = deployed.post(f"/api/{path}", json={})
    assert response.status_code == 401
    assert response.json()["error"] == "AUTH_REQUIRED"


def test_valid_session_reaches_engine(deployed, monkeypatch):
    monkeypatch.setattr(production, "verify_session", lambda _: "test-user")
    response = deployed.post("/api/analyze", json={
        "project_type": "housing", "location": {"lat": 20.676, "lon": -101.354}
    })
    assert response.status_code == 200
    assert response.json()["schema_version"] == "engine_result/v1"


def test_body_limit_prevents_engine_call(deployed, monkeypatch):
    monkeypatch.setattr(production, "verify_session", lambda _: "test-user")
    response = deployed.post("/api/analyze", content=b"x" * 65537)
    assert response.status_code == 413


def test_assistant_limit_survives_user_switch(deployed, monkeypatch):
    monkeypatch.setenv("ATLAS_ASSISTANT_HOURLY_LIMIT", "1")
    monkeypatch.setattr(production, "verify_session", lambda header: header)
    first = deployed.post("/api/assistant", headers={"Authorization": "user-one"}, json={})
    assert first.status_code == 422
    second = deployed.post("/api/assistant", headers={"Authorization": "user-two"}, json={})
    assert second.status_code == 429
    assert second.headers["retry-after"] == "60"


def test_session_issuer_is_checked(monkeypatch):
    monkeypatch.setenv("ATLAS_FIREBASE_PROJECT_ID", "atlas-test")
    monkeypatch.setattr(auth.id_token, "verify_firebase_token", lambda *a, **k: {
        "sub": "abc", "iss": "https://securetoken.google.com/another-project", "auth_time": time.time() - 60
    })
    with pytest.raises(APIError) as exc:
        auth.verify_session("Bearer signed-token")
    assert exc.value.status_code == 401


def test_expired_or_forged_token_is_rejected(monkeypatch):
    monkeypatch.setenv("ATLAS_FIREBASE_PROJECT_ID", "atlas-test")
    def invalid(*a, **k):
        raise ValueError("invalid signature")
    monkeypatch.setattr(auth.id_token, "verify_firebase_token", invalid)
    with pytest.raises(APIError) as exc:
        auth.verify_session("Bearer forged-token")
    assert exc.value.status_code == 401


def test_pack_is_repeatable_and_install_checks_integrity(tmp_path):
    first, second = tmp_path / "first.tar.gz", tmp_path / "second.tar.gz"
    sha = pack(ROOT / "data/processed/v1", first)
    assert pack(ROOT / "data/processed/v1", second) == sha
    target = tmp_path / "installed"
    install(first.read_bytes(), sha, target)
    assert verify_data(target)["records"] == 755
    with pytest.raises(ValueError, match="SHA-256"):
        install(first.read_bytes() + b"tampered", sha, target)
    (target / "analysis_units.json").write_text("[]")
    with pytest.raises(ValueError, match="Integridad"):
        verify_data(target)


def test_bundle_rejects_path_traversal(tmp_path):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as archive:
        item = tarfile.TarInfo("../outside")
        item.size = 1
        archive.addfile(item, io.BytesIO(b"x"))
    blob = stream.getvalue()
    with pytest.raises(ValueError, match="inesperados"):
        install(blob, hashlib.sha256(blob).hexdigest(), tmp_path / "data")
    assert not (tmp_path / "outside").exists()


def test_production_fails_without_firebase_project(monkeypatch):
    monkeypatch.setenv("ATLAS_ENV", "production")
    monkeypatch.delenv("ATLAS_FIREBASE_PROJECT_ID", raising=False)
    with pytest.raises(RuntimeError, match="ATLAS_FIREBASE_PROJECT_ID"):
        create_app()
