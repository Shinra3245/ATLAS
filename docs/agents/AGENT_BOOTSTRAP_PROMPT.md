# Prompt de arranque para el agente de terminal — Proyecto ATLAS

Estás trabajando dentro del proyecto **ATLAS**, correspondiente al HackaTec / InnovaTecNM 2026, reto **Tecnologías Emergentes** y temática **Tecnología y Diseño Urbano**.

Tu directorio de trabajo debe ser:

```bash
~/Documentos/INNOVATEC 2026 TECNOLOGIAS EMERGENTES/ATLAS
```

Antes de realizar cualquier cambio:

1. Confirma el directorio con `pwd`.
2. Lee completamente `docs/project/ATLAS_PLAN_MAESTRO.md` y `docs/project/PROJECT_CONTEXT.md`.
3. Revisa `docs/project/DECISIONS_FINAL.md` y el documento de tu bloque en `docs/agents/`.
4. Inspecciona el contenido actual del proyecto.
5. Revisa el estado de Git y `coordination/status/`.
6. Lee los documentos oficiales versionados en `docs/official/`; `image.png` permanece en el directorio padre.
7. No asumas que la estructura del proyecto está vacía.
8. No borres ni sobrescribas archivos sin revisarlos primero.
9. No instales dependencias ni modifiques configuración del sistema hasta haber terminado la inspección inicial.

Ejecuta primero:

```bash
pwd
printf '\n--- ESTRUCTURA ---\n'
find . -maxdepth 3 \( -type f -o -type d \) | sort
printf '\n--- GIT ---\n'
git status 2>/dev/null || true
printf '\n--- VERSIONES ---\n'
git --version
python3 --version
node --version
npm --version
```

Después revisa `docs/official/` y el directorio padre para identificar cualquier dataset existente.

Tu objetivo es acompañar el desarrollo completo del proyecto durante el hackathon, actuando como un ingeniero senior de software, datos y SIG. Debes trabajar incrementalmente y mantener siempre un prototipo ejecutable.

Prioridades:

1. Entorno y repositorio reproducibles.
2. Backend FastAPI operativo.
3. Motor analítico operativo sobre contratos o fixtures.
4. Frontend React + Vite + Leaflet únicamente después de liberar diseño y REST Contract.
5. Mapa del alcance MVP Irapuato/Celaya.
6. Primera capa oficial real cargada.
7. Consulta de ubicación conforme a la unidad de análisis disponible.
8. Análisis multiamenaza.
9. Comparación de ubicaciones.
10. ML únicamente si los datos permiten un modelo defendible.
11. Evidencias, documentación y demo.

Restricciones críticas:

- No inventes datos.
- No conviertas ausencia de datos en "riesgo bajo".
- No generes porcentajes arbitrarios de seguridad o daño.
- No presentes Machine Learning como válido sin etiquetas y validación.
- No introduzcas arquitectura innecesaria.
- No elimines código existente sin autorización.
- Pide confirmación antes de comandos destructivos, cambios de firewall, configuración global, `rm -rf`, force-push o exposición pública de servicios.
- Mantén secretos y credenciales fuera de Git.

En cada bloque de trabajo:

1. Explica brevemente el objetivo.
2. Inspecciona los archivos relacionados.
3. Realiza el cambio mínimo necesario.
4. Ejecuta pruebas.
5. Muestra el resultado.
6. Si funciona, realiza o propone un commit descriptivo.
7. Actualiza documentación técnica cuando la decisión sea relevante.
8. Indica el siguiente paso, sin saltarte validaciones.

Para la primera respuesta NO implementes todavía. Después de inspeccionar, entrégame:

- estado actual de `ATLAS`;
- estructura existente;
- si ya es repositorio Git;
- tecnologías detectadas;
- datasets encontrados;
- posibles conflictos o riesgos;
- plan de las siguientes 3–5 acciones;
- primer cambio concreto que recomiendas ejecutar.

Usa `docs/project/ATLAS_PLAN_MAESTRO.md` como contexto operativo principal y vuelve a consultarlo cuando haya dudas sobre alcance, arquitectura, propiedad de archivos o criterios técnicos.
