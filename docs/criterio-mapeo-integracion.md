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
