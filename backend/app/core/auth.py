"""Verifica tokens de Firebase con certificados públicos; no necesita clave Admin."""
from __future__ import annotations

import os
import threading
import time

import cachecontrol
import requests
from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2 import id_token

from app.core.errors import APIError

_local = threading.local()


def _request():
    if not hasattr(_local, "request"):
        _local.request = Request(session=cachecontrol.CacheControl(requests.Session()))
    return _local.request


def verify_session(authorization: str) -> str:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token or len(token) > 8192:
        raise APIError(401, "AUTH_REQUIRED", "Inicia sesión para continuar con esta consulta.")
    project = os.environ.get("ATLAS_FIREBASE_PROJECT_ID", "").strip()
    if not project:
        raise APIError(503, "AUTH_UNAVAILABLE", "El acceso no está disponible temporalmente.")

    def transport(*args, **kwargs):
        kwargs["timeout"] = 8
        return _request()(*args, **kwargs)

    try:
        claims = id_token.verify_firebase_token(token, transport, audience=project)
    except exceptions.TransportError as exc:
        raise APIError(503, "AUTH_UNAVAILABLE", "No se pudo verificar la sesión. Intenta nuevamente.") from exc
    except (ValueError, exceptions.GoogleAuthError) as exc:
        raise APIError(401, "AUTH_INVALID", "La sesión venció o no es válida. Vuelve a iniciar sesión.") from exc
    uid = claims.get("sub")
    auth_time = claims.get("auth_time")
    if (
        claims.get("iss") != f"https://securetoken.google.com/{project}"
        or not isinstance(uid, str) or not 1 <= len(uid) <= 128
        or not isinstance(auth_time, (int, float)) or auth_time > time.time()
    ):
        raise APIError(401, "AUTH_INVALID", "La sesión no es válida para ATLAS.")
    return uid
