"""Verifica el despliegue; --auth crea y elimina una cuenta temporal sin perfil Firestore."""
import argparse
import json
from pathlib import Path
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request

from prepare_env import ROOT, read_env


def request(url, body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=55)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        return response.status, json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--auth", action="store_true")
    parser.add_argument("--assistant", action="store_true")
    args = parser.parse_args()
    base = args.url.rstrip("/")
    checks = []

    def check(name, condition):
        checks.append({"check": name, "passed": bool(condition)})
        print(("PASS " if condition else "FAIL ") + name, flush=True)
        if not condition:
            raise RuntimeError(name)

    status, ready = request(base + "/api/ready")
    check("datos disponibles", status == 200 and ready.get("records") == 755)
    status, locations = request(base + "/api/locations")
    check("catálogo real", status == 200 and len(locations.get("locations", [])) == 755)
    body = {"project_type": "housing", "location": {"lat": 20.676, "lon": -101.354}}
    status, result = request(base + "/api/analyze", body)
    check("consulta anónima rechazada", status == 401)
    status, result = request(base + "/api/analyze", body, "not-a-valid-token")
    check("token inválido rechazado", status == 401)
    if not args.auth:
        return

    config = read_env(ROOT / "frontend/.env")
    auth_base = "https://identitytoolkit.googleapis.com/v1/accounts:"
    key = urllib.parse.quote(config["VITE_FIREBASE_API_KEY"])
    token = None
    try:
        status, account = request(auth_base + "signUp?key=" + key, {
            "email": f"atlas-deploy-{secrets.token_hex(8)}@example.com",
            "password": secrets.token_urlsafe(24), "returnSecureToken": True,
        })
        check("Firebase permite registro", status == 200 and bool(account.get("idToken")))
        token = account["idToken"]
        start = time.monotonic()
        status, result = request(base + "/api/analyze", body, token)
        check("sesión Firebase y análisis real", status == 200 and result.get("schema_version") == "engine_result/v1")
        print(f"Análisis con verificación inicial de sesión: {time.monotonic()-start:.2f} s")
        status, result = request(base + "/api/compare", {
            "project_type": "housing", "location_a": body["location"],
            "location_b": {"lat": 20.523, "lon": -100.815},
        }, token)
        check("comparación real", status == 200 and bool(result.get("factors")))
        if args.assistant:
            status, result = request(base + "/api/assistant", {
                "messages": [{"role": "user", "content": "En una frase: ¿qué cobertura territorial tiene ATLAS?"}]
            }, token)
            check("asistente conectado", status == 200 and bool(result.get("reply")))
    finally:
        if token:
            status, _ = request(auth_base + "delete?key=" + key, {"idToken": token})
            check("cuenta temporal eliminada", status == 200)


if __name__ == "__main__":
    main()
