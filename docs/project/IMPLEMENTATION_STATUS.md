# Cierre verificable de los diez puntos

Registro actualizado con el desarrollo técnico del 29 de septiembre de 2026.
Las evidencias JSON incluyen su propia fecha UTC. Viabilidad económica y
financiamiento permanecen fuera de esta etapa.

## Etapas realizadas por esta sesión

| Etapa | Estado | Evidencia |
|---|---|---|
| Integridad y publicación de los datos disponibles | Implementada y verificada | 15 libros inventariados, cuatro copias raw adicionales, 57 campos municipales reconstruidos y manifestados. `data/metadata/validation_report.json`. |
| Motor y API sobre los datos disponibles | Implementados y verificados | Validación de rangos y asociación aproximada; selección por clave coherente entre motor/API. Pruebas y HTTP reales en `docs/evidence/technical_verification.json`. |
| Recorrido visual | En desarrollo en otra sesión | Esta sesión no modifica ni certifica frontend. |
| Nuevas capas del núcleo territorial | Pendientes de insumos validados | `docs/data/PENDING_LAYERS.md` y `data/metadata/availability.json`. |
| Umbrales profesionales y pruebas con usuarios | Pendientes de revisión real | `docs/analytics/RULES_VALIDATION_V1.md`. |

## Estado por punto del Plan Maestro

| Punto | Estado | Implementado | Falta para cerrarlo |
|---|---|---|---|
| 1. Integración, comparación y contextualización | Parcial | Datos reales, comparación homogénea y énfasis por tipo de obra. | Recorrido visual y completar factores espaciales. ML sigue condicionado. |
| 2. Usuarios y clientes | Definido; validación pendiente | Segmentos acordados y protocolo de prueba disponible. | Sesiones documentadas con usuarios reales. |
| 3. Identificar condicionantes antes de construir | Parcial | Antecedentes/contexto y faltantes explicados. | Capas y validación que sustenten condicionantes del sitio. |
| 4. Evaluación integrada, explicable y comparable | Parcial | Publicación reproducible, fuentes visibles, explicación y A/B comprobados. | Procedencia/licencias completas, capas y validación del flujo visual. |
| 5. Apoyo a decisiones y ficha | Completo en motor/API | Ficha estructurada, aspectos a revisar y comparación sin ganador. | Integración visual y validación de uso. |
| 6. Tres tipos de obra | Completo en motor/API; criterios especializados parciales | Vivienda, edificación y vialidad comprobados por HTTP; datos invariantes y prioridades específicas. | Interfaz y justificación/revisión de umbrales especializados cuando se incorporen. |
| 7. Factores núcleo | Parcial | Antecedente histórico de inundación y altitud censal auxiliar; faltantes conservados. | DEM/pendiente, fallas, inundación espacial, laderas y uso de suelo validado. Los libros municipales no cierran esas dependencias. |
| 8. Ficha con fuentes, cobertura y faltantes | Completo en motor/API | Resultados, cobertura y comparación concordantes por HTTP. | Presentación final en interfaz. Exportación PDF es opcional. |
| 9. ML complementario condicionado | Conforme a la decisión | ML desactivado y motor/API independientes. | Solo para activar ML: superar gate; no bloquea el MVP. |
| 10. MVP de principio a fin | Parcial | Flujo de API probado para los tres tipos y sus errores. | Navegador, mapa, interacción, adaptación móvil y demostración reproducible del recorrido visual. |

## Criterio de cierre

Una etapa se declara completada únicamente con funcionalidad implementada,
prueba aprobada, evidencia guardada y documentación vigente. Un resultado
técnico no certifica un dictamen territorial ni valida automáticamente una
regla profesional o la aceptación comercial.

Comando de verificación técnica:

```bash
python3 scripts/demo/verify_technical.py
```
