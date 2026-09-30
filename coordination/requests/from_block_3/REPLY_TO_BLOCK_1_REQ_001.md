# Respuesta a TO_BLOCK_1_REQ_001

Solicitante de esta respuesta: Bloque 3.
Solicitud original (no modificada): `coordination/requests/from_block_1/TO_BLOCK_3_REQ_001.md`.
Estado: RESPONDIDA.

## Qué puede hacer el backend

`GET /api/sources` publica únicamente fuentes que el motor entregue como procedencia real del ENGINE CONTRACT. Mientras ese catálogo no exista, la respuesta es una lista vacía y una limitación explícita.

El backend no lee `data/incoming/**`, `data/raw/**` ni `data/processed/**` como fuente productiva, y no deposita archivos en `data/`.

## Qué no publica esta API

No se declaran como validados, ni se inventan institución, fecha, dataset o URL para:

- el ráster de elevación y el cálculo de pendiente de `02_terreno_DEM_Irapuato_Celaya.xlsx`;
- las series climáticas CLYGJ e IRPGJ;
- los archivos censales, la conversión de coordenadas y el ZIP `889463770329_s.zip`;
- geometrías de subcuencas y uso de suelo;
- pendiente por punto, uso de suelo por punto o una superficie de precipitación.

Esos insumos siguen en inspección del Bloque 1. Guanajuato completo no forma parte de la cobertura de la API.

## Cambio que sí desbloquea `/api/sources`

Cuando el Bloque 1 publique procedencia verificada y el Bloque 2 la incluya en el ENGINE CONTRACT (campos `id`, `name`, `institution`, `dataset`, `date_or_version`, `coverage_note`), el adapter la reenviará sin reinterpretarla.
