# Documentación del Bloque 4 — Frontend

Interfaz implementada con autorización expresa del equipo para utilizar las 13 imágenes nuevas de `../../../Mockup/` como referencia visual. Datos, estados, campos y restricciones se ajustan a los contratos existentes, no a los números ilustrativos de las imágenes.

- [Ejecución, tecnología, rutas y límites](../../frontend/README.md).
- [Validación y pruebas pendientes del equipo](VALIDATION.md).
- [Procedencia de los datos y fuentes oficiales candidatas](SOURCE_REVIEW_2026-09-29.md).
- [QA de los diez puntos del Plan Maestro](QA_PLAN_MAESTRO_10_PUNTOS.md).
- [Aprobación de diseño](../../design/DESIGN_READY.md).
- [Contrato REST consumido](../api/REST_CONTRACT_V1.md).
- [Contexto del proyecto](../project/PROJECT_CONTEXT.md).

Se mantiene el flujo localidad A → evidencia/ficha → localidad B → comparación. MVP únicamente Irapuato y Celaya; vivienda, edificación y vialidad. No se implementan selección de predios, autorización técnica de obras, puntuaciones de riesgo, Machine Learning, cuentas ni historial.

La interfaz diferencia los seis estados del contrato, separa contexto municipal, muestra temporalidad y hace explícita la información desconocida. El mapa es referencia visual; CRS_UNKNOWN no queda resuelto por colocar un marcador. El PDF se obtiene mediante impresión del navegador.

Pendiente del equipo: revisión manual de navegación, interpretación, impresión y comportamiento en sus dispositivos. La disponibilidad del preview privado no equivale a aprobación de producción ni a validación científica de los datos.
