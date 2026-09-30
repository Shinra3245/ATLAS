# Solicitud de punto de entrada del ENGINE CONTRACT v1

Bloque solicitante: Bloque 3.
Bloque propietario: Bloque 2.
Fecha: 2026-09-29.
Estado: PARCIAL. Las funciones `analyze_location` y `compare_locations` ya se importan desde `engine`. Sigue abierto el markdown del contrato y los catálogos.

## Actualización 2026-09-29

El paquete `engine` ya exporta `analyze_location` y `compare_locations`. La API las llama y reenvía el JSON. No hace falta volver a publicar esas funciones.

Sigue sin existir `engine/contracts/ENGINE_CONTRACT_V1.md` (ni `docs/analytics/ENGINE_CONTRACT_v1.md`). Tampoco hay `list_sources`, `list_layers` ni `list_locations`. El estado ML se lee de `disabled_ml_info()` mientras no exista `ml_status()`.

## Contrato esperado

Un módulo importable desde la raíz del repositorio, sin que el backend copie reglas científicas, con:

- `analyze_location(location, project_type) -> AnalysisResult`
- `compare_locations(location_a, location_b, project_type) -> ComparisonResult`
- catálogo opcional de fuentes reales (`list_sources`), capas (`list_layers`) y localidades (`list_locations`)
- estado ML (`ml_status`) con los valores ya definidos en `engine/schemas/enums.py`: `DISABLED_PENDING_TARGET_VALIDATION`, `HISTORICAL_EXPERIMENT`, `ENABLED`

Y el documento `engine/contracts/ENGINE_CONTRACT_V1.md` (o `docs/analytics/ENGINE_CONTRACT_v1.md` si esa es la ruta que el bloque congela), alineado con `engine/schemas/` y `engine/contracts/engine_result.schema.json`.

La ubicación de entrada que el backend puede construir es `engine.schemas.Location` (`lat`, `lon`, `locality_id` opcional, `label` opcional). El `project_type` es `housing`, `building` o `road`.

## Contrato recibido

Existen esquemas Python (`engine/schemas/`), serialización `to_jsonable`, compuerta `engine.utils.geo` y el JSON Schema `engine/contracts/engine_result.schema.json`.

No existe `ENGINE_CONTRACT_V1.md`. Las funciones de análisis ya están en el paquete `engine` (ver actualización). No hay catálogo de fuentes, capas ni localidades publicado para la API.

## Ejemplo mínimo

```python
from engine.schemas import Location, ProjectType

result = analyze_location(
    Location(lat=20.676700, lon=-101.356000),
    ProjectType.BUILDING,
)
payload = result.to_dict()
```

El JSON debe conservar `DATA_AVAILABLE`, `PARTIAL_DATA`, `INSUFFICIENT_DATA`, `NO_REGISTERED_CONDITION`, `OUTSIDE_SUPPORTED_AREA` y `BLOCKED_DATA_VALIDATION`. No debe incluir `winner`, `best_location`, `global_risk` ni porcentajes de riesgo, seguridad o factibilidad.

## Impacto

`POST /api/analyze` y `POST /api/compare` ya reenvían el resultado del motor. `GET /api/sources`, `GET /api/layers` y `GET /api/locations` siguen vacíos, con limitación explícita, hasta que exista catálogo.

## Cambio solicitado

Publicar el markdown del contrato y, si ya hay fuentes reales, el catálogo (`list_sources`, `list_layers`, `list_locations`). El backend no modificará `engine/`.
