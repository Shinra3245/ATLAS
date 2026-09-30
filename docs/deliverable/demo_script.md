# Guion de demostración

## Propósito

Definir una demostración presencial reproducible que muestre el flujo principal y las limitaciones sin depender de funciones no terminadas.

## Restricción oficial

La demostración del prototipo o prueba de concepto dura 7 minutos y puede involucrar a todas y todos los estudiantes del equipo.

## Guion propuesto; ensayo visual pendiente

La API y los datos de estos casos están verificados. El guion de pantalla debe
ensayarse cuando la otra sesión complete el frontend. No se registra aún como
demostración ejecutada.

| Tiempo | Acción | Evidencia que debe mostrarse |
|---|---|---|
| 0:00–0:40 | Explicar alcance: Irapuato/Celaya, evaluación preliminar por localidad. | Aviso visible; no prometer cobertura estatal o dictamen de predio. |
| 0:40–1:20 | Elegir Edificación y Los Aguirre, Celaya, CVEGEO 110070078. | Localidad, coordenadas publicadas y tipo de obra. |
| 1:20–2:40 | Consultar ficha A. | Antecedente de inundación 2014, altitud de referencia y factores sin información. |
| 2:40–3:30 | Seleccionar Irapuato, CVEGEO 110170001, como B. | Mismo tipo de obra; localidad distinta. |
| 3:30–5:00 | Mostrar comparación A/B. | Valores y cobertura concordantes con fichas; sin ganador. Antecedente disponible en A y dato ausente en B no permiten concluir que B sea más seguro. |
| 5:00–6:00 | Abrir fuentes y limitaciones. | Procedencia parcial, fechas/periodos y contexto municipal diferenciado del predio. |
| 6:00–7:00 | Explicar faltantes y siguientes pasos. | Capas pendientes y ML apagado. Mostrar prevención de comparación de la misma localidad si la interfaz está lista. |

## Precondiciones

- Ejecutar `python3 scripts/demo/verify_technical.py` y revisar PASS en sus
  reportes. Esta verificación sí fue ejecutada y no sustituye el ensayo visual.
- El responsable del Uvicorn en puerto 8000 debe reiniciarlo tras cambios para
  cargar la publicación actual. Contrato REST V1 y datos locales disponibles.
- Confirmar frontend integrado, fuentes/avisos visibles y recursos del mapa
  disponibles sin Internet o con respaldo local comprobado.
- Asignar integrantes y comprobar duración con un ensayo real.

## Contingencia técnica disponible

`python3 scripts/demo/verify_api.py --launch` muestra por HTTP real análisis,
comparación y errores sin Internet externo. Sirve para diagnóstico y respaldo
técnico; no acredita por sí solo el funcionamiento de la interfaz requerida.

Capturas, ensayo visual, participantes y responsables de exposición siguen
pendientes de registro. No utilizar valores ilustrativos de los mockups.
