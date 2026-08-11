# QA Automatizada - Módulo 1 Usuarios y Accesos

## 1. Suite aislada con Pytest

Copiar `test/test_modulo1.py` dentro de `Backend/test/`.

La suite usa SQLite en memoria y reemplaza `get_db`, por lo que NO modifica PostgreSQL.

Ejecutar desde `Backend/`:

```powershell
pytest test/test_modulo1.py -v
```

Para detenerse en el primer fallo:

```powershell
pytest test/test_modulo1.py -v -x
```

Para ejecutar un grupo concreto:

```powershell
pytest test/test_modulo1.py -v -k login
pytest test/test_modulo1.py -v -k usuario
pytest test/test_modulo1.py -v -k rol
pytest test/test_modulo1.py -v -k permiso
pytest test/test_modulo1.py -v -k area
pytest test/test_modulo1.py -v -k estado
```

## 2. Cobertura

La suite valida:

- Login correcto.
- Password incorrecta -> 401.
- Usuario inexistente -> 401.
- Usuario inactivo -> 403.
- `/auth/me` sin token -> 401.
- Token inválido -> 401.
- Token expirado -> 401.
- Token válido -> 200.
- Cambio de password.
- RBAC con y sin permisos.
- CRUD completo de usuarios.
- Búsqueda y filtros de usuarios.
- Consulta de permisos de usuario.
- Reset de password.
- Baja lógica.
- Autoeliminación bloqueada -> 409.
- Duplicado de email -> 409.
- Duplicado de RUT -> 409.
- FK de rol/estado/área inexistente -> 422.
- PATCH vacío -> 422.
- CRUD completo de roles.
- Rol asignado a usuario no eliminable -> 409.
- CRUD completo de permisos.
- Asignar/reemplazar/quitar permisos de un rol.
- IDs de permiso inexistentes -> 422.
- IDs duplicados en permisos -> 422.
- CRUD completo de áreas.
- Área en uso no eliminable -> 409.
- CRUD completo de estados.
- Estado en uso no eliminable -> 409.
- Password corta -> 422.
- Email inválido -> 422.
- Campos extra -> 422.

## 3. Resultado esperado

Todos los tests deben terminar como `PASSED`.

Un resultado ideal termina con algo similar a:

```text
==================== 40+ passed in X.XXs ====================
```

El número exacto puede variar si se agregan nuevos casos.

## 4. Runner LIVE contra Docker/PostgreSQL

Archivo: `live/test_modulo1_live.py`.

Este runner valida la API real en `http://127.0.0.1:8000`. Requiere una cuenta Administrador válida.

PowerShell:

```powershell
$env:QA_ADMIN_EMAIL="tu-admin@dominio.cl"
$env:QA_ADMIN_PASSWORD="TuPasswordReal"
python live/test_modulo1_live.py
```

Si la API usa otra URL:

```powershell
$env:SAKURA_API_URL="http://localhost:8000"
```

El runner crea datos con identificadores QA únicos. Intenta limpiar roles, permisos, áreas y estados al terminar. Los usuarios se dejan asociados al estado `Eliminado` porque el API implementa baja lógica y no DELETE físico; por eso se recomienda ejecutar esta capa contra una BD Docker de QA/desarrollo, nunca contra producción.

Resultado esperado:

```text
[PASS] Login incorrecto -> 401
[PASS] Usuario inexistente -> 401
[PASS] Sin token /auth/me -> 401
...
RESULTADO: PASSED - Todos los casos live finalizaron correctamente.
```
