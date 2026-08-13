# Criterio de mapeo e integracion

Este criterio aplica para todos los modulos del frontend que se conectan con backend/BD.

## Regla general

- Los modelos API y payloads deben usar la misma nomenclatura del backend/BD.
- Los modelos de pantalla pueden usar nombres mas simples, solo despues de mapear desde el service.
- Las funciones que integran o transforman datos deben quedar comentadas.

## Capas

- Backend/BD: nombres fisicos como `usr_email`, `sol_titulo`, `cand_nombres`, `ctev_fecha_hora_inicio`.
- Service/API: conserva esos nombres al enviar o recibir datos.
- Vista: puede usar `correo`, `nombre`, `fecha`, `estado`, siempre que venga desde una funcion de mapeo.

## Estado por modulo

| Modulo | Estado | Criterio aplicado |
| --- | --- | --- |
| Auth/Usuarios | Integrado | Consume `/auth/login` y `/usuarios/{id}` con campos `usr_*`; mapea a nombre/rol visible. |
| Catalogos | Integrado | Consume catalogos con prefijos reales como `crgo_*`, `prsol_*`, `essl_*`, `mdld_*`, `hab_*`. |
| Solicitudes | Integrado | Usa `SolicitudApi` y payloads con `sol_*`/`solhb_*`; mapea a `SolicitudResumen` para tabla. |
| Candidatos | Pendiente de endpoint | Se dejo `CandidatoApi` con campos `cand_*` como referencia fisica. |
| Entrevistas | Pendiente de endpoint | Se dejo `CitaEntrevistaApi` con campos `ctev_*` como referencia fisica. |
| Cuestionarios | Pendiente de endpoint | Se dejo `PreguntaApi`/`CuestionarioApi` con campos `preg_*`/`cues_*` como referencia fisica. |

## Ejemplo

```ts
// API / BD
solicitud.sol_titulo

// Pantalla
solicitudResumen.nombre
```

La traduccion debe vivir en el service:

```ts
// Mapeo API -> pantalla: traduce campos tecnicos sol_* a nombres legibles para la tabla.
private mapearSolicitudResumen(solicitud: SolicitudApi): SolicitudResumen {
  return {
    id: String(solicitud.sol_id),
    nombre: solicitud.sol_titulo || 'Sin nombre',
  };
}
```

## Definition of Done para una integracion

Una integracion se considera lista solo cuando pasa este ritual completo. La idea es encontrar los errores en la capa correcta antes de culpar a la pantalla o al backend completo.

### 1. Contrato claro

- Endpoint definido con metodo y ruta exacta, por ejemplo `GET /solicitudes` o `POST /clientes`.
- Payload documentado con nombres fisicos del backend/BD.
- Respuesta esperada documentada con un ejemplo real.
- Permisos requeridos identificados.
- Errores esperados identificados: `401`, `403`, `404`, `422`, `500`.

### 2. Backend probado de forma aislada

- Endpoint probado sin frontend, usando Swagger, Postman, test o comando directo.
- Token valido usado en la prueba si el endpoint requiere autenticacion.
- Migracion aplicada si la integracion depende de nuevas tablas, columnas, restricciones o datos base.
- Datos minimos disponibles en BD para probar el flujo feliz.
- Error `422` revisado contra el schema antes de cambiar codigo de frontend.

### 3. Service frontend conectado

- El service usa la ruta real del backend.
- El service envia payloads con nombres fisicos: `sol_*`, `cand_*`, `ctev_*`, `usr_*`, etc.
- El service no inventa datos que debe generar backend, como ids, codigos definitivos, fechas de auditoria o usuario creador.
- Los errores pasan por `obtenerMensajeError` o una utilidad equivalente.
- Durante desarrollo, el error se puede diagnosticar con status, ruta y detalle del backend.

### 4. Mapper implementado

- Existe funcion de mapeo API -> pantalla cuando la vista necesita nombres legibles.
- Existe funcion de mapeo pantalla -> API cuando un formulario envia datos.
- El mapper tolera valores opcionales o nulos cuando el backend puede devolverlos.
- No hay campos fisicos del backend repartidos innecesariamente en componentes HTML.
- Los comentarios explican transformaciones importantes, no asignaciones obvias.

### 5. Pantalla validada

- La pantalla muestra estado de carga.
- La pantalla muestra estado vacio cuando no hay datos.
- La pantalla muestra error entendible cuando falla la peticion.
- Formularios validan campos obligatorios antes de enviar.
- Botones de guardar/actualizar evitan doble envio mientras la peticion esta en curso.
- La pantalla no oculta errores del backend que sean utiles para corregir datos.

### 6. Flujo completo probado

- Flujo feliz probado desde la pantalla.
- Al menos un error controlado probado, por ejemplo sin permiso, campo obligatorio faltante o backend apagado.
- Se reviso en DevTools la request real: URL, metodo, payload, status y response.
- Se confirmo que la BD queda con el dato esperado despues de crear o editar.
- Si hay reglas de negocio, se probo al menos una regla que bloquee la accion.

### 7. Cierre tecnico

- No quedan `console.log` temporales con datos sensibles.
- No quedan rutas hardcodeadas fuera de la configuracion o proxy.
- No se mezclan nombres de pantalla con nombres fisicos en modelos API.
- La documentacion del modulo queda actualizada si cambia contrato, permiso, payload o flujo.
- El cambio compila y, cuando corresponde, tiene prueba automatizada o prueba manual registrada.

## Diagnostico rapido de errores

Cuando una integracion falle, revisar en este orden:

```text
1. Backend corriendo.
2. Ruta existente y metodo correcto.
3. Proxy frontend apuntando al backend correcto.
4. Token enviado y no expirado.
5. Permiso suficiente para la accion.
6. Payload coincide con schema backend.
7. Migracion aplicada y BD con columnas esperadas.
8. Mapper transforma en la direccion correcta.
9. Pantalla espera el mismo formato que entrega el mapper.
```

Si el error aparece en navegador, primero identificar la frontera exacta:

```text
Pantalla -> Service -> Proxy -> Router backend -> Schema -> Service backend -> BD
```

La correccion debe hacerse en la frontera donde nace el problema, no en la capa donde solamente se hace visible.
