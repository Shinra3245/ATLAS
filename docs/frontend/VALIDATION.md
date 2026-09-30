# Validación del preview del Bloque 4

Fecha: 29 de septiembre de 2026. Propósito: registrar las comprobaciones de implementación antes de las pruebas manuales del equipo. No certifica producción, precisión científica ni calidad de los datos.

## Acceso privado

- Landing: `http://192.168.10.10:5174/`, desde la misma LAN.
- Sistema: `http://192.168.10.10:5174/#/sistema`.
- Tailscale autorizado: `http://100.121.183.26:5174/`.
- En el nodo: `http://127.0.0.1:5174/`.

Los tres enlaces respondieron HTTP 200 desde el nodo para interfaz, salud y catálogo. Esto no demuestra alcance desde otra computadora: depende de conectividad LAN o pertenencia a la red Tailscale. No se modificaron firewall ni NetworkManager. El servicio escucha solo en esas tres interfaces; no se publicó en la interfaz Wi-Fi institucional ni en `0.0.0.0`. El puerto 5174 evita interferir con una instancia de desarrollo ajena que ocupa 5173 en loopback.

El preview usa una instancia aislada del backend vigente en loopback:8001. La API compartida en :8000 no se reinició, reemplazó ni modificó; conserva un comportamiento anterior y quedó solicitada su actualización al Bloque 3. Si termina la API aislada o el preview, el enlace deja de responder; los comandos de arranque están en [frontend/README.md](../../frontend/README.md). No se creó servicio de arranque automático.

## Comprobaciones automatizadas

| Comprobación | Resultado |
| --- | --- |
| Construcción `npm run build` | Correcta |
| Unidad `npm test` | 14/14 |
| Navegador `npm run test:e2e` | 16/16 |
| Dependencias `npm audit --audit-level=moderate` | 0 vulnerabilidades reportadas en esta revisión |
| Navegación, análisis y comparación | Sin excepciones de página en el flujo comprobado |
| Consulta real | Irapuato 110170001 y Celaya 110070001 |
| Altitud real | 1715 m y 1759 m; sin convertirla en DEM |
| Pendiente | Estado de validación bloqueada preservado |
| A = B | Impide ejecutar comparación de la misma localidad |
| API no disponible | Error visible; no genera resultados de respaldo |
| Teselas externas bloqueadas | Selección por catálogo y análisis siguen operativos |
| Responsive | 320, 390, 768, 1024 y 1920 px; sin desbordamiento horizontal de página en las vistas comprobadas |
| Evidencia | Apertura, contenido real y cierre con Escape |
| Procedencia visible | Sin nombres de XLSX ni códigos internos en evidencia y ficha; fuente original no verificada se distingue de una atribución declarada |
| Marca proporcionada en el mockup | Logo y nombre originales cargan en landing, sistema, información, ficha y laboratorio visual; favicon actualizado |
| Tipos de obra en navegador | Vivienda, edificación y vialidad: análisis, ficha y comparación A/B |
| API actual del preview | 14/14 comprobaciones HTTP; la instancia compartida antigua en :8000 falla 2 |
| Teclado | Saltar al contenido conserva la ruta y enfoca el área principal |
| Preview | Rechaza archivos privados, métodos ajenos y Origin externo |

Pruebas en Google Chrome del nodo, no en todos los motores de navegador. Las pruebas consumen consultas reales de la API; la respuesta de error y el bloqueo de teselas se simulan exclusivamente dentro del entorno de prueba.

Capturas reproducibles en `frontend/test-results/`: landing y selección de escritorio, análisis, evidencia, comparación, móvil y ficha. PDF de comprobación: `ficha-browser.pdf`. Son salidas de pruebas locales, no nuevos datasets ni documentos oficiales.

La ficha de Irapuato 110170001 se exportó en A4 y se verificó con `pdfinfo` y lectura de su texto: tres páginas, con los seis factores núcleo, contexto seleccionado, cinco fuentes utilizadas y limitaciones. Se revisaron también capturas del PDF; sin hojas reservadas únicamente para el pie en este caso comprobado. No implica tres páginas para todos los resultados futuros.

## Adaptaciones respecto a las imágenes

- Se mantiene la identidad visual azul marino/turquesa, tarjetas claras, mapa, panel de selección/resultados, evidencia y ficha.
- Se sustituyen cifras ilustrativas por valores y estados del contrato.
- Se ampliaron textos de tarjetas, títulos y cuadros en las vistas; se corrigió el desbordamiento a 320 px.
- El menú cambia a diseño compacto a 1250 px para evitar desbordamiento a 1024 px con la marca nueva. La guía móvil mantiene un botón pequeño y solo muestra el texto cuando se solicita, evitando cubrir acciones.
- Solo se seleccionan localidades publicadas; no se promete búsqueda de predios ni polígonos analíticos inexistentes.
- No se presenta una clasificación ganadora ni puntuaciones de riesgo.
- Los indicadores municipales aparecen separados del contexto de localidad.
- La ficha incluye los seis factores núcleo y una selección explícita de cuatro variables de contexto; el resto se consulta en el sistema. Las fuentes usadas y las limitaciones se conservan.
- El mapa de OpenStreetMap es una referencia externa, no evidencia territorial validada. CRS_UNKNOWN continúa visible.
- Impresión mediante navegador, sin modificar contratos o crear endpoints PDF.

## Pruebas manuales pendientes del equipo

1. Abrir el enlace desde la computadora y el móvil que se utilizarán en la demo.
2. Elegir vivienda, edificación y vialidad; consultar localidades urbanas y rurales de ambos municipios.
3. Abrir evidencias y verificar que significado, temporalidad y limitaciones se comprenden.
4. Comparar localidades del mismo municipio y de municipios distintos; comprobar regreso a A y cambio de B.
5. Guardar la ficha A y la ficha B en PDF y revisar legibilidad y paginación en el navegador elegido. Usar A4, escala 100 %, sin encabezados/pies automáticos del navegador; activar fondos para conservar colores. El contenido variable puede ocupar más de tres hojas.
6. Revisar Safari/Firefox si serán parte de la demo; aún no se validaron.
7. Validar visualmente las adaptaciones respecto de los mockups y registrar los ajustes deseados.

Los resultados permanecen solo en memoria de la sesión: recargar exige volver a consultar. No hay cuentas, historial ni ML activo. No exponer el preview directamente a Internet sin una revisión independiente de despliegue y seguridad.

Referencias: [contexto](../project/PROJECT_CONTEXT.md), [decisiones finales](../project/DECISIONS_FINAL.md), [contrato REST](../api/REST_CONTRACT_V1.md). La revisión manual y la aceptación final del Bloque 4 siguen pendientes del equipo.

La investigación de fuentes oficiales candidatas y las lagunas de atribución están en [revisión de procedencia](SOURCE_REVIEW_2026-09-29.md). Se solicitó el cotejo y la posible integración de insumos nuevos al propietario del Bloque 1; no se incorporó ninguna fuente sin verificar al catálogo de datos utilizados.

La [matriz QA de los diez puntos](QA_PLAN_MAESTRO_10_PUNTOS.md) separa implementación técnica de validación territorial y con usuarios.
