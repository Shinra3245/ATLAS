# ATLAS - Bloque 3: Backend, API e Integración

## Rol del agente

Eres el propietario de **FastAPI, integración, contratos REST, ejecución local y estabilidad de la demo**. No decides qué significa una variable geográfica ni cómo se calcula una condición: eso pertenece a Datos/SIG y Motor Analítico.

## Propiedad exclusiva

```text
backend/**
tests/api/**
docs/api/**
```

No modifiques:

```text
data/**
engine/**
ml/**
frontend/**
```

## Objetivo

Exponer una API estable para que el frontend pueda:
- conocer cobertura y capas;
- listar/buscar puntos de análisis;
- analizar A;
- analizar B;
- comparar A/B;
- consultar metadatos/fuentes;
- mostrar estado de ML;
- manejar faltantes y errores de forma explícita.

## Stack

- Python.
- FastAPI.
- Uvicorn.
- Pydantic.
- CORS limitado a los orígenes de desarrollo/demo.
- Logging estructurado.
- Pruebas con pytest/TestClient o equivalente compatible.

**Compatibilidad:** el equipo usa Python 3.14.7. Antes de fijar dependencias SIG pesadas, comprobar wheels/compatibilidad. Si hay problemas, usar entorno aislado Python 3.12/3.13 o contenedor; no alterar el Python del sistema.

## Estructura sugerida

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── health.py
│   │   ├── locations.py
│   │   ├── analysis.py
│   │   ├── comparison.py
│   │   └── metadata.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── schemas/
│   ├── services/
│   └── adapters/
│       ├── data_adapter.py
│       └── engine_adapter.py
└── tests/
```

## Desarrollo continuo

### B1 - API sobre mocks
No esperes al Bloque 2. Implementa endpoints con fixtures compatibles con el Engine Contract propuesto.

### B2 - Endpoints mínimos

```text
GET  /api/health
GET  /api/meta
GET  /api/layers
GET  /api/locations?municipality=Irapuato&query=...
GET  /api/locations/{id}
POST /api/analyze
POST /api/compare
GET  /api/sources
GET  /api/ml/status
```

`POST /api/analyze` preferido porque el payload crecerá.

Ejemplo:

```json
{
  "project_type": "building",
  "location": {"type": "analysis_point", "id": "11017..."}
}
```

### B3 - Scope geográfico
Rechazar o marcar fuera de alcance cualquier solicitud fuera de Irapuato/Celaya para MVP.

Respuesta recomendada:

```json
{
  "error": "OUT_OF_MVP_SCOPE",
  "message": "El prototipo actual cubre Irapuato y Celaya. Guanajuato estatal está planificado como expansión futura."
}
```

### B4 - Adaptadores
Backend no debe leer directamente XLSX en cada request.

```text
processed/v1 -> data_adapter -> engine -> API schema
```

Cargar/cachear dataset al iniciar si el tamaño lo permite.

### B5 - Manejo de faltantes
No utilizar HTTP 500 para datos ausentes válidos. Un análisis puede ser exitoso y contener condiciones `INSUFFICIENT_INFORMATION`.

Errores 4xx/5xx solo para:
- request inválido;
- unidad inexistente;
- scope inválido;
- contrato roto;
- fallo interno real.

### B6 - Comparación
El backend valida:
- A != B;
- mismo `project_type`;
- ambas dentro del MVP;
- mismo Engine Contract version.

No calcula un ganador.

### B7 - Metadatos
`/api/sources` debe permitir al frontend mostrar:
- institución;
- dataset;
- año/fecha;
- cobertura;
- limitación;
- enlace/identificador si está disponible.

### B8 - Integración real
Solo cambia `engine_adapter` al recibir `ENGINE_CONTRACT_v1`. No reescribas rutas o frontend para adaptar semánticas no congeladas.

## REST Contract v1

Publicar:

```text
docs/api/REST_CONTRACT_v1.md
```

Incluye:
- endpoints;
- schemas;
- ejemplos;
- códigos de error;
- versión;
- CORS;
- timeout esperado.

Este contrato es la única fuente que debe consumir el frontend.

## STOP / conflictos

### Engine Contract no coincide
- marca integración `BLOCKED_CONTRACT`;
- sigue trabajando con fixtures;
- crea solicitud al Bloque 2;
- NO parchees semántica dentro de la API.

### Data Contract no coincide
La discrepancia se reporta a Bloque 1 a través de Bloque 2 si afecta análisis.

### Frontend solicita campo nuevo
Si es solo presentación y ya existe dato, puede añadirse mediante versión compatible. Si cambia semántica, escala al propietario del contrato.

## Estabilidad de demo

Antes de hora 21:
- deshabilitar auto-reload;
- crear comando único de arranque;
- healthcheck;
- datos locales disponibles;
- fallback offline;
- logs a archivo;
- puerto documentado;
- prueba desde otra laptop por red/Tailscale si corresponde.

## Seguridad mínima

- no exponer secretos;
- `.env` fuera de Git;
- no habilitar escritura arbitraria;
- validar coordenadas/IDs;
- limitar CORS;
- sin panel admin innecesario.

## Pruebas mínimas

- health 200;
- analysis válido 200;
- compare válido 200;
- fuera de Irapuato/Celaya -> respuesta explícita;
- ubicación inexistente -> 404/422 coherente;
- datos parciales -> 200 con faltantes;
- engine deshabilita ML -> API sigue funcionando;
- contratos serializan/deserializan correctamente.

## Handoff al Frontend

Entregar:
- URL base;
- OpenAPI;
- REST Contract;
- fixtures JSON;
- ejemplos curl;
- estados de loading/error/partial.

## Definition of Done

El frontend puede implementar todo el flujo del MVP sin acceder directamente a archivos de datos ni a funciones internas del motor.
