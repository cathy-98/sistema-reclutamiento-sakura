# Integración - Recuperación de contraseña con Gmail

## Archivos a agregar

- `Backend/app/auth/models.py`
- `Backend/app/auth/email_service.py`
- `Backend/app/auth/password_reset_service.py`

## Archivos a reemplazar

- `Backend/app/auth/router.py`
- `Backend/app/auth/schemas.py`
- `Backend/app/auth/utils.py`
- `Backend/app/usuarios/service.py`

## Base de datos

Ejecutar desde la raíz del proyecto:

```powershell
Get-Content -Raw .\migrations\003_password_reset_gmail.sql | docker compose exec -T postgres_db psql -U elitsoft_admin -d db_reclutamiento_elitsoft
```

## Variables de entorno

Agregar al `.env` utilizado por Docker:

```env
PASSWORD_RESET_EXPIRE_MINUTES=30
FRONTEND_RESET_PASSWORD_URL=http://localhost:4200/reset-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=cuenta.gmail@gmail.com
SMTP_PASSWORD=APP_PASSWORD_DE_GMAIL
SMTP_FROM_EMAIL=cuenta.gmail@gmail.com
SMTP_FROM_NAME=Sakura Reclutamiento
SMTP_USE_TLS=true
SMTP_TIMEOUT_SECONDS=15
```

`SMTP_PASSWORD` debe ser una App Password de Google asociada a la cuenta que enviará los correos.

No subir `.env` al repositorio.

## Docker

Asegurarse de que el servicio backend cargue el `.env`, por ejemplo:

```yaml
env_file:
  - .env
```

Después reiniciar el backend:

```powershell
docker compose restart backend
```

Si el backend no usa un volumen y los archivos se copian durante build:

```powershell
docker compose up -d --build
```

## Endpoints nuevos

### Solicitar recuperación

`POST /auth/forgot-password`

```json
{
  "email": "usuario@dominio.cl"
}
```

Respuesta normal:

```http
202 Accepted
```

```json
{
  "message": "Si el correo corresponde a una cuenta válida, recibirás instrucciones para restablecer tu contraseña."
}
```

La misma respuesta se entrega cuando el usuario no existe o no está activo.

### Establecer nueva contraseña

`POST /auth/reset-password`

```json
{
  "token": "TOKEN_RECIBIDO_EN_EL_ENLACE",
  "nueva_contrasena": "NuevaPassword123!"
}
```

Respuesta exitosa:

```http
204 No Content
```

## Comportamiento de seguridad

- El token original nunca se almacena en PostgreSQL.
- Se guarda únicamente `SHA-256(token)`.
- El token es de un solo uso.
- Al generar un token nuevo se revocan los anteriores pendientes del usuario.
- Un token expirado no puede usarse.
- Si falla el envío Gmail, el token generado queda revocado y el error queda en logs; la respuesta HTTP permanece genérica para evitar enumeración de usuarios.
- Un cambio de contraseña propio o un reset administrativo revoca todos los enlaces de recuperación pendientes del usuario.
- Solo usuarios con estado `Activo` reciben recuperación.
- La respuesta de `/forgot-password` no revela si un correo existe.
- La nueva contraseña se guarda con bcrypt.

## Frontend

El correo contendrá una URL como:

```text
http://localhost:4200/reset-password?token=XXXX
```

La pantalla Angular debe leer `token` desde query string y enviar luego:

```json
{
  "token": "XXXX",
  "nueva_contrasena": "NuevaPassword123!"
}
```

a `POST /auth/reset-password`.

## Nota sobre sesiones existentes

El cambio de contraseña no revoca Access Tokens JWT ya emitidos. Estos continuarán siendo válidos hasta su expiración. La revocación completa de sesiones debe integrarse cuando se implemente Refresh Token + Logout persistente.
