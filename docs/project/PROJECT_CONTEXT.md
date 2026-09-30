# ATLAS — Contexto operativo

## Propósito

Servir como entrada breve al proyecto. El detalle operativo y las decisiones consolidadas están en `ATLAS_PLAN_MAESTRO.md`; el contexto anterior se conserva sin alteraciones en `PROJECT_CONTEXT_LEGACY.md`.

## Autoridad documental

1. Los documentos de `../official/` prevalecen ante contradicciones.
2. `ATLAS_PLAN_MAESTRO.md` define el alcance y la coordinación vigente.
3. `DECISIONS_FINAL.md` separa acuerdos aprobados de asuntos abiertos.
4. Los documentos de `../agents/` delimitan la propiedad de cada bloque.

## Contexto confirmado

- Evento: HackaTec / InnovaTecNM 2026, Etapa Regional.
- Reto: Tecnologías Emergentes.
- Temática: Tecnologías y diseño urbano.
- MVP: Irapuato y Celaya.
- Producto: apoyo preliminar para identificar y comparar condicionantes territoriales de proyectos urbanos.
- Resultado: ficha explicable con condiciones, fuentes, cobertura, faltantes y aspectos a revisar.
- Núcleo: análisis geoespacial; ML permanece opcional y condicionado a validación.

## Organización vigente

- Bloque 1 es propietario de `data/**`, `scripts/data/**` y `docs/data/**`.
- Bloque 2 es propietario de `engine/**`, `ml/**`, `tests/engine/**` y `docs/analytics/**`.
- Bloque 3 es propietario de `backend/**`, `tests/api/**` y `docs/api/**`.
- Bloque 4 será propietario de `frontend/**` y `docs/frontend/**` cuando sea liberado.
- `design/**` conserva exclusivamente material aprobado para Bloque 4.
- Las solicitudes entre bloques se registran en `../../coordination/requests/`.

## Guardas obligatorias

- No equiparar `sin registro` con `sin riesgo`.
- Separar amenaza, exposición, vulnerabilidad, riesgo, daño y contexto.
- Mostrar fuente, fecha o versión, cobertura y limitaciones.
- No producir una puntuación global arbitraria ni un ganador automático entre A y B.
- No presentar el antecedente histórico de 2014 como riesgo actual.
- No presentar ML como válido sin objetivo, etiquetas y validación defendibles.
- ATLAS no emite permisos ni sustituye dictámenes o estudios técnicos.

## Estado de desarrollo

Datos actuales, motor y API están implementados e integrados. El frontend está
en desarrollo en otra sesión. Las capas territoriales faltantes y la validación
con usuarios/especialistas siguen pendientes. El cierre verificable por punto
está en `IMPLEMENTATION_STATUS.md` y las evidencias en `../evidence/`.

Cada bloque debe mantener su estado en `../../coordination/status/` y respetar
contratos y gates del Plan Maestro. Viabilidad económica y financiamiento
permanecen separados por instrucción del equipo en esta etapa.
