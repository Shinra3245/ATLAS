"""Contextualización por tipo de obra.

REGLA CRÍTICA: el tipo de obra NO altera el dato territorial bruto. Una
pendiente de 14 % sigue siendo 14 % para vivienda, edificación o carretera.
Lo único que cambia es:
  - la PRIORIDAD de lectura del factor;
  - la EXPLICACIÓN/contextualización;
  - los ASPECTOS A REVISAR (review_items).

Aquí no se calculan puntuaciones ni umbrales de riesgo (los umbrales por factor
y tipo de obra están PENDIENTES DE DECISIÓN DEL EQUIPO, DP-03). Los review_items
usan lenguaje de "considerar evaluación...", nunca una obligación legal.
"""

from __future__ import annotations

from dataclasses import replace

from ..schemas.condition import Condition
from ..schemas.enums import ConditionStatus, Priority, ProjectType

#: Prioridad de cada factor núcleo según el tipo de obra (agente Bloque 2, E3).
_PRIORITY: dict[ProjectType, dict[str, Priority]] = {
    ProjectType.HOUSING: {
        "flood_history": Priority.PRIMARY,
        "land_use": Priority.PRIMARY,
        "slope": Priority.PRIMARY,
        "faults": Priority.SECONDARY,
        "landslide_susceptibility": Priority.SECONDARY,
        "elevation": Priority.CONTEXTUAL,
    },
    ProjectType.BUILDING: {
        "flood_history": Priority.PRIMARY,
        "faults": Priority.PRIMARY,
        "slope": Priority.PRIMARY,
        "land_use": Priority.PRIMARY,
        "landslide_susceptibility": Priority.SECONDARY,
        "elevation": Priority.CONTEXTUAL,
    },
    ProjectType.ROAD: {
        "slope": Priority.PRIMARY,
        "landslide_susceptibility": Priority.PRIMARY,
        "faults": Priority.PRIMARY,
        "flood_history": Priority.SECONDARY,
        "land_use": Priority.SECONDARY,
        "elevation": Priority.CONTEXTUAL,
        "hydrography_proximity": Priority.PRIMARY,
        "road_proximity": Priority.PRIMARY,
    },
}

#: Nota de contextualización por tipo de obra y factor (texto de apoyo).
_PROJECT_LABEL = {
    ProjectType.HOUSING: "vivienda",
    ProjectType.BUILDING: "edificación",
    ProjectType.ROAD: "carretera/vialidad",
}

#: Sugerencia de revisión (no legal) por factor y tipo de obra cuando el dato
#: está disponible. Lenguaje "considerar evaluación...".
_REVIEW_WHEN_AVAILABLE: dict[str, dict[ProjectType, str]] = {
    "faults": {
        ProjectType.BUILDING: "Considerar evaluación geotécnica estructural para la edificación.",
        ProjectType.ROAD: "Considerar evaluación geológico-estructural del trazo.",
    },
    "slope": {
        ProjectType.ROAD: "Considerar análisis de pendiente y cortes/terraplenes del trazo.",
        ProjectType.BUILDING: "Considerar evaluación de estabilidad y cimentación.",
    },
    "landslide_susceptibility": {
        ProjectType.ROAD: "Considerar estudio de estabilidad de laderas en el trazo.",
    },
    "flood_history": {
        ProjectType.HOUSING: "Considerar verificación de drenaje pluvial y cota de desplante.",
    },
    "land_use": {
        ProjectType.HOUSING: "Considerar compatibilidad con el uso de suelo municipal vigente.",
        ProjectType.BUILDING: "Considerar compatibilidad con el uso de suelo municipal vigente.",
    },
}


def _priority(factor: str, project_type: ProjectType) -> Priority:
    return _PRIORITY.get(project_type, {}).get(factor, Priority.CONTEXTUAL)


def _review_items(
    condition: Condition, project_type: ProjectType, priority: Priority
) -> list[str]:
    items: list[str] = []
    # Falta de dato en un factor prioritario -> aspecto a revisar (obtener el dato).
    if priority in (Priority.PRIMARY, Priority.SECONDARY) and condition.status in (
        ConditionStatus.INSUFFICIENT_DATA,
        ConditionStatus.BLOCKED_DATA_VALIDATION,
        ConditionStatus.PARTIAL_DATA,
    ):
        items.append(
            f"Obtener/validar dato de «{condition.label}» relevante para "
            f"{_PROJECT_LABEL[project_type]} antes de concluir."
        )
    # Dato disponible en factor con sugerencia específica.
    if condition.status == ConditionStatus.DATA_AVAILABLE:
        suggestion = _REVIEW_WHEN_AVAILABLE.get(condition.factor, {}).get(project_type)
        if suggestion:
            items.append(suggestion)
    return items


def contextualize(condition: Condition, project_type: ProjectType) -> Condition:
    """Devuelve una copia de la condición con prioridad y review_items del tipo de obra.

    No modifica ``value``, ``unit``, ``status``, ``category``, ``coverage``,
    ``source`` ni ``temporal_context``: el dato bruto es invariante.
    """

    priority = _priority(condition.factor, project_type)
    review_items = _review_items(condition, project_type, priority)
    return replace(condition, priority=priority, review_items=review_items)
