# REQ-2026-09-29 — Bloque 2 → Bloque 3: ENGINE CONTRACT v1 disponible

- Bloque solicitante: 2 (Motor analítico / ML)
- Bloque destinatario: 3 (Backend / Integración)
- Estado del motor: WORKING — API estable e integrable desde ya (sobre fixtures)

## Qué se publica

El motor analítico está listo para integración. El ÚNICO documento que Backend
necesita leer es:

- `engine/contracts/ENGINE_CONTRACT_V1.md` (contrato)
- `engine/contracts/engine_result.schema.json` (esquema JSON formal)

No es necesario conocer las estructuras internas del motor.

## Interfaz importable

```python
from engine import analyze_location, compare_locations

result = analyze_location({"lat": 20.674, "lon": -101.349}, "building").to_dict()
cmp = compare_locations(A, B, "building").to_dict()
```

- Determinista, sin red externa, sin dependencias de terceros (solo stdlib).
- `project_type`: `housing` | `building` | `road`.
- Errores: `InvalidProjectTypeError`, `InvalidLocationError` (ambos `ValueError`).
- Fuera de Irapuato/Celaya NO es error: `area_status = "outside_supported_area"`.

## Qué puede consumir Backend hoy

- Estructura completa de `analyze_location` y `compare_locations` (estados,
  categorías, cobertura, fuentes, explicaciones, limitaciones, review_items).
- Para desarrollo/mock puede inyectar la fuente de prueba (marcada TEST_FIXTURE):
  `load_fixture("tests/engine/fixtures/atlas_test_fixture.json")`.

## Qué NO debe hacer Backend

- No redefinir la semántica del análisis (autoridad: ENGINE CONTRACT).
- No esperar `winner`, `*_score` ni porcentaje global: NO existen por diseño.
- Si detecta discrepancia de contrato, registrar solicitud en
  `coordination/requests/from_block_3/`; Bloque 2 resuelve y versiona.

## Pendiente (no bloquea la integración)

Los valores reales por factor dependen de que Bloque 1 publique
`DATA_CONTRACT_V1.md` + `data/processed/v1/` (ver `TO_BLOCK_1_REQ_001.md`).
Mientras tanto, la fuente de producción devuelve `INSUFFICIENT_DATA`/
`BLOCKED_DATA_VALIDATION`, nunca "riesgo bajo".
