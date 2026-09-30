"""Configuración local y de producción mediante variables del entorno."""

from __future__ import annotations

import os
from pathlib import Path

SYSTEM_NAME = "ATLAS"
API_VERSION = "0.1.0"
SUPPORTED_MUNICIPALITIES = ("Irapuato", "Celaya")
PROJECT_TYPES = ("housing", "building", "road")

#: Estado ML inicial del motor mientras no exista activación formal.
DEFAULT_ML_STATUS = "DISABLED_PENDING_TARGET_VALIDATION"
DEFAULT_ML_REASON = (
    "ML permanece apagado: el motor no ha publicado una activación formal."
)

DEV_CORS_ORIGIN = "http://localhost:5173"

OUTSIDE_AREA_MESSAGE = (
    "El prototipo actual cubre Irapuato y Celaya. "
    "Guanajuato estatal está planificado como expansión futura."
)

CATALOG_UNPUBLISHED = (
    "El ENGINE CONTRACT todavía no publica este catálogo. "
    "ATLAS no inventa instituciones, fechas, datasets, capas ni localidades."
)


def load_local_env() -> None:
    """Lee `backend/.env` sin pisar variables ya exportadas en el entorno."""

    if os.environ.get("ATLAS_ENV") == "production":
        return
    path = Path(__file__).resolve().parents[2] / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        os.environ[key] = value.strip().strip('"').strip("'")


load_local_env()


def cors_origins() -> list[str]:
    """Orígenes explícitos. `ATLAS_CORS_ORIGINS` añade LAN o Tailscale."""

    origins = [] if os.environ.get("ATLAS_ENV") == "production" else [DEV_CORS_ORIGIN]
    extra = os.environ.get("ATLAS_CORS_ORIGINS", "")
    for item in extra.split(","):
        origin = item.strip()
        if origin and origin not in origins and origin != "*":
            origins.append(origin)
    return origins
