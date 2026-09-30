# Coordinación entre bloques

## Propósito

Evitar modificaciones cruzadas y mantener visibles estados, bloqueos y solicitudes de contrato.

## Estados

Cada bloque mantiene un único archivo en `status/`. Antes del primer reporte puede figurar `PENDIENTE DE REPORTE DEL BLOQUE`; una vez activo debe usar uno de los estados definidos por el Plan Maestro: `READY`, `IN_PROGRESS`, `BLOCKED_CONTRACT`, `BLOCKED_DATA`, `REVIEW` o `DONE`.

## Solicitudes

Si un bloque necesita un cambio propiedad de otro, crea un archivo en su propia carpeta `requests/from_block_N/` con nombre `REQ-AAAA-MM-DD-descripcion.md`. Debe incluir bloque solicitante, bloque propietario, contrato esperado, contrato recibido, ejemplo mínimo, impacto y cambio solicitado.

No se corrige directamente un archivo de otro bloque. El propietario responde, versiona su contrato y actualiza el estado correspondiente.
