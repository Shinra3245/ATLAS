# ATLAS - Bloque 1: Datos y SIG

## Rol del agente

Eres el **propietario exclusivo del pipeline de datos y geoprocesamiento** de ATLAS. Tu trabajo es transformar archivos oficiales y datasets entregados en artefactos reproducibles, documentados y consumibles por el motor analítico. No debes modificar backend, frontend ni lógica del motor analítico.

## Alcance geográfico obligatorio

**Únicamente Irapuato y Celaya.** Cualquier dato estatal/nacional se filtra a estos municipios para el MVP. Guanajuato completo se conserva solo como insumo de expansión futura.

## Directorios bajo tu propiedad

```text
data/**
scripts/data/**
docs/data/**
```

No modifiques:

```text
engine/**
ml/**
backend/**
frontend/**
```

## Entradas prioritarias

1. `irapuato_celaya_dataset_ml_geoespacial (2).xlsx`
2. `subcuencas_Guanajuato_RNA(1).xlsx`
3. `subcuencas_hidrograficas_RNA(2).xlsx`
4. `datos_ferroviarios_para_RNA(2).xlsx`
5. `uso_suelo_vegetacion_serie_I_historico_F14_7_F14_8.xlsx`
6. `uso_suelo_vegetacion_serie_IV_F14_7_F14_8.xlsx`
7. Nuevos datasets depositados en `data/incoming/`.

## Hechos que NO debes reinterpretar

- Dataset maestro: 755 localidades, 434 Irapuato, 321 Celaya.
- CRS de distancias: EPSG:6372.
- No existe variable objetivo ML válida definida.
- Pendiente no tiene cobertura homogénea.
- Subcuencas XLSX: puntos/BBOX de referencia; para cruce preciso se requieren polígonos originales.
- Serie I es histórica.
- Serie IV aún requiere cruce espacial y, para polígonos, geometría original.

## Estructura que debes garantizar

```text
data/
├── incoming/
├── raw/
│   ├── census/
│   ├── transport/
│   ├── hydrology/
│   ├── landuse/
│   ├── vegetation/
│   ├── infrastructure/
│   └── reference_xlsx/
├── pending/
│   ├── dem/
│   ├── geology_faults/
│   ├── landslides/
│   ├── anp/
│   ├── modern_flood_surface/
│   ├── precipitation/
│   ├── soils/
│   └── potential_land_use/
├── intermediate/
├── processed/v1/
├── metadata/
└── contracts/
```

## Artefactos obligatorios de salida

### 1. `data/metadata/source_manifest.csv`
Campos mínimos:

```text
source_id,file_name,institution,source_year,download_date,
coverage,crs,geometry_type,license_or_terms,status,
processing_script,limitations
```

### 2. `data/metadata/field_dictionary.md`
Para cada variable:
- nombre;
- tipo;
- unidad;
- fuente;
- interpretación;
- valores nulos;
- si es amenaza, factor o contexto;
- prohibiciones de interpretación.

### 3. `data/contracts/analysis_unit.schema.json`
Contrato de una unidad de análisis. Debe incluir ID, municipio, coordenadas, tipo de unidad y disponibilidad de capas.

### 4. `data/contracts/layer_manifest.schema.json`
Contrato de capa: código, título, categoría, fuente, fecha, CRS, cobertura, unidad y limitación.

### 5. `data/processed/v1/`
Datos listos para consumir. Nunca publicar un archivo en `processed/v1` sin metadatos.

## Plan continuo de desarrollo

### D1 - Inventario y copia inmutable
- Copia los XLSX suministrados a `raw/reference_xlsx/`.
- Calcula checksum SHA-256.
- Registra cada archivo.
- No edites los originales.

### D2 - Dataset maestro normalizado
- Extrae únicamente Irapuato/Celaya (ya debería estar filtrado; verifica).
- Valida coordenadas y municipio.
- Estandariza nulos.
- Mantén variables originales y crea columnas derivadas solo con nombre explícito.
- Genera CSV/GeoJSON de puntos de análisis.

### D3 - Variables por grupos
Construye un catálogo para:
- socioeconómico;
- servicios;
- movilidad;
- vialidad;
- ferrocarril;
- industria;
- electricidad;
- hidrología;
- uso de suelo/vegetación;
- riesgos históricos;
- elevación.

No conviertas estas categorías en una puntuación única.

### D4 - Hidrología
- Conserva distancias del maestro.
- Subcuencas XLSX = referencia hasta tener geometría poligonal.
- Si llega SHP/GPKG, filtra espacialmente Irapuato/Celaya y documenta método.

### D5 - Ferrocarril
- Filtra nodos e instalaciones a área relevante.
- Para proximidad al municipio usa buffer solo si está documentado.
- No uses nodos nacionales fuera de contexto.

### D6 - Uso de suelo/vegetación
- Serie I: etiqueta obligatoria `historical=true`.
- Serie IV: integrar solo mediante clave/geometry válida. No inferir ubicación de polígonos desde atributos sin geometría.
- Cultivos con coordenadas pueden tratarse como puntos cuando la semántica lo permita.

### D7 - Datos faltantes
Cada nuevo archivo llega a `data/incoming/` y sigue:

```text
incoming -> inspección -> source_manifest -> raw/<grupo>
-> reproyección/limpieza -> intermediate -> processed/v1
```

Prioridad:
1. DEM homogéneo.
2. Fallas/fracturas.
3. Inundación espacial moderna.
4. Deslizamientos.
5. Precipitación.
6. ANP.
7. Suelos/uso potencial.

### D8 - DEM
Cuando llegue:
- verificar cobertura completa de ambos municipios;
- CRS y resolución;
- NoData;
- derivar pendiente;
- derivar rugosidad solo si hay tiempo y definición acordada;
- documentar algoritmo/unidades;
- no mezclar MDS parcial con DEM completo sin justificación.

## Dataset Contract v1 - gate de integración

Publica `DATA_CONTRACT_v1.md` con:
- archivos exactos;
- columnas exactas;
- unidades;
- nulos;
- CRS;
- campos obligatorios;
- categorías permitidas;
- ejemplos de 3 registros.

Después etiqueta el commit como listo para integración.

## STOP / conflictos

Si el Motor Analítico pide cambiar significado de una variable:
- NO lo cambies directamente.
- exige una solicitud en `coordination/requests/from_block_2/REQ-...md`.
- evalúa impacto.
- publica v1.1 si procede.

Si falta un dataset crítico:
- marca la variable `missing`;
- entrega el resto del contrato;
- no bloquees todo el pipeline.

Si no existe geometría original para una capa:
- prohíbe cruces poligonales aproximados;
- documenta `reference_only`.

## Pruebas mínimas

- 755 registros esperados en maestro, salvo que se documente otra unidad.
- municipios solo Irapuato/Celaya.
- lat/lon válidas.
- distancias no negativas.
- CRS declarado.
- ninguna capa `current` basada exclusivamente en Serie I histórica.
- ningún nulo convertido automáticamente a 0.

## Handoff al Bloque 2

Entrega únicamente:
- `processed/v1`;
- schemas;
- manifiesto;
- diccionario;
- reporte de cobertura.

No entregues archivos ambiguos sin versión.

## Definition of Done

Tu bloque está terminado cuando el motor puede cargar `processed/v1` sin conocer detalles de los XLSX originales y puede distinguir claramente valor, fuente, cobertura y limitación.
