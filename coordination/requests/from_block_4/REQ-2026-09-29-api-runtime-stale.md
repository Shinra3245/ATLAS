# Solicitud al Bloque 3: actualizar la instancia compartida de API

Fecha: 2026-09-29
Solicitante: Bloque 4 — Frontend / QA
Propietario: Bloque 3 — Backend e integración
Estado: PENDIENTE DE RESPUESTA

## Contrato esperado

La clave `locality_id` publicada tiene prioridad sobre coordenadas auxiliares. Comparar dos entradas que resuelven a la misma localidad devuelve `422 SAME_LOCATION`; comparar dos claves publicadas distintas debe funcionar aunque las coordenadas auxiliares sean iguales. Esto está documentado por el Bloque 3 y pasa en una instancia nueva del código actual.

## Contrato recibido en el proceso compartido

La instancia que escucha en `:8000` se inició a las 19:44 del 29 de septiembre, antes del cambio de código del motor a las 21:09. `python3 scripts/demo/verify_api.py --base-url http://127.0.0.1:8000 --output <archivo temporal>` falló en dos comprobaciones:

- Misma clave con coordenadas auxiliares `(0, 0)`: devuelve `422 OUTSIDE_SUPPORTED_AREA` en vez de `422 SAME_LOCATION`.
- Dos claves distintas con coordenadas auxiliares `(0, 0)`: rechaza una comparación que el contrato permite.

La misma verificación con una instancia aislada de código actual en `127.0.0.1:8001` pasó **14/14**, al igual que el preview `:5174` apuntando a esa instancia. Por ello el problema observado es del proceso compartido desactualizado, no de una discrepancia comprobada en el código fuente actual.

## Impacto y cambio solicitado

La demo o clientes que llamen directamente a `:8000` siguen viendo el comportamiento anterior. Corresponde al responsable del Bloque 3 acordar la ventana de actualización del servicio compartido, reiniciarlo sin interferir con sesiones activas, ejecutar las 14 verificaciones HTTP y registrar el resultado en su status. Bloque 4 no detuvo ni modificó la instancia de `:8000`.
