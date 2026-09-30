"""Modelo de fuente/procedencia de un dato.

Toda condición con dato debe declarar su fuente. Las fuentes de prueba se
marcan explícitamente con ``is_test_fixture=True`` y ``TEST_FIXTURE`` en el
nombre para que NUNCA se confundan con datos reales.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Source:
    """Procedencia de un dato consumido por el motor."""

    #: Identificador estable de la fuente en el DATA CONTRACT (o del fixture).
    id: str
    #: Nombre legible de la fuente.
    name: str
    #: Institución responsable, cuando aplica.
    institution: Optional[str] = None
    #: Nombre del dataset/capa concreta.
    dataset: Optional[str] = None
    #: Fecha del dato o versión (año, versión de serie, etc.).
    date_or_version: Optional[str] = None
    #: Nota de cobertura declarada por la fuente.
    coverage_note: Optional[str] = None
    #: Marca inequívoca de dato simulado de prueba.
    is_test_fixture: bool = False

    @staticmethod
    def test_fixture(id: str, name: str, **kwargs: object) -> "Source":
        """Construye una fuente de prueba, siempre marcada como TEST_FIXTURE."""

        prefixed = name if name.startswith("TEST_FIXTURE") else f"TEST_FIXTURE — {name}"
        return Source(
            id=id,
            name=prefixed,
            is_test_fixture=True,
            **kwargs,  # type: ignore[arg-type]
        )
