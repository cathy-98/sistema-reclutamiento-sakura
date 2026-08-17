# Módulo 5 — Entrevistas (Backend completo)

Este paquete fue construido sobre `sistema-reclutamiento-sakura0.3.zip` y reutiliza las tablas existentes de entrevistas.

## Reglas implementadas

- La solicitud debe estar en estado `En Entrevistas` y la postulación en `En entrevista` para crear/modificar/evaluar entrevistas.
- Una cita puede tener múltiples tipos de entrevista.
- Cada tipo puede tener uno o más entrevistadores internos.
- Un mismo usuario puede participar en varios tipos de la misma cita.
- Todo entrevistador asignado debe estar activo y poseer `INT_EVALUATE`.
- El Reclutador recibe `INT_EVALUATE` mediante migración 006.
- Cada usuario registra su propia evaluación por tipo.
- Restricción lógica/física: una evaluación por `(cita, usuario, tipo)`.
- Las evaluaciones solo se permiten cuando la cita está `Realizada`.
- Las evaluaciones no cambian automáticamente el estado de `tbl_solicitud_candidato`.
- El candidato puede consultar agenda/histórico, pero nunca resultados ni observaciones de evaluación.
- Reprogramar conserva la misma cita y sus participantes.
- Cancelar/no-asistió no elimina físicamente la cita.
- El agendamiento masivo es transaccional/atómico.

## Archivos nuevos

- `Backend/app/entrevistas/__init__.py`
- `Backend/app/entrevistas/models.py`
- `Backend/app/entrevistas/schemas.py`
- `Backend/app/entrevistas/services.py`
- `Backend/app/entrevistas/router.py`
- `Backend/migrations/006_modulo5_entrevistas.sql`

## Archivo a reemplazar

- `Backend/app/main.py`

## Orden de instalación

1. Respaldar BD.
2. Ejecutar `Backend/migrations/006_modulo5_entrevistas.sql` en PostgreSQL/DBeaver.
3. Copiar `Backend/app/entrevistas/`.
4. Reemplazar `Backend/app/main.py`.
5. Reiniciar/reconstruir backend.
6. Revisar `/docs`.

### Docker

Si `Backend` está montado como volumen:

```powershell
docker compose restart backend
```

Si el código va dentro de la imagen:

```powershell
docker compose up -d --build
```

## Endpoints internos

- `POST /entrevistas`
- `POST /entrevistas/agendar-masivo`
- `GET /entrevistas`
- `GET /entrevistas/{id}`
- `PATCH /entrevistas/{id}`
- `PUT /entrevistas/{id}/participantes`
- `POST /entrevistas/{id}/confirmar`
- `POST /entrevistas/{id}/reprogramar`
- `POST /entrevistas/{id}/cancelar`
- `POST /entrevistas/{id}/no-asistio`
- `POST /entrevistas/{id}/realizar`
- `POST /entrevistas/{id}/tipos/{tipo_id}/evaluar`
- `PATCH /entrevistas/{id}/tipos/{tipo_id}/evaluacion`
- `GET /entrevistas/{id}/evaluaciones`
- `GET /entrevistas/me`
- `GET /solicitudes/{id}/entrevistas`
- `GET /candidatos/{id}/entrevistas`

## Portal candidato

- `GET /candidatos/me/entrevistas`
- `GET /candidatos/me/entrevistas/{id}`

Estos endpoints no serializan `resultado`, `observacion`, `usuario evaluador` ni ninguna evaluación interna.

## Permisos

- `INT_CREATE`: crear/agendar masivamente.
- `INT_VIEW`: listar/detalle/mis entrevistas/resultados internos.
- `INT_UPDATE`: editar convocatoria, participantes, confirmar, reprogramar, cancelar, no-asistió y realizar.
- `INT_EVALUATE`: crear/editar evaluación propia.

La existencia de `INT_EVALUATE` no basta para evaluar: el usuario además debe estar asignado a la cita para el tipo solicitado.

## Nota de compatibilidad

`tbl_cita_entrevista.ctev_tipo_entrevista_id` se conserva por compatibilidad con datos/frontend anteriores, pero M5 usa `tbl_cita_tipo_entrevista` como fuente de verdad para los múltiples tipos. M5 sincroniza el campo legado con el primer tipo configurado.

Las evaluaciones históricas pueden conservar `even_usuario_id/even_tipo_entrevista_id` nulos si no es posible inferir de forma segura su autor/tipo. Las nuevas evaluaciones M5 siempre contienen ambos datos.
