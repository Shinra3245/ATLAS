# Limitaciones y responsabilidad

## Propósito

Explicar de forma visible qué no puede concluir ATLAS, bajo qué condiciones opera y qué responsabilidades conserva el usuario.

## Limitaciones verificadas de la implementación actual

- Solo Irapuato y Celaya, con 755 localidades censales. La asociación a un
  punto cercano no equivale a una medición del predio ni a un límite municipal.
- Datum del maestro pendiente: CRS_UNKNOWN. No se declara una reproyección.
- Población, servicios y altitud son datos de referencia 2020; los antecedentes
  de daño 2014 son históricos. No se presentan como observaciones actuales.
- Los 57 campos municipales son contexto con PARTIAL_DATA. Repetir un valor
  por localidad no produce resolución local.
- Faltan capas validadas de pendiente, fallas, laderas, inundación espacial y
  uso de suelo. Una serie de vegetación no acredita compatibilidad urbanística.
- La procedencia original, URL y licencias de las compilaciones siguen
  pendientes; los catálogos muestran SOURCE_PROVENANCE_PARTIAL.
- No hay umbrales profesionales validados, pruebas con usuarios documentadas
  ni ML activado. No se calcula una puntuación global o un ganador A/B.
- La API local no tiene autenticación ni despliegue público validado; el
  proceso debe reiniciarse tras cambios para renovar la caché del motor.
- La verificación técnica no certifica interfaz, accesibilidad móvil o respaldo
  cartográfico sin Internet; corresponden a la sesión de frontend.

La salida conserva el aviso de evaluación preliminar: no emite permisos,
dictámenes ni declaración de seguridad; ausencia de información no equivale
a ausencia de riesgo. La revisión legal detallada de DP-08 sigue pendiente.
