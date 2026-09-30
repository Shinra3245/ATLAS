"""Aplicación FastAPI de ATLAS."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analysis, assistant, comparison, health, layers, locations, meta, metadata
from app.core.config import API_VERSION, SYSTEM_NAME, cors_origins
from app.core.errors import register_exception_handlers
from app.core.logging import get_logger
from app.core.production import configure_production

logger = get_logger("main")


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{SYSTEM_NAME} API",
        version=API_VERSION,
        description=(
            "API de integración para Irapuato y Celaya. "
            "No declara cobertura estatal ni reinterpretar resultados del motor."
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept", "Authorization"],
    )
    register_exception_handlers(app)

    for module in (
        health,
        meta,
        layers,
        locations,
        analysis,
        comparison,
        metadata,
        assistant,
    ):
        app.include_router(module.router, prefix="/api")

    configure_production(app)
    logger.info("api_started version=%s", API_VERSION)
    return app


app = create_app()
