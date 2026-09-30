# Entrega verificada del Data Contract V1

Estado: DELIVERED. Responsable: Bloque 1. Versión: 1.0.0.

Se entregan `data/processed/v1/analysis_units.csv` y `analysis_units.json`: 755 unidades de localidad (434 Irapuato, 321 Celaya), 64 campos. Clave `id` CVEGEO de 9 caracteres, `municipality`, `locality`, `latitude`, `longitude`, `altitude_m` y variables censales/históricas/distancias documentadas campo por campo. No contiene predios ni geometrías poligonales.

Contrato definitivo: `data/contracts/DATA_CONTRACT_V1.md`. Nulos CSV: celda vacía; JSON: null. Nunca sustituir por cero ni aplicar atributos de localidad a una coordenada arbitraria.

Pendiente, elevación DEM y rugosidad no se habilitarán desde la tabla de terreno mientras no se entregue el ráster original y el método. CRS de las coordenadas censales: CRS_UNKNOWN; CRS de distancias declarado: EPSG:6372. No confundir ambos.

Precipitación publicada en `climate_station_monthly.json` y `.csv`: 50 registros (25 meses por estación), enero 2024–enero 2026. Uso CONTEXT_ONLY, no superficie ni unión por cercanía a localidades. Los registros repetidos de marzo 2025 fueron consolidados en productos, conservando ambos ARCHIVO_ORIGEN y original_rows; incoming/raw no fueron alterados.

## Integración

- `layer_manifest.json`: inventario de atributos por localidad, no capas de geometría continua.
- `sources_catalog.json`: 10 compilaciones recibidas, identificadores de procedencia estables. Contiene los campos solicitados por Bloque 3, pero todas llevan SOURCE_PROVENANCE_PARTIAL. No publicar atribuciones declaradas como procedencia autenticada; UNKNOWN y PENDING_SOURCE_PROVENANCE deben permanecer visibles.
- `manifest.json`: hashes de todos los productos, alcance, conteos y versión.
- `data/contracts/analysis_unit.schema.json` y `layer_manifest.schema.json`: esquema de cada objeto, no de la lista contenedora.
- `data/metadata/field_dictionary.json`, `dataset_registry.csv`, `availability.json`: diccionario, trazabilidad y disponibilidad.
- `data/metadata/validation_report.json`: 15 pruebas aprobadas y reconstrucción determinista; los originales permanecen idénticos.

Usar las claves exactamente como se documentan. En CSV conservar ceros iniciales de id/municipality_code/locality_code; preferir JSON para evitar inferencia automática de tipos. Códigos históricos "riesgo_*_2014" significan daño reportado en 2014, no probabilidad actual ni variable objetivo ML. Las distancias son precalculadas por la fuente recibida y no fueron regeneradas a partir de geometría original.

Solicitud: confirmar recepción del contrato mediante una respuesta propia de Bloque 2, sin modificar estos archivos. Si cambia la unidad de análisis o el esquema, coordinar una nueva versión; no reinterpretar V1 silenciosamente.
