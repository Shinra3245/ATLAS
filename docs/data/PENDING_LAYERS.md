# Capas pendientes para cerrar el punto 7

La recepción e integración de los cuatro libros municipales no resuelve estas
dependencias. Un valor municipal de peligro, una altitud censal o una tabla de
pendientes no sustituyen una capa espacial validada.

| Prioridad de recepción | Capacidad | Insumo requerido | Condiciones de publicación |
|---|---|---|---|
| 1 | Pendiente | DEM con cobertura homogénea de Irapuato y Celaya | Fuente, licencia, fecha, resolución, CRS horizontal, datum/unidad vertical, NoData y algoritmo reproducible. Pendiente con unidades explícitas; no confundir grados y porcentaje. |
| 2 | Fallas/fracturas | Geometrías originales con atributos | Fuente, escala, fecha, CRS, cobertura y significado de cada entidad. Registrar intersección/proximidad con método documentado; no fijar distancias de exclusión arbitrarias. |
| 3 | Inundación espacial | Capa de amenaza o susceptibilidad identificada por su productor | Geometría, fecha/periodo, escenario, escala/resolución, cobertura y significado de las categorías. No sustituirla por daño censal 2014 ni por proximidad a río. |
| 4 | Susceptibilidad de laderas | Capa original de susceptibilidad | Fuente, metodología, fecha, escala, cobertura y categorías. No deducir un nivel local a partir de un indicador municipal. |
| 5 | Uso de suelo | Geometrías de cobertura/uso y, para compatibilidad normativa, instrumento municipal aplicable | Distinguir cobertura física de autorización urbanística. Una serie de vegetación no demuestra que la obra esté permitida. Identificar vigencia y resolución espacial. |

## Recepción

1. Conservar el archivo recibido en `data/incoming/`, sin editarlo.
2. Ejecutar inventario y registrar fuente original, enlace, fecha, licencia,
   cobertura, CRS, significado, checksum y limitaciones.
3. Incorporar una política explícita al constructor; los archivos nuevos sin
   política permanecen `PENDING_INSPECTION`.
4. Crear copia inmutable raw, validar calidad y documentar transformación.
5. Publicar datos/metadatos y actualizar `availability.json` mediante el
   constructor, con pruebas y hashes reproducibles.
6. Informar al motor mediante `coordination/requests/from_block_1/`; un cambio
   incompatible requiere nueva versión del contrato.

## Evidencia necesaria para declarar un factor completo

Debe existir un caso con dato utilizable, un caso sin cobertura y una
comprobación contra la fuente. Para un raster: validar también NoData y borde;
para geometrías: límites, intersecciones y precisión del cruce. Las reglas que
interpretan valores deben justificarse por separado.

Mientras falte el insumo, conservar `INSUFFICIENT_DATA` o
`BLOCKED_DATA_VALIDATION`. No completar el punto 7 solo porque la ficha muestre
tarjetas para todos los factores.
