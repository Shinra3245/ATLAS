"""Serialización determinista a estructuras JSON-compatibles.

El motor debe ser reproducible: la misma entrada produce exactamente la misma
salida. Por eso la serialización no introduce marcas de tiempo de reloj ni
identificadores aleatorios; los IDs se derivan de forma determinista a partir
de la entrada (ver ``engine.utils.ids``).
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any


def to_jsonable(value: Any) -> Any:
    """Convierte dataclasses, enums y contenedores a tipos JSON-compatibles.

    - ``Enum`` -> su ``.value``.
    - ``dataclass`` -> ``dict`` (recursivo).
    - ``list``/``tuple``/``set`` -> ``list`` (recursivo).
    - ``dict`` -> ``dict`` (recursivo; claves convertidas a ``str``).
    - Tipos primitivos (``str``, ``int``, ``float``, ``bool``, ``None``) tal cual.
    """

    # Enum primero: varias enums heredan de ``str``, así que deben convertirse
    # a su ``.value`` antes de la comprobación de primitivos.
    if isinstance(value, Enum):
        return value.value
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        result: dict[str, Any] = {}
        for field in dataclasses.fields(value):
            result[field.name] = to_jsonable(getattr(value, field.name))
        return result
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(v) for v in value]
    # Último recurso: representación textual estable.
    return str(value)
