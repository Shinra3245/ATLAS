# ATLAS — Frontend (Bloque 4)

Interfaz implementada tras la autorización del equipo: landing responsive, selección de localidad, evaluación con evidencia, comparación A/B, fuentes y ficha imprimible. Las 13 imágenes nuevas de `../../Mockup/` son referencias visuales; los valores, campos y estados mostrados proceden de la API, no de las imágenes.

## Tecnología

React 19.1.1, Vite 7.3.6, Leaflet 1.9.4, Lucide React 0.468.0 y Manrope 5.2.8. CSS propio, sin servicios de mapas de pago. Node >= 22.12.0. Versiones exactas en `package-lock.json`; instalaciones únicamente locales.

## Ejecución

Desde `frontend/`, para reproducir en otro entorno:

```bash
npm ci
npm run build
npm start
```

Por defecto sirve la construcción en `http://127.0.0.1:5173` y conecta la API existente en `http://127.0.0.1:8000` mediante un proxy `/api`. No inicia ni modifica el backend. Si falta la API, muestra un error explícito.

Para el preview privado del nodo, con esas direcciones todavía asignadas:

```bash
ATLAS_API_TARGET=http://127.0.0.1:8001 ATLAS_PREVIEW_PORT=5174 ATLAS_PREVIEW_HOSTS=127.0.0.1,192.168.10.10,100.121.183.26 npm start
```

Enlaces actuales: `http://192.168.10.10:5174` (LAN), `http://100.121.183.26:5174` (Tailscale autorizado) y `http://127.0.0.1:5174` (nodo). Este preview apunta a una API aislada del código vigente en loopback:8001. El proceso compartido en 8000 conserva una versión anterior y requiere actualización por su responsable. El puerto 5173 está ocupado por otra instancia de desarrollo; no detener procesos ajenos.

Si la API aislada deja de funcionar, su arranque manual desde `backend/` es `.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001`. Antes de reutilizar ese puerto, comprobar su disponibilidad y no detener procesos ajenos. El preview se inicia por separado con el comando anterior.

`npm run dev` ofrece desarrollo local con recarga en el mismo puerto; requiere que no esté ocupado por el preview. Variables disponibles en `.env.example`; el servidor Node no carga automáticamente archivos `.env`, se proporcionan en el entorno del proceso.

No se configuró publicación en Internet, TLS, dominio ni autenticación. Este preview no es un despliegue público de producción. El proxy solo admite las operaciones publicadas del contrato y destinos de API en loopback; no sirve documentos, fuentes del repositorio ni variables privadas.

## Rutas y flujo

| Ruta hash | Vista |
| --- | --- |
| `#/` | Landing |
| `#/sistema` | Selección A → análisis → selección B → comparación |
| `#/metodologia` | Metodología y alcance |
| `#/fuentes` | Catálogo real de fuentes |
| `#/estados` | Seis estados de información y limitaciones |
| `#/ficha/a`, `#/ficha/b` | Ficha de un resultado existente |

La selección admite solo localidades publicadas de Irapuato y Celaya, mediante catálogo o marcador. CVEGEO y coordenadas se conservan al consultar. La comparación bloquea A = B y utiliza el mismo tipo de proyecto para ambas localidades. Las fichas dependen del análisis de la sesión; recargar la página elimina los resultados en memoria y exige volver a consultar. No se implementaron cuentas, historial ni almacenamiento persistente.

## Integración y significado de la información

ATLAS Geo Pulse utiliza el logo original con ondas topográficas. Las cargas de catálogos lo muestran sin etapas tras 300 ms; el mapa base tras 450 ms, solo en su carga inicial o al reactivarlo. Las consultas muestran el icono en el botón y, si superan 1.2 segundos, un modal cancelable con el estado real de cada solicitud. La comparación consulta análisis y contraste en paralelo y marca cada operación al recibir y validar su respuesta. No se simulan porcentajes ni avances internos del backend. El mapa deja de esperar tras 12 segundos sin completar su carga y mantiene disponible el catálogo; moverlo o ampliarlo después de cargar no abre otro loader. Se respeta movimiento reducido. Las fichas y el resumen en memoria se muestran directamente.

Contrato: `../docs/api/REST_CONTRACT_V1.md`. Todas las consultas pasan por `/api`; no hay respuestas ficticias de respaldo. Se valida identidad, esquema y estados antes de mostrar un resultado. Se conservan nulos, temporalidad, procedencia parcial y bloqueos; no se calculan puntuaciones, porcentajes de riesgo, ganadores ni dictámenes.

Los seis factores núcleo se separan del contexto territorial y de los indicadores municipales. Un indicador municipal no se presenta como medición de una localidad o predio. El sistema muestra etiquetas comprensibles de procedencia, pero la fuente institucional original de varias variables sigue sin verificarse; véase [revisión de fuentes](../docs/frontend/SOURCE_REVIEW_2026-09-29.md). El sistema de referencia de coordenadas permanece sin verificar: los marcadores usan coordenadas numéricas recibidas solo como referencia visual, no como una transformación espacial validada.

Mapa base: OpenStreetMap, con atribución visible y consultas directas de teselas desde el navegador. Requiere conexión externa; no se descargan mapas completos. Si falla, catálogo, consultas y comparación siguen funcionando. No se dibujan polígonos, predios ni capas analíticas inexistentes.

La ficha tiene tres secciones documentales, con valores reales y trazabilidad. `Imprimir / guardar PDF` utiliza la impresión del navegador; no existe un endpoint de exportación PDF. La paginación puede ampliarse según contenido, navegador y opciones de impresión. No se recorta texto para imponer un número de hojas.

## Validación

```bash
npm test
npm run test:e2e
npm audit --audit-level=moderate
```

Las pruebas de navegador requieren el preview y la API activos. Utilizan Google Chrome instalado en `/usr/bin/google-chrome`; se puede cambiar con `ATLAS_CHROME_PATH`. `ATLAS_TEST_URL` permite probar otro enlace privado. Capturas y PDF de comprobación quedan en `test-results/`, regenerados por Playwright. Detalle y pendientes: `../docs/frontend/VALIDATION.md`.

## Recursos y propiedad

Manrope se sirve localmente mediante Fontsource. Iconos Lucide y cartografía Leaflet se distribuyen con sus licencias en las dependencias. `public/atlas-logo.png` y `public/atlas-name.png` son copias sin modificación de las dos imágenes proporcionadas por el equipo en `../../Mockup/`. Se muestran mediante el componente de marca compartido en todas las vistas, incluida la ficha; el SVG anterior se conservó sin uso en la interfaz.

Foto de Irapuato: Juan Carlos Fonseca Mata, **CC BY-SA 4.0**, [archivo original en Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Irapuato,_Guanajuato,_Mx.jpg). `public/irapuato.jpg` es la miniatura descargada, sin edición del archivo; encuadre y superposición cromática se aplican por CSS. Crédito y enlace a licencia también aparecen en la landing.

Se conservó el `index.html` de la raíz del proyecto y los archivos de los bloques 1–3. Referencias: `../docs/project/PROJECT_CONTEXT.md`, `../docs/project/DECISIONS_FINAL.md`, `../design/DESIGN_READY.md` y [QA de los diez puntos](../docs/frontend/QA_PLAN_MAESTRO_10_PUNTOS.md).
