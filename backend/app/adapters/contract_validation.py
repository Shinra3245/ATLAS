"""Valida la salida del motor contra los JSON Schema publicados por el Bloque 2."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from app.core.errors import EngineContractError

_SCHEMA_FILES = {
    "analysis": "engine_result.schema.json",
    "comparison": "engine_comparison.schema.json",
}


@lru_cache(maxsize=2)
def _validator(kind: str) -> Draft202012Validator:
    filename = _SCHEMA_FILES[kind]
    repo = Path(__file__).resolve().parents[3]
    path = repo / "engine" / "contracts" / filename
    schema = json.loads(path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema)


def validate_engine_payload(payload: dict[str, Any], kind: str) -> None:
    """Rechaza un JSON que no cumple el ENGINE CONTRACT v1.

    No rellena campos ni elimina puntuaciones: si el documento no es válido,
    la API no lo publica.
    """

    errors = sorted(
        _validator(kind).iter_errors(payload),
        key=lambda item: (list(item.absolute_path), item.message),
    )
    if not errors:
        return
    first: ValidationError = errors[0]
    location = "/".join(str(part) for part in first.absolute_path) or "(raíz)"
    raise EngineContractError(f"{location}: {first.message}")
