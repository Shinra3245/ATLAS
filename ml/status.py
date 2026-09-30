"""Estado del módulo de Machine Learning de ATLAS.

ML es COMPLEMENTARIO. ATLAS funciona por completo sin ML. El estado inicial es
``DISABLED_PENDING_TARGET_VALIDATION`` y NO cambia hasta superar el gate de
validación documentado en ``ml/experiments/README.md`` y
``docs/analytics/ML_VALIDATION_GATE.md``.

Este módulo no entrena nada ni importa dependencias pesadas: solo declara el
estado y el checklist del gate de forma inspeccionable.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Estado actual del módulo ML. No modificar sin superar el gate.
ML_STATUS = "DISABLED_PENDING_TARGET_VALIDATION"

#: Motivo del estado.
ML_STATUS_REASON = (
    "El dataset maestro declara que la variable objetivo de ML no está creada. "
    "No hay etiqueta validada; el análisis SIG/reglas es el núcleo obligatorio."
)


@dataclass(frozen=True)
class GateCheck:
    """Un ítem del gate de validación de ML."""

    number: int
    name: str
    passed: bool
    note: str


#: Checklist obligatorio ANTES de entrenar (todos deben cumplirse).
GATE_CHECKS: list[GateCheck] = [
    GateCheck(1, "variable_objetivo", False, "Sin variable objetivo definida y documentada."),
    GateCheck(2, "significado_real", False, "Significado exacto de la etiqueta sin confirmar."),
    GateCheck(3, "fuente", False, "Fuente de la etiqueta no verificada."),
    GateCheck(4, "anio", False, "Año/vigencia de la etiqueta no fijado (p. ej. 2014)."),
    GateCheck(5, "observaciones", False, "Número de observaciones utilizables sin auditar."),
    GateCheck(6, "distribucion", False, "Distribución de la variable sin analizar."),
    GateCheck(7, "clases", False, "Balance/clases sin auditar."),
    GateCheck(8, "balance", False, "Estrategia ante desbalance no definida."),
    GateCheck(9, "fuga_espacial", False, "Riesgo de fuga espacial sin controlar."),
    GateCheck(10, "train_test", False, "Partición train/test (espacial/por grupos) no definida."),
    GateCheck(11, "baseline", False, "Baseline simple no construido."),
    GateCheck(12, "metricas", False, "Métricas apropiadas no seleccionadas."),
    GateCheck(13, "utilidad_real", False, "Utilidad real del modelo sin demostrar sobre baseline."),
]


def is_ml_enabled() -> bool:
    """True solo si TODOS los checks del gate pasan. Hoy: False."""

    return all(check.passed for check in GATE_CHECKS)


def gate_summary() -> dict[str, object]:
    """Resumen inspeccionable del gate."""

    return {
        "status": ML_STATUS,
        "reason": ML_STATUS_REASON,
        "enabled": is_ml_enabled(),
        "checks": [
            {"number": c.number, "name": c.name, "passed": c.passed, "note": c.note}
            for c in GATE_CHECKS
        ],
    }
