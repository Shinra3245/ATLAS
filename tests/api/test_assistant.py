"""Chat de la guía: contrato local, sin llamar a Claude."""

from __future__ import annotations

import json

from app.services import assistant as assistant_service


class _Body:
    def __init__(self, payload: dict) -> None:
        self._raw = json.dumps(payload).encode()

    def read(self) -> bytes:
        return self._raw

    def __enter__(self) -> _Body:
        return self

    def __exit__(self, *_exc: object) -> bool:
        return False


def test_assistant_without_key(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    response = client.post(
        "/api/assistant",
        json={"messages": [{"role": "user", "content": "¿Por dónde empiezo?"}]},
    )
    assert response.status_code == 503
    assert response.json()["error"] == "ASSISTANT_UNAVAILABLE"


def test_assistant_rejects_two_user_turns(client):
    response = client.post(
        "/api/assistant",
        json={
            "messages": [
                {"role": "user", "content": "hola"},
                {"role": "user", "content": "otra vez"},
            ]
        },
    )
    assert response.status_code == 422


def test_assistant_returns_claude_text(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-local")
    captured: dict = {}

    def fake_urlopen(request, timeout=0):
        captured["timeout"] = timeout
        captured["key"] = request.get_header("X-api-key")
        captured["body"] = json.loads(request.data.decode())
        return _Body(
            {"content": [{"type": "text", "text": "Elige una localidad de Irapuato o Celaya."}]}
        )

    monkeypatch.setattr(assistant_service.urllib.request, "urlopen", fake_urlopen)
    response = client.post(
        "/api/assistant",
        json={
            "messages": [{"role": "user", "content": "¿Por dónde empiezo?"}],
            "context": {
                "route": "/",
                "locality_a": "",
                "factors_a": [],
                "factors_b": [],
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["reply"].startswith("Elige una localidad")
    assert captured["key"] == "sk-test-local"
    assert captured["body"]["messages"][0]["content"] == "¿Por dónde empiezo?"
    assert "sk-test-local" not in response.text


def test_assistant_hides_upstream_failure(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-secret")

    def fake_urlopen(request, timeout=0):
        raise assistant_service.urllib.error.HTTPError(
            request.full_url,
            401,
            "unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(assistant_service.urllib.request, "urlopen", fake_urlopen)
    response = client.post(
        "/api/assistant",
        json={"messages": [{"role": "user", "content": "hola"}]},
    )
    assert response.status_code == 502
    assert response.json()["error"] == "ASSISTANT_UPSTREAM"
    assert "sk-ant-secret" not in response.text
