# REST CONTRACT v1

Estado: **estable en nombres de campo** para el frontend. Un cambio incompatible exige una versión nueva o una solicitud en `coordination/requests/` antes de aplicarlo.

`POST /api/analyze` y `POST /api/compare` llaman a `analyze_location` y `compare_locations` del paquete `engine`. La API valida esa salida contra `engine/contracts/engine_result.schema.json` y `engine/contracts/engine_comparison.schema.json` antes de publicarla. Un documento incompleto, con `schema_version` distinta de `engine_result/v1` o con `risk_score` no se reenvía: responde `500` `ENGINE_CONTRACT_VIOLATION`.

La comparación reenvía `locality_id` y `label` de cada ubicación. Una coordenada no finita, como `1e309`, responde `422` `VALIDATION_ERROR`. Un `locality_id` inexistente responde `404` `NOT_FOUND` (no "fuera de alcance"). Si A y B resuelven a la misma localidad censal, la API responde `422` `SAME_LOCATION` usando el campo `same_locality` del motor. El markdown `ENGINE_CONTRACT_V1.md` **ya está publicado** (`engine/contracts/ENGINE_CONTRACT_V1.md`), junto con `engine/contracts/engine_comparison.schema.json`; la API se apoya en esos contratos, en `engine/__init__.py` y en `engine/schemas/`.

El DATA CONTRACT de producción **ya está publicado y conectado** (755 localidades, 53 atributos de catálogo y 14 fuentes; extensión separada de 57 campos municipales). El motor responde `200` con valores reales para factores censales y de contexto (población, servicios, altitud 2020 marcados `reference_period`; distancias), y marca `INSUFFICIENT_DATA` o `BLOCKED_DATA_VALIDATION` los factores sin capa validada (pendiente/DEM, fallas, uso de suelo actual). Eso es el resultado del motor, no una ficha inventada por la API. `503` queda reservado a que esas funciones dejen de poder importarse.

Versión de la API: `0.1.0`.

Timeout esperado de una solicitud de análisis, cuando el motor exista: 30 segundos. La API no impone un corte más corto.

## Alcance

Cobertura operativa: **Irapuato** y **Celaya**.

Guanajuato completo es implementación futura. La API no declara cobertura estatal.

Tipos de obra: `housing`, `building`, `road`.

CORS de desarrollo: `http://localhost:5173`. Orígenes adicionales de LAN o Tailscale se añaden con la variable `ATLAS_CORS_ORIGINS` (lista separada por comas). No se usa `*`. El servicio no está pensado para Internet público.

Base local: `http://127.0.0.1:8000`. Documentación interactiva: `http://127.0.0.1:8000/docs`.

## Estados que se conservan

La API reenvía los estados del motor. No los traduce.

| Estado | Significado que la API no altera |
|---|---|
| `DATA_AVAILABLE` | El motor reporta dato con cobertura suficiente. |
| `PARTIAL_DATA` | El motor reporta dato parcial. |
| `INSUFFICIENT_DATA` | No hay información suficiente. No es riesgo bajo. |
| `NO_REGISTERED_CONDITION` | La fuente cubre la zona y no registra la condición. No es seguro. |
| `OUTSIDE_SUPPORTED_AREA` | La coordenada queda fuera de Irapuato y Celaya. |
| `BLOCKED_DATA_VALIDATION` | Hay un candidato de datos aún no publicado. |

`INSUFFICIENT_DATA` no se convierte en `LOW_RISK`. `NO_REGISTERED_CONDITION` no se convierte en `SAFE`.

La API no añade `winner`, `best_location`, `global_risk`, `risk_percentage`, `safety_percentage`, `feasibility_percentage` ni puntuaciones equivalentes. Si el motor las emitiera, la API responde `500` con `ENGINE_CONTRACT_VIOLATION` y no las publica.

## Estado de ML

Valores del motor, sin renombrar:

| Valor del motor | Lectura informal |
|---|---|
| `DISABLED_PENDING_TARGET_VALIDATION` | apagado |
| `HISTORICAL_EXPERIMENT` | experimental |
| `ENABLED` | disponible, solo tras validación formal |

Valor actual, tomado del motor: `HISTORICAL_EXPERIMENT`, `enabled: true`. El análisis incluye `ml.experiment` con la etiqueta histórica de la localidad y la validación. `useful_for_a_decision` es `false`: no hay probabilidad ni susceptibilidad publicada. Fuera del área soportada, `enabled` vuelve a `false` y `experiment` es `null`.

## Envelope de error

```json
{
  "error": "CODIGO",
  "message": "texto",
  "details": {}
}
```

`details` se omite cuando no aporta nada.

| HTTP | `error` | Cuándo |
|---|---|---|
| 400 | `BAD_REQUEST` | El cuerpo no es JSON válido. |
| 404 | `NOT_FOUND` | El identificador de localidad no está publicado. |
| 422 | `VALIDATION_ERROR` | El esquema de entrada no se cumple. |
| 422 | `OUTSIDE_SUPPORTED_AREA` | La coordenada o el municipio quedan fuera del MVP. No hay análisis. |
| 422 | `SAME_LOCATION` | Las dos coordenadas de una comparación son la misma. |
| 500 | `INTERNAL_ERROR` | Fallo no previsto. |
| 500 | `ENGINE_CONTRACT_VIOLATION` | La salida del motor no se puede reenviar. |
| 503 | `ENGINE_UNAVAILABLE` | El motor no publica la operación pedida. |

## GET /api/health

No depende del motor.

Respuesta `200`:

```json
{ "status": "ok" }
```

```bash
curl -s http://127.0.0.1:8000/api/health
```

## GET /api/meta

Respuesta `200`:

```json
{
  "system_name": "ATLAS",
  "version": "0.1.0",
  "supported_area": {
    "municipalities": ["Irapuato", "Celaya"],
    "state_coverage": "future",
    "note": "El MVP cubre únicamente Irapuato y Celaya. Guanajuato completo es implementación futura."
  },
  "supported_municipalities": ["Irapuato", "Celaya"],
  "project_types": ["housing", "building", "road"],
  "ml_status": "HISTORICAL_EXPERIMENT"
}
```

| Campo | Tipo |
|---|---|
| `system_name` | string |
| `version` | string |
| `supported_area.municipalities` | lista de string |
| `supported_area.state_coverage` | string; hoy `future` |
| `supported_area.note` | string |
| `supported_municipalities` | lista de string |
| `project_types` | lista de string |
| `ml_status` | string; enum de ML del motor |

## GET /api/layers

Respuesta `200` actual: catálogo del motor con 53 atributos por localidad. No son geometrías continuas. El siguiente es únicamente el fallback cuando no exista catálogo:

```json
{
  "layers": [],
  "limitation": "El ENGINE CONTRACT todavía no publica este catálogo. ATLAS no inventa instituciones, fechas, datasets, capas ni localidades."
}
```

Con el catálogo actual, `layers` contiene la lista serializada de `list_layers` y no incluye `limitation`. La API no inventa capas.

## GET /api/locations

Query opcional:

| Parámetro | Tipo | Regla |
|---|---|---|
| `municipality` | string | Solo `Irapuato` o `Celaya`. Otro valor: `422` `OUTSIDE_SUPPORTED_AREA`. |
| `query` | string | Subcadena sin distinguir mayúsculas sobre `id`, `locality`, `municipality`, `label` o `name`. |

Respuesta `200` actual: 755 localidades, o el subconjunto que cumple los filtros. El siguiente es únicamente el fallback sin catálogo:

```json
{
  "locations": [],
  "municipality": null,
  "query": null,
  "limitation": "El ENGINE CONTRACT todavía no publica este catálogo. ATLAS no inventa instituciones, fechas, datasets, capas ni localidades."
}
```

## GET /api/locations/{id}

`404` `NOT_FOUND` si el identificador no está en el catálogo publicado, incluido el caso en que el catálogo aún no existe.

```json
{
  "error": "NOT_FOUND",
  "message": "No existe una localidad publicada con ese identificador.",
  "details": { "id": "no-existe" }
}
```

## POST /api/analyze

Solicitud:

```json
{
  "project_type": "building",
  "location": {
    "lat": 20.676,
    "lon": -101.354,
    "locality_id": null,
    "label": null
  }
}
```

| Campo | Tipo | Regla |
|---|---|---|
| `project_type` | string | `housing`, `building` o `road`. |
| `location.lat` | number | -90 a 90. |
| `location.lon` | number | -180 a 180. |
| `location.locality_id` | string o null | Opcional. Si existe en el catálogo, tiene prioridad y el motor usa sus coordenadas canónicas. Una clave inexistente responde 404. |
| `location.label` | string o null | Opcional. No se inventa. |

Sin clave explícita, el motor asocia la coordenada a la localidad publicada más cercana dentro del límite de 0.05 grados. Toda asociación que no coincida con el punto publicado incluye una nota de aproximación. Si no hay localidad dentro del límite, la respuesta es `422` y no se llama al análisis:

```json
{
  "error": "OUTSIDE_SUPPORTED_AREA",
  "message": "El prototipo actual cubre Irapuato y Celaya. Guanajuato estatal está planificado como expansión futura.",
  "details": {
    "supported_municipalities": ["Irapuato", "Celaya"]
  }
}
```

La asociación no representa un polígono municipal oficial ni una medición del predio. Con `locality_id` válido se usa la localidad seleccionada; lat/lon siguen siendo obligatorias, finitas y dentro de los rangos globales, pero la respuesta contiene las coordenadas canónicas.

Dentro del área, el cuerpo `200` es el objeto `AnalysisResult` del motor, sin renombrar campos. Si `analyze_location` no puede importarse, la respuesta es `503`:

```json
{
  "error": "ENGINE_UNAVAILABLE",
  "message": "El motor analítico no está disponible para esta operación.",
  "details": { "reason": "analyze_location no está publicado" }
}
```

Forma del `200`:

| Campo | Tipo |
|---|---|
| `analysis_id` | string |
| `schema_version` | string (`engine_result/v1`) |
| `engine_version` | string |
| `project_type` | string |
| `location` | objeto (`lat`, `lon`, `municipality`, `area_status`, `analysis_unit`, `locality_id`, `label`, `notes`) |
| `conditions` | lista de condiciones |
| `territorial_factors` | lista de condiciones |
| `context` | lista de condiciones |
| `coverage` | conteos de estados de dato, no un porcentaje de riesgo |
| `sources` | lista de fuentes |
| `limitations` | lista de string |
| `review_items` | lista de string |
| `ml` | `enabled`, `status`, `reason` |
| `disclaimer` | string |

Cada condición incluye `factor`, `label`, `category`, `status`, `coverage`, `temporal_context`, `explanation`, `value`, `unit`, `source`, `limitations`, `priority`, `review_items`.

El contexto puede incluir indicadores municipales (`*_mun_context` y campos de los cuatro libros de localidad). Su estado es `PARTIAL_DATA`: el valor se repite en todas las localidades del municipio y no es una medición local ni un nivel de riesgo del predio.

`coverage` cuenta `expected`, `data_available`, `partial_data`, `insufficient_data`, `no_registered_condition`, `blocked_data_validation` y `by_category`. No es un porcentaje.

```bash
curl -s -X POST http://127.0.0.1:8000/api/analyze \
  -H 'content-type: application/json' \
  -d '{"project_type":"building","location":{"lat":20.676,"lon":-101.354}}'
```

## POST /api/compare

Un solo `project_type` para las dos ubicaciones.

```json
{
  "project_type": "building",
  "location_a": { "lat": 20.676, "lon": -101.354 },
  "location_b": { "lat": 20.523, "lon": -100.815 }
}
```

Reglas previas a llamar al motor:

- ambas ubicaciones resueltas dentro del MVP, dando prioridad a una clave publicada; si una queda fuera, `422` `OUTSIDE_SUPPORTED_AREA` y `details.location` vale `location_a` o `location_b`;
- sin claves explícitas, coordenadas distintas a 6 decimales; si no, `422` `SAME_LOCATION`;
- con claves explícitas, el motor resuelve la identidad antes de comparar. Dos claves distintas son comparables incluso con coordenadas auxiliares iguales; la misma localidad resuelta responde `422` `SAME_LOCATION`;
- el mismo `project_type`.

No se calcula un ganador.

Dentro del área, el cuerpo `200` es `ComparisonResult`. Si `compare_locations` no puede importarse, la respuesta es `503` `ENGINE_UNAVAILABLE`.

Forma del `200`:

| Campo | Tipo |
|---|---|
| `comparison_id` | string |
| `schema_version` | string |
| `engine_version` | string |
| `project_type` | string |
| `location_a` | ubicación resuelta |
| `location_b` | ubicación resuelta |
| `factors` | lista de diferencias observables |
| `coverage_a` | conteo de cobertura |
| `coverage_b` | conteo de cobertura |
| `limitations` | lista de string |
| `notes` | lista de string |
| `disclaimer` | string |

Cada factor incluye `factor`, `label`, `category`, `unit`, `value_a`, `value_b`, `status_a`, `status_b`, `coverage_a`, `coverage_b`, `source_a`, `source_b`, `observable_difference`, `difference_detected`, `more_data_available_at`, `condition_only_in`, `limitations`.

`more_data_available_at` y `condition_only_in` son `"A"`, `"B"` o `null`. Describen disponibilidad de dato, no cuál ubicación es mejor.

## GET /api/sources

Actualmente devuelve 14 fuentes recibidas, conservando `SOURCE_PROVENANCE_PARTIAL`, `UNKNOWN` y licencias pendientes. Solo fuentes reales que el motor publique. Las marcadas `is_test_fixture: true` no se listan.

Sin catálogo real:

```json
{
  "sources": [],
  "limitation": "El ENGINE CONTRACT todavía no publica este catálogo. ATLAS no inventa instituciones, fechas, datasets, capas ni localidades."
}
```

Campos de una fuente, cuando exista: `id`, `name`, `institution`, `dataset`, `date_or_version`, `coverage_note`, `is_test_fixture`.

## GET /api/ml/status

```json
{
  "enabled": true,
  "status": "HISTORICAL_EXPERIMENT",
  "reason": "Experimento histórico sobre daño por inundación reportado en 2014. Está visible en el análisis. No es riesgo actual y no asigna una probabilidad."
}
```

| Campo | Tipo |
|---|---|
| `enabled` | boolean |
| `status` | string, enum de ML del motor |
| `reason` | string |

## Limitaciones

- El análisis real está conectado al DATA CONTRACT V1: reporta valores reales para factores censales y de contexto, y `INSUFFICIENT_DATA`/`BLOCKED_DATA_VALIDATION` donde no hay capa validada (pendiente/DEM, fallas, uso de suelo actual). La API no rellena esos huecos.
- Catálogos publicados por el motor: 14 fuentes, 53 atributos por localidad y 755 localidades (`/api/sources`, `/api/layers`, `/api/locations`). La API no lee `data/incoming`, `data/raw` ni `data/processed`; solo reenvía lo que publica el motor.
- El markdown `ENGINE_CONTRACT_V1.md` y `engine_comparison.schema.json` ya están publicados. La integración usa esos contratos y la API Python pública del paquete `engine`.
- La compuerta geográfica usa la resolución del motor con un límite efectivo de asociación (0.05°) sobre las localidades reales, no polígonos oficiales ni cajas fijas.
- ML publica el experimento histórico de inundación 2014 y no asigna una susceptibilidad.
- No hay autenticación, usuarios, pagos ni exposición pública a Internet.
- Python del entorno: 3.14.7, en `backend/.venv`. No se modificó el Python del sistema. FastAPI 0.142.1, Uvicorn 0.54.0 y Pydantic 2.13.5 instalaron con wheels compatibles.
