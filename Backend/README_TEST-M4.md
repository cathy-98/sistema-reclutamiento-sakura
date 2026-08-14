
# QA LIVE Completo — Módulo 4 Sakura

Este runner valida M4 contra la API real y PostgreSQL real.

## Requisitos previos

1. Backend iniciado.
2. Migraciones M1-M4 aplicadas.
3. Suite aislada M4 completa en `PASSED`.
4. Usuario interno Administrador con permisos M4.
5. Candidato real activo con contraseña conocida.
6. Una solicitud real a la que ese candidato esté asociado.
7. La solicitud debe tener idealmente 2 o más candidatos para validar todos los casos masivos.

El runner reutiliza una pregunta válida existente del banco. No crea preguntas nuevas.

## Variables obligatorias

PowerShell:

```powershell
$env:SAKURA_API_URL="http://127.0.0.1:8000"

$env:QA_ADMIN_EMAIL="admin@dominio.cl"
$env:QA_ADMIN_PASSWORD="password-admin"

$env:QA_M4_CANDIDATE_EMAIL="candidato@dominio.cl"
$env:QA_M4_CANDIDATE_PASSWORD="password-candidato"

$env:QA_M4_SOLICITUD_ID="10"
```

`QA_M4_SOLICITUD_ID` debe corresponder a una solicitud a la que el candidato QA esté asociado.

## Variable opcional

Para comprobar LIVE la atomicidad cuando se intenta asignar un candidato que no pertenece a
la solicitud:

```powershell
$env:QA_M4_OUTSIDER_CANDIDATE_ID="99"
```

El ID informado debe existir, pero NO debe estar asociado a `QA_M4_SOLICITUD_ID`.

Si no se informa, ese único caso se marca `SKIP`; el resto continúa.

## Ejecutar

Desde `Backend`:

```powershell
python test/test_modulo4_live_completo.py
```

o desde la carpeta donde copie el archivo:

```powershell
python test_modulo4_live_completo.py
```

## Cobertura LIVE

### Seguridad
- API disponible.
- login administrador.
- login candidato.
- `principal_type=candidato`.
- 401 sin token.
- 403 al usar token interno en portal candidato.

### Banco / cuestionario
- lectura de pregunta real válida.
- creación de cuestionarios.
- asociación de pregunta existente.
- cálculo real de puntaje máximo y duración.

### Asignación individual
- candidato de la solicitud.
- estado `Asignado`.
- visibilidad en `candidatos-disponibles`.
- visibilidad en `/cuestionarios/me`.

### Portal candidato
- preguntas ocultas antes de iniciar.
- inicio y `fecha_inicio`.
- `En Progreso`.
- preguntas disponibles después de iniciar.
- no exposición de `opcr_es_correcta`.
- guardado progresivo.
- upsert.
- finalización.
- cálculo del resultado.
- resultado detallado interno.
- prohibición de reintento directo desde `Finalizado`.

### Asignación masiva
- candidatos de la solicitud.
- lista vacía -> 422.
- IDs duplicados -> 422.
- vencimiento pasado -> 422.
- asignación masiva válida.
- conflicto por ya asignado -> 409.
- candidato ajeno a solicitud -> 409, si se informa `QA_M4_OUTSIDER_CANDIDATE_ID`.

### Asignar todos
- preasignación individual.
- `asignar-todos`.
- omisión de ya asignado.
- creación exacta de pendientes.
- segunda ejecución sin duplicados.
- vencimiento pasado -> 422.

### Error técnico
- inicio.
- respuesta guardada.
- marcar `Error Tecnico`.
- habilitar reintento.
- limpieza del intento inválido.
- regreso a `Asignado`.
- nuevo inicio permitido.

## Datos creados

El runner deja los cuestionarios y asignaciones QA creados en PostgreSQL intencionalmente.
Esto facilita revisar las tablas y la trazabilidad después del test.

Todos los cuestionarios se identifican por nombres que comienzan con:

`QA LIVE M4`
