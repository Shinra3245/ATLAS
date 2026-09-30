# ACK Bloque 2 → Bloque 1: recepción del DATA CONTRACT V1

- Bloque emisor: 2 (Motor analítico / ML)
- Bloque propietario: 1 (Datos / SIG)
- Referencia: `coordination/requests/from_block_1/TO_BLOCK_2_REQ_001.md` (no modificada)
- Estado: CONTRATO RECIBIDO Y CONECTADO

## Confirmación

Bloque 2 confirma la recepción de `DATA_CONTRACT_V1.md` (v1.0.0) y de
`data/processed/v1/` (755 localidades, 64 campos; `sources_catalog.json`,
`layer_manifest.json`, `manifest.json`). El motor ya CONSUME estos productos a
través de `ContractDataSource`, sin modificar ningún archivo de `data/`.

Se respetan las reglas del contrato:
- Unidad de análisis = localidad censal (clave CVEGEO de 9 caracteres); municipio
  y clave se toman del registro documentado, no de cajas geográficas.
- Coordenadas `CRS_UNKNOWN`: no se reproyectan ni se declara EPSG:4326.
- Nulos = sin información suficiente; nunca sustituidos por cero.
- `riesgo_inundacion_2014`: `1=Con daño` (DATA_AVAILABLE histórico), `0=Sin daño`
  (NO_REGISTERED_CONDITION, no "seguro"), `null` (INSUFFICIENT_DATA). Tratado
  como daño histórico 2014, no como riesgo actual ni etiqueta ML.
- `altitude_m` usado solo como elevación auxiliar (no DEM, no pendiente).
- Distancias EPSG:6372 usadas como contexto, no como amenaza.
- Precipitación por estación tratada como `CONTEXT_ONLY`; no unida a localidades.
- Procedencia `SOURCE_PROVENANCE_PARTIAL` trasladada de forma visible al motor.

## Capacidades pendientes (siguen abiertas, no bloquean el MVP)

`slope` permanece `BLOCKED_DATA_VALIDATION`; `faults`, `landslide`, `land_use`,
`agriculture_vegetation` permanecen `INSUFFICIENT_DATA` hasta que se publiquen
DEM/pendiente validada y las capas con geometría. La solicitud original de
insumos (`TO_BLOCK_1_REQ_001.md`) sigue vigente para esas capacidades.

No se solicita ningún cambio al contrato V1. Si cambiara la unidad de análisis o
el esquema, se coordinará una nueva versión; V1 no se reinterpreta en silencio.
