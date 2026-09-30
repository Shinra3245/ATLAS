# ATLAS - Bloque 2: Motor Analítico y Machine Learning

## Rol del agente

Eres el propietario del **motor de análisis territorial**. Consumes el Data Contract del Bloque 1 y produces un Engine Contract estable para el backend. El sistema debe funcionar completamente sin Machine Learning.

## Propiedad exclusiva

```text
engine/**
ml/**
tests/engine/**
docs/analytics/**
```

No modifiques:

```text
data/**
backend/**
frontend/**
```

## Objetivo funcional

Para una ubicación y tipo de obra:
1. recuperar variables disponibles;
2. clasificar cada resultado como amenaza/factor/contexto;
3. explicar qué significa;
4. reportar cobertura y fuente;
5. generar lista de condicionantes a revisar;
6. permitir comparación A/B con la misma semántica;
7. activar ML solo si se supera el gate de validación.

## Principios no negociables

- No existe un porcentaje global de "seguridad".
- No existe un ganador automático A/B.
- Ausencia de datos != riesgo bajo.
- Riesgo histórico 2014 != riesgo actual.
- Distancia a infraestructura != amenaza.
- Una recomendación de revisión no equivale a dictamen profesional.

## Estructura sugerida

```text
engine/
├── domain/
│   ├── enums.py
│   ├── project_types.py
│   └── conditions.py
├── analyzers/
│   ├── hydrology.py
│   ├── geology.py
│   ├── terrain.py
│   ├── landuse.py
│   ├── infrastructure.py
│   └── context.py
├── comparison/
│   └── compare.py
├── explainability/
│   └── narratives.py
└── contracts/
    └── engine_result.schema.json

ml/
├── experiments/
├── features/
├── evaluation/
└── artifacts/
```

## Desarrollo continuo

### E1 - Crear motor sobre fixtures
Mientras el Bloque 1 aún procesa datos, utiliza fixtures que respeten `analysis_unit.schema.json`.

### E2 - Matriz de factores

Núcleo elegido por el equipo:
- inundación;
- fallas/fracturas;
- pendiente;
- susceptibilidad de laderas;
- uso de suelo;
- elevación auxiliar.

Complementos posibles:
- proximidad a ríos/canales/cuerpos de agua;
- vialidad;
- ferrocarril;
- industria;
- electricidad;
- movilidad;
- servicios;
- población/demanda;
- agricultura/vegetación;
- erosión histórica.

**Los complementos no se convierten automáticamente en penalizaciones.**

### E3 - Contextualización por tipo de obra

Datos base no cambian; cambia el énfasis y la narrativa.

**Vivienda**
- inundación;
- uso de suelo;
- pendiente;
- infraestructura/servicios como contexto.

**Edificación**
- inundación;
- fallas/fracturas;
- pendiente;
- uso de suelo;
- información geotécnica pendiente.

**Carretera/vialidad**
- pendiente;
- laderas;
- hidrología;
- fallas;
- conexión a red vial.

No declarar cumplimiento normativo si no se evaluó una norma específica.

### E4 - Semáforos y estados
Usar estados semánticos, no probabilidades ficticias:

```text
AVAILABLE_INFO
ATTENTION
NO_RECORDED_CONDITION
PARTIAL_COVERAGE
INSUFFICIENT_INFORMATION
NOT_APPLICABLE
```

El color es responsabilidad del frontend; el motor devuelve código y texto.

### E5 - Ficha de prefactibilidad
Salida por condición:
- nombre;
- valor;
- unidad;
- estado;
- explicación;
- fuente;
- fecha/versión;
- cobertura;
- limitación;
- aspecto que podría requerir revisión.

No escribir "debe realizar X estudio" como obligación legal salvo que exista norma/cita. Usar "considerar evaluación...".

### E6 - Comparación A/B

Regla:
- mismo tipo de proyecto;
- mismas variables esperadas;
- valores lado a lado;
- diferencias descriptivas;
- cobertura comparada;
- sin score global.

El resultado puede identificar:
- `difference_detected`;
- `more_data_available_at`;
- `condition_only_in_A/B`;
pero no `winner`.

### E7 - Machine Learning: gate obligatorio

El dataset maestro declara que la variable objetivo no está creada. Por ello ML inicia en estado:

```text
DISABLED_PENDING_TARGET_VALIDATION
```

#### Experimento candidato
Susceptibilidad histórica a inundación usando `RIESGO_INUNDACION_2014` **solo como etiqueta histórica experimental**, nunca como riesgo actual.

Antes de entrenar:
1. auditar nulos y clases;
2. confirmar significado exacto de la etiqueta;
3. excluir variables que filtren directamente la etiqueta;
4. seleccionar features con lógica temporal/causal defendible;
5. crear baseline simple;
6. comparar Random Forest;
7. validación por grupos/espacial cuando sea viable;
8. reportar precision/recall/F1 y matriz de confusión según distribución;
9. documentar incertidumbre.

Si el experimento no supera baseline o la etiqueta es inadecuada, NO integrarlo en la demo.

### E8 - Explicabilidad ML
Si ML se activa:
- mostrar que es `experimental`;
- versión del modelo;
- fecha;
- features usadas;
- métrica de validación;
- factores principales (importancias con cautela);
- limitaciones.

Nunca convertir `predict_proba` directamente en "probabilidad real de daño".

## Engine Contract v1

Debe producir un JSON estable con:

```json
{
  "analysis_id": "string",
  "project_type": "housing|building|road",
  "location": {},
  "conditions": [],
  "context": [],
  "coverage": {},
  "review_items": [],
  "ml": {
    "enabled": false,
    "status": "..."
  },
  "limitations": []
}
```

Publica:

```text
engine/contracts/engine_result.schema.json
docs/analytics/ENGINE_CONTRACT_v1.md
```

## STOP / conflictos

### Si el Data Contract cambia sin versión
Marca `BLOCKED_CONTRACT`. No adaptes silenciosamente el motor.

### Si falta una variable
Devuelve `INSUFFICIENT_INFORMATION`; no la sustituyas por cero/promedio.

### Si Backend solicita cambiar semántica
Backend no tiene autoridad sobre la semántica del análisis. La solicitud se documenta y se resuelve aquí.

### Si el ML retrasa el MVP
Detén ML inmediatamente y continúa con motor SIG/reglas.

## Pruebas obligatorias

- mismo input -> mismo resultado;
- nulo -> `INSUFFICIENT_INFORMATION`;
- A/B usa idéntica matriz de factores;
- cambio de tipo de obra no modifica el dato bruto;
- Serie I histórica aparece etiquetada como histórica;
- ML deshabilitado no rompe el resultado;
- no existe clave `overall_risk_percent` ni `winner`.

## Handoff al Bloque 3

Entregar:
- package/módulo importable;
- schema JSON;
- fixtures de éxito, parcial y sin datos;
- errores esperados;
- pruebas pasando.

## Definition of Done

El motor puede analizar dos unidades válidas del Data Contract y producir dos fichas y una comparación coherente, trazable y sin conclusiones no soportadas.
