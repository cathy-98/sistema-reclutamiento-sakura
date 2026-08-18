# Módulo 3 - Endpoints de consulta por candidato

Este paquete es aditivo sobre el Módulo 3 ya instalado y validado.

## Archivos a reemplazar

Copiar sobre el proyecto:

- `Backend/app/candidatos/router.py`
- `Backend/app/candidatos/services.py`
- `Backend/app/candidatos/schemas.py`

No requiere migración SQL ni cambios de tablas.

## Endpoints disponibles

Los existentes se conservan. Se agregan:

- `GET /candidatos/{candidate_id}/perfil-completo`
- `GET /candidatos/{candidate_id}/habilidades`
- `GET /candidatos/{candidate_id}/estudios`
- `GET /candidatos/{candidate_id}/experiencias`
- `GET /candidatos/{candidate_id}/cursos`
- `GET /candidatos/{candidate_id}/direcciones`

Además se amplía el endpoint ya existente:

- `GET /candidatos/{candidate_id}/solicitudes`

con parámetros opcionales:

- `estado_id`
- `skip` (default 0)
- `limit` (default 100, máximo efectivo 500)

Todos requieren `CAN_VIEW`.

## Nota sobre GET /candidatos/{id}

`GET /candidatos/{candidate_id}` continúa devolviendo `CandidatoPerfilResponse`, que ya incluye los bloques anidados `direccion`, `habilidades`, `estudios`, `experiencias` y `cursos`.

`GET /candidatos/{candidate_id}/perfil-completo` se agrega como endpoint explícito/semántico para frontend y devuelve la misma ficha estructurada completa.

## Dirección

El modelo físico actual define una sola dirección por candidato mediante `UNIQUE(drcd_candidato_id)`. Por consistencia REST, `GET /candidatos/{id}/direcciones` devuelve una lista de cero o un elemento.

## Instalación

Después de reemplazar los archivos, si el backend está montado como volumen:

```powershell
docker compose restart backend
```

Si la imagen contiene el código:

```powershell
docker compose up -d --build
```

Verificar en Swagger:

`http://127.0.0.1:8000/docs`

Luego volver a ejecutar las suites ya validadas:

```powershell
pytest test/test_modulo3.py -v -x
python live/test_modulo3_live.py
```
