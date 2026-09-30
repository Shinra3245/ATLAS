"""Enumeraciones semánticas del motor analítico de ATLAS (Bloque 2).

Estas enumeraciones son parte del ENGINE CONTRACT v1. Sus *valores string*
son estables y forman parte del JSON público consumido por el Bloque 3.

Principios no negociables reflejados aquí:
- Un estado de datos nunca es una conclusión de riesgo.
- INSUFFICIENT_DATA != LOW_RISK.
- NO_REGISTERED_CONDITION != SAFE.
- No existen puntuaciones globales ni ganadores automáticos.
"""

from __future__ import annotations

from enum import Enum


class ConditionStatus(str, Enum):
    """Estado del dato para una condición/factor concreto.

    IMPORTANTE (regla crítica del proyecto):
    - ``INSUFFICIENT_DATA`` NO significa "riesgo bajo".
    - ``NO_REGISTERED_CONDITION`` NO significa "seguro".
    - ``OUTSIDE_SUPPORTED_AREA`` NO significa "sin riesgo"; significa que ATLAS
      no cubre esa zona en el MVP (solo Irapuato y Celaya).
    - ``BLOCKED_DATA_VALIDATION`` significa que existe un dataset candidato pero
      el DATA CONTRACT aún no lo publica como disponible; no debe interpretarse
      como ausencia de la condición.
    """

    #: El DATA CONTRACT publica el dato con cobertura suficiente para la unidad.
    DATA_AVAILABLE = "DATA_AVAILABLE"
    #: Existe dato pero con cobertura o resolución parcial/incompleta.
    PARTIAL_DATA = "PARTIAL_DATA"
    #: No hay información suficiente para pronunciarse. NO equivale a "bajo riesgo".
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    #: La fuente cubre la zona y NO registra la condición. NO equivale a "seguro".
    NO_REGISTERED_CONDITION = "NO_REGISTERED_CONDITION"
    #: La ubicación queda fuera del área soportada por el MVP (Irapuato/Celaya).
    OUTSIDE_SUPPORTED_AREA = "OUTSIDE_SUPPORTED_AREA"
    #: Dataset candidato existe pero pendiente de validación/publicación por Bloque 1.
    BLOCKED_DATA_VALIDATION = "BLOCKED_DATA_VALIDATION"


class Category(str, Enum):
    """Clasificación semántica de cada resultado.

    Estas categorías NO son equivalentes entre sí (distinción obligatoria):
    amenaza vs. factor territorial vs. contexto vs. dato histórico vs. derivado.
    """

    #: Amenaza / susceptibilidad territorial (inundación, fallas, laderas...).
    HAZARD = "hazard"
    #: Antecedente histórico de una amenaza (p. ej. inundación censal 2014).
    #: NUNCA debe presentarse como riesgo actual.
    HAZARD_HISTORY = "hazard_history"
    #: Factor territorial medible (pendiente, uso de suelo, elevación auxiliar).
    TERRITORIAL_FACTOR = "territorial_factor"
    #: Contexto territorial (infraestructura, accesibilidad, población...).
    #: No se convierte automáticamente en amenaza ni penalización.
    CONTEXT = "context"
    #: Resultado derivado de una operación explícita y trazable sobre datos.
    DERIVED = "derived"


class TemporalContext(str, Enum):
    """Marco temporal del dato, para no confundir histórico con actual."""

    #: Dato vigente/actual según la fuente (observación del presente).
    CURRENT = "current"
    #: Dato histórico (antecedente de una amenaza); no representa el presente.
    HISTORICAL = "historical"
    #: Dato de un PERÍODO DE REFERENCIA fechado (p. ej. Censo 2020). No es una
    #: observación del presente ni un antecedente de amenaza: describe el valor
    #: publicado para ese año, que puede haber cambiado desde entonces.
    REFERENCE_PERIOD = "reference_period"
    #: El marco temporal no aplica a este tipo de dato.
    NOT_APPLICABLE = "not_applicable"
    #: Marco temporal desconocido o no declarado por la fuente.
    UNKNOWN = "unknown"


class CoverageState(str, Enum):
    """Cobertura espacial del dato para la unidad de análisis consultada."""

    AVAILABLE = "available"
    PARTIAL = "partial"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


class ProjectType(str, Enum):
    """Tipo de obra. NO altera el dato territorial bruto; solo su lectura."""

    HOUSING = "housing"
    BUILDING = "building"
    ROAD = "road"


class Priority(str, Enum):
    """Prioridad de lectura del factor según el tipo de obra.

    Es una guía de énfasis/orden para la ficha y el frontend. NO es una
    ponderación de riesgo ni un score.
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"
    CONTEXTUAL = "contextual"
    NOT_APPLICABLE = "not_applicable"


class AreaStatus(str, Enum):
    """Estado de soporte geográfico de la ubicación analizada."""

    SUPPORTED = "supported"
    OUTSIDE_SUPPORTED_AREA = "outside_supported_area"


class AnalysisUnit(str, Enum):
    """Unidad de análisis efectiva del resultado (Plan Maestro, sección 11)."""

    #: Punto/localidad soportado por atributos por localidad del dataset maestro.
    LOCALITY = "locality"
    #: Coordenada arbitraria con cobertura de una capa geográfica continua.
    CONTINUOUS_LAYER = "continuous_layer"
    #: No se pudo determinar (p. ej. fuera de área o sin contrato de datos).
    UNDETERMINED = "undetermined"


class MLStatus(str, Enum):
    """Estado del módulo de Machine Learning (complementario y apagado)."""

    #: Estado inicial: sin variable objetivo validada. ATLAS funciona sin ML.
    DISABLED_PENDING_TARGET_VALIDATION = "DISABLED_PENDING_TARGET_VALIDATION"
    #: Solo si el gate se supera y únicamente como experimento histórico.
    HISTORICAL_EXPERIMENT = "HISTORICAL_EXPERIMENT"
    #: ML validado y activo (no alcanzable en el MVP actual).
    ENABLED = "ENABLED"
