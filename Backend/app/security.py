import datetime
from typing import Dict, Any
import jwt
from passlib.context import CryptContext

# =====================================================================
# 1. ENCRIPCIÓN DE CONTRASEÑAS (BCRYPT)
# =====================================================================
# CryptContext configura passlib para usar bcrypt como algoritmo de hasheo.
# Esto asegura que las contraseñas nunca se guarden en texto plano en la BD.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verificar_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Compara una contraseña en texto plano con el Hash criptográfico almacenado.
#     Retorna True si coinciden, de lo contrario False.
#     """
#     return pwd_context.verify(plain_password, hashed_password)

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password == hashed_password:
        return True

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def obtener_password_hash(password: str) -> str:
    """
    Toma una contraseña en texto plano y genera su Hash seguro usando Bcrypt.
    Útil para registrar nuevos usuarios o inyectar datos de prueba (seeders).
    """
    return pwd_context.hash(password)


# =====================================================================
# 2. CONFIGURACIÓN DE TOKENS JWT (JSON Web Tokens)
# =====================================================================
# CLAVE_SECRETA: Firma el token para que nadie pueda alterarlo en el camino.
# En producción, esta clave debe ser compleja y cargarse desde variables de entorno.
SECRET_KEY = "EL_TESORO_DEL_PIRATA_ELITSOFT"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def crear_token_acceso(datos: Dict[str, Any]) -> str:
    """
    Genera un Token JWT firmado digitalmente.
    Inyecta los datos del usuario (Payload) y calcula la fecha de expiración del token.
    """
    # Creamos una copia del diccionario para evitar alterar los datos originales
    payload = datos.copy()
    
    # Definimos el tiempo de vida del Token (60 minutos por defecto)
    expiracion = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Añadimos la fecha de expiración estándar de JWT ("exp") al payload
    payload.update({"exp": expiracion})
    
    # Encriptamos y firmamos el token usando nuestro algoritmo y clave secreta
    token_firmado = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return token_firmado