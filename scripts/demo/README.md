# Verificación técnica de ATLAS

Desde la raíz del repositorio:

```bash
python3 scripts/demo/verify_technical.py
```

Este comando reconstruye y verifica los datos, ejecuta las pruebas del motor y
la API, y comprueba el recorrido por HTTP real con una instancia local aislada.
Si una fase falla, no ejecuta las posteriores y escribe un reporte FAIL.

Requiere `openpyxl` en el Python que ejecuta datos y las dependencias existentes
de `backend/.venv`. No instala paquetes ni modifica el frontend.

Evidencias:

- `data/metadata/validation_report.json`: reconstrucción determinista,
  originales conservados y pruebas de datos.
- `docs/evidence/technical_verification.json`: resultado de las tres fases.
- `docs/evidence/api_verification.json`: casos verificados por HTTP real.

Solo HTTP, sin reconstruir datos ni ejecutar las suites:

```bash
python3 scripts/demo/verify_api.py --launch
```

Para comprobar una API que ya está ejecutándose:

```bash
python3 scripts/demo/verify_api.py --base-url http://127.0.0.1:8000
```

El comando `--launch` crea y detiene su propio proceso Uvicorn, sin tocar
procesos existentes. No utiliza fixtures ni necesita Internet. No demuestra
funcionamiento del mapa, responsividad, exportación o recorrido de navegador;
esas pruebas corresponden a la sesión encargada del frontend.
