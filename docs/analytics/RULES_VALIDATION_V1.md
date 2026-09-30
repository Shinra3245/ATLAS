# Reglas implementadas y validación pendiente

Este registro describe la implementación vigente; no constituye aprobación
de umbrales técnicos por especialistas ni modificación de DP-03.

| Regla | Implementación verificable | Límite |
|---|---|---|
| Inundación histórica | 1: antecedente reportado; 0: sin condición registrada; null: información insuficiente. Marco temporal histórico. | Ninguno de esos estados demuestra el riesgo actual ni seguridad. |
| Altitud | Valor censal en metros, periodo de referencia 2020. | No es elevación precisa del predio, DEM ni pendiente. |
| Contexto municipal | 57 campos separados del maestro, categoría contexto y PARTIAL_DATA. | Repetir por localidad no cambia la resolución municipal. |
| Distancias | Conservación de valores recibidos y unidades en metros. | Procedencia parcial; no se convierten en amenaza, conectividad efectiva ni costo. |
| Tipo de obra | Conservación de valor, unidad, estado, fuente y temporalidad. Cambian prioridades y aspectos a revisar. | Prioridades no son ponderaciones ni umbrales normativos. |
| Coordenadas | Finitas, rangos globales y límite de asociación del contrato. Toda asociación aproximada se informa. | La resolución por localidad no es cobertura continua ni evaluación de predio. |
| Clave de localidad | La clave publicada tiene prioridad y usa coordenadas canónicas. | Clave desconocida se rechaza; no se inventa una localidad. |
| Comparación | Misma matriz y tipo de obra; diferencias descriptivas. | No calcula ganador, aprobación ni puntuación global. |
| ML | Desactivado, análisis independiente. | Activación condicionada al gate de validación. |

Pruebas automatizadas y comprobaciones HTTP: `../evidence/technical_verification.json`
y `../evidence/api_verification.json`. Reproducción:

```bash
python3 scripts/demo/verify_technical.py
```

## Revisión con especialista aún no ejecutada

Por cada regla o umbral propuesto registrar:

| Factor y tipo de obra | Fuente técnica y alcance | Regla propuesta y unidad | Casos revisados | Resultado y limitación | Especialista y fecha |
|---|---|---|---|---|---|
| Pendiente de revisión | | | | | |

No asignar distancias, porcentajes ni categorías de peligro hasta contar con
justificación y casos de validación. Toda corrección debe conservar la
distinción entre antecedente, amenaza, exposición, vulnerabilidad y contexto.

## Validación con usuarios aún no ejecutada

Pedir a un participante del segmento definido que seleccione una localidad,
interprete su ficha, compare otra ubicación e identifique fuentes y faltantes.
Registrar perfil, fecha, caso, tareas completadas, tiempo, dificultades y
comprensión del alcance. Comprobar si distingue localidad de predio y ausencia
de información de ausencia de riesgo. No presentar esta guía como entrevistas
realizadas ni como evidencia de disposición a pagar.
