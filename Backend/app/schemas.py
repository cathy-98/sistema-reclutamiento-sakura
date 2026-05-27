from pydantic import BaseModel, EmailStr

# Esquema para recibir los datos de inicio de sesión
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Esquema para responderle al frontend con el Token JWT
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    nombre: str
    rol: str