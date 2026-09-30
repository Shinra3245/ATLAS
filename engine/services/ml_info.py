"""Estado de ML embebido en el resultado del motor.

El experimento histórico de inundación 2014 se publica en cada análisis dentro
del área soportada. No asigna una susceptibilidad: la validación por municipio
no separa el daño con utilidad. Fuera del área, el bloque sigue apagado.

El motor no entrena en cada consulta y no importa el paquete ``ml/``.
"""

from __future__ import annotations

from typing import Any, Optional

from ..schemas.enums import MLStatus
from ..schemas.result import MLInfo

ML_DISABLED_REASON = (
    "Sin análisis de una localidad de Irapuato o Celaya, el experimento "
    "histórico no aplica. El análisis SIG/reglas sigue siendo independiente."
)

ML_EXPERIMENT_REASON = (
    "Experimento histórico sobre daño por inundación reportado en 2014. "
    "Está visible en el análisis. No es riesgo actual y no asigna una probabilidad."
)

READING = (
    "No se publica una susceptibilidad para esta localidad. El modelo no "
    "separa el daño de 2014 con utilidad suficiente."
)

_FEATURES: list[dict[str, str]] = [
    {"id": "altitude_m", "label": "Altitud censal"},
    {"id": "dist_rio_arroyo_m", "label": "Distancia a río o arroyo"},
    {"id": "dist_cuerpo_agua_m", "label": "Distancia a cuerpo de agua"},
    {"id": "dist_canal_m", "label": "Distancia a canal"},
    {"id": "dist_infra_hidrica_m", "label": "Distancia a infraestructura hídrica"},
    {"id": "dist_camino_m", "label": "Distancia a camino"},
    {"id": "dist_carretera_m", "label": "Distancia a carretera"},
    {"id": "pobtot", "label": "Población total"},
]

_HOLDOUTS: list[dict[str, Any]] = [
    {
        "held_out": "Celaya",
        "precision": 0.062,
        "recall": 0.333,
        "f1": 0.105,
        "true_positives": 6,
        "false_positives": 90,
    },
    {
        "held_out": "Irapuato",
        "precision": 0.041,
        "recall": 0.5,
        "f1": 0.077,
        "true_positives": 9,
        "false_positives": 208,
    },
]

_LIMITATIONS: list[str] = [
    "La etiqueta es un antecedente de daño en 2014, no la condición del sitio hoy.",
    "La procedencia de esa etiqueta no está verificada de forma independiente.",
    "De 755 localidades, 610 tienen etiqueta y 36 registran daño. 145 quedan sin dato y no se rellenan.",
    "En la prueba por municipio, la precisión sobre el daño quedó en 6.2 % para Celaya y 4.1 % para Irapuato.",
    "No sustituye los factores publicados ni autoriza una decisión de obra.",
]


def disabled_ml_info() -> MLInfo:
    """Estado fuera del área soportada: el experimento no se publica."""

    return MLInfo(
        enabled=False,
        status=MLStatus.DISABLED_PENDING_TARGET_VALIDATION,
        reason=ML_DISABLED_REASON,
        experiment=None,
    )


def _recorded(value: Any) -> tuple[str, str]:
    if value == 1:
        return "con_dano", "Con daño reportado en 2014."
    if value == 0:
        return "sin_dano", "Sin daño reportado en 2014."
    return "sin_dato", "Sin información suficiente en 2014."


def historical_experiment_info(record: Optional[dict[str, Any]]) -> MLInfo:
    """Experimento visible para una localidad. No incluye una puntuación."""

    code, label = _recorded(
        None if record is None else record.get("riesgo_inundacion_2014")
    )
    return MLInfo(
        enabled=True,
        status=MLStatus.HISTORICAL_EXPERIMENT,
        reason=ML_EXPERIMENT_REASON,
        experiment={
            "name": "Susceptibilidad histórica a inundación",
            "target": "riesgo_inundacion_2014",
            "target_meaning": (
                "Daño por inundación reportado en 2014. 1 significa con daño, "
                "0 sin daño y vacío sin información."
            ),
            "year": 2014,
            "model": "Regresión logística con mayor peso en la clase con daño",
            "version": "historical-flood-2014-v1",
            "features": list(_FEATURES),
            "validation": {
                "strategy": (
                    "Regresión logística entrenada en un municipio y probada en "
                    "el otro. No se usaron las demás etiquetas de daño de 2014."
                ),
                "baseline": (
                    "Clase mayoritaria: predecir siempre sin daño. El F1 de la "
                    "clase con daño de ese baseline es 0."
                ),
                "useful_for_a_decision": False,
                "holdouts": list(_HOLDOUTS),
            },
            "locality": {
                "recorded": code,
                "recorded_label": label,
                "reading": READING,
            },
            "limitations": list(_LIMITATIONS),
        },
    )
