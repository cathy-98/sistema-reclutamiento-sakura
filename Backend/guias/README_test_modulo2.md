# QA Automatizada - Módulo 2 Sakura

Suite para validar **Empresas, Clientes y Solicitudes** después de integrar el Módulo 2.

## Archivos

- `test/test_modulo2.py`: integración aislada con SQLite + FastAPI TestClient. No toca PostgreSQL.
- `live/test_modulo2_live.py`: integración real contra Docker/FastAPI/PostgreSQL.
- `requirements-test-modulo2.txt`: dependencias adicionales de QA.

## Cobertura aislada

La suite valida:

- 401 sin JWT y 403 sin permisos.
- `CAT_ADMIN` para Empresas/Clientes.
- `SOL_CREATE`, `SOL_VIEW`, `SOL_UPDATE`, `SOL_DELETE`.
- CRUD completo de Empresa.
- CRUD completo de Cliente.
- búsqueda, filtros y paginación.
- duplicados y recursos en uso (`409`).
- referencias inválidas y payloads inválidos (`422`).
- creación de Solicitud en `Pendiente`.
- código automático `SOL-000001`, `SOL-000002`, etc.
- creador y fecha controlados por backend.
- obligación de al menos una habilidad excluyente.
- protección de la última habilidad excluyente.
- CRUD de relaciones Solicitud-Habilidad.
- filtros completos de Solicitudes.
- usuario asignado obligatorio con rol `Reclutador` y estado `Activo` cuando se informa.
- flujo de estados oficial.
- `Pausado` y `Cancelado` con observación obligatoria.
- estados `Cancelado`/`Cerrado` con `SOL_DELETE`.
- estados terminales.
- historial/auditoría con usuario real.
- evaluación de requisitos excluyentes.
- ausencia intencional de DELETE físico de Solicitud.

La regla **Cerrado requiere candidato seleccionado/contratado** no se prueba todavía porque quedó acordada para integrarse al finalizar Módulo 3.

## Ejecución aislada

Copie `test_modulo2.py` dentro de `Backend/test/` y ejecute desde `Backend`:

```powershell
pytest test/test_modulo2.py -v
```

Para detenerse en el primer fallo:

```powershell
pytest test/test_modulo2.py -v -x
```

## Ejecución LIVE

Requisitos previos:

1. Docker y PostgreSQL levantados.
2. Migración `002_modulo2_codigo_solicitud.sql` aplicada.
3. Backend disponible en `http://127.0.0.1:8000`.
4. Usuario administrador real con permisos de M0/M1/M2.
5. Al menos un usuario `Activo` con rol exacto `Reclutador`, o definir su ID manualmente.
6. Catálogos M0 con al menos Cargo, Prioridad, Modalidad, TipoContrato y Habilidad.

Configure PowerShell:

```powershell
$env:SAKURA_API_URL="http://127.0.0.1:8000"
$env:QA_ADMIN_EMAIL="admin@dominio.cl"
$env:QA_ADMIN_PASSWORD="PasswordReal"
```

Si el runner no puede descubrir un reclutador activo:

```powershell
$env:QA_RECRUITER_USER_ID="2"
```

Ejecute desde `Backend`:

```powershell
python live/test_modulo2_live.py
```

### Importante sobre LIVE

El runner genera una Solicitud real y al finalizar la deja en estado `Cancelado`. Esto es intencional porque el Módulo 2 no expone DELETE físico de solicitudes para preservar trazabilidad. El título, observación y RUN permiten identificar el registro como QA.

El runner sí elimina la Empresa y Cliente descartables utilizados exclusivamente para probar CRUD. Si no existe ningún Cliente previo en la BD y debe crear uno para la Solicitud, ese Cliente/Empresa quedará referenciado por la solicitud QA y no será eliminado.
