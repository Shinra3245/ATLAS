"""Entrega web y API en el mismo origen para el primer despliegue de ATLAS."""
from __future__ import annotations

from collections import deque
import os
from pathlib import Path
import time

from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import Headers, MutableHeaders
from starlette.staticfiles import StaticFiles

from app.core.auth import verify_session
from app.core.errors import APIError, error_body

ROOT = Path(__file__).resolve().parents[3]
PROTECTED = {"/api/analyze", "/api/compare", "/api/assistant"}
MAX_BODY = 65536


class ProductionGuard:
    """Una instancia/worker: límites acotados en memoria, sin almacenar tokens."""

    def __init__(self, app):
        self.app = app
        self.users = {}
        self.assistant_calls = deque()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def secured_send(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "SAMEORIGIN"
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                headers["Permissions-Policy"] = "camera=(), microphone=()"
                # Firebase y las teselas funcionan sin una CSP que bloquee sus conexiones.
                headers["Content-Security-Policy"] = "object-src 'none'; base-uri 'self'; frame-ancestors 'self'"
                headers["Cache-Control"] = (
                    "public, max-age=31536000, immutable"
                    if scope["path"].startswith("/assets/") and message["status"] == 200
                    else "no-store"
                )
            await send(message)

        path = scope["path"].rstrip("/")
        if scope["method"] != "POST" or path not in PROTECTED:
            return await self.app(scope, receive, secured_send)
        try:
            uid = await run_in_threadpool(verify_session, Headers(scope=scope).get("authorization", ""))
            now = time.monotonic()
            # Solo quedan usuarios activos durante el último minuto; tope defensivo.
            self.users = {key: times for key, times in self.users.items() if times and times[-1] > now - 60}
            key = (uid, path == "/api/assistant")
            if key not in self.users and len(self.users) >= 10000:
                raise APIError(429, "BUSY", "Hay muchas consultas. Intenta nuevamente en un minuto.")
            times = self.users.setdefault(key, deque())
            while times and times[0] <= now - 60:
                times.popleft()
            limit = 6 if path == "/api/assistant" else 30
            if len(times) >= limit:
                raise APIError(429, "RATE_LIMITED", "Espera un minuto antes de realizar más consultas.")
            if path == "/api/assistant":
                while self.assistant_calls and self.assistant_calls[0] <= now - 3600:
                    self.assistant_calls.popleft()
                cap = int(os.environ.get("ATLAS_ASSISTANT_HOURLY_LIMIT", "200"))
                if len(self.assistant_calls) >= cap:
                    raise APIError(429, "ASSISTANT_BUSY", "El asistente alcanzó su límite temporal. El análisis territorial sigue disponible.")
                self.assistant_calls.append(now)
            times.append(now)
            payload = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                payload.extend(message.get("body", b""))
                if len(payload) > MAX_BODY:
                    raise APIError(413, "BODY_TOO_LARGE", "La solicitud es demasiado grande.")
                if not message.get("more_body", False):
                    break
        except APIError as exc:
            response = JSONResponse(error_body(exc.error, exc.message), status_code=exc.status_code)
            if exc.status_code == 429:
                response.headers["Retry-After"] = "60"
            return await response(scope, receive, secured_send)

        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(payload), "more_body": False}
            return await receive()

        await self.app(scope, replay, secured_send)


def configure_production(app):
    if os.environ.get("ATLAS_ENV") != "production":
        return
    if not os.environ.get("ATLAS_FIREBASE_PROJECT_ID", "").strip():
        raise RuntimeError("Falta ATLAS_FIREBASE_PROJECT_ID para verificar las sesiones.")
    from scripts.deploy.data_bundle import verify_data

    manifest = verify_data(ROOT / "data/processed/v1")
    dist = Path(os.environ.get("ATLAS_STATIC_DIR", str(ROOT / "frontend/dist")))
    if not (dist / "index.html").is_file():
        raise RuntimeError("Falta compilar el frontend de producción.")
    app.add_middleware(ProductionGuard)

    @app.get("/api/ready", include_in_schema=False)
    def ready():
        return {"status": "ready", "records": manifest["records"], "data_version": manifest["contract_version"]}

    # Las rutas de API se registran antes. El sistema usa rutas #/, sin reescribir 404 a HTML.
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
