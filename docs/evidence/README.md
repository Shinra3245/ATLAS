# Evidencias

## Propósito

Conservar trazabilidad verificable para la memoria técnica, la demostración y la reproducción del trabajo.

## Qué conservar

Fuentes y descargas, transformaciones, controles de calidad, decisiones, errores relevantes, pruebas, endpoints, interfaces, análisis, comparación, validación y, solo si existe, entrenamiento de ML. Cada evidencia debe tener fecha, responsable, contexto y relación con un requisito.

No guardar secretos, datos personales innecesarios ni archivos pesados sin acordar su manejo. Registre cada elemento en `evidence_log.md` y cite `../project/PROJECT_CONTEXT.md` cuando documente guardas o limitaciones.

**PENDIENTE DE DECISIÓN DEL EQUIPO:** convención de nombres, almacenamiento de capturas pesadas y responsables de revisión.

## Evidencias técnicas disponibles

- `technical_verification.json`: estado, fecha, comandos y resultados de las
  fases de datos, pruebas de motor/API y HTTP real.
- `api_verification.json`: catorce comprobaciones de HTTP sobre datos reales;
  no utiliza fixtures ni certifica frontend.
- `../../data/metadata/validation_report.json`: integridad de originales,
  reconstrucción determinista y pruebas de datos.
- `evidence_log.md`: registro de actividades realizadas y límites.

Reproducción: `python3 scripts/demo/verify_technical.py`. Los reportes se
actualizan con fecha real y pueden registrar FAIL; verificar el contenido antes
de afirmar un cierre. El frontend y la validación profesional requieren sus
propias evidencias. No hay entrevistas ni ensayos visuales inventados.
