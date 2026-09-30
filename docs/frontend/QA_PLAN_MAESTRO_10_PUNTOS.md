# QA de los diez puntos del Plan Maestro — 29 de septiembre de 2026

## Alcance y criterio

Se contrasta la sección 3 de `../project/ATLAS_PLAN_MAESTRO.md` con el MVP que está publicado para Irapuato y Celaya. «Implementado técnicamente» significa que el flujo o contrato funciona y tiene una prueba; **no** significa que la fuente territorial, regla profesional o aceptación por usuarios estén validadas. No se asigna estado «completo» a datos inexistentes ni se presenta una prueba automatizada como entrevista real.

## Resultado por punto

| Punto | Estado QA | Evidencia comprobada | Falta para cierre pleno |
| --- | --- | --- | --- |
| 1. Integración, comparación, interpretación por obra y ML condicionado | PARCIAL | El flujo web compara A/B con la misma matriz; la API conserva datos entre tipos de obra y ML apagado. | Capas espaciales del núcleo y justificación de criterios especializados. ML sigue siendo opcional. |
| 2. Usuarios/clientes principales | DEFINIDO; VALIDACIÓN PENDIENTE | Los segmentos están en `../project/DECISIONS_FINAL.md` y se explican en la landing. | Sesiones y observaciones de usuarios de esos segmentos. No se han simulado. |
| 3. Identificar condicionantes antes de construir | PARCIAL | La ficha muestra antecedentes, contexto, cobertura y aspectos a revisar, sin dictamen. | DEM/pendiente, fallas, inundación espacial, laderas y uso de suelo con geometría y validación. |
| 4. Evaluación integrada, explicable y comparable | PARCIAL | Evidencia, ficha, comparación y procedencia parcial visibles; sin nombres internos de XLSX al cliente. | Acreditar fuentes originales, licencias, fechas, método de distancias y capas faltantes. |
| 5. Apoyo a decisiones y ficha | IMPLEMENTADO TÉCNICAMENTE | La interfaz y el PDF muestran ficha preliminar y advertencias; no hay ganador ni permiso. | Prueba de comprensión con usuarios y revisión profesional del lenguaje. |
| 6. Vivienda, edificación y vialidad | IMPLEMENTADO TÉCNICAMENTE | Tres recorridos API y tres recorridos web A/B verificados. | Umbrales y criterios normativos por tipo de obra siguen pendientes de acuerdo y revisión técnica. |
| 7. Factores núcleo | PARCIAL | Los seis factores aparecen; faltantes no se convierten en cero o seguridad. Altitud censal y antecedente 2014 mantienen su temporalidad. | Capas y métodos descritos en `../data/PENDING_LAYERS.md`; los indicadores municipales no las sustituyen. |
| 8. Ficha con fuentes, cobertura, faltantes y revisión | IMPLEMENTADO TÉCNICAMENTE; PROCEDENCIA PARCIAL | Ficha A/B, cobertura y fuentes usadas en pantalla y PDF A4; la ficha comprobada ocupa tres páginas. | Enlaces originales y cotejo institucional de los datos recibidos. |
| 9. ML complementario y explicable | CONFORME AL GATE ACTUAL | La API declara ML desactivado y el sistema funciona sin modelo. | Si el equipo decide activarlo: objetivo, etiquetas, baseline, validación espacial y métricas defendibles. No bloquea este MVP. |
| 10. Mapa, tipo de obra, análisis, ficha, fuentes y A/B | IMPLEMENTADO TÉCNICAMENTE; CIERRE DE DEMO PENDIENTE | Flujo web, móvil, error de API, mapa externo caído, tres tipos de obra, teclado y salida PDF probados. | Ensayo cronometrado con el equipo, prueba en sus dispositivos y copia estable de presentación. |

## Ejecución QA de esta revisión

- Integridad de datos publicados: **27/27** pruebas `unittest` con Python del sistema. No se reconstruyó ni alteró `incoming`, `raw` o `processed`.
- Motor y API en proceso: **102/102** pruebas `pytest` con `backend/.venv`. Una advertencia de deprecación de Starlette/httpx, sin fallo.
- API aislada actual y API del preview: **14/14** comprobaciones HTTP cada una, incluidos los tres tipos de obra, A/B, temporalidad, estados faltantes y errores.
- Frontend: **14/14** pruebas unitarias, **16/16** pruebas de navegador sobre el preview con API actualizada; anchos 320, 390, 768, 1024 y 1920 px, sin desbordamiento en las vistas comprobadas.
- `npm audit --audit-level=moderate`: **0 vulnerabilidades reportadas** en esta ejecución.
- La marca original `../../../Mockup/Logo.png` y `Nombre.png` se copió sin alteración a `frontend/public/` y aparece en landing, sistema, información y las tres páginas de la ficha; la comprobación incluye carga real de ambas imágenes.
- La ficha de prueba se imprimió en A4, tres páginas. Se revisó visualmente la primera página. No se certifican todos los tamaños futuros de informe ni todos los navegadores.

## Incidencia de integración encontrada

El Uvicorn compartido en `127.0.0.1:8000` se inició antes de la actualización del motor y falla **2 de 14** comprobaciones HTTP: comparación de la misma clave con coordenadas auxiliares distintas y prioridad de `locality_id`. No se reinició ni detuvo ese proceso. Se inició una instancia aislada del código vigente en `127.0.0.1:8001`, que pasa las 14 comprobaciones, y el preview privado de `:5174` apunta a ella. El propietario del Bloque 3 debe actualizar el servicio compartido cuando corresponda.

Durante esta revisión apareció otra edición simultánea: `frontend/src/pages/LoaderShowcase.jsx` importó `loader-showcase.css` antes de que ese archivo existiera; una compilación falló temporalmente por esa dependencia. Se preservó el trabajo ajeno. El archivo CSS se completó después y **la construcción volvió a pasar**. La prueba de marca verifica también esa vista de demostración en móvil. El preview privado permaneció disponible.

## Dependencias para cerrar los puntos parciales

1. Bloque 1: recuperar y cotejar fuentes originales de los libros recibidos; integrar solo capas geoespaciales con cobertura, CRS, fecha, escala, licencia, geometría y método verificados para Irapuato/Celaya. Véase `SOURCE_REVIEW_2026-09-29.md` y `../data/PENDING_LAYERS.md`.
2. Bloque 2 y especialistas: justificar y probar reglas/umbrales por factor y obra después de recibir capas. No fijar porcentajes ni umbrales por conveniencia visual.
3. Equipo: realizar sesiones reales con usuarios definidos, revisar comprensión de ficha, fuentes y límites, ensayar la demo en menos de siete minutos y conservar una copia estable.

Hasta completar estas dependencias no corresponde declarar «10/10 terminado» ni presentar la evaluación como riesgo actual o dictamen de obra.

## Re-verificación 2026-09-30 (sesión técnica)

Se re-confirmó el estado real por código, datos y pruebas. **Los estados de los
diez puntos NO cambian**: los puntos 1, 3, 4 y 7 siguen PARCIAL; 2 DEFINIDO con
validación pendiente; 5, 6, 8 y 10 implementados técnicamente con validación
externa pendiente; 9 conforme al gate con ML apagado. Lo que cambió es la
evidencia y el endurecimiento de garantías, no el cierre.

Evidencia ejecutada (2026-09-30T06:02Z):

- Motor (Bloque 2): **72/72** `pytest` con `engine/.venv` (incluye 6 pruebas
  nuevas de garantía en `tests/engine/test_missing_layers_guarantee.py`).
- API (Bloque 3): **37/37** `pytest` con `backend/.venv` (incluye 1 prueba nueva
  de garantía en el borde HTTP con el motor real).
- Integridad de datos publicados: las **7 salidas** de `data/processed/v1/`
  coinciden con los `sha256` de `manifest.json` (verificación no destructiva; no
  se reconstruyó ni alteró `incoming`, `raw` ni `processed`).
- Suite de datos (`tests/data`): **no ejecutada aquí** por falta de `openpyxl` en
  este entorno; pertenece al entorno del Bloque 1. Bloqueo de entorno, no de código.

Garantía obligatoria endurecida ("una capa faltante nunca se representa como
riesgo bajo ni como dato disponible"): pruebas automatizadas verifican que
`slope` (BLOCKED), `faults`, `landslide_susceptibility` y `land_use`
(INSUFFICIENT) nunca aparecen como `DATA_AVAILABLE`/`PARTIAL_DATA`; que ningún
factor usa etiquetas de "riesgo bajo/seguro"; que el antecedente de inundación
2014 permanece histórico; y que los indicadores `*_mun_context` son contexto,
nunca la amenaza del predio.

Preparación de validación con personas (Prioridad D): se creó
[`../validation/VALIDATION_PROTOCOLS.md`](../validation/VALIDATION_PROTOCOLS.md)
con protocolo, tareas, criterios y formato de registro para usuarios, revisión
profesional y ensayo de demo. Todo queda **PENDIENTE DE VALIDACIÓN EXTERNA**; no
se inventaron sesiones, opiniones ni tiempos.

Procedencia (Prioridad A): sin cambio. Todas las fuentes siguen
`SOURCE_PROVENANCE_PARTIAL` con institución declarada (no verificada), URL/licencia
`UNKNOWN`/`PENDING`. No se acreditó ninguna fuente nueva ni se atribuyó a
INEGI/CONAGUA/CENAPRED/CONABIO/CFE un valor sin cotejo. Capas espaciales del
núcleo (DEM/pendiente, fallas, inundación moderna, laderas, uso de suelo con
geometría): siguen pendientes.

Coordinación/servidores: no se detuvo ni reinició ningún proceso. La instancia
antigua en `:8000` sigue en pie sin tocarse; el preview aislado en `:8001`/`:5174`
y el Vite en `:5173` (edición simultánea de frontend) se preservaron. No se
modificó `frontend/` ni `data/`. Sin `commit`/`push`.
