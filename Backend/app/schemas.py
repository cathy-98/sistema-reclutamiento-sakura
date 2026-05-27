from pydantic import BaseModel, EmailStr

# Esquema para recibir los datos de inicio de sesión (se mantiene igual)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Esquema para responderle al frontend con el Token JWT
# Se cambia la clave 'nombre' por 'usuario' para ir en perfecta sintonía con la base de datos
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: str  # Adaptado de 'nombre' a 'usuario'
    rol: str