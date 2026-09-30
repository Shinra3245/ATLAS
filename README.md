# ATLAS

Plataforma web de apoyo a la prefactibilidad territorial para proyectos urbanos del HackaTec / InnovaTecNM 2026.

## Estado y alcance vigente

El alcance operativo consolidado del MVP se limita a **Irapuato y Celaya**. ATLAS integrará evidencia territorial, generará una ficha preliminar y permitirá comparar dos ubicaciones sin declarar automáticamente una zona segura ni sustituir estudios técnicos.

La fuente operativa principal es [ATLAS_PLAN_MAESTRO.md](docs/project/ATLAS_PLAN_MAESTRO.md). Las decisiones aprobadas y los asuntos todavía abiertos se registran en [DECISIONS_FINAL.md](docs/project/DECISIONS_FINAL.md).

## Bloques de trabajo

- `data/`: Bloque 1, Datos y SIG.
- `engine/` y `ml/`: Bloque 2, motor analítico y ML condicionado a validación.
- `backend/`: Bloque 3, API e integración.
- `frontend/`: Bloque 4, interfaz implementada y en revisión con usuarios.
- `design/`: materiales de referencia para la implementación visual.
- `coordination/`: estados y solicitudes entre bloques.
- `scripts/`: automatizaciones auxiliares.
- `tests/`: pruebas compartidas por área.
- `docs/`: documentación del proyecto, agentes, fuentes oficiales y entregables.

## Orden de lectura

1. `docs/official/`: documentos oficiales del evento; prevalecen ante contradicciones.
2. `docs/project/ATLAS_PLAN_MAESTRO.md`: alcance, arquitectura de referencia y contratos.
3. `docs/project/PROJECT_CONTEXT.md`: reglas y contexto operativo.
4. `docs/project/DECISIONS_FINAL.md`: decisiones consolidadas y pendientes.
5. `docs/agents/`: responsabilidad exclusiva de cada bloque.
6. `coordination/README.md`: protocolo para estados y solicitudes.

## Guardas

- Ausencia de datos no significa riesgo bajo.
- No se publican porcentajes, métricas ni conclusiones sin respaldo.
- El análisis SIG es obligatorio; ML es opcional y debe superar su gate de validación.
- Ningún bloque modifica archivos propiedad de otro bloque; solicita el cambio mediante `coordination/requests/`.

## Verificación y cierre técnico

```bash
python3 scripts/demo/verify_technical.py
```

Reconstruye y verifica datos, prueba motor/API y recorre los casos por HTTP
real en una instancia aislada. Evidencias en `docs/evidence/`; no certifica
la interfaz ni las capas todavía pendientes. El estado por cada uno de los
diez puntos está en [IMPLEMENTATION_STATUS.md](docs/project/IMPLEMENTATION_STATUS.md).

## Datos y estado del repositorio

Este repositorio versiona código, contratos, pruebas, documentación y recursos
de interfaz. Los originales de `data/incoming/` y `data/raw/`, el inventario
con muestras `data/metadata/inventory.json` y los productos derivados de
`data/processed/` permanecen fuera de Git: las
compilaciones recibidas todavía tienen procedencia y condiciones de uso
parcialmente verificadas. Para ejecutar el análisis con datos reales se
requiere disponer de esos archivos por un canal autorizado y seguir las
instrucciones de [data/README.md](data/README.md). Un clon sin esos datos no
puede ofrecer el catálogo territorial real ni pasar las pruebas de integración
que dependen de él.

La QA del MVP se resume en
[QA_PLAN_MAESTRO_10_PUNTOS.md](docs/frontend/QA_PLAN_MAESTRO_10_PUNTOS.md):
hay flujo web y API verificados, pero siguen pendientes capas espaciales,
procedencia completa y validación con usuarios. El primer commit es un corte
del avance, no una declaración de cierre de esos pendientes.
