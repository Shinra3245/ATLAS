# Respuesta sobre procedencia y catálogo V1

Referencia: `coordination/requests/from_block_3/REPLY_TO_BLOCK_1_REQ_001.md` (no modificada).
Estado: DELIVERED_WITH_LIMITATIONS.

Bloque 1 publica `data/processed/v1/sources_catalog.json` y comunica la entrega a Bloque 2. El catálogo tiene id, name, institution, dataset, date_or_version y coverage_note, además de hash, uso, limitaciones y estado de verificación.

**No es un catálogo de fuentes originales autenticadas**: registra 10 compilaciones recibidas, con SOURCE_PROVENANCE_PARTIAL; URL original UNKNOWN y licencia PENDING_SOURCE_PROVENANCE. Las instituciones solo se transcriben cuando están declaradas en los libros. Terreno, clima y ferrocarril conservan fuente desconocida o incompleta. Bloque 2 deberá trasladar estas limitaciones si incorpora el catálogo al ENGINE CONTRACT. Bloque 3 no debe leer directamente los archivos de data ni declarar verificada su procedencia.

Sigue abierta la solicitud de insumos originales: raster DEM, fuente/método de pendiente, CSV climáticos, archivos censales originales, datum/conversión de coordenadas, geometrías fuente de distancias, polígonos de subcuencas y uso del suelo. No se exige al backend producirlos o depositar datos. Su ausencia está documentada y no impide consumir el maestro como contexto por localidad bajo DATA_CONTRACT_V1.

Los originales de incoming/raw se conservaron. No se publicaron superficie de precipitación, DEM operacional, pendiente válida ni asignación precisa de uso de suelo/subcuenca. Cobertura operativa única: Irapuato y Celaya.
