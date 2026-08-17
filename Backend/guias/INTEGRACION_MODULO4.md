# Integración Módulo 4 - Cuestionarios y Evaluaciones Técnicas

## Archivos a agregar

Copiar completa la carpeta:

`Backend/app/cuestionarios/`

Contiene `__init__.py`, `models.py`, `schemas.py`, `dependencies.py`, `services.py` y `router.py`.

No reemplaza archivos de M1, M2 ni M3.

## Registrar el router

En `Backend/app/main.py`, agregar junto a los demás imports:

```python
from app.cuestionarios.router import router as cuestionarios_router
```

Y junto a los `app.include_router(...)` existentes:

```python
app.include_router(cuestionarios_router)
```

No se entrega un `main.py` completo para no sobrescribir integraciones recientes ya validadas.

## Migración obligatoria

Copiar `migrations/005_modulo4_cuestionarios.sql` a la carpeta de migraciones del proyecto y ejecutar una vez:

```powershell
Get-Content -Raw .\migrations\005_modulo4_cuestionarios.sql | docker compose exec -T postgres_db psql -U elitsoft_admin -d db_reclutamiento_elitsoft
```

La migración:

- agrega `cdcu_fecha_inicio`;
- agrega `cdcu_fecha_vencimiento`;
- deja `cdcu_permitir_reintento` con `false` por defecto y NOT NULL;
- agrega unicidad candidato+cuestionario, pregunta+cuestionario y respuesta por pregunta/asignación;
- agrega índices;
- asigna `CUEST_CREATE` al rol cuyo nombre sea `Reclutador`, sin crear permisos nuevos.

Para datos históricos sin vencimiento se asigna, solo como compatibilidad inicial, `fecha_asignacion + 30 días`.

## Permisos

- `CUEST_CREATE`: preguntas, opciones, cuestionarios y composición.
- `CUEST_ASSIGN`: asignar/cancelar, Error Tecnico y reintento.
- `CUEST_VIEW`: consultas, asignaciones y resultados.

La autorización se basa en permisos, no en nombres de rol.

## Reglas implementadas

- M4 v1 usa exclusivamente selección simple.
- Una pregunta debe tener mínimo dos opciones y exactamente una correcta para incorporarse a un cuestionario.
- Puntaje = `tbl_nivel_habilidad.nvhb_puntaje_base`.
- Duración = `tbl_nivel_habilidad.nvhb_duracion`.
- Puntaje máximo y duración total se calculan dinámicamente; frontend no los envía.
- Un cuestionario pertenece a una Solicitud.
- Solo se asigna a un candidato asociado a esa misma Solicitud en `tbl_solicitud_candidato`.
- Estado inicial: `Asignado`.
- Candidato inicia: `Asignado -> En Progreso`; backend genera `cdcu_fecha_inicio`.
- Reclutador define `cdcu_fecha_vencimiento` al asignar.
- No iniciado al vencer: `Vencido`.
- Tiempo agotado después de iniciar: finalización automática con las respuestas guardadas.
- Respuestas se guardan progresivamente y pueden cambiarse mientras está En Progreso.
- Backend calcula correctitud, puntaje, porcentaje y `cdcu_aprobado`.
- Las respuestas del candidato nunca incluyen `opcr_es_correcta`.
- Un resultado técnico no modifica automáticamente el estado de postulación del candidato.
- El reintento solo se habilita desde `Error Tecnico`.
- Habilitar reintento exige una nueva fecha de vencimiento futura, borra respuestas del intento inválido y vuelve a `Asignado`.
- Reprobar normalmente no habilita reintento.
- Al existir una asignación, se congelan preguntas, opciones y composición para no cambiar puntaje/tiempo durante una evaluación.

## Endpoints

### Banco

- GET `/preguntas`
- POST `/preguntas`
- GET `/preguntas/{id}`
- PUT/PATCH `/preguntas/{id}`
- DELETE `/preguntas/{id}`
- GET `/preguntas/{id}/opciones`
- POST `/preguntas/{id}/opciones`
- PUT/PATCH `/preguntas/{id}/opciones/{opcion_id}`
- DELETE `/preguntas/{id}/opciones/{opcion_id}`

### Cuestionarios

- GET `/cuestionarios`
- POST `/cuestionarios`
- GET `/cuestionarios/{id}`
- PUT/PATCH `/cuestionarios/{id}`
- DELETE `/cuestionarios/{id}`
- GET `/cuestionarios/{id}/preguntas`
- POST `/cuestionarios/{id}/preguntas/{pregunta_id}`
- DELETE `/cuestionarios/{id}/preguntas/{pregunta_id}`
- POST `/cuestionarios/{id}/asignar`
- GET `/cuestionarios/{id}/resultados`

### Gestión interna

- GET `/asignaciones-cuestionario`
- GET `/asignaciones-cuestionario/{id}`
- POST `/asignaciones-cuestionario/{id}/cancelar`
- POST `/asignaciones-cuestionario/{id}/error-tecnico`
- POST `/asignaciones-cuestionario/{id}/habilitar-reintento`
- GET `/asignaciones-cuestionario/{id}/resultado`
- GET `/candidatos/{id}/cuestionarios`

`habilitar-reintento` recibe:

```json
{
  "fecha_vencimiento": "2026-08-20T23:59:59-04:00"
}
```

### Portal candidato

- GET `/cuestionarios/me`
- GET `/cuestionarios/me/{asignacion_id}`
- POST `/cuestionarios/me/{asignacion_id}/iniciar`
- GET `/cuestionarios/me/{asignacion_id}/preguntas`
- PUT `/cuestionarios/me/{asignacion_id}/respuesta`
- POST `/cuestionarios/me/{asignacion_id}/finalizar`

El `cand_id` se obtiene del JWT con `principal_type=candidato`.

## Respuesta progresiva

Ejemplo:

```json
{
  "pregunta_cuestionario_id": 15,
  "opcion_respuesta_id": 42
}
```

El backend valida que ambos IDs pertenezcan al cuestionario activo.

## Reinicio

```powershell
docker compose restart backend
```

Si la imagen no monta el código como volumen:

```powershell
docker compose up -d --build
```

Luego revisar `http://127.0.0.1:8000/docs`.
