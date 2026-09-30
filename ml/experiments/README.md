# ML — Experimentos (estado: HISTORICAL_EXPERIMENT)

ML es COMPLEMENTARIO. ATLAS funciona sin ML. No se entrena ningún modelo hasta
superar el gate de validación completo. El estado se declara en
[`ml/status.py`](../status.py) y el gate en
[`docs/analytics/ML_VALIDATION_GATE.md`](../../docs/analytics/ML_VALIDATION_GATE.md).

## Experimento candidato (NO activo)

Susceptibilidad histórica a inundación usando `RIESGO_INUNDACION_2014`
**solo como etiqueta histórica experimental** (`HISTORICAL_EXPERIMENT`), nunca
como riesgo actual 2026.

## Antes de entrenar (13 verificaciones obligatorias)

1. variable objetivo definida y documentada;
2. significado real de la etiqueta;
3. fuente verificada;
4. año/vigencia (p. ej. 2014);
5. número de observaciones utilizables;
6. distribución de la variable;
7. clases;
8. balance / estrategia ante desbalance;
9. control de fuga espacial;
10. partición train/test (espacial o por grupos, no ingenua);
11. baseline simple;
12. métricas apropiadas (precision/recall/F1, matriz de confusión);
13. utilidad real demostrada sobre el baseline.

Si el experimento no supera el baseline o la etiqueta es inadecuada, NO se
integra en la demo.

## Orden de algoritmos

1. baseline simple (p. ej. regresión logística / regla mayoritaria);
2. Random Forest;
3. XGBoost solo si demuestra una mejora real y defendible.

NO se usan redes neuronales solo para "añadir IA".

## Validación espacial

Localidades cercanas comparten características espaciales: evitar particiones
ingenuas. Documentar siempre `train/test strategy`, `spatial leakage risk` y
`limitations`.

## Reglas de dependencias

Las dependencias de ML (pandas, scikit-learn, etc.) NO se instalan mientras el
módulo esté deshabilitado. Cuando el gate se supere, se declararán en un archivo
de requisitos separado dentro de `ml/`, en un entorno virtual propio, sin
instalación global.
