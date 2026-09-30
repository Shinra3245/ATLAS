# Matriz de factores del motor analítico (Bloque 2)

Relación entre cada factor del motor, su categoría, el campo real del DATA
CONTRACT V1 que consume y su estado con los datos publicados por Bloque 1. El
contrato autoritativo del motor es
[`../../engine/contracts/ENGINE_CONTRACT_V1.md`](../../engine/contracts/ENGINE_CONTRACT_V1.md).

> Regla: un factor solo se implementa/consume si está sustentado por el DATA
> CONTRACT. El motor NO lee `data/incoming/**` ni `data/raw/**`. Unidad de
> análisis: localidad censal (clave CVEGEO).

## Factores núcleo

| Factor (`factor`) | Categoría | Campo DATA CONTRACT | Unidad | Marco temporal | Estado con datos reales |
|---|---|---|---|---|---|
| `flood_history` | `hazard_history` | `riesgo_inundacion_2014` | — | historical | `DATA_AVAILABLE` (1) / `NO_REGISTERED_CONDITION` (0) / `INSUFFICIENT_DATA` (null) |
| `faults` | `hazard` | — (sin capa en V1) | — | current | `INSUFFICIENT_DATA` |
| `landslide_susceptibility` | `hazard` | — (sin capa en V1) | — | current | `INSUFFICIENT_DATA` |
| `slope` | `territorial_factor` | — (DEM no validado en V1) | `%` | current | `BLOCKED_DATA_VALIDATION` |
| `land_use` | `territorial_factor` | — (sin capa actual en V1) | — | current/historical | `INSUFFICIENT_DATA` |
| `elevation` (auxiliar) | `territorial_factor` | `altitude_m` | `m` | reference_period (2020) | `DATA_AVAILABLE` |

Notas:
- `flood_history` es antecedente censal 2014 (`1=Con daño`, `0=Sin daño`,
  `null=sin dato`); NUNCA se presenta como riesgo actual. `0` no demuestra
  seguridad.
- `elevation` usa la altitud censal (ITER 2020), NO un DEM; no derivar pendiente.
- Marco temporal `reference_period`: `population`, `services_coverage` y
  `elevation` provienen del Censo/ITER 2020; se marcan como período de referencia
  fechado, NUNCA `current`, para no confundirlos con una observación de 2026.
- `slope` permanece `BLOCKED_DATA_VALIDATION`: el DATA CONTRACT V1 excluye la
  tabla de terreno candidata hasta contar con ráster/método validados.

## Factores de contexto (no son amenazas)

| Factor (`factor`) | Categoría | Campo DATA CONTRACT | Unidad | Estado con datos reales |
|---|---|---|---|---|
| `hydrography_proximity` | `context` | `dist_rio_arroyo_m` | `m` | `DATA_AVAILABLE` |
| `road_proximity` | `context` | `dist_carretera_m` | `m` | `DATA_AVAILABLE` |
| `rail_proximity` | `context` | `dist_via_ferrea_m` | `m` | `DATA_AVAILABLE` |
| `industry_proximity` | `context` | `dist_industria_m` | `m` | `DATA_AVAILABLE` |
| `power_infrastructure_proximity` | `context` | `dist_linea_transmision_m` | `m` | `DATA_AVAILABLE` |
| `population` | `context` | `pobtot` | persons | `DATA_AVAILABLE` |
| `services_coverage` | `context` | `cob_electrica` | `ratio_0_1` | `DATA_AVAILABLE` / `INSUFFICIENT_DATA` |
| `mobility` | `context` | `dis_trans_2014` | category | `DATA_AVAILABLE` / `INSUFFICIENT_DATA` |
| `agriculture_vegetation` | `context` | — (sin capa en V1) | — | `INSUFFICIENT_DATA` |
| `precipitation` | `context` | serie por estación (`CONTEXT_ONLY`) | `mm` | `INSUFFICIENT_DATA` a nivel localidad |

El contexto/infraestructura NUNCA se convierte automáticamente en amenaza ni en
penalización. Las distancias están en EPSG:6372 (precalculadas por la fuente),
con procedencia/fecha incompletas: no son amenaza ni distancia vial medida.
`precipitation` es una serie mensual por estación (una por municipio),
`CONTEXT_ONLY`; el DATA CONTRACT V1 prohíbe unirla a la localidad por cercanía.

## Prioridad por tipo de obra (solo énfasis; no altera el dato)

| Factor | Vivienda | Edificación | Carretera |
|---|---|---|---|
| `flood_history` | primary | primary | secondary |
| `faults` | secondary | primary | primary |
| `landslide_susceptibility` | secondary | secondary | primary |
| `slope` | primary | primary | primary |
| `land_use` | primary | primary | secondary |
| `elevation` | contextual | contextual | contextual |
| `hydrography_proximity` | contextual | contextual | primary |
| `road_proximity` | contextual | contextual | primary |

La prioridad ordena la lectura de la ficha; no es una ponderación de riesgo. No
existen umbrales por factor todavía (DP-03, pendiente de decisión del equipo);
por eso no se calculan puntuaciones.
