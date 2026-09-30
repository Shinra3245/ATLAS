# Solicitud: cotejo de procedencia y nuevos insumos territoriales

Fecha: 2026-09-29
Solicitante: Bloque 4 — Frontend
Destinatario: Bloque 1 — Datos y SIG
Estado: PENDIENTE DE RESPUESTA

## Contrato esperado y recibido

Esperado por el cliente: fuente institucional exacta, producto/edición, URL original, fecha, licencia, cobertura y método de cálculo por variable publicada.

Recibido: el catálogo publica 14 registros con `SOURCE_PROVENANCE_PARTIAL`; en una evaluación de Irapuato 110170001 aparecen cinco compilaciones usadas, sin enlaces originales verificados. `data_origin` entrega el nombre del archivo interno. El frontend ya muestra etiquetas legibles y la procedencia declarada o no documentada, sin modificar las respuestas del motor.

## Evidencia mínima

- El libro principal atribuye `ALTITUD`, `POBTOT` y coordenadas a ITER 2020; las notas atribuyen distancias a cartografía de INEGI. La pestaña Fuentes menciona un CSV maestro y un ZIP cartográfico; faltan originales y ejecución reproducible de las distancias.
- Los cuatro libros municipales dicen provenir de otros libros temáticos y documentos anexos; los insumos originales no están acreditados en el registro actual.
- La liga INEGI UPC 702825739911 compartida por el equipo corresponde a San Bartolo de Berrios, San Felipe; no puede cubrir por sí sola los dos municipios del MVP.
- Inventario de candidatos y límites: `docs/frontend/SOURCE_REVIEW_2026-09-29.md`.

## Cambio solicitado al propietario

1. Cotejar las variables censales publicadas con [ITER 2020](https://www.inegi.org.mx/programas/ccpv/2020/) por CVEGEO y registrar discrepancias.
2. Solicitar al equipo el CSV maestro, ZIP cartográfico y los cuatro libros temáticos originales con anexos o enlaces exactos. Sin esos originales, mantener institución y proceso como parciales/no documentados.
3. Evaluar productos oficiales de INEGI, CENAPRED, CONAGUA/SMN y CONANP para DEM, pendiente, fallas, inundación, precipitación, uso de suelo y ANP, exclusivamente donde cubran Irapuato/Celaya y con CRS, fecha, escala y licencia comprobados.
4. Preservar `incoming` y `raw`, generar nuevos artefactos reproducibles y actualizar registro, contrato, catálogo de fuentes y documentación solo tras validación. No reutilizar automáticamente la cartografía consultada como origen de valores antiguos.
5. Notificar al Bloque 4 las nuevas etiquetas públicas y estados verificados por factor para reflejarlos en la interfaz.

Impacto: trazabilidad comprensible para el usuario y posibilidad de resolver factores actualmente pendientes sin crear afirmaciones de procedencia no demostradas.
