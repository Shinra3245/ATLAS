# Protocolos de validación con personas — ATLAS

Fecha de preparación: 2026-09-30. Autor: sesión técnica (andamiaje).
Estado global: **PENDIENTE DE VALIDACIÓN EXTERNA**.

Este documento prepara **protocolo, tareas y formato de registro** para tres
validaciones que solo el equipo puede ejecutar con participantes reales:

1. Usuarios de los segmentos definidos (DF-02).
2. Revisión profesional de la ficha (especialista en riesgos/urbanismo/SIG).
3. Ensayo cronometrado de la demo.

No contiene entrevistas, opiniones, aprobaciones ni tiempos inventados. Todo
campo de resultado queda vacío hasta que exista evidencia real. Una prueba
automatizada NO cuenta como sesión con usuario.

Enlaces: [DECISIONS_FINAL](../project/DECISIONS_FINAL.md) ·
[QA de los 10 puntos](../frontend/QA_PLAN_MAESTRO_10_PUNTOS.md) ·
[VALIDATION del preview](../frontend/VALIDATION.md) ·
[demo_script](../deliverable/demo_script.md).

---

## 1. Validación con usuarios

### 1.1 Segmentos (DF-02)

| Segmento | Perfil objetivo | Nº mínimo sugerido | Participantes reales |
|---|---|---|---|
| Despachos de arquitectura/ingeniería | Responsable técnico que evalúa sitios | 2 | PENDIENTE |
| Desarrolladores inmobiliarios | Analista de suelo/prospección | 2 | PENDIENTE |
| Gobierno municipal / planeación | Personal de planeación urbana | 1–2 | PENDIENTE |
| Profesionales/organizaciones urbanas | Consultor/ONG en proyectos urbanos | 1–2 | PENDIENTE |
| (Secundario) Constructora pequeña/mediana | Responsable de obra | opcional | PENDIENTE |

Reclutamiento: PENDIENTE (contactos, consentimiento informado, fecha).

### 1.2 Preparación

- Enlace del preview y dispositivo definidos (ver [VALIDATION](../frontend/VALIDATION.md)).
- Consentimiento verbal/escrito para observar y anotar (sin datos personales sensibles).
- Moderador que NO guíe las respuestas; observador que registre.
- No anticipar conclusiones ("esto es seguro/riesgoso"): el sistema es de apoyo.

### 1.3 Tareas (think-aloud, sin ayuda salvo bloqueo)

| # | Tarea | Éxito observable | Criterio |
|---|---|---|---|
| T1 | Seleccionar una localidad de Irapuato en el mapa/catálogo | Llega a la ficha de esa localidad | Sin ayuda |
| T2 | Elegir tipo de obra (vivienda) y analizar | Ve la ficha con factores y estados | Sin ayuda |
| T3 | Explicar con sus palabras un factor `INSUFFICIENT_DATA` | Dice que falta dato, NO que "no hay riesgo" | Comprensión correcta |
| T4 | Explicar el antecedente de inundación 2014 | Lo entiende como histórico, no actual | Comprensión correcta |
| T5 | Identificar de dónde provienen los datos | Encuentra "Fuentes utilizadas" y la advertencia de procedencia parcial | Sin confundir con dictamen |
| T6 | Comparar A vs B (misma obra) | Ve diferencias por factor, sin "ganador" | Entiende que no hay veredicto |
| T7 | Exportar/leer la ficha (PDF/impresión) | Obtiene la ficha legible | Sin bloqueo |

### 1.4 Métricas de registro (por participante)

- Tareas completadas sin ayuda: __/7 — PENDIENTE
- Malinterpretaciones críticas (faltante = "seguro"; histórico = "actual"; comparación = "ganador"): PENDIENTE
- Comprensión de procedencia parcial (sí/parcial/no): PENDIENTE
- Comentarios textuales: PENDIENTE
- Severidad de incidencias (bloqueante/mayor/menor): PENDIENTE

### 1.5 Criterios de aceptación (propuestos, a ratificar por el equipo)

- 0 malinterpretaciones críticas no corregidas por la interfaz.
- ≥ 5 de 7 tareas completadas sin ayuda por la mayoría de participantes.
- Los participantes distinguen "apoyo a decisión" de "dictamen".

> Estos umbrales son una PROPUESTA de trabajo; el equipo debe aprobarlos
> (DP-04). No se han medido.

---

## 2. Revisión profesional de la ficha

Especialista sugerido: riesgos/geotecnia/planeación urbana con experiencia SIG.
Participante real: **PENDIENTE**.

Lista de comprobación (respuesta: Correcto / Ajustar / Incorrecto + nota):

| # | Punto a revisar | Resultado |
|---|---|---|
| P1 | El lenguaje no promete seguridad ni permiso de obra | PENDIENTE |
| P2 | Los estados de dato (disponible/parcial/insuficiente/bloqueado) se usan bien | PENDIENTE |
| P3 | El antecedente 2014 se presenta como histórico, no como riesgo actual | PENDIENTE |
| P4 | La altitud censal no se confunde con DEM ni pendiente | PENDIENTE |
| P5 | Los indicadores municipales no se leen como medición del predio | PENDIENTE |
| P6 | Las limitaciones y "aspectos a revisar" son suficientes y correctos | PENDIENTE |
| P7 | La procedencia parcial se comunica con honestidad | PENDIENTE |
| P8 | No hay umbrales/porcentajes de riesgo inventados por tipo de obra | PENDIENTE |

Reglas y umbrales por factor/obra (DP-03): cualquier criterio profesional debe
quedar **documentado y justificado** antes de incorporarse al motor. Referencia:
[RULES_VALIDATION_V1](../analytics/RULES_VALIDATION_V1.md). Estado: PENDIENTE.

---

## 3. Ensayo de la demo

Objetivo: recorrido reproducible en **< 7 minutos** en el dispositivo real.
Guion base: [demo_script](../deliverable/demo_script.md).

| # | Paso | Tiempo objetivo | Tiempo medido | OK |
|---|---|---|---|---|
| D1 | Contexto y problema | ~0:45 | PENDIENTE | ☐ |
| D2 | Selección de localidad + tipo de obra | ~1:00 | PENDIENTE | ☐ |
| D3 | Lectura de la ficha (factores, estados, temporalidad) | ~1:30 | PENDIENTE | ☐ |
| D4 | Fuentes y procedencia parcial | ~0:45 | PENDIENTE | ☐ |
| D5 | Comparación A/B sin ganador | ~1:30 | PENDIENTE | ☐ |
| D6 | Límites, faltantes y cierre | ~1:00 | PENDIENTE | ☐ |
| | **Total** | **< 7:00** | PENDIENTE | ☐ |

Plan de contingencia (a preparar): captura estable de respaldo si falla la red o
las teselas externas; copia local del preview. Estado: PENDIENTE.

---

## 4. Formato de registro de sesión (copiar por sesión)

```
SESIÓN DE VALIDACIÓN — ATLAS
Fecha/hora:                         (real, no estimada)
Tipo:                               [ ] Usuario  [ ] Profesional  [ ] Demo
Segmento/rol del participante:
Moderador / Observador:
Dispositivo / navegador / enlace:
Consentimiento registrado:          [ ] Sí

Tareas / puntos:
  - Resultado por ítem:
  - Tareas sin ayuda: __/__
  - Incidencias (severidad):

Malinterpretaciones críticas observadas:
  [ ] faltante interpretado como "seguro/sin riesgo"
  [ ] histórico 2014 interpretado como riesgo actual
  [ ] comparación interpretada como "ganador"
  [ ] procedencia parcial interpretada como fuente verificada

Citas textuales del participante:

Acuerdos / cambios solicitados:
Evidencia adjunta (ruta/enlace):
Estado: PENDIENTE DE VALIDACIÓN EXTERNA hasta ejecutarse con participante real.
```

---

## 5. Qué NO se puede cerrar aquí

- No se declara ningún punto "validado con usuarios" ni "validado por
  especialista" sin sesiones reales registradas.
- No se inventan participantes, tiempos ni aprobaciones.
- La activación de ML permanece fuera (gate no superado; DP-01).
