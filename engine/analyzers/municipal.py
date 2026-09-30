"""Contexto municipal publicado aparte del maestro de 64 campos.

Cada indicador se repite en todas las localidades de su municipio. El motor lo
conserva como contexto y no lo convierte en una medición local ni en un riesgo.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..schemas.enums import ConditionStatus, TemporalContext
from ..services.data_source import FactorReading
from .context import ContextAnalyzer

MUNICIPAL_CONTEXT_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "processed" / "v1" / "municipal_context.json"
)

MUNICIPAL_MEANING = (
    "Indicador municipal publicado y repetido en las localidades de ese municipio. "
    "No es una medición de la localidad."
)
MUNICIPAL_NOT_MEANING = (
    "No es un riesgo de la localidad, ni un porcentaje de seguridad, "
    "ni una medición del predio."
)
MUNICIPAL_LIMITATION = (
    "El sufijo _MUN_CONTEXT indica contexto municipal. Repetir el valor por "
    "localidad no le da resolución local."
)


class MunicipalContextAnalyzer(ContextAnalyzer):
    """Pasa un campo municipal sin reinterpretarlo."""

    def _meaning(self, status: ConditionStatus, reading: FactorReading | None) -> str:
        return MUNICIPAL_MEANING

    def _not_meaning(self, status: ConditionStatus, reading: FactorReading | None) -> str:
        return MUNICIPAL_NOT_MEANING

    def _limitation_text(self, status: ConditionStatus, reading: FactorReading | None) -> str:
        return MUNICIPAL_LIMITATION


def municipal_context_analyzers() -> list[MunicipalContextAnalyzer]:
    """Un analyzer por campo del JSON publicado. Lista vacía si aún no existe."""

    if not MUNICIPAL_CONTEXT_PATH.exists():
        return []
    payload = json.loads(MUNICIPAL_CONTEXT_PATH.read_text(encoding="utf-8"))
    analyzers: list[MunicipalContextAnalyzer] = []
    for item in payload.get("fields", []):
        analyzers.append(
            MunicipalContextAnalyzer(
                str(item["code"]),
                str(item.get("label") or item["code"]),
                temporal_context=TemporalContext.UNKNOWN,
            )
        )
    return analyzers
