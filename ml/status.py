"""Estado del módulo de Machine Learning de ATLAS.

ML es COMPLEMENTARIO. ATLAS funciona por completo sin una puntuación de ML.
El estado publicado es ``HISTORICAL_EXPERIMENT``: el experimento de inundación
2014 es visible y no asigna susceptibilidad porque el gate de utilidad no pasa.

Este módulo no entrena nada ni importa dependencias pesadas: solo declara el
estado y el checklist del gate de forma inspeccionable.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Experimento histórico publicado. No es ENABLED: la utilidad sobre el
#: baseline no está demostrada y no se asigna una susceptibilidad.
ML_STATUS = "HISTORICAL_EXPERIMENT"

#: Motivo del estado.
ML_STATUS_REASON = (
    "El experimento usa daño por inundación reportado en 2014. La prueba por "
    "municipio no alcanza utilidad para una decisión, así que no se publica "
    "una probabilidad ni un riesgo actual."
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
    GateCheck(1, "variable_objetivo", True, "riesgo_inundacion_2014, solo como daño histórico."),
    GateCheck(2, "significado_real", True, "1 con daño, 0 sin daño, vacío sin información. No es riesgo actual."),
    GateCheck(3, "fuente", False, "Procedencia de la etiqueta aún parcial."),
    GateCheck(4, "anio", True, "2014."),
    GateCheck(5, "observaciones", True, "610 etiquetadas de 755; 145 sin dato."),
    GateCheck(6, "distribucion", True, "574 sin daño, 36 con daño, 145 sin dato."),
    GateCheck(7, "clases", True, "Dos clases más el faltante, que no se rellena."),
    GateCheck(8, "balance", True, "Peso mayor a la clase con daño. Siguen siendo 36 casos."),
    GateCheck(9, "fuga_espacial", True, "Prueba dejando fuera un municipio. Sin las otras etiquetas de daño de 2014."),
    GateCheck(10, "train_test", True, "Entrenar en un municipio y probar en el otro."),
    GateCheck(11, "baseline", True, "Clase mayoritaria: F1 de la clase con daño = 0."),
    GateCheck(12, "metricas", True, "Precisión, recall y F1 en Celaya e Irapuato."),
    GateCheck(13, "utilidad_real", False, "Precisión 6.2 % y 4.1 %. No se publica susceptibilidad."),
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
