# Handoff de cierre técnico para la sesión de frontend

## Alcance

El usuario confirmó que otra sesión desarrolla la interfaz. Esta sesión
modificó datos, motor, backend y documentación de cierre; no frontend ni diseño.

## Contratos compatibles

Se conservan rutas, nombres de campos y `engine_result/v1`. Los catálogos
actuales contienen 755 localidades, 53 atributos por localidad y 14 fuentes.
La ficha mantiene 57 campos municipales como PARTIAL_DATA y categoría contexto.

La API ahora respeta la clave publicada `locality_id` en la compuerta de
cobertura. La clave es autoritativa; el motor devuelve la coordenada canónica.
Comparar claves distintas no se rechaza por coordenadas auxiliares iguales.
Una misma localidad resuelta sigue respondiendo 422 SAME_LOCATION.

Toda asociación aproximada de una coordenada a una localidad incluye una nota
que explica que los datos describen la localidad, no el predio. Debe mostrarse
`location.notes`, además de las limitaciones generales.

## Verificación disponible

```bash
python3 scripts/demo/verify_technical.py
```

Resultados en `docs/evidence/technical_verification.json` y
`docs/evidence/api_verification.json`. La verificación HTTP usa una API propia
aislada y no interrumpe el puerto 8000.

## Dependencia de ejecución

El Uvicorn existente en puerto 8000 comenzó antes de estos cambios. Su
responsable debe reiniciarlo para cargar código y datos nuevos, porque el
motor conserva caché por proceso. Esta sesión no mata procesos ajenos.

## Cierre visual pendiente

Comprobar A → ficha → B → comparación en navegador para los tres tipos de
obra; fuentes/faltantes, errores, mensajes de aproximación y uso sin Internet
externo o con respaldo. No presentar cifras de los mockups como resultados.
Los estados globales de cierre están en `docs/project/IMPLEMENTATION_STATUS.md`.
