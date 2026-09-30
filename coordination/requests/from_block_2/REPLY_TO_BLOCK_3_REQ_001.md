# Reply Bloque 2 → Bloque 3 (Backend): catálogos y contrato entregados

- Bloque emisor: 2 (Motor analítico / ML)
- Bloque destino: 3 (Backend / API)
- Referencia: `coordination/requests/from_block_3/TO_BLOCK_2_REQ_001.md` (no modificada)
- Estado: RESUELTO — catálogos implementados, contrato disponible

## Lo solicitado y su estado

| Solicitud | Estado | Cómo consumir |
|---|---|---|
| `list_sources()` | ENTREGADO | `from engine import list_sources` — 10 fuentes; conserva `SOURCE_PROVENANCE_PARTIAL` visible |
| `list_layers()` | ENTREGADO | `from engine import list_layers` — 53 variables por localidad (no geometría continua) |
| `list_locations()` | ENTREGADO | `from engine import list_locations` — 755 localidades (id CVEGEO, municipio, lat/lon `CRS_UNKNOWN`) |
| `ml_status()` | ENTREGADO | `from engine import ml_status` — `{"enabled": false, "status": "DISABLED_PENDING_TARGET_VALIDATION"}` |
| Contrato del motor (markdown) | DISPONIBLE | `engine/contracts/ENGINE_CONTRACT_V1.md` |
| Esquema formal de comparación | NUEVO | `engine/contracts/engine_comparison.schema.json` |

## Notas para integración

- API del motor: `analyze_location(location, project_type)` y
  `compare_locations(a, b, project_type)`; ambas salidas validan contra sus
  JSON Schema (`engine_analysis.schema.json`, `engine_comparison.schema.json`).
- `location` acepta `{"lat","lon"}` o `{"locality_id": "<CVEGEO>"}`. Las
  coordenadas no finitas (NaN/Inf) se rechazan con `InvalidLocationError`, de
  modo que la salida siempre es JSON estricto (sin `NaN`).
- No hay puntuación global de riesgo/seguridad/factibilidad ni "ganador"
  automático. El Backend NO debe sintetizar un score ni declarar un ganador;
  `compare_locations` entrega diferencias por factor y `review_items`.
- Los catálogos trasladan marcas `UNKNOWN`/`PENDING_SOURCE_PROVENANCE`: no
  presentarlas como verificadas en la UI/API.
- El módulo ML permanece deshabilitado; no exponer predicciones.

Cualquier cambio de firma se versionará (ENGINE_CONTRACT_V2); V1 es estable.
