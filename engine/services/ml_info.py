"""Estado de ML embebido en el resultado del motor.

El motor NO depende del paquete ``ml/``. ATLAS funciona con ML deshabilitado.
Este módulo expone el estado por defecto (apagado) que se incluye en cada
resultado. El paquete ``ml/`` mantiene su propia declaración de estado y gate.
"""

from __future__ import annotations

from ..schemas.enums import MLStatus
from ..schemas.result import MLInfo

ML_DISABLED_REASON = (
    "Sin variable objetivo validada. El módulo ML permanece deshabilitado; el "
    "análisis SIG/reglas funciona de forma independiente. RIESGO_INUNDACION_2014 "
    "solo podría usarse como experimento histórico, nunca como riesgo actual."
)


def disabled_ml_info() -> MLInfo:
    """Devuelve el estado ML por defecto: deshabilitado pendiente de validación."""

    return MLInfo(
        enabled=False,
        status=MLStatus.DISABLED_PENDING_TARGET_VALIDATION,
        reason=ML_DISABLED_REASON,
    )
