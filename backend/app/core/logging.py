"""Registro estructurado a stderr y a un archivo local ignorado por git."""

from __future__ import annotations

import logging
import os
from pathlib import Path

_CONFIGURED = False


def configure_logging() -> None:
    """Configura el logger `atlas.api` una sola vez."""

    global _CONFIGURED
    if _CONFIGURED:
        return

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    root = logging.getLogger("atlas.api")
    root.setLevel(logging.INFO)

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    root.handlers.clear()
    root.addHandler(stream)
    if os.environ.get("ATLAS_ENV") != "production":
        log_dir = Path(__file__).resolve().parents[2] / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "api.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(f"atlas.api.{name}")
