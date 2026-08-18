# Módulo 1 - Usuarios y Accesos Administrativos

## Archivos a reemplazar

* `app/usuarios/models.py`
* `app/usuarios/schemas.py`
* `app/usuarios/router.py`
* `app/auth/utils.py`
* `app/auth/schemas.py`
* `app/auth/router.py`

## Archivos nuevos

* `app/usuarios/service.py`
* `app/auth/dependencies.py`

## main.py

No requiere un cambio de rutas si ya contiene:

```python
from app.auth import router as auth\_router
from app.usuarios import router as usuarios\_router

app.include\_router(auth\_router.router)
app.include\_router(usuarios\_router.router)
```

## Variables de entorno obligatorias

`JWT\_SECRET\_KEY` ya no tiene valor hardcodeado. Debe configurarse antes de iniciar la API.

PowerShell:

```powershell
$env:JWT\_SECRET\_KEY="reemplace-esto-por-un-secreto-muy-largo-y-aleatorio"
$env:JWT\_ALGORITHM="HS256"
$env:ACCESS\_TOKEN\_EXPIRE\_MINUTES="60"
```

Docker Compose, ejemplo:

```yaml
environment:
  JWT\_SECRET\_KEY: ${JWT\_SECRET\_KEY}
  JWT\_ALGORITHM: HS256
  ACCESS\_TOKEN\_EXPIRE\_MINUTES: 60
```

## Endpoints relevantes

* `POST /auth/login`
* `GET /auth/me`
* `POST /auth/change-password`
* CRUD de usuarios en `/usuarios/`
* reset administrativo en `/usuarios/{id}/reset-password`
* CRUD de roles `/usuarios/roles/...`
* CRUD de permisos `/usuarios/permisos/...`
* administración rol-permiso `/usuarios/roles/{rol\_id}/permisos`
* áreas `/usuarios/areas/...`
* estados `/usuarios/estados/...`

## Autorización

* `USR\_VIEW`: listar/consultar usuarios.
* `USR\_CREATE`: crear usuarios.
* `USR\_UPDATE`: editar usuarios y resetear contraseña.
* `USR\_DELETE`: baja lógica de usuarios.
* Solo rol `Administrador`: modificar roles, permisos, áreas, estados y asignaciones rol-permiso.

## Importante

Los permisos no se confían desde el JWT. Cada request protegido vuelve a consultar usuario, estado, rol y permisos en la base de datos. Si se quita un permiso a un rol, el cambio aplica inmediatamente al siguiente request.

