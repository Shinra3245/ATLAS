# Bloque 3 — Backend / Integración

STATUS: DONE
CURRENT_PHASE: CURRENT_CONTRACT_REAL_HTTP_VERIFIED

AVAILABLE_ENDPOINTS:
- GET /api/health
- GET /api/meta
- GET /api/layers
- GET /api/locations
- GET /api/locations/{id}
- POST /api/analyze
- POST /api/compare
- GET /api/sources
- GET /api/ml/status

ENGINE_INTEGRATION_STATUS: connected_real_data
La API llama a `engine.analyze_location` y `engine.compare_locations` y reenvía su JSON.
El markdown `ENGINE_CONTRACT_V1.md` YA está publicado, junto con
`engine_comparison.schema.json`. El DATA CONTRACT V1 está conectado: 755
localidades, 53 atributos de catálogo, 14 fuentes y extensión separada de 57
campos municipales (datos reales, no fixtures; procedencia parcial visible).

FUNCTIONAL_FIXES_APPLIED:
- Búsqueda de localidades consulta los campos reales `locality` y `municipality`
  (buscar "Irapuato" ya devuelve resultados).
- `locality_id` inexistente responde 404 NOT_FOUND (antes 200 "fuera de alcance").
- Comparar la misma localidad consigo misma (coordenadas distintas) responde 422
  SAME_LOCATION, usando el campo `same_locality` del motor.
- Contrato REST y este status actualizados: contrato del motor y datos reales
  publicados.
- La compuerta de cobertura respeta locality_id cuando existe; usa la localidad
  canónica del motor y permite comparar claves distintas con coordenadas
  auxiliares iguales. La misma localidad resuelta sigue respondiendo 422.

VALIDATION: 36_API_TESTS_PASSED, 66_ENGINE_TESTS_PASSED, 14_REAL_HTTP_CHECKS_PASSED
EVIDENCE: docs/evidence/technical_verification.json, docs/evidence/api_verification.json
REPRODUCE: python3 scripts/demo/verify_technical.py
FRONTEND_HANDOFF: coordination/requests/from_block_3/HANDOFF_TECHNICAL_CLOSURE.md
RUNTIME_NOTE: el Uvicorn existente en puerto 8000 comenzó antes de los cambios;
su responsable debe reiniciarlo para cargar código/datos actuales. Se validó una
instancia propia aislada sin matar procesos ajenos.

ML_STATUS: DISABLED_PENDING_TARGET_VALIDATION

KNOWN_LIMITATIONS:
- Cobertura operativa: solo Irapuato y Celaya. Guanajuato completo es implementación futura.
- La compuerta geográfica usa la resolución del motor sobre las localidades publicadas, no una caja fija.
- La API valida el JSON del motor contra el ENGINE CONTRACT antes de publicarlo. No rellena factores ni traduce estados.
- /api/sources, /api/layers y /api/locations reenvían los catálogos que publique el motor. No se leen data/incoming, data/raw ni data/processed desde el backend.
- El contexto municipal de los cuatro libros de localidad llega dentro de `context` con estado `PARTIAL_DATA`. No es medición local ni nivel de riesgo.
- ML permanece apagado.
- No hay autenticación. CORS de desarrollo: http://localhost:5173, más `ATLAS_CORS_ORIGINS`. Sin comodín y sin exposición pensada para Internet.
- Un solo proceso Uvicorn, sin recarga automática. Hay que reiniciarlo para tomar cambios del motor.

LOCAL_API: http://127.0.0.1:8000
LAN_API: http://192.168.10.10:8000
OPENAPI: http://127.0.0.1:8000/docs
REST_CONTRACT: docs/api/REST_CONTRACT_V1.md
