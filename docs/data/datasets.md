# Inventario de datasets — Bloque 1

Inventario recursivo de todos los archivos de `data/incoming/`. Los originales permanecen inmutables.

## AVAILABLE_DATASETS

Maestro canónico de 755 localidades (434 Irapuato, 321 Celaya): identificadores, coordenadas numéricas, altitud censal, contexto y distancias recibidas. Disponible para análisis por localidad; la procedencia de las compilaciones es parcial y las coordenadas tienen CRS_UNKNOWN.

## PARTIAL_DATASETS

Complemento estatal filtrado por claves; precipitación de estación CONTEXT_ONLY; terreno EXPERIMENTAL_REFERENCE_ONLY; subcuencas, ferrocarril y uso/vegetación REFERENCE_ONLY; cuatro libros de contexto municipal con 57 campos, conservados separados del maestro. La completitud de atributos no valida automáticamente su procedencia científica.

## Duplicados

Los maestros (1) y (2) tienen el mismo SHA256, tamaño, hojas, columnas, tipos, valores y metadatos internos. Se elige (2) como CANONICAL_SOURCE por continuidad con Plan Maestro, después de comparar contenido; (1) es EXACT_DUPLICATE y se conserva íntegro. Comparación: `data/metadata/duplicate_comparison.json`.

## PENDING_DATASETS

- `dem`: PENDING. No raster; 755-point table has no source, resolution, date or algorithm.
- `dem_elevation`: PARTIAL. Values present for 755 points but unvalidated; not published as usable DEM elevation.
- `slope`: PENDING. Derived values present; source/resolution/algorithm missing; do not use operationally.
- `roughness`: PENDING. No roughness column or raster.
- `geology_faults`: PENDING. No fault/fracture geometry received.
- `landslides`: PENDING. No susceptibility geometry received.
- `anp`: PENDING. No protected-area geometry received.
- `modern_flood_surface`: PENDING. Historical 2014 damage is not a modern flood surface.
- `precipitation`: PARTIAL. CONTEXT_ONLY: 2 stations/25 months; institution/CRS unverified.
- `precipitation_spatial`: PENDING. No validated homogeneous spatial precipitation layer.
- `temperature`: PENDING. No temperature column in received climate workbooks.
- `soils`: PENDING. No complete soil dataset received.
- `potential_land_use`: PENDING. No potential-land-use dataset received.
- `landuse_current`: PENDING. Series I/IV attributes do not establish current point coverage without geometries.
- `subbasin_assignment`: PENDING. GEOMETRY_LIMITATION: representative point/BBOX is not a polygon.

## climate_celaya

- Archivo original: `data/incoming/climate/Clima_Celaya_2024_2026.xlsx`
- Formato: .xlsx; tamaño: 5685 bytes; SHA256: `96415f3ec2e668f1f3a820cfba67136660ba4c8979481b91e044751f8287b258`.
- source: CSV aportados por usuario; institución/URL UNKNOWN
- municipality: Celaya
- coverage: Una estación puntual por municipio; 25 meses únicos
- date: UNKNOWN
- temporal_scope: 2024-01 a 2026-01, mensual
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: CONTEXT_ONLY
- limitations: Marzo 2025 repetido con distinto archivo de origen; no superficie homogénea, temperatura ausente, institución y datum sin verificar.
- raw_file: data/raw/celaya/Clima_Celaya_2024_2026.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Precipitacion_mensual | 26 | 9 | 0 |
| Resumen | 7 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## climate_irapuato

- Archivo original: `data/incoming/climate/Clima_Irapuato_2024_2026.xlsx`
- Formato: .xlsx; tamaño: 5692 bytes; SHA256: `307d405787a9d7b073ecdb3fe99137b22d3e51a2e2654d310e02d3665770c167`.
- source: CSV aportados por usuario; institución/URL UNKNOWN
- municipality: Irapuato
- coverage: Una estación puntual por municipio; 25 meses únicos
- date: UNKNOWN
- temporal_scope: 2024-01 a 2026-01, mensual
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: CONTEXT_ONLY
- limitations: Marzo 2025 repetido con distinto archivo de origen; no superficie homogénea, temperatura ausente, institución y datum sin verificar.
- raw_file: data/raw/irapuato/Clima_Irapuato_2024_2026.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Precipitacion_mensual | 26 | 9 | 0 |
| Resumen | 7 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## core_exact_duplicate

- Archivo original: `data/incoming/duplicates_review/irapuato_celaya_dataset_ml_geoespacial (1).xlsx`
- Formato: .xlsx; tamaño: 167993 bytes; SHA256: `463106c6232317da7c7934f9c28942d1d39af4dd20615303d1e13c5cce942567`.
- source: INEGI declarado por libro; compilación entregada por equipo
- municipality: Irapuato;Celaya
- coverage: 755 localidades
- date: UNKNOWN
- temporal_scope: 2020/2014; fecha vectorial UNKNOWN
- crs: Coordenadas CRS_UNKNOWN; distancias EPSG:6372 declarado
- status: EXACT_DUPLICATE
- usage: RETAIN_ONLY
- limitations: No geometrías originales ni script original de distancias; datum de coordenadas no identificado; sin variable objetivo ML.
- raw_file: NO COPIADO
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Dataset_ML | 755 | 39 | 0 |
| Resumen | 7 | 2 | 0 |
| Diccionario | 39 | 4 | 0 |
| Notas | 8 | 2 | 0 |
| Fuentes | 6 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## core_geospatial

- Archivo original: `data/incoming/duplicates_review/irapuato_celaya_dataset_ml_geoespacial (2).xlsx`
- Formato: .xlsx; tamaño: 167993 bytes; SHA256: `463106c6232317da7c7934f9c28942d1d39af4dd20615303d1e13c5cce942567`.
- source: INEGI declarado por libro; compilación entregada por equipo
- municipality: Irapuato;Celaya
- coverage: 755 localidades
- date: UNKNOWN
- temporal_scope: 2020/2014; fecha vectorial UNKNOWN
- crs: Coordenadas CRS_UNKNOWN; distancias EPSG:6372 declarado
- status: CANONICAL_SOURCE
- usage: LOCALITY_ANALYSIS
- limitations: No geometrías originales ni script original de distancias; datum de coordenadas no identificado; sin variable objetivo ML.
- raw_file: data/raw/shared/irapuato_celaya_dataset_ml_geoespacial (2).xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Dataset_ML | 755 | 39 | 0 |
| Resumen | 7 | 2 | 0 |
| Diccionario | 39 | 4 | 0 |
| Notas | 8 | 2 | 0 |
| Fuentes | 6 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## subbasins_state

- Archivo original: `data/incoming/hydrography/subcuencas_Guanajuato_RNA(1).xlsx`
- Formato: .xlsx; tamaño: 10481 bytes; SHA256: `e708a4f4c1ac9a1b263417fa53aa9dd12415e367c5d908a7a9b8a8d0018751ad`.
- source: INEGI/CONABIO declarado en libro nacional; redsub84gw.zip
- municipality: UNKNOWN
- coverage: 23 subcuencas reportadas para Guanajuato
- date: UNKNOWN
- temporal_scope: UNKNOWN
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: REFERENCE_ONLY
- limitations: GEOMETRY_LIMITATION: faltan polígonos; puntos representativos/BBOX no permiten asignación municipal precisa.
- raw_file: data/raw/shared/subcuencas_Guanajuato_RNA(1).xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Subcuencas_Guanajuato | 23 | 28 | 0 |
| Resumen | 7 | 2 | 0 |
| Diccionario | 12 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## subbasins_national

- Archivo original: `data/incoming/hydrography/subcuencas_hidrograficas_RNA(2).xlsx`
- Formato: .xlsx; tamaño: 189228 bytes; SHA256: `d8e30644d46749bc60bcd854601b7d55425f3b7209437c0fb2dce5a9fac1b05b`.
- source: INEGI/CONABIO declarado en libro nacional; redsub84gw.zip
- municipality: UNKNOWN
- coverage: México
- date: UNKNOWN
- temporal_scope: UNKNOWN
- crs: EPSG:4326 declarado
- status: PARTIAL
- usage: REFERENCE_ONLY
- limitations: GEOMETRY_LIMITATION: faltan polígonos; puntos representativos/BBOX no permiten asignación municipal precisa.
- raw_file: data/raw/shared/subcuencas_hidrograficas_RNA(2).xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Subcuencas | 976 | 28 | 0 |
| Diccionario | 17 | 2 | 0 |
| Resumen | 9 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## landuse_series_iv

- Archivo original: `data/incoming/landuse_vegetation/uso_suelo_vegetacion_serie_IV_F14_7_F14_8.xlsx`
- Formato: .xlsx; tamaño: 522556 bytes; SHA256: `c3d6c9f7dcaec1f37934834c9d65a627f50c269a150036749d4944c2d7b0dd39`.
- source: INEGI declarado en README interno
- municipality: UNKNOWN
- coverage: Cartas F14-7/F14-8
- date: UNKNOWN
- temporal_scope: Serie IV, año UNKNOWN; no condición actual verificada
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: REFERENCE_ONLY
- limitations: GEOMETRY_LIMITATION: faltan geometrías de polígonos. DMS en puntos Serie IV con datum no declarado. No asignar uso de suelo a localidades.
- raw_file: data/raw/shared/uso_suelo_vegetacion_serie_IV_F14_7_F14_8.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| README | 3 | 4 | 0 |
| F14_7_Vegetacion | 2096 | 10 | 0 |
| F14_7_Cobertura | 2042 | 8 | 0 |
| F14_7_Altura | 2040 | 8 | 0 |
| F14_7_Agricultura | 1243 | 10 | 0 |
| F14_7_Nom_Agricola | 1042 | 6 | 0 |
| F14_7_Cultivos | 46 | 15 | 0 |
| F14_7_Especies | 44 | 17 | 0 |
| F14_8_Vegetacion | 1176 | 10 | 0 |
| F14_8_Cobertura | 1237 | 8 | 0 |
| F14_8_Altura | 1161 | 8 | 0 |
| F14_8_Agricultura | 795 | 10 | 0 |
| F14_8_Nom_Agricola | 559 | 6 | 0 |
| F14_8_Cultivos | 114 | 15 | 0 |
| F14_8_Especies | 4 | 17 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## landuse_series_i

- Archivo original: `data/incoming/landuse_vegetation/uso_suelo_vegetacion_serie_I_historico_F14_7_F14_8.xlsx`
- Formato: .xlsx; tamaño: 341333 bytes; SHA256: `7b7d5d75a0e171dec34a88fb207e36f6ee0d4bf26a7f13f5d655ebfa00042b4c`.
- source: INEGI declarado en README interno
- municipality: UNKNOWN
- coverage: Cartas F14-7/F14-8
- date: UNKNOWN
- temporal_scope: Serie I histórica, año UNKNOWN
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: REFERENCE_ONLY
- limitations: GEOMETRY_LIMITATION: faltan geometrías de polígonos. DMS en puntos Serie IV con datum no declarado. No asignar uso de suelo a localidades.
- raw_file: data/raw/shared/uso_suelo_vegetacion_serie_I_historico_F14_7_F14_8.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| README | 3 | 4 | 0 |
| F14_7 | 2115 | 14 | 0 |
| F14_8 | 2824 | 14 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## riesgos_naturales_localidades

- Archivo original: `data/incoming/new_downloads/01_Riesgos_Naturales_Localidades_Celaya_Irapuato.xlsx`
- Formato: .xlsx; tamaño: 82093 bytes; SHA256: `583fc3b7d56b4808e64705b1db754e825215410f873a6a0f571642c82723be98`.
- source: UNKNOWN: compilación municipal entregada por equipo
- municipality: Irapuato;Celaya
- coverage: 755 localidades; indicadores constantes por municipio
- date: UNKNOWN
- temporal_scope: UNKNOWN; años incluidos en nombres de indicadores no autentican la fuente
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: MUNICIPAL_CONTEXT
- limitations: Indicadores municipales repetidos por localidad; no son mediciones del predio, amenaza local ni condición actual validada. Fuente original, fecha y licencia pendientes.
- raw_file: data/raw/municipal_context/01_Riesgos_Naturales_Localidades_Celaya_Irapuato.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Localidades | 755 | 20 | 0 |
| Notas | 7 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## vulnerabilidad_resiliencia_localidades

- Archivo original: `data/incoming/new_downloads/02_Vulnerabilidad_Resiliencia_Localidades_Celaya_Irapuato.xlsx`
- Formato: .xlsx; tamaño: 101199 bytes; SHA256: `dd303de71270efe0d4f3c469beb71f8def3f54a20906b4a41a6d130bd8337681`.
- source: UNKNOWN: compilación municipal entregada por equipo
- municipality: Irapuato;Celaya
- coverage: 755 localidades; indicadores constantes por municipio
- date: UNKNOWN
- temporal_scope: UNKNOWN; años incluidos en nombres de indicadores no autentican la fuente
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: MUNICIPAL_CONTEXT
- limitations: Indicadores municipales repetidos por localidad; no son mediciones del predio, amenaza local ni condición actual validada. Fuente original, fecha y licencia pendientes.
- raw_file: data/raw/municipal_context/02_Vulnerabilidad_Resiliencia_Localidades_Celaya_Irapuato.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Localidades | 755 | 27 | 0 |
| Notas | 7 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## riesgos_ambientales_localidades

- Archivo original: `data/incoming/new_downloads/03_Riesgos_Ambientales_Localidades_Celaya_Irapuato.xlsx`
- Formato: .xlsx; tamaño: 65498 bytes; SHA256: `1d1f582fd46278d6dc441841f26f092c4dfc22aedf7a51eee5a679e226b9f9a3`.
- source: UNKNOWN: compilación municipal entregada por equipo
- municipality: Irapuato;Celaya
- coverage: 755 localidades; indicadores constantes por municipio
- date: UNKNOWN
- temporal_scope: UNKNOWN; años incluidos en nombres de indicadores no autentican la fuente
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: MUNICIPAL_CONTEXT
- limitations: Indicadores municipales repetidos por localidad; no son mediciones del predio, amenaza local ni condición actual validada. Fuente original, fecha y licencia pendientes.
- raw_file: data/raw/municipal_context/03_Riesgos_Ambientales_Localidades_Celaya_Irapuato.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Localidades | 755 | 14 | 0 |
| Notas | 7 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## exposicion_riesgos_localidades

- Archivo original: `data/incoming/new_downloads/04_Exposicion_Riesgos_Localidades_Celaya_Irapuato.xlsx`
- Formato: .xlsx; tamaño: 91434 bytes; SHA256: `544de12a1ce5916306bf08755110c9c6d6f1097b37d46c02b5a1b3a605943e1e`.
- source: UNKNOWN: compilación municipal entregada por equipo
- municipality: Irapuato;Celaya
- coverage: 755 localidades; indicadores constantes por municipio
- date: UNKNOWN
- temporal_scope: UNKNOWN; años incluidos en nombres de indicadores no autentican la fuente
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: MUNICIPAL_CONTEXT
- limitations: Indicadores municipales repetidos por localidad; no son mediciones del predio, amenaza local ni condición actual validada. Fuente original, fecha y licencia pendientes.
- raw_file: data/raw/municipal_context/04_Exposicion_Riesgos_Localidades_Celaya_Irapuato.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Localidades | 755 | 24 | 0 |
| Notas | 7 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## statewide_census

- Archivo original: `data/incoming/statewide_future/guanajuato_dataset_ml_limpio.xlsx`
- Formato: .xlsx; tamaño: 10390907 bytes; SHA256: `b6e20d0257b6b4efb73d272ce81ddfa8e7b4ff9fc7f51afae334f52a683c28df`.
- source: INEGI declarado; fuentes censales listadas en libro
- municipality: 46 municipios; MVP filtra 007 y 017
- coverage: Guanajuato; extracción MVP validada por CVEGEO
- date: UNKNOWN
- temporal_scope: 2014/2015/2020
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: FILTERED_LOCALITY_ENRICHMENT
- limitations: EIC2015 tiene tres indicadores siempre cero: no utilizados. Manzanas sin geometría no se unen a localidades. CRS censal no identificado.
- raw_file: data/raw/shared/guanajuato_dataset_ml_limpio.xlsx
- Metadatos internos exactos: `{"creator": "openpyxl", "created": "2026-09-29T19:11:21Z", "modified": "2026-09-29T19:11:27Z"}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Localidades_ML | 8809 | 48 | 0 |
| Urbano_2020 | 66178 | 19 | 0 |
| Entorno_2015 | 54934 | 18 | 0 |
| EIC_Municipal_2015 | 46 | 7 | 0 |
| Diccionario | 92 | 6 | 0 |
| Notas_metodologicas | 7 | 2 | 0 |
| Fuentes | 5 | 4 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## terrain_candidate

- Archivo original: `data/incoming/terrain/02_terreno_DEM_Irapuato_Celaya.xlsx`
- Formato: .xlsx; tamaño: 54667 bytes; SHA256: `3195f4644fa2e30921ec3dd6d9d35d494fb24d596db46dac57acad14f8a259b0`.
- source: UNKNOWN: tabla derivada entregada por equipo
- municipality: Irapuato;Celaya
- coverage: 755 puntos; no ráster
- date: UNKNOWN
- temporal_scope: Fecha de valores DEM/pendiente UNKNOWN; altitud censal coincide con maestro
- crs: CRS_UNKNOWN
- status: PARTIAL
- usage: EXPERIMENTAL_REFERENCE_ONLY
- limitations: No identifica fuente DEM, resolución, datum vertical, fecha ni algoritmo. Pendiente no validada; rugosidad ausente. Excluido de análisis V1.
- raw_file: data/raw/shared/02_terreno_DEM_Irapuato_Celaya.xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Datos | 755 | 9 | 0 |
| Notas | 4 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## rail_national

- Archivo original: `data/incoming/transport/datos_ferroviarios_para_RNA(2).xlsx`
- Formato: .xlsx; tamaño: 109495 bytes; SHA256: `7b6bfc57253f60d93534e5c15c3cb9df29d19330bc5d83c26d6bdc2fbdaf3723`.
- source: Institución no declarada en libro; UNKNOWN
- municipality: UNKNOWN
- coverage: México
- date: 2025-07-18 (FECHA_ACT)
- temporal_scope: 2025-07-18
- crs: EPSG:6372 original; EPSG:4326 derivado (declarados)
- status: PARTIAL
- usage: REFERENCE_ONLY
- limitations: No municipio ni líneas completas; sin límites municipales no se publica filtro espacial aproximado. Fuente/licencia sin identificar.
- raw_file: data/raw/shared/datos_ferroviarios_para_RNA(2).xlsx
- Metadatos internos exactos: `{}`. No equivalen a fecha de observación o descarga.

| Hoja | Registros sin encabezado | Columnas | Filas exactamente repetidas |
|---|---:|---:|---:|
| Nodos | 988 | 10 | 0 |
| Origen_Destino | 314 | 8 | 0 |
| Diccionario | 14 | 5 | 0 |
| Resumen | 6 | 2 | 0 |

Detalle de todas las columnas, tipos, mínimos/máximos, valores nulos y muestras: `data/metadata/inventory.json`.

## Recepción continua

Pendientes de inspección específica: ninguno. Cada ejecución vuelve a inspeccionar incoming recursivamente; un archivo sin política queda PENDING_INSPECTION y no pasa automáticamente a raw/processed. No usar Git para coordinar.
