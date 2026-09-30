# Gate de validación de Machine Learning (Bloque 2)

Estado actual: **`DISABLED_PENDING_TARGET_VALIDATION`**.

ML es complementario y explicable. ATLAS funciona sin ML y el módulo puede
desactivarse sin romper la aplicación. Este documento define las condiciones que
deben cumplirse ANTES de entrenar o presentar cualquier resultado de ML. El
estado inspeccionable vive en [`../../ml/status.py`](../../ml/status.py).

## Por qué está apagado

El dataset maestro declara que **no existe variable objetivo de ML creada**. Sin
etiqueta validada no hay modelo defendible. El análisis SIG/reglas es el núcleo
obligatorio.

## Checklist obligatorio (todos deben cumplirse)

| # | Verificación | Estado |
|---|---|---|
| 1 | Variable objetivo definida y documentada | ✗ |
| 2 | Significado real de la etiqueta | ✗ |
| 3 | Fuente verificada | ✗ |
| 4 | Año / vigencia (p. ej. 2014) | ✗ |
| 5 | Número de observaciones utilizables | ✗ |
| 6 | Distribución de la variable | ✗ |
| 7 | Clases | ✗ |
| 8 | Balance / estrategia ante desbalance | ✗ |
| 9 | Control de fuga espacial | ✗ |
| 10 | Partición train/test (espacial o por grupos) | ✗ |
| 11 | Baseline simple | ✗ |
| 12 | Métricas apropiadas (precision/recall/F1, matriz de confusión) | ✗ |
| 13 | Utilidad real demostrada sobre baseline | ✗ |

## Experimento candidato (no activo)

`RIESGO_INUNDACION_2014` **solo como `HISTORICAL_EXPERIMENT`**, nunca como riesgo
actual. Si el experimento no supera el baseline o la etiqueta es inadecuada, NO
se integra.

## Orden de algoritmos

1. baseline simple → 2. Random Forest → 3. XGBoost solo si mejora demostrable.
No se usan redes neuronales solo para "añadir IA".

## Validación espacial

Localidades cercanas comparten características espaciales. Evitar particiones
ingenuas. Documentar `train/test strategy`, `spatial leakage risk` y
`limitations`.

## Explicabilidad de ML (si algún día se activa)

Cada resultado debe declarar: que es `experimental`, versión del modelo, fecha,
features usadas, métrica de validación, importancias con cautela y limitaciones.
Nunca convertir `predict_proba` directamente en "probabilidad real de daño".
