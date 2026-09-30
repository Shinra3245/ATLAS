# ATLAS - Plan Maestro de Proyecto y Desarrollo

## 0. Propósito de este documento

Este archivo es el contexto operativo principal para todos los agentes y equipos técnicos de **ATLAS**. Debe leerse antes de realizar cambios. Reúne las decisiones finales del equipo, el alcance geográfico, la arquitectura objetivo, el inventario real de datos entregado, las dependencias entre bloques, los contratos de integración y las reglas para evitar conflictos entre agentes.

**Regla superior del MVP:** todo el desarrollo evaluable se limita exclusivamente a **Irapuato y Celaya**. La cobertura del estado completo de Guanajuato se documenta solo como expansión futura. No se debe presentar al jurado una cobertura estatal completa si no existe en el prototipo.

## 1. Contexto del evento

- Evento: HackaTec / InnovaTecNM 2026, Etapa Regional.
- Reto: **Tecnologías Emergentes**.
- Temática: **Tecnología y Diseño Urbano**.
- Evaluación oficial: memoria técnica 20 %, exposición 30 %, prototipo/prueba de concepto 50 %.
- Tiempos: 7 min exposición, 7 min demostración, 6 min preguntas.
- Prioridad operativa: prototipo estable y demostrable antes de funciones experimentales.

## 2. Definición consolidada de ATLAS

**ATLAS es una plataforma web de apoyo a la prefactibilidad territorial para proyectos urbanos en Irapuato y Celaya. Integra información oficial, analiza condicionantes territoriales, explica la evidencia disponible, genera una ficha preliminar y permite comparar dos ubicaciones bajo los mismos criterios.**

ATLAS no emite permisos, dictámenes estructurales ni declara una zona como "segura". Cuando falten datos, la salida debe ser **"Sin información suficiente"**.

## 3. Decisiones finales del equipo

### Punto 1
Fusionar A+B+C+D: información territorial dispersa; dificultad de comparación; interpretación según tipo de obra; y aprovechamiento de datos/ML para susceptibilidad solo cuando sea validable.

### Punto 2
Usuarios/clientes principales: despachos de arquitectura e ingeniería, desarrolladores inmobiliarios, gobiernos municipales/planeación y profesionales/organizaciones vinculadas a proyectos urbanos. Clientes secundarios: constructoras pequeñas y medianas.

### Punto 3
Identificar condicionantes territoriales antes de construir.

### Punto 4
Transformar datos territoriales oficiales en una evaluación preliminar integrada, explicable y comparable.

### Punto 5
Diferenciación principal: sistema de apoyo a decisiones; complemento: generación de ficha de prefactibilidad.

### Punto 6
Tipos de obra: vivienda, edificación y carretera/vialidad.

### Punto 7
Núcleo: inundación, fallas/fracturas, pendiente, susceptibilidad de laderas y uso de suelo; elevación como variable auxiliar. Incorporar además datasets útiles encontrados sin convertirlos automáticamente en riesgo.

### Punto 8
Resultado: ficha de evaluación territorial preliminar con condiciones, fuentes, cobertura, faltantes y aspectos a revisar.

### Punto 9
ML complementario y explicable para una amenaza específica; el análisis SIG es el núcleo obligatorio.

### Punto 10
MVP: mapa + tipo de obra + análisis individual + ficha + fuentes + comparación A/B + ML opcional si está validado.


## 4. Problema que se busca resolver

El proyecto combina cuatro dimensiones del problema:

1. **Dispersión de datos:** información territorial y de infraestructura repartida entre múltiples fuentes y formatos.
2. **Dificultad de comparación:** comparar dos ubicaciones exige normalizar criterios y fuentes.
3. **Interpretación según tipo de obra:** una misma variable territorial necesita contextualización diferente para vivienda, edificación o vialidad.
4. **Aprovechamiento insuficiente de datos para anticipar susceptibilidad:** se explorará ML solo para una amenaza concreta y solo si las etiquetas y validación son defendibles.

La necesidad operativa elegida por el equipo es **identificar condicionantes antes de construir**. Por tanto, el sistema debe priorizar evidencia y trazabilidad sobre un supuesto "score" global.

## 5. Usuarios y clientes

### Principales
- Despachos de arquitectura e ingeniería.
- Desarrolladores inmobiliarios.
- Gobiernos municipales y áreas de planeación/desarrollo urbano.
- Profesionales y organizaciones vinculadas a la evaluación de proyectos urbanos.

### Secundarios
- Constructoras pequeñas y medianas.

### Caso de uso de demostración recomendado
Un despacho o desarrollador evalúa dos ubicaciones candidatas en Irapuato o Celaya para una **edificación**. ATLAS analiza las dos con la misma matriz de factores y genera una comparación explicable.

## 6. Alcance funcional del MVP

### Obligatorio
- Mapa centrado en Irapuato/Celaya.
- Selector de tipo de proyecto: vivienda / edificación / carretera-vialidad.
- Selección de ubicación A.
- Análisis territorial con fuentes y cobertura.
- Ficha de prefactibilidad preliminar.
- Selección de ubicación B.
- Comparación A/B sin "ganador" automático ni porcentaje global arbitrario.
- Estado explícito de datos faltantes.
- Trazabilidad: fuente, fecha o versión cuando exista, cobertura y limitación.

### Opcional, solo después de estabilizar el MVP
- ML para una amenaza concreta.
- Exportación de ficha a PDF.
- Historial de análisis.
- Autenticación.
- API pública.

## 7. Modelo de información territorial

ATLAS debe distinguir:

- **Amenaza / susceptibilidad:** inundación, laderas, fallas/fracturas cuando existan capas adecuadas.
- **Factores territoriales:** pendiente, elevación, uso de suelo, hidrología, infraestructura cercana.
- **Contexto socioeconómico y urbano:** población, vivienda, servicios, movilidad.
- **Cobertura de datos:** disponible / parcial / no disponible.
- **Limitación:** por qué un dato no permite una conclusión definitiva.

Nunca convertir automáticamente infraestructura, población o distancia a servicios en "riesgo". Son variables de contexto o prefactibilidad.

## 8. Auditoría de los archivos XLSX entregados

### 8.1 Dataset maestro: `irapuato_celaya_dataset_ml_geoespacial (2).xlsx`

Hechos verificados del libro:

- 755 localidades en total.
- 434 de Irapuato y 321 de Celaya.
- Distancias expresadas en metros.
- CRS usado para distancias: EPSG:6372.
- **No existe variable objetivo de ML creada.**
- **No existe pendiente con cobertura completa.** El propio archivo indica que se requiere DEM/MDS adecuado.
- 39 columnas en la tabla maestra.

Variables actualmente útiles:

**Contexto y demanda**
- población total, población 15-64, PEA, población ocupada, viviendas y viviendas habitadas;
- cobertura eléctrica y drenaje;
- automóviles por 100 viviendas y variables de disponibilidad/frecuencia/tiempo de transporte.

**Riesgo histórico censal explícito en la tabla maestra**
- inundación 2014;
- sequía 2014;
- helada 2014;
- incendio 2014.

Nota: el inventario del equipo menciona también temblor y ciclón, pero esas columnas **no aparecen en la tabla maestra inspeccionada**. Deben localizarse en la fuente original o integrarse posteriormente; no asumir que ya están en el dataset final.

**Proximidades geoespaciales**
- carretera;
- camino;
- río/arroyo;
- cuerpo de agua;
- canal;
- línea de transmisión;
- subestación;
- vía férrea;
- industria;
- infraestructura vial;
- infraestructura hídrica.

### 8.2 Subcuencas

`subcuencas_Guanajuato_RNA(1).xlsx`
- 23 registros filtrados con cobertura en Guanajuato.
- Incluye claves, cuenca, región hidrológica, relaciones de drenaje/descarga, punto representativo y BBOX.
- El área corresponde a la subcuenca completa, no al área dentro de Guanajuato.

`subcuencas_hidrograficas_RNA(2).xlsx`
- 976 registros nacionales.
- WGS84 / EPSG:4326.
- No incluye municipio; requiere cruce espacial.

**Restricción:** los XLSX contienen puntos/BBOX representativos, no la geometría poligonal completa necesaria para asignación espacial precisa. Conservar como referencia y metadatos. Para análisis de subcuenca por punto debe integrarse la geometría original SHP/GeoPackage/GeoJSON.

### 8.3 Ferrocarril

`datos_ferroviarios_para_RNA(2).xlsx`
- 988 nodos ferroviarios.
- 314 instalaciones origen-destino.
- EPSG:6372 y coordenadas WGS84.
- Uso recomendado: conectividad/proximidad e infraestructura.

El dataset es nacional: filtrar exclusivamente al área de trabajo de Irapuato/Celaya (con buffer documentado si se requiere medir proximidad externa).

### 8.4 Uso de suelo y vegetación Serie I

`uso_suelo_vegetacion_serie_I_historico_F14_7_F14_8.xlsx`
- Información histórica.
- Incluye entidad, tipo, fisonomía, vegetación secundaria, erosión y cultivos.
- **No tratar como estado actual.**
- Uso recomendado: cambio histórico, antecedente de cobertura y variable contextual; nunca como fotografía presente.

### 8.5 Uso de suelo y vegetación Serie IV

`uso_suelo_vegetacion_serie_IV_F14_7_F14_8.xlsx`
- Vegetación, cobertura, altura, agricultura, cultivos y especies.
- Atributos útiles para variables ambientales/categóricas.
- Aún no están cruzados a localidades/cuadrícula.
- Para unión espacial robusta se requieren las geometrías originales de los ZIP/SHP de fuente.

## 9. Datos disponibles vs. rol en ATLAS

| Grupo | Uso recomendado en MVP | Rol |
|---|---|---|
| Socioeconómicos | contexto de población/demanda | complementario |
| Servicios | contexto urbano y cobertura | complementario |
| Movilidad | accesibilidad/contexto | complementario |
| Carreteras/caminos | distancia y conectividad | importante para vialidad |
| Ferrocarril | proximidad/conectividad | complementario |
| Industria | proximidad/contexto | complementario |
| Electricidad | infraestructura cercana | complementario |
| Hidrología | proximidad a río/canal/cuerpo de agua | núcleo para inundación |
| Subcuencas | contexto hidrológico | integrar cuando exista geometría |
| Uso de suelo | compatibilidad/contexto territorial | núcleo |
| Vegetación/agricultura | contexto ambiental | complementario |
| Erosión histórica | antecedente, no estado actual | complementario |
| Riesgo histórico censal | antecedente histórico | núcleo explicable, no riesgo actual |
| Altitud | variable topográfica | núcleo auxiliar |

## 10. Datasets faltantes y carpeta de integración

Crear y mantener:

```text
data/
├── incoming/                       # zona de entrega temporal de nuevos archivos
│   └── README.md
├── raw/
│   ├── census/
│   ├── transport/
│   ├── hydrology/
│   ├── landuse/
│   ├── vegetation/
│   ├── infrastructure/
│   └── reference_xlsx/
├── pending/
│   ├── dem/
│   ├── geology_faults/
│   ├── landslides/
│   ├── anp/
│   ├── modern_flood_surface/
│   ├── precipitation/
│   ├── soils/
│   └── potential_land_use/
├── intermediate/
├── processed/
│   └── v1/
├── metadata/
│   ├── source_manifest.csv
│   └── field_dictionary.md
└── contracts/
    ├── analysis_unit.schema.json
    └── layer_manifest.schema.json
```

### Prioridad de adquisición
1. DEM homogéneo Irapuato + Celaya -> derivar pendiente y rugosidad.
2. Fallas/fracturas geológicas con geometría.
3. Inundación espacial moderna con geometría y fecha.
4. Susceptibilidad/deslizamientos.
5. Precipitación homogénea.
6. ANP.
7. Suelos y uso potencial con geometría actualizable.

## 11. Unidad de análisis: decisión técnica crítica

Los datos actuales están principalmente ligados a **localidades censales**. Por ello el MVP debe soportar dos niveles:

### Nivel A - totalmente soportado desde el dataset maestro
Selección de una localidad/punto de análisis entre las 755 observaciones.

### Nivel B - coordenada arbitraria
Solo habilitar análisis continuo para las capas geográficas originales que tengan geometría completa. Si una capa solo existe en forma de atributo por localidad, no interpolarla ni proyectarla a un punto arbitrario sin metodología explícita.

La UI debe mostrar el tipo de unidad analizada: `Localidad/punto de análisis` o `Coordenada con cobertura de capa`.

## 12. Arquitectura de referencia

```text
                FUENTES OFICIALES / XLSX / GIS
                           |
                           v
                    BLOQUE 1 - DATOS/SIG
                           |
                 dataset + capas normalizadas
                           |
                    DATA CONTRACT v1
                           |
             +-------------+--------------+
             |                            |
             v                            v
  BLOQUE 2 - MOTOR ANALÍTICO        fixtures para API
  reglas + análisis + ML opt.             |
             |                            |
             +-----------+----------------+
                         v
                 ENGINE CONTRACT v1
                         |
                         v
               BLOQUE 3 - BACKEND/API
                         |
                    REST CONTRACT v1
                         |
                         v
                FASE VISUAL / FRONTEND
```

## 13. Contratos y propiedad de archivos

### Bloque 1 - Datos/SIG
Propietario exclusivo de:
- `data/**`
- `scripts/data/**`
- `docs/data/**`

### Bloque 2 - Motor analítico/ML
Propietario exclusivo de:
- `engine/**`
- `ml/**`
- `tests/engine/**`
- `docs/analytics/**`

### Bloque 3 - Backend e integración
Propietario exclusivo de:
- `backend/**`
- `tests/api/**`
- `docs/api/**`

### Fase visual/frontend
Propietario exclusivo de:
- `frontend/**`
- `design/**`
- `docs/frontend/**`

Ningún bloque modifica directorios de otro bloque. Si requiere un cambio, crea una solicitud en `coordination/requests/`.

## 14. Protocolo anti-conflictos y STOP

Estados permitidos por tarea:

- `READY`
- `IN_PROGRESS`
- `BLOCKED_CONTRACT`
- `BLOCKED_DATA`
- `REVIEW`
- `DONE`

### Regla STOP
Si un agente detecta discrepancia en un contrato de otro bloque:

1. **No corrige el archivo ajeno.**
2. Marca su integración como `BLOCKED_CONTRACT`.
3. Escribe `coordination/requests/from_block_<n>/REQ-<fecha>-<bloque>.md` con:
   - contrato esperado;
   - contrato recibido;
   - ejemplo mínimo;
   - impacto;
   - cambio solicitado.
4. Continúa solo con tareas internas que no dependan de ese contrato.
5. El bloque propietario resuelve y publica una nueva versión del contrato.
6. El bloque detenido reanuda desde un commit estable.

### Orden de autoridad
`DATA CONTRACT` -> `ENGINE CONTRACT` -> `REST CONTRACT` -> `FRONTEND`.

Un bloque posterior nunca redefine semántica de uno anterior.

## 15. Fases continuas de trabajo

### Fase 0 - 0 a 1.5 h: congelamiento de contratos
Todos leen este documento, crean ramas y acuerdan schemas mínimos. No se modifica `main` en paralelo.

### Fase 1 - 1.5 a 6 h: desarrollo paralelo
- B1: ingestión, manifiesto, normalización, datasets v1.
- B2: motor analítico sobre fixtures del data contract.
- B3: FastAPI y endpoints sobre fixtures del engine contract.
- Visual: generar referencias y sistema de diseño; no bloquear backend.

### Gate G1 - ~6 h
Congelar `DATA CONTRACT v1` y `processed/v1` mínimo.

### Fase 2 - 6 a 12 h
- B1: capas prioritarias y cobertura.
- B2: conectar a datos reales, pruebas y reglas.
- B3: conectar engine, validar JSON, CORS, errores.
- Frontend: implementar mapa y flujo principal contra mock/API estable.

### Gate G2 - ~12 h
Congelar `ENGINE CONTRACT v1` y `REST CONTRACT v1`.

### Fase 3 - 12 a 18 h
Integración end-to-end A -> ficha -> B -> comparación.

### Fase 4 - 18 a 21 h
Corrección, rendimiento, manejo de faltantes, accesibilidad. Congelar funcionalidades a la hora 21.

### Fase 5 - 21 a 27 h
Documentación, evidencia, pitch, ensayo, demo offline y entrega.

## 16. Flujo funcional objetivo

```text
Inicio
 -> elegir tipo de obra
 -> mapa Irapuato/Celaya
 -> elegir A
 -> analizar
 -> ficha A
 -> "Comparar otra ubicación"
 -> elegir B
 -> analizar B con los mismos criterios
 -> comparación A/B
 -> detalle de fuentes y faltantes
 -> advertencia de alcance
```

ATLAS no elige un ganador. Compara evidencia y condicionantes.

## 17. Contrato conceptual de resultado

```json
{
  "analysis_id": "...",
  "project_type": "building",
  "location": {
    "municipality": "Irapuato",
    "lat": 0.0,
    "lon": 0.0,
    "analysis_unit": "locality|continuous_layer"
  },
  "conditions": [
    {
      "code": "flood_history",
      "category": "hazard_history",
      "value": "...",
      "status": "available|partial|missing",
      "source_id": "...",
      "source_date": "...",
      "explanation": "...",
      "limitation": "..."
    }
  ],
  "coverage": {"available": 0, "expected": 0},
  "ml": {"enabled": false, "reason": "target_not_validated"},
  "disclaimer": "Evaluación preliminar; no sustituye estudios técnicos."
}
```

## 18. ML: criterio de activación

El módulo ML permanece **apagado** hasta responder sí a todas:

1. Variable objetivo definida y documentada.
2. Etiquetas con significado claro.
3. Distribución de clases aceptable o estrategia justificada.
4. Features sin fuga de información.
5. Validación espacial o por grupos.
6. Métricas entendibles.
7. Resultados superiores a baseline simple.
8. Limitaciones documentadas.

Candidato recomendado: **susceptibilidad histórica a inundación** como experimento, comparando regresión logística/baseline contra Random Forest. No presentar el indicador histórico de 2014 como riesgo actual.

## 19. Evidencia a capturar desde el inicio

- hash/nombre/fecha de cada dataset;
- capturas del pipeline de datos;
- diccionario y CRS;
- primer mapa;
- primera llamada API;
- ejemplo de ficha;
- comparación A/B;
- pruebas de datos faltantes;
- métricas ML si se activa;
- diagrama de arquitectura;
- commits/hitos;
- capturas finales.

## 20. Definition of Done global

ATLAS está listo para demo cuando:

- funciona sin Internet externo o tiene fallback local;
- A y B se analizan bajo los mismos criterios;
- cada resultado muestra fuente/cobertura;
- faltantes no se muestran como "bajo riesgo";
- no existe un porcentaje global inventado;
- el módulo ML puede desactivarse sin romper la app;
- el frontend puede completar el flujo en menos de 7 minutos;
- existe copia estable etiquetada para presentación.

## 21. Fuentes oficiales del concurso

Revisar siempre los archivos ubicados en el directorio padre:
- `ERH26-Estructura Entregable V3 Semana 2.docx`
- `ERH26-KitMentoría V3.pdf`

En caso de contradicción, los documentos oficiales prevalecen sobre este archivo.
