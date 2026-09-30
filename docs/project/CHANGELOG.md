# Historial de cambios

Este archivo registra cambios relevantes de estructura, documentación y producto. Las decisiones se detallan en `DECISIONS_FINAL.md` y las evidencias en `../evidence/evidence_log.md`.

## 2026-09-29

### Reorganizado

- Documentación operativa trasladada a `docs/project/` y `docs/agents/`.
- Documentación temática distribuida entre `docs/data/`, `docs/analytics/`, `docs/api/`, `docs/frontend/`, `docs/business/`, `docs/evidence/` y `docs/deliverable/`.
- Creación de `engine/`, `design/` y la estructura de solicitudes en `coordination/`.
- `index.html` trasladado a `frontend/` sin cambiar su contenido.
- Copias verificadas de los documentos oficiales agregadas a `docs/official/`; los originales del directorio padre permanecen intactos.
- `DECISIONS_FINAL.md` actualizado con los acuerdos expresos del Plan Maestro y los asuntos todavía abiertos.

### Agregado

- Estructura base para frontend, backend, datos, ML, pruebas y documentación.
- Contexto operativo canónico y registro de decisiones pendientes.
- Plantillas documentales para el trabajo paralelo del equipo.
- Checklist basado en el documento oficial del entregable.
- Reglas de exclusión para secretos, dependencias y artefactos pesados.

### Conservado

- `PROJECT_CONTEXT_LEGACY.md` y `.skills-shared/` se conservaron como referencia histórica y herramientas locales.

### Pendiente

- **PENDIENTE DE DECISIÓN DEL EQUIPO:** acuerdos funcionales, datos, arquitectura, ML, validación, negocio y costos antes de implementar.

### Cierre técnico posterior del mismo día

- Incorporados al pipeline los cuatro libros de contexto municipal: inventario
  completo de 15 entradas, copias raw verificadas y extensión reconstruida con
  57 campos. Se conservan maestro, clima y originales previos.
- Añadida validación de identidad, duplicados, coordenadas, constancia municipal
  y valores finitos; hashes de la extensión y sus entradas en el manifiesto.
- Corregida la compuerta de API para respetar la selección por clave del motor.
  Comparar claves distintas con coordenadas auxiliares iguales ya es válido;
  comparar la misma localidad sigue rechazándose.
- El motor valida rangos globales e informa toda asociación aproximada al punto
  de localidad, diferenciándola de una medición del predio.
- Corregidos imports de utilidades de pruebas que dependían del orden de las
  suites. Añadidos comando único y reportes de verificación HTTP real.
- Resultado: 27 pruebas de datos, 66 del motor, 36 de API y 14 comprobaciones
  HTTP aprobadas. Cierre por punto y pendientes documentados en
  `IMPLEMENTATION_STATUS.md`.
- Frontend continúa en otra sesión; esta sesión no lo modifica. Capas del
  núcleo y validación con especialistas/usuarios siguen pendientes. Negocio,
  viabilidad económica y financiamiento se mantienen separados.
