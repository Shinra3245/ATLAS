# Calidad y limitaciones — Data V1

Informe verificable de pruebas, conservación de originales y reconstrucción determinista: `data/metadata/validation_report.json`, generado por `python3 scripts/data/verify_v1.py`. La fecha del manifiesto es el único elemento variable permitido al reconstruir.

## Comprobaciones ejecutadas

- 755 claves únicas con correspondencia entidad/municipio/localidad; 434 Irapuato y 321 Celaya.
- Coordenadas numéricas dentro del rango global; esto no confirma datum ni pertenencia por límites municipales.
- Distancias no negativas y sin nulos; EPSG:6372 solo es CRS declarado de su cálculo original.
- Filtrado estatal: 755 claves; todos los campos compartidos coinciden dentro de tolerancia numérica 1e-10 absoluta/1e-12 relativa.
- Razones de servicios y automóvil reproducen los numeradores recibidos y TVIVHAB; no se recalculan ni rellenan nulos.
- Códigos históricos 0/1 coinciden con Sin daño/Con daño en todas las filas enlazadas.
- Tabla de terreno enlaza 755 claves: altitud censal y coordenadas coinciden; diferencia de alturas aritmética correcta. Esto no valida DEM ni pendiente.
- Integridad SHA256 de incoming y copias raw verificada antes y después.

## Terreno

Tabla Datos: 755 filas, 9 columnas; ambas municipalidades. Elevación DEM recibida 1692–2202 m; pendiente 0–15.99993592924168 grados, 22 valores distintos. Las notas la llaman pendiente local aproximada. No hay raster, resolución, datum vertical, fuente, fecha, algoritmo ni rugosidad. DEM=PENDING; elevación DEM=PARTIAL solo como referencia; pendiente=PENDING; rugosidad=PENDING. Únicamente altitude_m censal se publica para contexto. El cálculo original no puede reproducirse con estos insumos.

## Clima y precipitación

Cada libro tiene 26 registros/25 meses, 2024-01 a 2026-01, sin nulos en la tabla recibida. Una estación fija por municipio: CLYGJ y IRPGJ. Variable única de clima: PRECIPITACION_MM; no temperatura. Marzo 2025 se repite con igual valor y distinto ARCHIVO_ORIGEN. Se consolida solo la observación idéntica, conservando ambas procedencias y original_rows=2. Resultado: 50 registros; no imputación, interpolación, superficie ni asignación a todas las localidades. Utilidad CONTEXT_ONLY; precipitación temporal=PARTIAL y precipitación espacial=PENDING. El promedio/acumulado original incluye la fila repetida y no se usa. Institución, licencia y CRS desconocidos.

## Geometría y procedencia

GEOMETRY_LIMITATION: subcuencas y uso del suelo sin polígonos. Libro estatal de subcuencas dice punto del centro de BBOX; nacional dice punto interior representativo: no son equivalentes ni garantizan una relación espacial. No realizar asignaciones precisas. Ferrocarril tiene coordenadas y fecha 2025-07-18, pero carece de municipio y fuente identificada: no se filtra mediante una caja aproximada. Series I/IV no demuestran estado actual.

## Contexto municipal

Los cuatro libros adicionales están inventariados y copiados de forma inmutable a raw/municipal_context. Se validan 755 claves por libro, sin duplicados, nombres/códigos/coordenadas coincidentes con el maestro y constancia de cada indicador dentro de su municipio. Se publican 57 campos en municipal_context.json, separado del maestro. NIVEL_FUENTE se conserva como texto de procedencia. Los grados municipales no son mediciones del predio ni sustituyen las capas espaciales pendientes. Institución, fecha, licencia y URL original siguen sin verificar; no se deducen de los nombres de indicadores.

## Hallazgo de archivo estatal

EIC_Municipal_2015 tiene electricidad, automóvil e Internet en cero para los 46 municipios. Es una anomalía de compilación pendiente, no ausencia demostrada de servicios; esa hoja se excluye. Urbano_2020 y Entorno_2015 se mantienen separados para no multiplicar localidades. Temblor: 9 antecedentes positivos/145 faltantes; ciclón: 0 positivos/145 faltantes en MVP, sin interpretación predictiva.

## Nulos del dataset consumible

| Campo | Disponibles | Faltantes |
|---|---:|---:|
| id | 755 | 0 |
| municipality_code | 755 | 0 |
| municipality | 755 | 0 |
| locality_code | 755 | 0 |
| locality | 755 | 0 |
| longitude | 755 | 0 |
| latitude | 755 | 0 |
| altitude_m | 755 | 0 |
| pobtot | 755 | 0 |
| pob15_64 | 443 | 312 |
| pea | 443 | 312 |
| pocupada | 443 | 312 |
| vivtot | 755 | 0 |
| tvivhab | 755 | 0 |
| cob_electrica | 443 | 312 |
| cob_drenaje | 443 | 312 |
| autos_por_100_viv | 443 | 312 |
| dis_trans_2014 | 610 | 145 |
| frecuencia_est_2014 | 331 | 424 |
| tiempo_est_min_2014 | 331 | 424 |
| drenaje_score_2014 | 200 | 555 |
| alumbrado_score_2014 | 200 | 555 |
| recub_score_2014 | 197 | 558 |
| riesgo_inundacion_2014 | 610 | 145 |
| riesgo_sequia_2014 | 610 | 145 |
| riesgo_helada_2014 | 610 | 145 |
| riesgo_incendio_2014 | 610 | 145 |
| dist_carretera_m | 755 | 0 |
| dist_camino_m | 755 | 0 |
| dist_rio_arroyo_m | 755 | 0 |
| dist_cuerpo_agua_m | 755 | 0 |
| dist_canal_m | 755 | 0 |
| dist_linea_transmision_m | 755 | 0 |
| dist_subestacion_m | 755 | 0 |
| dist_via_ferrea_m | 755 | 0 |
| dist_industria_m | 755 | 0 |
| dist_infra_vial_m | 755 | 0 |
| dist_infra_hidrica_m | 755 | 0 |
| municipio_objetivo | 755 | 0 |
| vph_c_elec | 443 | 312 |
| vph_s_elec | 443 | 312 |
| vph_aguadv | 443 | 312 |
| vph_drenaj | 443 | 312 |
| vph_nodren | 443 | 312 |
| vph_autom | 443 | 312 |
| transprin_2014 | 610 | 145 |
| frecuencia_2014 | 610 | 145 |
| tiempo_2014 | 610 | 145 |
| drenajecob_2014 | 200 | 555 |
| alumbcob_2014 | 200 | 555 |
| recubcob_2014 | 200 | 555 |
| inundacion_2014 | 610 | 145 |
| sequia_2014 | 610 | 145 |
| helada_2014 | 610 | 145 |
| incendio_2014 | 610 | 145 |
| temblor_2014 | 610 | 145 |
| ciclon_2014 | 610 | 145 |
| riesgo_temblor_2014 | 610 | 145 |
| riesgo_ciclon_2014 | 610 | 145 |
| match_localidades_2014 | 755 | 0 |
| analysis_unit | 755 | 0 |
| coordinate_crs | 755 | 0 |
| source_id | 755 | 0 |
| supplement_source_id | 755 | 0 |

Los 145 nulos históricos siguen siendo nulos; 0 no equivale a seguridad. No se rellenan los 312 faltantes comunes de ciertas variables censales. Las probabilidades y precisión ML no son parte del contrato.
