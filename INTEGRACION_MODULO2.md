# Integración Módulo 2 - Solicitudes, Empresas y Clientes

## Archivos a reemplazar

- `Backend/app/main.py`
- `Backend/app/clientes/__init__.py`
- `Backend/app/clientes/models.py`
- `Backend/app/solicitudes/__init__.py`
- `Backend/app/solicitudes/models.py`
- `Backend/app/solicitudes/schemas.py`
- `Backend/app/solicitudes/services.py`
- `Backend/app/solicitudes/router.py`
- `Backend/app/listeners/solicitud_listeners.py`
- `base_inicial.sql` (para instalaciones nuevas)

## Archivos a agregar

- `Backend/app/clientes/schemas.py`
- `Backend/app/clientes/service.py`
- `Backend/app/clientes/router.py`
- `migrations/002_modulo2_codigo_solicitud.sql`

## Migración obligatoria en una base PostgreSQL ya existente

Reemplazar `base_inicial.sql` NO modifica un volumen PostgreSQL que ya fue inicializado.
Ejecute una sola vez:

```powershell
docker compose exec -T postgres_db psql -U elitsoft_admin -d db_reclutamiento_elitsoft < migrations/002_modulo2_codigo_solicitud.sql
```

Si PowerShell no admite la redirección de esa forma, use:

```powershell
Get-Content -Raw .\migrations\002_modulo2_codigo_solicitud.sql | docker compose exec -T postgres_db psql -U elitsoft_admin -d db_reclutamiento_elitsoft
```

Luego reinicie el backend:

```powershell
docker compose restart backend
```

## Decisiones funcionales implementadas

- Código generado por backend: `SOL-000001` ... `SOL-999999`.
- El cliente NO envía `sol_codigo`.
- El cliente NO envía `sol_usuario_creador_id`.
- El cliente NO envía `sol_fecha_creacion`.
- Toda solicitud se crea en estado `Pendiente`.
- Toda solicitud debe tener desde su creación al menos una habilidad excluyente.
- No se permite eliminar ni desmarcar la última habilidad excluyente.
- Empresas y clientes requieren `CAT_ADMIN` en todas sus operaciones.
- Solicitudes usan `SOL_CREATE`, `SOL_VIEW`, `SOL_UPDATE`, `SOL_DELETE`.
- `SOL_DELETE` se utiliza para transiciones terminales `Cancelado` y `Cerrado`.
- No existe DELETE físico de solicitudes en el API.
- Auditoría de cambio de estado registra el usuario JWT real.
- La regla adicional para `Cerrado` que exige candidato seleccionado/contratado queda pendiente para Módulo 3.
- `SolicitudCandidato` NO se completa en este módulo; solo se corrige su FK `tbl_candidato.cand_id` para mantener coherencia del mapper. Su implementación completa corresponde al Módulo 3.

## Flujo de estados implementado

- Pendiente -> En Curso, Cancelado
- En Curso -> En Entrevistas, Pausado, Cancelado
- En Entrevistas -> En Curso, Pausado, Cerrado, Cancelado
- Pausado -> En Curso, Cancelado
- Cerrado -> terminal
- Cancelado -> terminal

Para pasar a `En Curso`, la solicitud debe poseer:

- cliente;
- cargo;
- vacantes > 0;
- reclutador asignado activo;
- modalidad;
- tipo de contrato;
- al menos una habilidad excluyente.

`Pausado` y `Cancelado` exigen una observación.

## Endpoints agregados para Empresas

- GET `/clientes/empresas`
- POST `/clientes/empresas`
- GET `/clientes/empresas/{empresa_id}`
- PUT `/clientes/empresas/{empresa_id}`
- PATCH `/clientes/empresas/{empresa_id}`
- DELETE `/clientes/empresas/{empresa_id}`

## Endpoints agregados para Clientes

- GET `/clientes`
- POST `/clientes`
- GET `/clientes/{cliente_id}`
- PUT `/clientes/{cliente_id}`
- PATCH `/clientes/{cliente_id}`
- DELETE `/clientes/{cliente_id}`

## Endpoints principales de Solicitudes

- GET `/solicitudes`
- POST `/solicitudes`
- GET `/solicitudes/{solicitud_id}`
- PUT `/solicitudes/{solicitud_id}`
- PATCH `/solicitudes/{solicitud_id}`
- PATCH `/solicitudes/{solicitud_id}/estado`
- GET `/solicitudes/{solicitud_id}/habilidades`
- POST `/solicitudes/{solicitud_id}/habilidades`
- PATCH `/solicitudes/{solicitud_id}/habilidades/{habilidad_id}`
- DELETE `/solicitudes/{solicitud_id}/habilidades/{habilidad_id}`
- GET `/solicitudes/{solicitud_id}/historial`
- POST `/solicitudes/{solicitud_id}/evaluar-candidato`

El endpoint anterior `/solicitudes/{id}/desactivar` deja de utilizarse. La cancelación se realiza mediante el endpoint de cambio de estado.
