# Pipeline reproducible de Bloque 1

Ejecutar desde la raíz de ATLAS:

```bash
python3 scripts/data/inspect_datasets.py
python3 scripts/data/build_v1.py
python3 -m unittest discover -s tests/data -v
python3 scripts/data/verify_v1.py
```

Entorno usado: Python 3.14.7, openpyxl 3.1.5 ya disponible. No se instalaron paquetes. En otro equipo, usar exclusivamente un entorno local `scripts/data/.venv` y `requirements.txt`; nunca instalar globalmente.

`inspect_datasets.py` descubre recursivamente todos los archivos de recepción y produce perfiles completos de hojas/columnas, nulos, rangos, tipos, muestras, duplicados y SHA256. No interpreta el nombre como garantía científica.

`build_v1.py` compara los dos maestros, crea copias exclusivas en raw, valida el alcance por municipio y clave, filtra el archivo estatal, contrasta campos comunes, normaliza encabezados solo en productos y preserva nulos. Publica el maestro enriquecido, la serie climática independiente y la extensión de contexto municipal, schemas, contrato, inventario, calidad y manifiesto.

Los cuatro libros de `incoming/new_downloads` se registran y copian a `raw/municipal_context`. `build_municipal_context.build_context` valida claves únicas, identidad, coordenadas y valores constantes por municipio antes de publicar 57 campos en `municipal_context.json`. Esta extensión se incluye en los hashes del manifiesto; no altera el maestro de 64 campos ni convierte indicadores municipales en mediciones locales. El antiguo comando `python3 scripts/data/build_municipal_context.py` delega en la publicación completa V1 para no dejar hashes desactualizados.

Los archivos unknown quedan registrados sin publicación operativa hasta revisar su contenido y agregar una política explícita. La tabla de terreno se conserva como referencia no validada en intermediate; no se usa para elevar DEM/pendiente a disponible.

`verify_v1.py` vuelve a ejecutar el constructor, compara todos los hashes de productos (el manifiesto solo puede cambiar su fecha de publicación), verifica que incoming/raw permanezcan idénticos y ejecuta las pruebas. Deja los resultados reales en `data/metadata/validation_report.json`.

Reejecutar es seguro para incoming/raw: una copia raw existente se reutiliza solo si coincide su hash; una colisión aborta sin reemplazarla. Los productos y documentos generados se reemplazan atómicamente dentro de la propiedad de Bloque 1; manifest.json se publica al final. Para cambios de semántica o nuevas columnas, acordar la versión con Bloque 2 antes de re-publicar V1.
