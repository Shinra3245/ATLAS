# Bloque 2 — Motor Analítico / ML

STATUS: DONE
CURRENT_PHASE: ENGINE_CONNECTED_TO_REAL_DATA_CONTRACT_V1

## Resumen

El motor analítico está construido, probado y CONECTADO a los datos REALES de
Bloque 1 (DATA CONTRACT V1: 755 localidades). Funciona de extremo a extremo
(`analyze_location`, `compare_locations`, cobertura, missing data,
explicabilidad, comparación A/B, catálogos). 66 pruebas pasan (unitarias +
integración con localidades reales + regresión de consistencia + validación de
ambas salidas contra sus JSON Schema).

Se marca READY_FOR_BLOCK_3: el criterio de "datos REALES" ya se cumple. El motor
consume `data/processed/v1/analysis_units.json`, `sources_catalog.json` y
`layer_manifest.json` a través de `ContractDataSource`, sin modificar `data/`.

ENGINE_CONTRACT: PUBLISHED (`engine/contracts/ENGINE_CONTRACT_V1.md`)
COMPARISON_SCHEMA: PUBLISHED (`engine/contracts/engine_comparison.schema.json`)
ENGINE_READY_FOR_BLOCK_3_INTEGRATION: true (sobre datos reales)

## Correcciones aplicadas (respuesta a pendientes de Bloque 1)

1. Contrato real conectado: `ContractDataSource` mapea factores a campos reales
   (`altitude_m`, `pobtot`, `cob_electrica`, `dist_*_m`, `riesgo_inundacion_2014`).
2. Resolución territorial data-driven: clave CVEGEO + municipio del registro
   documentado; snapping a la localidad más cercana dentro del área soportada.
   Se aceptan las 15 localidades de Celaya que las cajas aproximadas rechazaban.
3. Interpretación corregida: inundación `0` → NO_REGISTERED_CONDITION (no
   "antecedente reportado"); `null` con cobertura parcial → INSUFFICIENT_DATA;
   coordenadas NaN/Inf rechazadas (JSON estricto, `allow_nan=False`).
4. Esquema formal de comparación publicado y ambas salidas validadas.
5. Catálogos opcionales implementados para Backend (ver más abajo).

## Correcciones de consistencia (segunda ronda)

6. Asociación geográfica con LÍMITE EFECTIVO (0.05°): una coordenada distante de
   toda localidad ya NO hereda datos de la más cercana; se reporta
   OUTSIDE_SUPPORTED_AREA con la distancia en `location.notes`.
7. `analysis_id` incluye la identidad de la localidad resuelta: mismas
   coordenadas + distinta localidad ⇒ identificadores distintos (sin colisión).
   `comparison_id` incorpora la identidad de ambos lados.
8. Temporalidad: población, servicios y altitud (Censo/ITER 2020) se marcan
   `reference_period` (nuevo valor del enum), NUNCA `current`; limitación legible
   lo declara inequívocamente. Inundación 2014 sigue `historical`.
9. Señal `same_locality` en `compare_locations` para que Backend rechace comparar
   una localidad consigo misma aunque difieran las coordenadas de entrada.

## IMPLEMENTED_FACTORS (con dato real disponible)

- flood_history (hazard_history, histórico 2014 — nunca riesgo actual):
  DATA_AVAILABLE(1) / NO_REGISTERED_CONDITION(0) / INSUFFICIENT_DATA(null)
- elevation (territorial_factor auxiliar, altitud censal ITER 2020 — no DEM)
- population, hydrography/road/rail/industry/power_proximity (context)
- services_coverage, mobility (context; INSUFFICIENT_DATA si nulo)

## BLOCKED / INSUFFICIENT_FACTORS

- slope: BLOCKED_DATA_VALIDATION (DEM/pendiente no validados en V1)
- faults, landslide_susceptibility, land_use, agriculture_vegetation:
  INSUFFICIENT_DATA (sin capa en V1)
- precipitation: INSUFFICIENT_DATA a nivel localidad (serie por estación,
  CONTEXT_ONLY, no unible por el contrato)
- DEPENDENCY (capacidades futuras): coordination/requests/from_block_2/TO_BLOCK_1_REQ_001.md

## CONTEXT_FACTORS (contexto, nunca amenaza)

- hydrography_proximity, road_proximity, rail_proximity, industry_proximity,
  power_infrastructure_proximity, population, services_coverage, mobility,
  agriculture_vegetation, precipitation

## ML_STATUS

DISABLED_PENDING_TARGET_VALIDATION (ATLAS funciona sin ML; gate de 13 checks sin
superar; ver docs/analytics/ML_VALIDATION_GATE.md y ml/status.py)

## Qué puede consumir Backend (Bloque 3) hoy

- `from engine import analyze_location, compare_locations` → `.to_dict()`.
- Catálogos: `list_sources` (14), `list_layers` (53), `list_locations` (755),
  `ml_status`.
- Contratos: `engine/contracts/ENGINE_CONTRACT_V1.md`,
  `engine_analysis.schema.json`, `engine_comparison.schema.json`.
- `location`: `{"lat","lon"}` o `{"locality_id": "<CVEGEO>"}`; NaN/Inf rechazados.
- Estados: DATA_AVAILABLE, PARTIAL_DATA, INSUFFICIENT_DATA,
  NO_REGISTERED_CONDITION, OUTSIDE_SUPPORTED_AREA, BLOCKED_DATA_VALIDATION.
- Salida: location, conditions, territorial_factors, context, coverage, sources,
  limitations, review_items, ml, disclaimer. Sin winner/score/porcentaje global.
- Detalle: coordination/requests/from_block_2/REPLY_TO_BLOCK_3_REQ_001.md

## Solicitudes emitidas / respondidas

- ACK_TO_BLOCK_1_REQ_001 (recepción y conexión del DATA CONTRACT V1)
- REPLY_TO_BLOCK_3_REQ_001 (catálogos + contrato + schema de comparación)
- TO_BLOCK_1_REQ_001 (capacidades futuras: DEM, pendiente, capas de amenaza)

## Solicitudes entrantes atendidas

- from_block_1/TO_BLOCK_2_REQ_001 (contrato entregado) → ACK emitido.
- from_block_3/TO_BLOCK_2_REQ_001 (catálogos + contrato) → REPLY emitido.

## Cierre técnico posterior

- Validación de lat/lon finitas y rangos globales también en biblioteca.
- Toda coordenada distinta del punto publicado (tolerancia numérica 1e-9°)
  muestra nota de asociación aproximada y alcance de localidad, no predio.
- Imports de utilidades de pruebas independientes del orden motor/API.
- Contexto municipal se reconstruye desde raw y se incluye en el manifiesto;
  sigue siendo PARTIAL_DATA, separado de los factores de amenaza.
- Evidencia conjunta: docs/evidence/technical_verification.json y
  docs/evidence/api_verification.json. DONE corresponde al motor sobre datos
  actuales, no a completar las capas pendientes ni validar umbrales profesionales.
