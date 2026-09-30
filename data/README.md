# Datos

## Propósito

Organizar datos por etapa sin perder su procedencia: `incoming/` es el buzón original inmutable; tras validación se copia a `raw/` (también inmutable). Las transformaciones se generan en `intermediate/`, los productos en `processed/v1/` y la trazabilidad en `metadata/`.

## Información por registrar

Toda fuente debe documentarse primero en `sources.md`: institución, URL, archivo, fechas, cobertura, CRS, variables, uso, limitaciones y licencia. Cada transformación deberá poder reproducirse mediante un script y dejar evidencia.

## Reglas

- No mover, eliminar ni modificar originales en `incoming/` o `raw/`.
- La coordinación se realiza por archivos de status y solicitudes; no por Git.
- No interpretar ausencia de registro como ausencia de riesgo.
- No declarar aptitud, riesgo o calidad sin criterios documentados.

## Entrega V1

Alcance único: Irapuato y Celaya. `processed/v1/analysis_units.json` y `.csv` contienen 755 localidades y 64 campos documentados. La precipitación se entrega por separado como serie de dos estaciones (50 meses-estación); no como superficie territorial. No se genera GeoJSON porque el datum de las coordenadas del maestro está pendiente.

Consultar `contracts/DATA_CONTRACT_V1.md`, `metadata/availability.json`, `metadata/validation_report.json` y `../docs/data/`. Reproducir mediante los scripts de `../scripts/data/README.md`.

La publicación incorpora 15 libros recibidos y 14 fuentes no duplicadas. `municipal_context.json` conserva 57 campos municipales para las mismas 755 localidades, separados del maestro. Los cuatro libros adicionales tienen copias raw verificadas y hashes de entrada/salida en el manifiesto; sus valores no representan mediciones del predio.

Pendientes: procedencia y licencias de las compilaciones, CRS del maestro, fuentes originales para reproducir distancias y datos derivados, geometrías originales y capas que registra `metadata/availability.json`. Las decisiones de producto siguen `../docs/project/PROJECT_CONTEXT.md` y `../docs/project/DECISIONS_FINAL.md`; no se definen aquí criterios de riesgo, aptitud o ML.
