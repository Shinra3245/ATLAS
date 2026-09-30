# Nota Bloque 2 → Bloque 3 (Backend): señales para los pendientes funcionales

- Bloque emisor: 2 (Motor analítico / ML)
- Bloque destino: 3 (Backend / API)
- Contexto: revisión de integración con datos reales. Los 4 pendientes de la API
  son del dominio de Bloque 3; esta nota aporta las SEÑALES del motor para
  resolverlos sin ambigüedad. Bloque 2 no modifica `backend/`.

## Correcciones ya aplicadas en el motor (Bloque 2)

- Asociación geográfica con límite efectivo (0.05°): coordenadas distantes ⇒
  `area_status = outside_supported_area` (no heredan datos de una localidad).
- `analysis_id` incluye la localidad resuelta ⇒ sin colisión de identificadores.
- Datos censales 2020 marcados `temporal_context = reference_period` (no `current`).
- `compare_locations` expone `same_locality: bool` y una nota explícita.

## Guía para los 4 pendientes del Backend

1. **Buscar "Irapuato" devuelve 0 resultados.**
   `list_locations()` entrega por localidad los campos `locality` y
   `municipality`. El filtro de búsqueda debe consultar `locality` (y/o
   `municipality`), no solo `id`/`locality_code`. Ejemplo: buscar "Irapuato"
   debe coincidir por `municipality == "Irapuato"` y por `locality` que contenga
   el término.

2. **`locality_id` inexistente devuelve HTTP 200 "fuera de alcance".**
   El motor distingue el caso: cuando se resuelve por clave y NO existe, la
   `ResolvedLocation` trae `area_status = outside_supported_area` **y** una nota
   `"locality_id no reconocido en el DATA CONTRACT: <id>"`. Recomendación:
   cuando la petición trae un `locality_id` explícito y esa nota está presente,
   el Backend debe responder `404 Not Found` (clave inexistente), reservando
   "fuera de alcance" para coordenadas válidas fuera de Irapuato/Celaya.

3. **Comparar la misma localidad consigo misma.**
   Usar el nuevo campo `same_locality` de la salida de comparación: si es `true`,
   el Backend puede rechazar con `400/422` (o advertir), aunque las coordenadas
   de entrada difieran. La señal es programática; no hay que parsear notas.

4. **Status/contrato REST con afirmaciones desactualizadas.**
   El Engine Contract (`engine/contracts/ENGINE_CONTRACT_V1.md`) y los datos
   reales YA están disponibles y conectados (755 localidades, 53 atributos, 10
   fuentes; catálogos `list_sources/list_layers/list_locations/ml_status`). El
   contrato REST y el status de Bloque 3 deberían actualizar cualquier texto que
   afirme la ausencia del Engine Contract o de datos reales.

Sin cambios de firma en el motor. Si Backend requiere una señal adicional
programática (p. ej. distinguir "clave inexistente" de "fuera de área" con un
campo dedicado), se puede coordinar en ENGINE_CONTRACT V2 sin romper V1.

## Estado: IMPLEMENTADO (verificación integral del proyecto)

A petición del responsable del proyecto ("implementar lo que se pueda hasta el
bloque tres"), los 4 puntos se aplicaron en el backend y se cubrieron con
pruebas de regresión (suite API: 32 pruebas, todas verdes):

1. `catalog_service.locations`: la búsqueda consulta `locality` y `municipality`.
2. `analysis_service`: `locality_id` inexistente ⇒ 404 `NOT_FOUND` (analyze y compare).
3. `analysis_service.compare`: si `same_locality` es `true` ⇒ 422 `SAME_LOCATION`.
4. `docs/api/REST_CONTRACT_V1.md` y `coordination/status/BLOQUE_3.md`: textos
   actualizados (contrato del motor y datos reales publicados y conectados).

Si el responsable de Bloque 3 prefiere una implementación distinta, estos
cambios son puntuales y reversibles.
