# DATA CONTRACT V1 — Bloque 1 → Bloque 2

Versión: **1.0.0**. Estado: listo para consumir una vez que `coordination/status/BLOQUE_1.md` indique READY_FOR_BLOCK_2.

## Archivos y lectura

- `data/processed/v1/analysis_units.json`: lista de 755 objetos tipados; opción recomendada para evitar inferencia CSV.
- `data/processed/v1/analysis_units.csv`: UTF-8, separador coma, encabezados, punto decimal, nulos como celdas vacías, identificadores como cadenas.
- `data/processed/v1/climate_station_monthly.json` y `.csv`: 50 observaciones de estación/mes, separadas del maestro.
- `data/processed/v1/layer_manifest.json`: metadatos de variables, disponibles/esperados, fuente y limitación. Son atributos por localidad, no polígonos descargables.
- `data/processed/v1/sources_catalog.json`: lista de fuentes recibidas y atribuciones declaradas, con SOURCE_PROVENANCE_PARTIAL; no equivale a autenticar cada compilación. Campos: id, name, institution, dataset, date_or_version, coverage_note, verification_status, usage, limitations, sha256, original_url, license_or_terms. Todos son strings. No ocultar UNKNOWN ni PENDING.
- `data/processed/v1/manifest.json`: versión, hashes, entradas y conteos. Verificar antes de integrar.
- `data/metadata/dataset_registry.csv`, `source_manifest.csv`, `field_dictionary.json` y `availability.json`: procedencia y capacidades.
- Schemas: `data/contracts/analysis_unit.schema.json` y `layer_manifest.schema.json`.

## Semántica y cobertura

Unidad única = locality; 434 Irapuato, 321 Celaya. Identificador CVEGEO, 9 caracteres. Coordenadas recibidas numéricas con CRS_UNKNOWN; no se emite GeoJSON ni se inventa EPSG:4326. Altitud censal en metros; no DEM. Las distancias son precalculadas en EPSG:6372 según el libro, sin reprocesar geometría original. No aplicar datos de localidad a coordenada arbitraria, promediar clima sobre municipios ni inferir una superficie.

Los indicadores `riesgo_*_2014` conservan nombre heredado, pero significan daño histórico reportado: 1=Con daño, 0=Sin daño, null=Sin información suficiente. No son probabilidad ni condición actual. No se crea variable objetivo ML. Los scores de cobertura son codificaciones ordinales heredadas y no porcentajes medidos. Fuente/temporalidad de distancias incompleta.

## Campos de análisis

La tabla siguiente es normativa para nombres, tipos, unidades, nullable, significado, fuente, temporalidad, cobertura y limitaciones.

| Nombre | Tipo JSON | Unidad | Nullable | Significado | Fuente / columna original | Temporalidad | Cobertura | Limitaciones |
|---|---|---|---|---|---|---|---|---|
| id | string | not_applicable | false | Clave CVEGEO de localidad, 9 caracteres | core_geospatial / CVEGEO | 2020 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| municipality_code | string | not_applicable | false | Clave municipal de 3 caracteres: 007/017 | core_geospatial / MUN | 2020 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| municipality | string | not_applicable | false | Nombre municipal | core_geospatial / NOM_MUN | 2020 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| locality_code | string | not_applicable | false | Clave de localidad de 4 caracteres | core_geospatial / LOC | 2020 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| locality | string | not_applicable | false | Nombre censal de localidad | core_geospatial / NOM_LOC | 2020 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| longitude | number | decimal_degrees | false | Coordenada de localidad recibida en grados decimales; no reproyectada | core_geospatial / LONGITUD | 2020 | 755/755 localidades | Datum original y método de conversión pendientes; CRS_UNKNOWN. No declarar EPSG:4326. |
| latitude | number | decimal_degrees | false | Coordenada de localidad recibida en grados decimales; no reproyectada | core_geospatial / LATITUD | 2020 | 755/755 localidades | Datum original y método de conversión pendientes; CRS_UNKNOWN. No declarar EPSG:4326. |
| altitude_m | integer | m | false | Altitud censal de la localidad respecto al nivel medio del mar (ITER 2020) | core_geospatial / ALTITUD | 2020 | 755/755 localidades | No equivale a un DEM ni a elevación precisa del predio; no derivar pendiente de puntos censales. |
| pobtot | integer | persons | false | Población total | core_geospatial / POBTOT | 2020 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| pob15_64 | integer | persons | true | Población de 15 a 64 años | core_geospatial / POB15_64 | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| pea | integer | persons | true | Población económicamente activa | core_geospatial / PEA | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| pocupada | integer | persons | true | Población ocupada | core_geospatial / POCUPADA | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| vivtot | integer | dwellings | false | Viviendas totales | core_geospatial / VIVTOT | 2020 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| tvivhab | integer | dwellings | false | Viviendas habitadas | core_geospatial / TVIVHAB | 2020 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| cob_electrica | number | ratio_0_1 | true | Indicador derivado de disponibilidad de servicios o automóvil en viviendas | core_geospatial / COB_ELECTRICA | 2020 | 443/755 localidades | No es amenaza ni índice de calidad estructural; denominadores reproducidos del archivo estatal. |
| cob_drenaje | number | ratio_0_1 | true | Indicador derivado de disponibilidad de servicios o automóvil en viviendas | core_geospatial / COB_DRENAJE | 2020 | 443/755 localidades | No es amenaza ni índice de calidad estructural; denominadores reproducidos del archivo estatal. |
| autos_por_100_viv | number | per_100_dwellings | true | Indicador derivado de disponibilidad de servicios o automóvil en viviendas | core_geospatial / AUTOS_POR_100_VIV | 2020 | 443/755 localidades | No es amenaza ni índice de calidad estructural; denominadores reproducidos del archivo estatal. |
| dis_trans_2014 | string | category | true | Categoría original: DIS_TRANS_2014 | core_geospatial / DIS_TRANS_2014 | 2014 | 610/755 localidades | No extrapolar fuera de la unidad de localidad. |
| frecuencia_est_2014 | integer | estimated_departures | true | Frecuencia ya aproximada a partir de intervalos categóricos | core_geospatial / FRECUENCIA_EST_2014 | 2014 | 331/755 localidades | Periodicidad exacta debe confirmarse con cuestionario fuente; no frecuencia medida. |
| tiempo_est_min_2014 | integer | minutes_approximate | true | Tiempo aproximado ya derivado de categoría de transporte | core_geospatial / TIEMPO_EST_MIN_2014 | 2014 | 331/755 localidades | No extrapolar fuera de la unidad de localidad. |
| drenaje_score_2014 | number | ordinal_score_0_1 | true | Codificación ordinal preexistente de cobertura descrita en etiqueta original | core_geospatial / DRENAJE_SCORE_2014 | 2014 | 200/755 localidades | No porcentaje medido ni probabilidad; escala heredada, no diseñada por ATLAS. |
| alumbrado_score_2014 | number | ordinal_score_0_1 | true | Codificación ordinal preexistente de cobertura descrita en etiqueta original | core_geospatial / ALUMBRADO_SCORE_2014 | 2014 | 200/755 localidades | No porcentaje medido ni probabilidad; escala heredada, no diseñada por ATLAS. |
| recub_score_2014 | number | ordinal_score_0_1 | true | Codificación ordinal preexistente de cobertura descrita en etiqueta original | core_geospatial / RECUB_SCORE_2014 | 2014 | 197/755 localidades | No porcentaje medido ni probabilidad; escala heredada, no diseñada por ATLAS. |
| riesgo_inundacion_2014 | integer | binary_code | true | Antecedente de daño reportado en 2014: 1=Con daño, 0=Sin daño; null=no dato | core_geospatial / RIESGO_INUNDACION_2014 | 2014 | 610/755 localidades | Código heredado, no probabilidad ni riesgo actual. 0 no demuestra seguridad. |
| riesgo_sequia_2014 | integer | binary_code | true | Antecedente de daño reportado en 2014: 1=Con daño, 0=Sin daño; null=no dato | core_geospatial / RIESGO_SEQUIA_2014 | 2014 | 610/755 localidades | Código heredado, no probabilidad ni riesgo actual. 0 no demuestra seguridad. |
| riesgo_helada_2014 | integer | binary_code | true | Antecedente de daño reportado en 2014: 1=Con daño, 0=Sin daño; null=no dato | core_geospatial / RIESGO_HELADA_2014 | 2014 | 610/755 localidades | Código heredado, no probabilidad ni riesgo actual. 0 no demuestra seguridad. |
| riesgo_incendio_2014 | integer | binary_code | true | Antecedente de daño reportado en 2014: 1=Con daño, 0=Sin daño; null=no dato | core_geospatial / RIESGO_INCENDIO_2014 | 2014 | 610/755 localidades | Código heredado, no probabilidad ni riesgo actual. 0 no demuestra seguridad. |
| dist_carretera_m | number | m | false | Distancia euclidiana precalculada a carretera | core_geospatial / DIST_CARRETERA_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_camino_m | number | m | false | Distancia euclidiana precalculada a camino | core_geospatial / DIST_CAMINO_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_rio_arroyo_m | number | m | false | Distancia euclidiana precalculada a rio arroyo | core_geospatial / DIST_RIO_ARROYO_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_cuerpo_agua_m | number | m | false | Distancia euclidiana precalculada a cuerpo agua | core_geospatial / DIST_CUERPO_AGUA_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_canal_m | number | m | false | Distancia euclidiana precalculada a canal | core_geospatial / DIST_CANAL_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_linea_transmision_m | number | m | false | Distancia euclidiana precalculada a linea transmision | core_geospatial / DIST_LINEA_TRANSMISION_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_subestacion_m | number | m | false | Distancia euclidiana precalculada a subestacion | core_geospatial / DIST_SUBESTACION_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_via_ferrea_m | number | m | false | Distancia euclidiana precalculada a via ferrea | core_geospatial / DIST_VIA_FERREA_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_industria_m | number | m | false | Distancia euclidiana precalculada a industria | core_geospatial / DIST_INDUSTRIA_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_infra_vial_m | number | m | false | Distancia euclidiana precalculada a infra vial | core_geospatial / DIST_INFRA_VIAL_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| dist_infra_hidrica_m | number | m | false | Distancia euclidiana precalculada a infra hidrica | core_geospatial / DIST_INFRA_HIDRICA_M | UNKNOWN | 755/755 localidades | EPSG:6372 declarado por libro; geometría/fecha/script original ausentes. No es amenaza ni distancia vial. |
| municipio_objetivo | integer | binary_code | false | Marcador original de pertenencia al subconjunto recibido; siempre 1 | core_geospatial / MUNICIPIO_OBJETIVO | UNKNOWN | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| vph_c_elec | integer | dwellings | true | Viviendas particulares habitadas con electricidad | statewide_census / VPH_C_ELEC | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| vph_s_elec | integer | dwellings | true | Viviendas particulares habitadas sin electricidad | statewide_census / VPH_S_ELEC | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| vph_aguadv | integer | dwellings | true | Viviendas particulares habitadas con agua entubada según variable ITER | statewide_census / VPH_AGUADV | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| vph_drenaj | integer | dwellings | true | Viviendas particulares habitadas con drenaje | statewide_census / VPH_DRENAJ | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| vph_nodren | integer | dwellings | true | Viviendas particulares habitadas sin drenaje | statewide_census / VPH_NODREN | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| vph_autom | integer | dwellings | true | Viviendas particulares habitadas con automóvil | statewide_census / VPH_AUTOM | 2020 | 443/755 localidades | No extrapolar fuera de la unidad de localidad. |
| transprin_2014 | string | category | true | Categoría original: TRANSPRIN_2014 | statewide_census / TRANSPRIN_2014 | 2014 | 610/755 localidades | No extrapolar fuera de la unidad de localidad. |
| frecuencia_2014 | string | category | true | Categoría original: FRECUENCIA_2014 | statewide_census / FRECUENCIA_2014 | 2014 | 610/755 localidades | No extrapolar fuera de la unidad de localidad. |
| tiempo_2014 | string | category | true | Categoría original: TIEMPO_2014 | statewide_census / TIEMPO_2014 | 2014 | 610/755 localidades | No extrapolar fuera de la unidad de localidad. |
| drenajecob_2014 | string | category | true | Categoría original: DRENAJECOB_2014 | statewide_census / DRENAJECOB_2014 | 2014 | 200/755 localidades | No extrapolar fuera de la unidad de localidad. |
| alumbcob_2014 | string | category | true | Categoría original: ALUMBCOB_2014 | statewide_census / ALUMBCOB_2014 | 2014 | 200/755 localidades | No extrapolar fuera de la unidad de localidad. |
| recubcob_2014 | string | category | true | Categoría original: RECUBCOB_2014 | statewide_census / RECUBCOB_2014 | 2014 | 200/755 localidades | No extrapolar fuera de la unidad de localidad. |
| inundacion_2014 | string | category | true | Etiqueta de daño histórico original: Con daño / Sin daño | statewide_census / INUNDACION_2014 | 2014 | 610/755 localidades | Daño histórico reportado; no condición actual ni etiqueta ML validada. |
| sequia_2014 | string | category | true | Etiqueta de daño histórico original: Con daño / Sin daño | statewide_census / SEQUIA_2014 | 2014 | 610/755 localidades | Daño histórico reportado; no condición actual ni etiqueta ML validada. |
| helada_2014 | string | category | true | Etiqueta de daño histórico original: Con daño / Sin daño | statewide_census / HELADA_2014 | 2014 | 610/755 localidades | Daño histórico reportado; no condición actual ni etiqueta ML validada. |
| incendio_2014 | string | category | true | Etiqueta de daño histórico original: Con daño / Sin daño | statewide_census / INCENDIO_2014 | 2014 | 610/755 localidades | Daño histórico reportado; no condición actual ni etiqueta ML validada. |
| temblor_2014 | string | category | true | Etiqueta de daño histórico original: Con daño / Sin daño | statewide_census / TEMBLOR_2014 | 2014 | 610/755 localidades | Daño histórico reportado; no condición actual ni etiqueta ML validada. |
| ciclon_2014 | string | category | true | Etiqueta de daño histórico original: Con daño / Sin daño | statewide_census / CICLON_2014 | 2014 | 610/755 localidades | Daño histórico reportado; no condición actual ni etiqueta ML validada. |
| riesgo_temblor_2014 | integer | binary_code | true | Antecedente de daño reportado en 2014: 1=Con daño, 0=Sin daño; null=no dato | statewide_census / RIESGO_TEMBLOR_2014 | 2014 | 610/755 localidades | Código heredado, no probabilidad ni riesgo actual. 0 no demuestra seguridad. |
| riesgo_ciclon_2014 | integer | binary_code | true | Antecedente de daño reportado en 2014: 1=Con daño, 0=Sin daño; null=no dato | statewide_census / RIESGO_CICLON_2014 | 2014 | 610/755 localidades | Código heredado, no probabilidad ni riesgo actual. 0 no demuestra seguridad. |
| match_localidades_2014 | integer | binary_code | false | Coincidencia de clave en la unión censal original, 1=sí/0=no | statewide_census / MATCH_LOCALIDADES_2014 | 2014 | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| analysis_unit | string | not_applicable | false | Unidad soportada: locality | pipeline_v1 / ANALYSIS_UNIT | UNKNOWN | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| coordinate_crs | string | not_applicable | false | CRS declarado o CRS_UNKNOWN | pipeline_v1 / COORDINATE_CRS | UNKNOWN | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| source_id | string | not_applicable | false | Dataset fuente del maestro | pipeline_v1 / SOURCE_ID | UNKNOWN | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |
| supplement_source_id | string | not_applicable | false | Dataset fuente de las variables complementarias | pipeline_v1 / SUPPLEMENT_SOURCE_ID | UNKNOWN | 755/755 localidades | No extrapolar fuera de la unidad de localidad. |

## Serie climática independiente

| Campo | Tipo | Unidad | Nullable | Significado / fuente | Temporalidad / cobertura / limitación |
|---|---|---|---|---|---|
| station_id | string | identifier | false | Clave original CLAVE | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| station_name | string | not_applicable | false | Nombre original ESTACION | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| municipality | string | not_applicable | false | Municipio indicado en el libro, sin intersección geométrica | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| period | string | YYYY-MM | false | Mes original PERIODO | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| year | integer | year | false | Año original ANIO | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| month | integer | month | false | Mes original MES | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| longitude | number | decimal_degrees | false | LONGITUD original | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| latitude | number | decimal_degrees | false | LATITUD original | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| precipitation_mm | number | mm | false | PRECIPITACION_MM original, sin imputación | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| origin_files | string | not_applicable | false | ARCHIVO_ORIGEN; múltiples separados por punto y coma | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| original_rows | integer | rows | false | Número de filas idénticas consolidadas | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| source_id | string | identifier | false | climate_celaya o climate_irapuato | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| coordinate_crs | string | identifier | false | CRS_UNKNOWN | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |
| usage | string | not_applicable | false | CONTEXT_ONLY | Libro de clima recibido; 2024-01–2026-01; una estación por municipio; institución/CRS no verificados. |

## Capacidades que NO habilita V1

DEM, pendiente, rugosidad, fallas, laderas, ANP, suelo, uso potencial, inundación moderna, uso de suelo actual por punto y subcuenca por intersección permanecen pendientes. Consultar availability.json. No sustituir por cero ni inferir seguridad.

## Extensión de contexto municipal

`data/processed/v1/municipal_context.json` se reconstruye desde los cuatro libros de raw/municipal_context durante build_v1. Contiene `limitation` (string), `sources` (4 fuentes con metadatos), `fields` (57 objetos con code, column, label, source_id) y `values_by_id` (755 claves CVEGEO con valores string, number o null). Los indicadores son constantes por municipio; no modifican los 64 campos del maestro ni habilitan evaluación espacial del predio. El motor debe conservar PARTIAL_DATA y temporalidad UNKNOWN. Los hashes de entradas y extensión están incluidos en manifest.json.

## Ejemplos reales

```json
[
  {
    "id": "110070001",
    "municipality_code": "007",
    "municipality": "Celaya",
    "locality_code": "0001",
    "locality": "Celaya",
    "longitude": -100.81357305555555,
    "latitude": 20.521523888888886,
    "altitude_m": 1759,
    "pobtot": 378143,
    "pob15_64": 260410,
    "pea": 196254,
    "pocupada": 192614,
    "vivtot": 135989,
    "tvivhab": 108600,
    "cob_electrica": 0.994401473296501,
    "cob_drenaje": 0.9931860036832413,
    "autos_por_100_viv": 56.24033149171271,
    "dis_trans_2014": null,
    "frecuencia_est_2014": null,
    "tiempo_est_min_2014": null,
    "drenaje_score_2014": null,
    "alumbrado_score_2014": null,
    "recub_score_2014": null,
    "riesgo_inundacion_2014": null,
    "riesgo_sequia_2014": null,
    "riesgo_helada_2014": null,
    "riesgo_incendio_2014": null,
    "dist_carretera_m": 2797.6,
    "dist_camino_m": 5024.2,
    "dist_rio_arroyo_m": 3233.0,
    "dist_cuerpo_agua_m": 19528.1,
    "dist_canal_m": 1643.9,
    "dist_linea_transmision_m": 3324.7,
    "dist_subestacion_m": 3634.6,
    "dist_via_ferrea_m": 1196.6,
    "dist_industria_m": 5354.6,
    "dist_infra_vial_m": 2797.6,
    "dist_infra_hidrica_m": 1643.9,
    "municipio_objetivo": 1,
    "vph_c_elec": 107992,
    "vph_s_elec": 215,
    "vph_aguadv": 107546,
    "vph_drenaj": 107860,
    "vph_nodren": 221,
    "vph_autom": 61077,
    "transprin_2014": null,
    "frecuencia_2014": null,
    "tiempo_2014": null,
    "drenajecob_2014": null,
    "alumbcob_2014": null,
    "recubcob_2014": null,
    "inundacion_2014": null,
    "sequia_2014": null,
    "helada_2014": null,
    "incendio_2014": null,
    "temblor_2014": null,
    "ciclon_2014": null,
    "riesgo_temblor_2014": null,
    "riesgo_ciclon_2014": null,
    "match_localidades_2014": 0,
    "analysis_unit": "locality",
    "coordinate_crs": "CRS_UNKNOWN",
    "source_id": "core_geospatial",
    "supplement_source_id": "statewide_census"
  },
  {
    "id": "110170001",
    "municipality_code": "017",
    "municipality": "Irapuato",
    "locality_code": "0001",
    "locality": "Irapuato",
    "longitude": -101.34811694444444,
    "latitude": 20.67280138888889,
    "altitude_m": 1715,
    "pobtot": 452090,
    "pob15_64": 307155,
    "pea": 223448,
    "pocupada": 219419,
    "vivtot": 138737,
    "tvivhab": 117925,
    "cob_electrica": 0.997252490990036,
    "cob_drenaje": 0.9959550561797753,
    "autos_por_100_viv": 54.92304430782277,
    "dis_trans_2014": null,
    "frecuencia_est_2014": null,
    "tiempo_est_min_2014": null,
    "drenaje_score_2014": null,
    "alumbrado_score_2014": null,
    "recub_score_2014": null,
    "riesgo_inundacion_2014": null,
    "riesgo_sequia_2014": null,
    "riesgo_helada_2014": null,
    "riesgo_incendio_2014": null,
    "dist_carretera_m": 2556.5,
    "dist_camino_m": 3864.0,
    "dist_rio_arroyo_m": 2407.1,
    "dist_cuerpo_agua_m": 8045.2,
    "dist_canal_m": 1556.3,
    "dist_linea_transmision_m": 3864.2,
    "dist_subestacion_m": 4631.5,
    "dist_via_ferrea_m": 942.4,
    "dist_industria_m": 11550.9,
    "dist_infra_vial_m": 2556.5,
    "dist_infra_hidrica_m": 1556.3,
    "municipio_objetivo": 1,
    "vph_c_elec": 117601,
    "vph_s_elec": 132,
    "vph_aguadv": 117145,
    "vph_drenaj": 117448,
    "vph_nodren": 277,
    "vph_autom": 64768,
    "transprin_2014": null,
    "frecuencia_2014": null,
    "tiempo_2014": null,
    "drenajecob_2014": null,
    "alumbcob_2014": null,
    "recubcob_2014": null,
    "inundacion_2014": null,
    "sequia_2014": null,
    "helada_2014": null,
    "incendio_2014": null,
    "temblor_2014": null,
    "ciclon_2014": null,
    "riesgo_temblor_2014": null,
    "riesgo_ciclon_2014": null,
    "match_localidades_2014": 0,
    "analysis_unit": "locality",
    "coordinate_crs": "CRS_UNKNOWN",
    "source_id": "core_geospatial",
    "supplement_source_id": "statewide_census"
  },
  {
    "id": "110070078",
    "municipality_code": "007",
    "municipality": "Celaya",
    "locality_code": "0078",
    "locality": "Los Aguirre",
    "longitude": -100.88004638888889,
    "latitude": 20.61018638888889,
    "altitude_m": 1761,
    "pobtot": 459,
    "pob15_64": 274,
    "pea": 195,
    "pocupada": 194,
    "vivtot": 116,
    "tvivhab": 105,
    "cob_electrica": 0.9904761904761905,
    "cob_drenaje": 0.9809523809523809,
    "autos_por_100_viv": 41.904761904761905,
    "dis_trans_2014": "Dispone",
    "frecuencia_est_2014": 3,
    "tiempo_est_min_2014": 45,
    "drenaje_score_2014": 0.75,
    "alumbrado_score_2014": 0.75,
    "recub_score_2014": 0.0,
    "riesgo_inundacion_2014": 1,
    "riesgo_sequia_2014": 1,
    "riesgo_helada_2014": 1,
    "riesgo_incendio_2014": 0,
    "dist_carretera_m": 30.1,
    "dist_camino_m": 2131.9,
    "dist_rio_arroyo_m": 2748.3,
    "dist_cuerpo_agua_m": 8018.3,
    "dist_canal_m": 2868.3,
    "dist_linea_transmision_m": 4070.6,
    "dist_subestacion_m": 8642.5,
    "dist_via_ferrea_m": 10204.4,
    "dist_industria_m": 9483.7,
    "dist_infra_vial_m": 30.1,
    "dist_infra_hidrica_m": 2748.3,
    "municipio_objetivo": 1,
    "vph_c_elec": 104,
    "vph_s_elec": 1,
    "vph_aguadv": 104,
    "vph_drenaj": 103,
    "vph_nodren": 2,
    "vph_autom": 44,
    "transprin_2014": "Autobús",
    "frecuencia_2014": "De 1 a 5 salidas",
    "tiempo_2014": "De 30 a 60 minutos",
    "drenajecob_2014": "La mayor parte de la localidad",
    "alumbcob_2014": "La mayor parte de la localidad",
    "recubcob_2014": "No hay recubrimiento en calles",
    "inundacion_2014": "Con daño",
    "sequia_2014": "Con daño",
    "helada_2014": "Con daño",
    "incendio_2014": "Sin daño",
    "temblor_2014": "Sin daño",
    "ciclon_2014": "Sin daño",
    "riesgo_temblor_2014": 0,
    "riesgo_ciclon_2014": 0,
    "match_localidades_2014": 1,
    "analysis_unit": "locality",
    "coordinate_crs": "CRS_UNKNOWN",
    "source_id": "core_geospatial",
    "supplement_source_id": "statewide_census"
  }
]
```

## Reproducción y cambios

```bash
python3 scripts/data/inspect_datasets.py
python3 scripts/data/build_v1.py
python3 -m unittest discover -s tests/data -v
```

Dependencia existente: openpyxl. Versiones exactas en `scripts/data/requirements.txt`. Nunca se sobrescribe raw; una colisión de hash aborta. No se edita incoming. Cada ejecución detecta nuevas entradas; las no reconocidas quedan pendientes de inspección. Los cambios de semántica deben solicitarse en coordination/requests/from_block_1/; no usar Git para coordinación.
