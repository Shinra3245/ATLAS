# Requisitos verificables del MVP

Derivados de los diez puntos del Plan Maestro. La viabilidad económica no
forma parte de esta etapa. La verificación técnica corresponde a la API y
motor; el cierre visual exige evidencia de navegador adicional.

| ID | Requisito | Prioridad | Criterio de aceptación | Estado y evidencia |
|---|---|---|---|---|
| R-01 | Alcance Irapuato/Celaya | Obligatoria | Catálogo de 755 localidades; puntos sin asociación y municipios ajenos rechazados. | Verificado en datos, API y HTTP. |
| R-02 | Tres tipos de obra | Obligatoria | housing/building/road admitidos; tipo inválido rechazado; valores base invariantes. | Verificado en motor/API/HTTP; selector visual pendiente de validación. |
| R-03 | Conservación de originales | Obligatoria | Incoming y raw no cambian; conflicto de hash aborta; entradas y salidas trazables. | Verificado por `data/metadata/validation_report.json`. |
| R-04 | Resolución territorial explícita | Obligatoria | Clave autoritativa o asociación limitada; aproximación y localidad/predio diferenciados. | Verificado por pruebas y HTTP; visualización de notas pendiente. |
| R-05 | Factores núcleo | Obligatoria | Fuente, geometría/método, cobertura y unidades válidas por factor. | Parcial; faltan capas de `../data/PENDING_LAYERS.md`. |
| R-06 | Ficha explicable | Obligatoria | Condiciones, fuentes, cobertura, limitaciones y aspectos a revisar en cada análisis. | Verificado en motor/API; presentación visual pendiente. |
| R-07 | Comparación homogénea | Obligatoria | A/B reproduce valores y estados de las fichas; misma localidad se rechaza; sin ganador. | Verificado por HTTP para tres tipos de obra. |
| R-08 | Faltantes e historia | Obligatoria | Nulo no se vuelve cero o riesgo bajo; daño 2014 no se presenta como amenaza actual. | Verificado en datos, motor/API/HTTP. |
| R-09 | Contexto municipal | Obligatoria al incorporar esos libros | Claves/identidad verificadas; valores municipales separados, PARTIAL_DATA y contexto. | Verificado en datos y HTTP; fuente original aún parcial. |
| R-10 | Operación sin ML | Obligatoria | ML desactivado no afecta análisis, catálogos ni comparación. | Verificado por HTTP y pruebas. |
| R-11 | Flujo de navegador | Obligatoria | A → ficha → B → comparación, fuentes y errores operables. | Desarrollo y validación en otra sesión. |
| R-12 | Demostración reproducible | Obligatoria | Recorrido de usuario en menos de siete minutos, respaldos y evidencias reales. | Guion técnico preparado; ensayo visual pendiente. |
| R-13 | Reglas profesionales y usuarios | Obligatoria para afirmar validación | Casos revisados, justificación de reglas y participantes reales documentados. | Pendiente; protocolo en `../analytics/RULES_VALIDATION_V1.md`. |
| R-14 | Exportación PDF | Opcional | Archivo derivado del resultado real, con fuentes y advertencia. | No certificada por esta sesión. |

Evidencias consolidadas: `../evidence/technical_verification.json`,
`../evidence/api_verification.json` y `../evidence/evidence_log.md`.
No se incorporan normas, permisos, certificaciones ni umbrales sin fundamento.
