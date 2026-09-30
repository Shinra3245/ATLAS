# Motor analítico

Directorio propiedad del Bloque 2 para reglas territoriales, comparación, explicabilidad y contratos del motor. El sistema debe funcionar sin Machine Learning.

Antes de implementar, leer `../docs/project/ATLAS_PLAN_MAESTRO.md` y `../docs/agents/ATLAS_BLOQUE_2_MOTOR_ANALITICO_ML.md`. Los cambios que dependan de Datos/SIG o Backend deben solicitarse mediante `../coordination/requests/`.

Estado: motor implementado, conectado a datos reales y probado; resultados
fechados en `../docs/evidence/technical_verification.json`. Contrato
publicado en `contracts/ENGINE_CONTRACT_V1.md` (+ `contracts/engine_result.schema.json`).

## Uso

```python
from engine import analyze_location, compare_locations
result = analyze_location({"lat": 20.674, "lon": -101.349}, "building").to_dict()
```

- Solo biblioteca estándar de Python; `pytest` solo para pruebas.
- Entorno local: `python3 -m venv engine/.venv && engine/.venv/bin/pip install -r engine/requirements-dev.txt`.
- Fuente de producción: `data/contracts/DATA_CONTRACT_V1.md` + `data/processed/v1/`
  (mientras no existan, los factores se reportan como información insuficiente o
  bloqueada, nunca como "riesgo bajo"). No se leen `data/incoming/**` ni `data/raw/**`.
- ML publica `HISTORICAL_EXPERIMENT` sobre daño por inundación en 2014 y no asigna una susceptibilidad. El análisis SIG funciona igual si ese bloque no se muestra.
- Las coordenadas se validan como finitas y dentro de rangos globales. Toda asociación aproximada al punto de una localidad incluye una nota que distingue localidad de predio.
- La clave explícita de localidad tiene prioridad: sus coordenadas canónicas se recuperan del contrato, sin interpretar coordenadas auxiliares como cobertura de un predio.
