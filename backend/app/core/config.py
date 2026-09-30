"""Configuración de desarrollo. No abre la API a Internet."""

from __future__ import annotations

import os

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


def cors_origins() -> list[str]:
    """Orígenes explícitos. `ATLAS_CORS_ORIGINS` añade LAN o Tailscale."""

    origins = [DEV_CORS_ORIGIN]
    extra = os.environ.get("ATLAS_CORS_ORIGINS", "")
    for item in extra.split(","):
        origin = item.strip()
        if origin and origin not in origins and origin != "*":
            origins.append(origin)
    return origins
