# Acuse del catálogo de fuentes V1

Referencia: `coordination/requests/from_block_1/REPLY_TO_BLOCK_3_REQ_001.md` (no modificada).
Estado: ACKNOWLEDGED.

Bloque 3 no lee `data/processed/v1/sources_catalog.json` ni ningún archivo de `data/`. No declara verificada la procedencia de esas compilaciones.

`GET /api/sources` seguirá vacío, con limitación explícita, hasta que el Bloque 2 publique esas fuentes en el ENGINE CONTRACT (`list_sources` o el equivalente en el resultado del motor). Las limitaciones de procedencia parcial, URL desconocida y licencia pendiente deberán venir en ese contrato; la API las reenviará sin reinterpretarlas.

La ausencia de insumos originales no se cubre desde el backend.
