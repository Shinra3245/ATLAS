# REQ-2026-09-29 — Bloque 2 → Bloque 1: DATA CONTRACT v1 y datos procesados

- Bloque solicitante: 2 (Motor analítico / ML)
- Bloque propietario: 1 (Datos / SIG)
- Estado del solicitante: WORKING (motor construido sobre TEST_FIXTURE; a la
  espera de datos reales)

## Contexto

El motor analítico (`engine/`) está implementado y probado, pero SOLO consume
datos de producción desde `data/contracts/DATA_CONTRACT_V1.md` y
`data/processed/v1/`. Hoy ninguno existe, por lo que todos los factores se
reportan como `INSUFFICIENT_DATA`/`BLOCKED_DATA_VALIDATION`. No leemos
`data/incoming/**` ni `data/raw/**` como fuente productiva.

## Solicitud

Publicar `DATA_CONTRACT_V1.md` y, en `data/processed/v1/`, un manifiesto
`engine_manifest.json` que declare los factores disponibles y su acceso por
unidad de análisis (localidad/punto).

### Formato propuesto de `engine_manifest.json`

```json
{
  "data_version": "v1",
  "analysis_unit": "locality",
  "factors": {
    "flood_history": true,
    "slope": false,
    "land_use": true
  }
}
```

### Por cada factor, el contrato debe declarar

- `data_key` (nombre estable), unidad, CRS, fecha/versión, cobertura;
- unidad de análisis (localidad/punto o capa continua);
- semántica de valores faltantes (ausencia de registro vs. ausencia de dato);
- fuente e institución.

## Factores que el motor espera (prioridad)

| `data_key` | Uso | Prioridad |
|---|---|---|
| `slope` | Pendiente (DEM candidato ya en poder de Bloque 1) | ALTA |
| `elevation` | Elevación auxiliar (mismo DEM) | ALTA |
| `flood_history` | Antecedente censal 2014 (histórico, no actual) | ALTA |
| `land_use` | Uso de suelo | ALTA |
| `faults` | Fallas/fracturas (geometría) | MEDIA |
| `landslide_susceptibility` | Susceptibilidad de laderas | MEDIA |
| `precipitation` | Clima 2024–2026 (contexto) | MEDIA |
| `hydrography_proximity`, `road_proximity`, `rail_proximity`, `industry_proximity`, `power_infrastructure_proximity`, `population`, `services_coverage`, `mobility`, `agriculture_vegetation` | Contexto | BAJA |

## Bloqueos actuales derivados

- `slope`, `elevation`, `precipitation`: `BLOCKED_DATA_VALIDATION` hasta que el
  contrato los publique como disponibles y validados.
- Resto de factores núcleo: `INSUFFICIENT_DATA` hasta su publicación.

## Impacto

Con el contrato publicado, `analyze_location` y `compare_locations` producirán
valores reales sin cambios en la interfaz del motor ni en el ENGINE CONTRACT v1.

## Referencias

- `engine/contracts/ENGINE_CONTRACT_V1.md`
- `docs/analytics/FACTOR_MATRIX.md`
