# Backend

API FastAPI de ATLAS para Irapuato y Celaya. Recibe solicitudes, las valida y reenvía el resultado del motor. No recalcula condiciones territoriales ni declara cobertura estatal.

El contrato HTTP está en `../docs/api/REST_CONTRACT_V1.md`. `POST /api/analyze` y `POST /api/compare` llaman a `engine.analyze_location` y `engine.compare_locations`.

## Entorno

Python del nodo: 3.14.7. El entorno aislado es `backend/.venv`. No se instaló nada en el Python del sistema.

FastAPI 0.142.1, Uvicorn 0.54.0 y Pydantic 2.13.5 tienen wheels compatibles con 3.14. No hay dependencias SIG.

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

## Arranque

Desde `backend/`, un solo proceso, sin recarga automática:

```bash
ss -ltnp | grep ':8000' || true
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

El adapter añade la raíz del repositorio a `sys.path` para importar `engine`.

- API: `http://127.0.0.1:8000`
- OpenAPI: `http://127.0.0.1:8000/docs`
- Salud: `http://127.0.0.1:8000/api/health`

CORS de desarrollo: `http://localhost:5173`. Para otra laptop en LAN o Tailscale, exportar `ATLAS_CORS_ORIGINS` con orígenes explícitos. No usar `*`.

Si el puerto 8000 está ocupado, no se mata el proceso ajeno. Se identifica al dueño y se documenta en `coordination/status/BLOQUE_3.md`.

## Pruebas

Desde la raíz del repositorio:

```bash
backend/.venv/bin/pytest tests/api
```

El doble de motor está solo en `tests/api/engine_double.py` y marca sus fuentes como `TEST_FIXTURE`.

## Limitaciones

- Motor y datos reales conectados: 755 localidades, 53 atributos de catálogo y 14 fuentes. Las fuentes conservan procedencia parcial; no se presentan como verificadas.
- La ficha incorpora 57 campos municipales como `PARTIAL_DATA`, separados de las mediciones por localidad. No equivalen a datos del predio.
- Fallas, laderas y uso de suelo permanecen sin capa validada; pendiente bloqueada hasta validar DEM/método. El antecedente de inundación 2014 no es riesgo actual.
- Una clave `locality_id` publicada tiene prioridad sobre coordenadas auxiliares, como establece el motor. La salida usa la coordenada canónica de esa localidad. Una clave inexistente responde 404 y dos entradas resueltas a la misma localidad responden 422.
- `/api/sources`, `/api/layers` y `/api/locations` reenvían catálogos del motor. El backend no lee directamente XLSX ni archivos de `data/`.
- ML: `HISTORICAL_EXPERIMENT`, leído de `ml_status()`. No publica una susceptibilidad.

## Verificación HTTP reproducible

Desde la raíz:

```bash
python3 scripts/demo/verify_api.py --launch
```

Inicia una API propia en un puerto local libre, comprueba los tres tipos de obra y comparación A/B con datos reales, y la detiene al terminar. No interrumpe la API que otra sesión esté usando. Evidencia: `docs/evidence/api_verification.json`.

Un proceso Uvicorn iniciado antes de cambios de código o datos debe reiniciarse por su responsable para cargar la nueva publicación: el motor conserva caché durante la vida del proceso.
