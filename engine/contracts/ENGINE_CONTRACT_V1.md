# ENGINE CONTRACT v1 — Motor Analítico ATLAS (Bloque 2 → Bloque 3)

Versión: `engine_result/v1` · Motor: `engine/1.0.0-mvp`

Este documento es el ÚNICO contrato que el Bloque 3 (Backend) necesita para
integrar el motor. No debe depender de las estructuras internas del paquete.
El esquema JSON formal está en [`engine_result.schema.json`](engine_result.schema.json).

> Autoridad de contratos: `DATA CONTRACT` → `ENGINE CONTRACT` → `REST CONTRACT`.
> El Backend no redefine la semántica del análisis.

---

## 1. Cómo integrar

El motor es un paquete Python importable ubicado en `engine/` (raíz del repo).

```python
from engine import analyze_location, compare_locations

result = analyze_location({"lat": 20.674, "lon": -101.349}, "building")
payload = result.to_dict()          # dict JSON-serializable y determinista

cmp = compare_locations(
    {"lat": 20.674, "lon": -101.349},
    {"lat": 20.523, "lon": -100.815},
    "building",
)
cmp_payload = cmp.to_dict()
```

- El motor funciona SIN Machine Learning y SIN red externa.
- No requiere dependencias de terceros para el análisis (solo biblioteca
  estándar). `pytest` se usa únicamente para las pruebas.
- La salida es determinista: la misma entrada produce exactamente el mismo JSON
  (los identificadores se derivan por hash de la entrada; no hay marcas de
  reloj ni aleatoriedad).

### Fuente de datos (DATA CONTRACT V1 conectado)

Por defecto, el motor usa `ContractDataSource`, que SOLO consume:

- `data/contracts/DATA_CONTRACT_V1.md` (fuente contractual)
- `data/processed/v1/analysis_units.json` (755 localidades reales)
- `data/processed/v1/sources_catalog.json` y `layer_manifest.json` (catálogos)
- `data/processed/v1/municipal_context.json` (57 campos de contexto municipal, separados del maestro)

Nunca lee `data/incoming/**` ni `data/raw/**`. Si el contrato no estuviera
disponible, los factores se reportan como `INSUFFICIENT_DATA`/
`BLOCKED_DATA_VALIDATION` (NUNCA "riesgo bajo").

### Resolución territorial

- Unidad de análisis: LOCALIDAD censal (clave CVEGEO de 9 caracteres). El
  municipio y la clave provienen del registro documentado, no de cajas.
- Una coordenada se asocia a la localidad censal más cercana SOLO si está dentro
  del límite efectivo de asociación (`0.05°` ≈ 5.5 km). Más allá de ese límite se
  reporta `OUTSIDE_SUPPORTED_AREA`: una coordenada distante NO hereda los datos de
  una localidad. Si el punto difiere del punto publicado (tolerancia numérica de 1e-9 grados), se anota en `location.notes` que los datos describen la localidad y no el predio.
- Se puede resolver directamente por clave: `{"lat":0,"lon":0,"locality_id":"110070078"}`.
- Coordenadas en `CRS_UNKNOWN`: no se reproyectan; no se declara EPSG:4326.
- Coordenadas no finitas (NaN/Inf) o fuera de latitud -90..90 / longitud -180..180 se rechazan con `InvalidLocationError`
  (garantiza JSON estricto, sin `NaN`).
- `analysis_id` incluye la IDENTIDAD de la localidad resuelta: dos consultas con
  las mismas coordenadas pero distinta localidad (p. ej. resueltas por
  `locality_id`) producen identificadores DISTINTOS.

Para pruebas/mock, el Backend puede inyectar una fuente de fixture:

```python
from engine import analyze_location, load_fixture
ds = load_fixture("tests/engine/fixtures/atlas_test_fixture.json")  # TEST_FIXTURE
result = analyze_location({"lat": 20.674, "lon": -101.349}, "building", data_source=ds)
```

### Catálogos para el Backend

```python
from engine import list_sources, list_layers, list_locations, ml_status
list_sources()    # 14 fuentes recibidas (SOURCE_PROVENANCE_PARTIAL visible)
list_layers()     # 53 variables por localidad (no geometría continua)
list_locations()  # 755 localidades (id CVEGEO, municipio, lat/lon CRS_UNKNOWN)
ml_status()        # {"enabled": true, "status": "HISTORICAL_EXPERIMENT", ...}
```

Los catálogos trasladan las marcas `UNKNOWN`/`PENDING_SOURCE_PROVENANCE` sin
ocultarlas; el Backend no debe declarar procedencia como verificada.

---

## 2. Entrada

### `analyze_location(location, project_type, data_source=None)`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `location` | `{"lat": float, "lon": float}` o `Location` | Coordenadas finitas. Campos opcionales: `locality_id` (clave CVEGEO), `label`. |
| `project_type` | `"housing" \| "building" \| "road"` | Tipo de obra. No altera el dato bruto. |
| `data_source` | `DataSource` (opcional) | Por defecto, producción (DATA CONTRACT). |

### `compare_locations(location_a, location_b, project_type, data_source=None, data_source_b=None)`

Analiza A y B con `analyze_location` y los alinea factor por factor con la MISMA
matriz. No usa un motor distinto para B.

---

## 3. Estados (`status`)

| Estado | Significado | NO significa |
|---|---|---|
| `DATA_AVAILABLE` | El contrato publica el dato con cobertura. | — |
| `PARTIAL_DATA` | Dato con cobertura/resolución parcial. | Que represente toda la unidad. |
| `INSUFFICIENT_DATA` | No hay información suficiente. | **NO** significa riesgo bajo. |
| `NO_REGISTERED_CONDITION` | La fuente cubre la zona y no registra la condición. | **NO** significa seguro. |
| `OUTSIDE_SUPPORTED_AREA` | Fuera de Irapuato/Celaya (MVP). | **NO** significa ausencia de riesgo. |
| `BLOCKED_DATA_VALIDATION` | Dataset candidato pendiente de validación por Bloque 1. | **NO** significa ausencia del factor. |

Regla crítica: `INSUFFICIENT_DATA != LOW_RISK` y `NO_REGISTERED_CONDITION != SAFE`.

---

## 4. Categorías (`category`)

`hazard` (amenaza) · `hazard_history` (antecedente histórico) ·
`territorial_factor` (factor territorial) · `context` (contexto/infraestructura) ·
`derived` (resultado derivado con operación explícita).

Estas categorías NO son equivalentes. El contexto no se convierte en amenaza.

---

## 5. Salida de `analyze_location`

Objeto de nivel superior:

| Campo | Tipo | Descripción |
|---|---|---|
| `analysis_id` | `string` | ID determinista del análisis. |
| `schema_version` | `"engine_result/v1"` | Versión del esquema. |
| `engine_version` | `string` | Versión del motor. |
| `project_type` | `"housing"\|"building"\|"road"` | Tipo de obra. |
| `location` | `object` | Ubicación resuelta (ver abajo). |
| `conditions` | `Condition[]` | Amenazas y antecedentes históricos. |
| `territorial_factors` | `Condition[]` | Pendiente, uso de suelo, elevación... |
| `context` | `Condition[]` | Infraestructura, accesibilidad, población... |
| `coverage` | `object` | Conteo de estados de dato (no es un %). |
| `sources` | `Source[]` | Fuentes únicas utilizadas. |
| `limitations` | `string[]` | Limitaciones globales del análisis. |
| `review_items` | `string[]` | Aspectos a revisar (lenguaje "considerar..."). |
| `ml` | `object` | Estado de ML (deshabilitado). |
| `disclaimer` | `string` | Advertencia de alcance obligatoria. |

### `location` (resuelta)

```json
{
  "lat": 20.674, "lon": -101.349,
  "municipality": "Irapuato",
  "area_status": "supported",
  "analysis_unit": "locality",
  "locality_id": null, "label": null, "notes": []
}
```

`area_status`: `supported` | `outside_supported_area`.
`analysis_unit`: `locality` | `continuous_layer` | `undetermined`.

### `Condition`

Cada condición/factor/contexto expresa:

| Campo | Tipo | Descripción |
|---|---|---|
| `factor` | `string` | Código estable (p. ej. `slope`). |
| `label` | `string` | Etiqueta legible. |
| `category` | `Category` | amenaza/histórico/factor/contexto/derivado. |
| `status` | `ConditionStatus` | Estado del dato. |
| `value` | `number\|string\|bool\|null` | Dato BRUTO (invariante al tipo de obra). |
| `unit` | `string\|null` | Unidad (`%`, `m`, `mm`...). |
| `coverage` | `{state, detail}` | Cobertura espacial del dato. |
| `source` | `Source\|null` | Procedencia del dato. |
| `temporal_context` | `current\|historical\|reference_period\|not_applicable\|unknown` | Marco temporal. `reference_period` = dato censal fechado (ITER 2020), NO observación de 2026. |
| `explanation` | `object` | Explicabilidad estructurada (ver abajo). |
| `limitations` | `string[]` | Limitaciones específicas. |
| `priority` | `primary\|secondary\|contextual\|not_applicable` | Énfasis según tipo de obra. |
| `review_items` | `string[]` | Aspectos a revisar. |

`explanation` responde las preguntas obligatorias de explicabilidad:

| Campo | Pregunta |
|---|---|
| `found` | ¿Qué se encontró? |
| `data_origin` | ¿Qué dato lo produjo / de dónde salió? |
| `operation` | ¿Cómo se obtuvo / qué operación se realizó? |
| `meaning` | ¿Qué significa? |
| `not_meaning` | ¿Qué NO significa? |
| `limitation` | ¿Qué limitación tiene? |

### `Source`

```json
{
  "id": "fixture:dem",
  "name": "TEST_FIXTURE — DEM candidato terreno",
  "institution": null, "dataset": null,
  "date_or_version": "2024", "coverage_note": null,
  "is_test_fixture": true
}
```

`is_test_fixture: true` marca datos SIMULADOS de prueba; nunca son datos reales.

### `coverage` (conteo, NO porcentaje)

```json
{
  "expected": 16,
  "data_available": 7, "partial_data": 0,
  "insufficient_data": 7, "no_registered_condition": 1,
  "blocked_data_validation": 1,
  "by_category": { "hazard": {"DATA_AVAILABLE": 1, "NO_REGISTERED_CONDITION": 1} }
}
```

### `ml` (experimento histórico, sin susceptibilidad)

Dentro del área soportada `enabled` es `true` y `experiment` describe la etiqueta de 2014 de esa localidad. `validation.useful_for_a_decision` es `false`. Fuera del área, `enabled` es `false` y `experiment` es `null`.

```json
{
  "enabled": true,
  "status": "HISTORICAL_EXPERIMENT",
  "reason": "Experimento histórico sobre daño por inundación reportado en 2014...",
  "experiment": {
    "name": "Susceptibilidad histórica a inundación",
    "version": "historical-flood-2014-v2",
    "locality": {
      "recorded": "sin_dato",
      "recorded_label": "Sin información suficiente en 2014.",
      "reading": "No se publica una susceptibilidad para esta localidad..."
    },
    "validation": { "useful_for_a_decision": false }
  }
}
```

---

## 6. Ejemplo: condición con dato (fixture)

```json
{
  "factor": "slope",
  "label": "Pendiente del terreno",
  "category": "territorial_factor",
  "status": "DATA_AVAILABLE",
  "coverage": {"state": "available", "detail": null},
  "temporal_context": "current",
  "explanation": {
    "found": "Pendiente del terreno: 14 %.",
    "data_origin": "TEST_FIXTURE — DEM candidato terreno (2024)",
    "operation": "Lectura directa del valor publicado para la unidad de análisis, sin transformación adicional.",
    "meaning": "Pendiente media aproximada de 14% derivada del DEM para la unidad de análisis.",
    "not_meaning": "No constituye un dictamen técnico ni una medición certificada.",
    "limitation": "La pendiente depende de la resolución del DEM; un valor puntual no captura microtopografía."
  },
  "value": 14,
  "unit": "%",
  "source": {"id": "fixture:dem", "name": "TEST_FIXTURE — DEM candidato terreno", "date_or_version": "2024", "is_test_fixture": true},
  "limitations": ["La pendiente depende de la resolución del DEM..."],
  "priority": "primary",
  "review_items": ["Considerar evaluación de estabilidad y cimentación."]
}
```

## 7. Ejemplo: antecedente histórico (no es riesgo actual)

```json
{
  "factor": "flood_history",
  "category": "hazard_history",
  "status": "DATA_AVAILABLE",
  "temporal_context": "historical",
  "value": true,
  "explanation": {
    "meaning": "La localidad reportó antecedente de inundación en el registro censal de 2014.",
    "not_meaning": "No representa el riesgo de inundación actual (2026): es un antecedente histórico de 2014."
  }
}
```

---

## 8. Salida de `compare_locations`

Esquema JSON formal: [`engine_comparison.schema.json`](engine_comparison.schema.json).

Campo `same_locality` (`bool`): `true` cuando A y B resuelven a la MISMA
localidad censal. El motor NO falla por comparar una localidad consigo misma,
pero lo declara de forma explícita para que el consumidor (Backend) pueda
rechazarlo o advertirlo. `comparison_id` incorpora la identidad de ambos lados.


| Campo | Tipo | Descripción |
|---|---|---|
| `comparison_id` | `string` | ID determinista. |
| `schema_version` | `"engine_result/v1"` | Versión. |
| `engine_version` | `string` | Versión del motor. |
| `project_type` | `string` | Tipo de obra (igual para A y B). |
| `location_a` / `location_b` | `object` | Ubicaciones resueltas. |
| `factors` | `FactorComparison[]` | Comparación lado a lado por factor. |
| `coverage_a` / `coverage_b` | `object` | Conteos de cobertura por lado. |
| `limitations` | `string[]` | Limitaciones de la comparación. |
| `notes` | `string[]` | Notas (misma matriz, sin ganador...). |
| `disclaimer` | `string` | Advertencia de alcance. |

### `FactorComparison`

```json
{
  "factor": "slope", "label": "Pendiente del terreno",
  "category": "territorial_factor", "unit": "%",
  "value_a": 14, "value_b": 9,
  "status_a": "DATA_AVAILABLE", "status_b": "PARTIAL_DATA",
  "coverage_a": "available", "coverage_b": "partial",
  "source_a": "TEST_FIXTURE — DEM candidato terreno", "source_b": "TEST_FIXTURE — DEM candidato terreno",
  "observable_difference": "Diferencia observable: A = 14 %, B = 9 %.",
  "difference_detected": true,
  "more_data_available_at": "A",
  "condition_only_in": null,
  "limitations": ["..."]
}
```

---

## 9. PROHIBIDO en la salida (garantizado por contrato y por pruebas)

El motor NUNCA emite, en ningún nivel del JSON:

- `overall_risk_percent`, `global_risk_score`, `risk_score`
- `safety_score`, `feasibility_score`
- `winner`, `best_location`, `ranking`

No hay porcentaje global de riesgo/seguridad/factibilidad ni ganador automático.
Una prueba dedicada verifica la ausencia de estas claves de forma recursiva.

---

## 10. Errores

| Excepción | Cuándo |
|---|---|
| `InvalidProjectTypeError` (`ValueError`) | `project_type` no es `housing`/`building`/`road`. |
| `InvalidLocationError` (`ValueError`) | `location` sin `lat`/`lon` numéricos. |

Una ubicación fuera del MVP NO es un error: devuelve un resultado válido con
`area_status = "outside_supported_area"` y listas de factores vacías.

---

## 11. Estado real de factores (DATA CONTRACT V1)

| Factor | Estado con datos reales | Fuente |
|---|---|---|
| `flood_history` | `DATA_AVAILABLE` (1=con daño) / `NO_REGISTERED_CONDITION` (0) / `INSUFFICIENT_DATA` (null) — histórico 2014 | `riesgo_inundacion_2014` |
| `elevation` (auxiliar) | `DATA_AVAILABLE` (altitud censal ITER 2020, no DEM) | `altitude_m` |
| `population`, `hydrography/road/rail/industry/power_proximity` | `DATA_AVAILABLE` (contexto) | distancias/censo |
| `services_coverage`, `mobility` | `DATA_AVAILABLE`/`INSUFFICIENT_DATA` según nulos | censo 2020/2014 |
| `slope` | `BLOCKED_DATA_VALIDATION` (DEM no validado en V1) | pendiente |
| `faults`, `landslide_susceptibility`, `land_use` | `INSUFFICIENT_DATA` (sin capa en V1) | pendiente |
| `precipitation` | `INSUFFICIENT_DATA` a nivel localidad (serie por estación, `CONTEXT_ONLY`, no unible) | clima 2024–2026 |

Limitaciones:
- Marco temporal `reference_period`: `population`, `services_coverage` y
  `elevation` son del Censo/ITER 2020, no observaciones de 2026.
- Coordenadas `CRS_UNKNOWN`; distancias precalculadas en EPSG:6372 (no reprocesadas).
- Procedencia de fuentes `SOURCE_PROVENANCE_PARTIAL`; instituciones/URL/licencia `UNKNOWN`/`PENDING`.
- La altitud censal no es un DEM y no debe usarse para derivar pendiente.
- El módulo ML publica `HISTORICAL_EXPERIMENT` y no asigna una susceptibilidad.
- Capacidades pendientes (DEM, pendiente, fallas, laderas, uso de suelo actual,
  inundación moderna, subcuenca por intersección): ver `data/processed/v1/*` y
  `coordination/requests/from_block_2/TO_BLOCK_1_REQ_001.md`.

## 12. Versionado

Cambios incompatibles del esquema incrementan `schema_version`
(`engine_result/v2`, ...). Si el Backend detecta una discrepancia de contrato,
NO adapta silenciosamente: registra una solicitud en
`coordination/requests/from_block_3/` y el Bloque 2 resuelve y versiona.
