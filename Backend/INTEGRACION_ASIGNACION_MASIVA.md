
# Modulo 4 - Asignacion masiva de cuestionarios

## Archivos a reemplazar

Reemplace:

- Backend/app/cuestionarios/schemas.py
- Backend/app/cuestionarios/services.py
- Backend/app/cuestionarios/router.py

No hay migracion SQL nueva.

## Endpoints agregados

### GET /cuestionarios/{cuestionario_id}/candidatos-disponibles

Devuelve exclusivamente candidatos asociados a la solicitud del cuestionario.

Incluye:
- candidato;
- estado de su postulacion;
- si ya tiene el cuestionario;
- asignacion existente;
- estado del cuestionario.

Permiso:
- CUEST_ASSIGN o CUEST_VIEW.

### POST /cuestionarios/{cuestionario_id}/asignar-masivo

Ejemplo:

```json
{
  "candidato_ids": [25, 27, 31],
  "fecha_vencimiento": "2026-08-25T23:59:59-04:00"
}
```

Reglas:
- CUEST_ASSIGN.
- todos deben pertenecer a la solicitud del cuestionario;
- ninguno puede estar duplicado en el request;
- ninguno puede tener ya el cuestionario;
- fecha futura;
- cuestionario valido;
- operacion atomica: ante un error no se crea ninguna asignacion.

### POST /cuestionarios/{cuestionario_id}/asignar-todos

Ejemplo:

```json
{
  "fecha_vencimiento": "2026-08-25T23:59:59-04:00"
}
```

Asigna a todos los candidatos asociados a la solicitud.

Los candidatos que ya tienen ese cuestionario se omiten y se informan en:

`total_omitidos_ya_asignados`

## Respuesta masiva

La respuesta informa:

- cuestionario_id;
- solicitud_id;
- fecha_vencimiento;
- total_candidatos_solicitud;
- total_solicitados;
- total_asignados;
- total_omitidos_ya_asignados;
- asignaciones creadas.

## Asignacion individual

Se mantiene sin cambios:

POST /cuestionarios/{cuestionario_id}/asignar

La regla candidato-solicitud sigue siendo la misma.

## Reinicio

Si Backend esta montado como volumen:

```powershell
docker compose restart backend
```

Si requiere reconstruccion:

```powershell
docker compose up -d --build
```

Verifique los tres endpoints en /docs.
