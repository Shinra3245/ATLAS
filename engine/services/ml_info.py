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
    {"id": "dist_canal_m", "label": "Distancia a canal"},
    {"id": "pobtot", "label": "Población total"},
]

_HOLDOUTS: list[dict[str, Any]] = [
    {
        "held_out": "Celaya",
        "precision": 0.250,
        "recall": 0.111,
        "f1": 0.154,
        "true_positives": 2,
        "false_positives": 6,
    },
    {
        "held_out": "Irapuato",
        "precision": 0.058,
        "recall": 0.556,
        "f1": 0.106,
        "true_positives": 10,
        "false_positives": 161,
    },
]

_LIMITATIONS: list[str] = [
    "La etiqueta es un antecedente de daño en 2014, no la condición del sitio hoy.",
    "La procedencia de esa etiqueta no está verificada de forma independiente.",
    "De 755 localidades, 610 tienen etiqueta y 36 registran daño. 145 quedan sin dato y no se rellenan.",
    "El entrenamiento usa solo altitud, distancia al canal y población: las variables cuyo sentido respecto al daño coincide en Celaya e Irapuato.",
    "Esa selección miró la etiqueta de los dos municipios, así que la prueba no es ciega respecto de qué variables entran.",
    "En la prueba por municipio, la precisión quedó en 25.0 % para Celaya (2 de 18) y en 5.8 % para Irapuato (10 de 18, con 161 marcas falsas).",
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
            "model": "Regresión logística con mayor peso en la clase con daño y solo variables coincidentes",
            "version": "historical-flood-2014-v2",
            "features": list(_FEATURES),
            "validation": {
                "strategy": (
                    "Regresión logística entrenada en un municipio y probada en "
                    "el otro. Solo entran las variables cuyo sentido coincide en "
                    "ambos municipios. No se usaron las demás etiquetas de daño de 2014."
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
