# Primera publicación de ATLAS · atlasgeo.click

## Distribución

Un Web Service Docker de Render entrega React compilado y FastAPI en el mismo
origen. Firebase conserva Authentication y Firestore. Hostinger conserva el
dominio y administra su DNS. No hace falta contratar hosting adicional en Hostinger.

Esta configuración usa una instancia de 512 MB y un worker. Los límites técnicos
del asistente están en memoria y se reinician al reiniciar el servicio. No son un
sistema de facturación ni sustituyen el control de presupuesto del proveedor de IA.
La selección de planes es una demostración gratuita; no hay pasarela de pago ni
cuotas comerciales verificadas en el servidor. No anunciar esta versión como un
servicio comercial con suscripciones activas.

## Preparación local

Desde la raíz de ATLAS:

```bash
python3 scripts/deploy/prepare_env.py
python3 scripts/deploy/build_local.py
docker run --rm --name atlasgeo-preview --memory=512m --cpus=0.5 -p 127.0.0.1:18080:10000 --env-file .deploy/render.env atlasgeo:deploy-check
```

`.deploy/render.env` contiene la configuración ya usada localmente. Es privado,
está excluido de Git y no se copia a la imagen. Las variables `VITE_FIREBASE_*`
son la configuración pública del SDK; `ANTHROPIC_API_KEY` solo pertenece al servidor.
Nunca poner esa clave en una variable `VITE_*`.

Los datos se obtienen de la release indicada en `deploy/data-release.json`.
El build verifica el SHA-256 del paquete; el arranque vuelve a comprobar hashes,
conteo y cobertura. Si falta un archivo o no coincide, se cancela el arranque.
El paquete solo contiene cinco JSON procesados; no incluye originales ni usuarios.

## Crear el servicio en Render

1. Conectar GitHub y autorizar solo `Shinra3245/ATLAS`.
2. Crear un **Blueprint**, seleccionar el repositorio y la rama
   `deploy/render-atlasgeo`. Render leerá `render.yaml`.
3. Completar las variables solicitadas con `.deploy/render.env`.
   `ATLAS_FIREBASE_PROJECT_ID` debe ser igual a `VITE_FIREBASE_PROJECT_ID`.
4. Revisar el precio mostrado antes de crear el servicio. Usar la instancia de
   pago de 512 MB para evitar la suspensión por inactividad. La memoria se debe
   revisar durante las pruebas; aumentar el tamaño si el uso real lo requiere.
5. Crear el servicio. La ruta de salud es `/api/ready` y debe devolver `ready`
   y 755 registros. El autodespliegue queda apagado para publicar cambios revisados.

También se puede crear un **Web Service** manual: misma rama, lenguaje **Docker**,
raíz vacía, Dockerfile `./Dockerfile`, región Virginia, ruta de salud `/api/ready`,
variables importadas con **Add from .env** y autodespliegue desactivado.
La compilación y el comando de inicio los define el Dockerfile.

## Firebase antes de compartir el enlace

Con una cuenta que tenga permiso de administración en el proyecto de
`VITE_FIREBASE_PROJECT_ID`:

1. Authentication → Settings → Authorized domains: añadir `atlasgeo.click`,
   `www.atlasgeo.click` y el host exacto `…onrender.com` asignado por Render.
   Mantener los dominios existentes.
2. Confirmar que Email/Password está habilitado.
3. Confirmar que Firestore existe y tiene las reglas de `firestore.rules`.
   Estas reglas permiten seleccionar planes de demostración. Antes de cobrar,
   reemplazar esa selección y el contador cliente por permisos y consumo del servidor.
4. Probar registro, inicio, cierre de sesión, selección de plan y recuperación.
   El envío de correo de recuperación se prueba manualmente con una cuenta propia.

La API verifica firma, audiencia, emisor y vigencia de los tokens Firebase en
análisis, comparación y asistente. Los catálogos son públicos. Esta verificación
no consulta revocación de tokens; un token ya emitido conserva su vigencia normal.

## Conectar atlasgeo.click en Hostinger

Primero probar la dirección `…onrender.com` del servicio.

1. En Render → Settings → Custom Domains, confirmar `atlasgeo.click`.
   Render añade la redirección de `www` y emite HTTPS automáticamente.
2. En Hostinger → Dominios → atlasgeo.click → DNS / Nameservers, guardar una
   copia de los registros actuales antes de editar los registros web.
3. Ajustar solo los registros siguientes, usando los valores que muestre Render:

| Tipo | Nombre | Destino |
| --- | --- | --- |
| A | @ | `216.24.57.1` (confirmar en Render al hacerlo) |
| CNAME | www | host exacto `…onrender.com`, sin `https://` |

Eliminar únicamente A/AAAA incompatibles de `@` o `www`, o redirecciones web que
entren en conflicto. Conservar MX, TXT de correo y verificaciones ajenas al sitio.
No cambiar nameservers para este procedimiento.
4. Volver a Render y verificar el dominio. Esperar DNS y emisión del certificado.
5. Comprobar `https://atlasgeo.click`, `https://www.atlasgeo.click` y
   `https://atlasgeo.click/api/ready`.

## Comprobación y recuperación

Recorrido mínimo: landing → registro/inicio → mapa → localidad → análisis →
fuentes → ficha → comparación con un plan de demostración que la permita →
asistente. Probar también desde móvil y una red distinta.

Comprobación automatizada del enlace público:

```bash
python3 scripts/deploy/smoke.py https://atlasgeo.click
```

`--auth` añade un registro temporal real de Firebase, análisis y comparación;
elimina esa cuenta al terminar y no crea documentos Firestore. `--assistant`
realiza además una consulta real al proveedor de IA y consume su cuota.

Confirmar las advertencias de cobertura en los resultados: desplegar no valida
las fuentes pendientes ni convierte el experimento histórico en riesgo actual.
Mapa, Firebase e IA dependen de proveedores externos; ninguna prueba garantiza
disponibilidad absoluta. Revisar los logs y el consumo de memoria de Render.

Para actualizar: probar una nueva revisión, subirla a la rama del servicio y
activar un despliegue manual. Para revertir: Render → Events → último deploy
correcto → Rollback. Mantener disponibles los paquetes de datos referidos por
revisiones anteriores; no sobrescribir una release que ya esté en uso.

## Referencias

- https://render.com/docs/docker
- https://render.com/docs/blueprint-spec
- https://render.com/docs/custom-domains
- https://render.com/docs/configure-other-dns
- https://www.hostinger.com/support/how-to-use-hostingers-dns-zone-editor/
- https://firebase.google.com/docs/auth/admin/verify-id-tokens
