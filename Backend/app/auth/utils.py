from datetime import datetime, timedelta, timezone
from typing import Union

import bcrypt
import jwt

# 2. Configuración para la generación de JSON Web Tokens (JWT)
# En un entorno de producción real, estos valores deben ser leídos desde variables de entorno.
SECRET_KEY = "tu_super_secreto_para_el_token_ats_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ==========================================
# Funciones para manejo de Contraseñas
# ==========================================

def hash_password(password: str) -> str:
    """
    Recibe una contraseña en texto plano y retorna su representación hash Bcrypt.
    Ideal para guardar en la columna `usr_contrasena` de la tabla `tbl_usuario`.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara una contraseña en texto plano con el hash guardado en la base de datos.
    Retorna True si coinciden, False en caso contrario.
    """
    if plain_password == hashed_password:
        return True

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


# ==========================================
# Funciones para manejo de Tokens JWT
# ==========================================

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    Genera un token JWT firmado.
    Guarda la información del usuario (payload) y le define un tiempo de expiración.
    """
    to_encode = data.copy()
    
    # Calcular tiempo de expiración del token (Por defecto 60 minutos)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    # Añadir el tiempo de expiración ('exp') al payload del JWT
    to_encode.update({"exp": expire})
    
    # Firmar el token con nuestro secreto y algoritmo
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt