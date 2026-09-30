# ATLAS — Contexto maestro del proyecto HackaTec / InnovaTecNM 2026

> Archivo de contexto para el agente de terminal y desarrollo.
> Este archivo debe considerarse la fuente operativa principal del proyecto, pero NO sustituye la lectura de los documentos oficiales ubicados en la carpeta padre.

## 1. Ubicación de trabajo

Directorio esperado del proyecto:

```bash
~/Documentos/INNOVATEC 2026 TECNOLOGIAS EMERGENTES/ATLAS
```

Los documentos de referencia están en:

```bash
~/Documentos/INNOVATEC 2026 TECNOLOGIAS EMERGENTES/
```

Archivos relevantes:

```text
ERH26-Estructura Entregable V3 Semana 2.docx
ERH26-KitMentoría V3.pdf
image.png
ATLAS/
```

Antes de modificar o implementar algo importante, revisa los archivos oficiales y confirma que lo propuesto sea compatible con sus requisitos.

---

## 2. Contexto del evento

Proyecto para HackaTec, etapa regional de InnovaTecNM 2026.

Reto registrado:

```text
Tecnologías Emergentes
```

Temática asignada:

```text
Tecnología y Diseño Urbano
```

La solución debe atender simultáneamente el reto y la temática.

La evaluación oficial se divide en:

- Memoria técnica: 20 %
- Exposición presencial: 30 %
- Funcionamiento del prototipo / prueba de concepto: 50 %

La presentación considera:

- 7 minutos de exposición.
- 7 minutos de demostración del prototipo.
- 6 minutos de preguntas y respuestas.

Por esta razón, la prioridad técnica es obtener un prototipo funcional, demostrable, estable y explicable antes de agregar funciones experimentales.

---

## 3. Idea del proyecto

Construir un sistema web geoespacial para el estado de Guanajuato que ayude a evaluar preliminarmente ubicaciones relacionadas con:

- casas;
- edificios;
- carreteras;
- otras obras o infraestructura urbana.

El sistema integrará información oficial y cartográfica para visualizar amenazas o condiciones relevantes del territorio.

La propuesta original contempla técnicas de Machine Learning como:

- Random Forest;
- XGBoost;
- eventualmente otras técnicas si los datos lo justifican.

Sin embargo, no se debe presentar un modelo predictivo como confiable si no existen etiquetas, datos de entrenamiento y validación suficientes.

El MVP debe funcionar incluso sin Machine Learning.

---

## 4. Alcance geográfico

El alcance inicial está limitado a:

```text
Estado de Guanajuato, México
```

No ampliar a todo México durante el hackathon salvo que el MVP esté completamente terminado.

---

## 5. Objetivo funcional del MVP

El sistema debe permitir que un usuario:

1. Abra un mapa de Guanajuato.
2. Seleccione una ubicación.
3. Opcionalmente seleccione un tipo de obra:
   - casa;
   - edificio;
   - carretera.
4. Consulte la información geoespacial disponible para ese sitio.
5. Visualice amenazas o factores territoriales relevantes.
6. Consulte la fuente, fecha y cobertura de cada capa.
7. Obtenga una ficha de evaluación preliminar.
8. Compare dos ubicaciones.
9. Distinga claramente:
   - información disponible;
   - información no disponible;
   - resultados calculados;
   - resultados experimentales de ML.

La interfaz NO debe declarar automáticamente que una zona es "segura".

Cuando no exista cobertura o información suficiente, debe utilizarse explícitamente:

```text
Sin información suficiente
```

---

## 6. Alcance científico y técnico

Es necesario diferenciar:

```text
amenaza / peligro
exposición
vulnerabilidad
riesgo
daño observado
```

Una capa de inundación, falla geológica o pendiente NO demuestra por sí sola que una construcción sufrirá daños.

No inventar:

- probabilidades de daño;
- porcentajes de seguridad;
- precisión de modelos;
- datos no presentes en las fuentes.

Si se utiliza ML, el agente debe exigir una variable objetivo claramente definida y una estrategia de validación defendible.

Ejemplos de objetivos potencialmente válidos dependerán del dataset disponible:

```text
susceptibilidad a inundación
susceptibilidad a deslizamientos
clasificación territorial
```

Evitar usar como objetivo:

```text
probabilidad de daño estructural
```

si no existen registros georreferenciados de estructuras dañadas y controles comparables.

---

## 7. Fuentes de datos consideradas

Fuentes principales identificadas:

### CENAPRED
Centro Nacional de Prevención de Desastres.

Posible información:

- atlas de riesgos;
- amenazas;
- información de desastres;
- capas geográficas.

### CONABIO
Comisión Nacional para el Conocimiento y Uso de la Biodiversidad.

Posible información:

- cobertura del suelo;
- vegetación;
- capas ambientales;
- cartografía.

### INEGI

Posible información:

- modelos de elevación;
- relieve;
- cartografía;
- datos territoriales;
- información municipal y estatal.

### Atlas Estatal de Riesgos de Guanajuato

Se identificaron previamente capas relacionadas con:

- puntos de inundación;
- polígonos de inundación;
- agrietamientos;
- fallas y fracturas;
- susceptibilidad de laderas.

### IPLANEG

Puede disponer de capas descargables y cartografía estatal.

Advertencia:

Algunas capas pueden ser antiguas. Registrar siempre:

```text
fuente
nombre del dataset
fecha
sistema de coordenadas
cobertura
fecha de descarga
licencia o términos cuando estén disponibles
URL de origen
```

---

## 8. Regla fundamental sobre los datos

Nunca asumir que:

```text
sin registro = sin riesgo
```

La aplicación debe diferenciar:

```text
riesgo bajo según información disponible
```

de:

```text
sin información suficiente
```

---

## 9. Arquitectura propuesta

Arquitectura inicial recomendada:

```text
FUENTES OFICIALES
    │
    ▼
Procesamiento geoespacial
Python / Pandas / GeoPandas
    │
    ├──────────────► Dataset tabular
    │                    │
    │                    ▼
    │              ML experimental
    │             Random Forest primero
    │
    ▼
GeoJSON / datos procesados
    │
    ▼
FastAPI
    │
    ▼
React + Vite + Leaflet
    │
    ▼
Mapa y análisis de ubicación
```

No introducir infraestructura innecesaria antes de que el MVP funcione.

---

## 10. Stack preferido

### Frontend

```text
React
Vite
Leaflet
React-Leaflet
JavaScript
```

### Backend

```text
Python
FastAPI
Uvicorn
```

### Geoprocesamiento

```text
Pandas
GeoPandas
Shapely
PyProj
```

Agregar Rasterio solo si se requieren archivos ráster.

### Machine Learning

Primera opción:

```text
scikit-learn
RandomForestClassifier o RandomForestRegressor
```

XGBoost solamente si:

1. existe dataset apropiado;
2. Random Forest funciona;
3. hay tiempo;
4. puede demostrarse una mejora mediante validación.

No utilizar redes neuronales únicamente para decir que el sistema usa IA.

---

## 11. Entorno actual del equipo maestro

Equipo principal:

```text
hostname: ProbookHP
usuario: omarbolanos
SO principal: Fedora
```

Versiones conocidas:

```text
Git: 2.55.0
Python: 3.14.7
Node: 24.16.0
npm: 11.13.0
```

Interfaces/IP observadas:

```text
Ethernet: 192.168.10.10/24
Wi-Fi: 172.20.10.9/28
Tailscale: 100.121.183.26/32
```

Docker está instalado porque existen interfaces/bridges de Docker.

Tailscale puede utilizarse para acceso SSH y colaboración remota entre integrantes.

Antes de instalar librerías geoespaciales sobre Python 3.14, verificar compatibilidad. Si una dependencia crítica falla, considerar usar Python 3.12 o 3.13 en un entorno virtual o contenedor, sin romper el Python del sistema.

---

## 12. Organización del equipo

Equipo total:

```text
5 personas
```

Distribución prevista:

### Persona 1 — Datos y SIG

Responsabilidades:

- localizar datasets;
- descargar capas;
- documentar fuentes;
- revisar CRS;
- limpiar datos;
- convertir formatos;
- generar GeoJSON optimizado;
- validar cobertura.

Entregables:

```text
data/raw/
data/processed/
data/sources.md
```

### Persona 2 — Modelo / análisis

Responsabilidades:

- definir variable objetivo;
- preparar features;
- revisar etiquetas;
- crear baseline;
- entrenar Random Forest si es válido;
- evaluar;
- documentar limitaciones.

Si no hay datos adecuados para ML, debe producir un motor de análisis geoespacial explicable en lugar de inventar un predictor.

### Persona 3 — Backend / integración

Responsabilidades:

- FastAPI;
- contratos de API;
- integración;
- Git;
- servidor;
- despliegue local;
- pruebas de comunicación.

### Persona 4 — Frontend

Responsabilidades:

- React;
- Leaflet;
- mapa;
- selección de ubicación;
- selector de capas;
- leyenda;
- ficha de resultados;
- comparación de ubicaciones.

### Persona 5 — Producto / documentación

Responsabilidades:

- memoria técnica;
- presentación;
- Business Model Canvas;
- SCAMPER;
- proyección de costos;
- recopilar capturas y evidencia;
- preparar pitch;
- preparar guion de demo.

---

## 13. Estructura recomendada del repositorio

El agente debe revisar primero qué existe realmente y NO borrar archivos existentes.

Estructura objetivo:

```text
ATLAS/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── services/
│   │   └── models/
│   └── requirements.txt
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sources.md
│
├── ml/
│   ├── notebooks/
│   ├── preprocessing/
│   ├── models/
│   └── evaluation/
│
├── docs/
│   ├── diagrams/
│   ├── evidence/
│   └── decisions/
│
├── scripts/
├── tests/
├── .gitignore
├── README.md
└── PROJECT_CONTEXT.md
```

No es obligatorio crear todo inmediatamente. Crear solo cuando corresponda.

---

## 14. Contrato inicial esperado de API

Endpoints mínimos previstos:

```text
GET /api/health
GET /api/layers
GET /api/analyze
GET /api/compare
```

Ejemplo:

```http
GET /api/analyze?lat=20.6767&lon=-101.3563
```

Respuesta conceptual:

```json
{
  "location": {
    "latitude": 20.6767,
    "longitude": -101.3563,
    "municipality": "Irapuato"
  },
  "hazards": {
    "flood": {
      "level": "medio",
      "source": "fuente oficial",
      "coverage": true
    },
    "geological_fault": {
      "level": "bajo",
      "distance_m": 1420,
      "coverage": true
    },
    "slope": {
      "level": "sin informacion suficiente",
      "coverage": false
    }
  }
}
```

Los nombres y estructuras pueden evolucionar, pero los cambios deben documentarse.

---

## 15. Flujo esperado de demostración

La demo debe ser rápida y comprensible.

Escenario base:

```text
1. Abrir aplicación.
2. Mostrar Guanajuato.
3. Seleccionar tipo de obra.
4. Elegir ubicación A.
5. Ejecutar análisis.
6. Mostrar capas/factores y fuentes.
7. Elegir ubicación B.
8. Comparar A vs B.
9. Mostrar qué información falta.
10. Explicar que es una herramienta de apoyo preliminar y no sustituye estudios técnicos.
```

Mantener este recorrido funcional antes de añadir características secundarias.

---

## 16. Requisitos documentales oficiales a considerar

La memoria técnica debe contemplar, según el documento oficial:

- portada;
- definición del problema u oportunidad de mejora;
- descripción de la propuesta;
- metodología;
- herramientas tecnológicas empleadas;
- especificación técnica;
- ejes transversales;
- Business Model Canvas;
- validación mediante SCAMPER;
- proyección de costos.

Formato general indicado:

```text
PDF
Noto Sans 11
interlineado sencillo
títulos/subtítulos hasta 13
```

Existen límites específicos de palabras e imágenes por sección.

NO asumir los límites de memoria: leer directamente el DOCX oficial antes de redactar el entregable.

---

## 17. Evidencia obligatoria durante el desarrollo

No esperar al final para documentar.

Guardar evidencia de:

- datasets originales;
- URLs;
- scripts;
- limpieza de datos;
- primera capa visualizada;
- arquitectura;
- backend funcionando;
- endpoints;
- mapa;
- análisis;
- comparación;
- entrenamiento ML si existe;
- métricas;
- errores relevantes resueltos;
- pruebas;
- capturas de la aplicación.

Usar:

```text
docs/evidence/
```

y:

```text
docs/decisions/
```

para decisiones técnicas importantes.

---

## 18. Git y trabajo colaborativo

Debe existir una rama principal estable:

```text
main
```

Sugerencia inicial:

```text
dev/data
dev/ml
dev/backend
dev/frontend
```

Reglas:

- no editar directamente `main` durante desarrollo paralelo;
- commits pequeños y descriptivos;
- revisar antes de integrar;
- evitar que varios agentes modifiquen simultáneamente los mismos archivos;
- no subir datasets pesados sin evaluarlo;
- mantener una versión funcional antes de cambios grandes.

Antes de crear ramas, revisar el estado actual del repositorio.

---

## 19. Prioridades por orden

Prioridad 1:

```text
Repositorio y entorno reproducible
```

Prioridad 2:

```text
Primera capa oficial visible en el mapa
```

Prioridad 3:

```text
Consulta de una coordenada
```

Prioridad 4:

```text
Análisis multiamenaza
```

Prioridad 5:

```text
Comparación de dos ubicaciones
```

Prioridad 6:

```text
Interfaz y experiencia de demo
```

Prioridad 7:

```text
ML, únicamente si los datos lo permiten
```

Prioridad 8:

```text
Pulido, documentación, presentación y ensayo
```

---

## 20. Regla de decisión para Machine Learning

Antes de entrenar:

1. ¿Existe una variable objetivo?
2. ¿Está claramente definida?
3. ¿Existen suficientes observaciones?
4. ¿Hay positivos y negativos válidos?
5. ¿Las etiquetas provienen de una fuente defendible?
6. ¿Hay coordenadas?
7. ¿Se puede evitar fuga espacial?
8. ¿Existe conjunto de prueba?
9. ¿La métrica puede explicarse?
10. ¿El modelo aporta valor frente a reglas geoespaciales?

Si varias respuestas son "no", detener el entrenamiento y continuar con análisis geoespacial explicable.

---

## 21. Reglas para el agente de terminal

Actúa como ingeniero senior que acompaña al equipo durante el hackathon.

### Antes de actuar

Siempre:

1. inspecciona el directorio actual;
2. revisa archivos existentes;
3. revisa Git;
4. lee `PROJECT_CONTEXT.md`;
5. lee los documentos oficiales cuando la tarea dependa de ellos;
6. explica brevemente qué vas a modificar.

### Para cambios de archivos

Antes de sobrescribir:

- lee el archivo;
- conserva código válido;
- evita reemplazos completos innecesarios;
- realiza cambios incrementales.

### Para terminal

Puedes ejecutar automáticamente comandos seguros como:

```text
pwd
ls
find
git status
git diff
cat
grep
python --version
node --version
npm --version
crear directorios del proyecto
instalar dependencias dentro de entornos del proyecto
ejecutar tests
ejecutar linters
```

Pide confirmación antes de:

- eliminar archivos;
- usar `rm -rf`;
- sobrescribir datasets;
- resetear Git;
- hacer force push;
- modificar firewall;
- modificar NetworkManager;
- cambiar configuración global;
- instalar paquetes globales del sistema;
- exponer servicios a Internet;
- manipular credenciales.

Nunca mostrar secretos o tokens en commits o documentación.

---

## 22. Comportamiento esperado del agente

El agente debe:

- trabajar paso por paso;
- completar una tarea comprobable antes de iniciar otra;
- ejecutar pruebas después de cambios importantes;
- informar errores reales;
- no declarar éxito sin verificar;
- priorizar estabilidad;
- evitar sobreingeniería;
- mantener trazabilidad;
- documentar decisiones.

Cuando exista más de una alternativa, priorizar:

```text
simplicidad
rapidez
explicabilidad
estabilidad
reproducibilidad
```

en ese orden durante las 27 horas.

---

## 23. Primer procedimiento obligatorio del agente

Al recibir este contexto, NO empieces instalando paquetes inmediatamente.

Primero ejecuta únicamente inspección:

```bash
pwd
find . -maxdepth 3 -type f -o -type d | sort
git status 2>/dev/null || true
python3 --version
node --version
npm --version
```

Después inspecciona los archivos oficiales disponibles en el directorio padre.

Determina:

1. qué estructura ya existe;
2. si `ATLAS` ya es un repositorio Git;
3. qué código hay;
4. qué datasets hay;
5. qué dependencias hay;
6. qué falta para iniciar el MVP.

Luego presenta un plan corto para el siguiente bloque de trabajo.

No borres ni reestructures nada hasta haber realizado esta inspección.

---

## 24. Primera meta de implementación

La primera meta verificable será conseguir:

```text
Backend FastAPI operativo
+
Frontend React/Vite operativo
+
Mapa Leaflet visible
+
Primera capa geográfica oficial de Guanajuato cargada
```

Solo después desarrollar:

```text
/api/analyze
comparación
motor multiamenaza
ML
```

---

## 25. Criterios de calidad

El proyecto debe poder defender:

- de dónde proviene cada dato;
- qué fecha tiene;
- qué representa;
- qué no representa;
- cómo se procesa;
- qué algoritmo se utilizó;
- por qué se utilizó;
- qué limitaciones existen;
- cómo se reproduce el resultado.

Nunca ocultar incertidumbre mediante porcentajes arbitrarios.

---

## 26. Objetivo final del agente

Ayudar al equipo a pasar de este directorio a un prototipo completo y demostrable durante el HackaTec, manteniendo sincronizados:

```text
datos
código
backend
frontend
ML
documentación
evidencia
demo
```

Cada decisión debe favorecer que el producto pueda demostrarse ante el jurado dentro del tiempo disponible.
