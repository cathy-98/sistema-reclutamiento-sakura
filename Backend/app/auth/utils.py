from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt


# ==========================================================
# UTILIDADES DE CONFIGURACIÓN
# ==========================================================

def _get_env_string(
    variable_name: str,
    default: str,
) -> str:
    """
    Obtiene una variable de entorno de texto.

    Si la variable:
    - no existe,
    - contiene "",
    - contiene solamente espacios,

    se utiliza el valor por defecto.

    Esto evita problemas típicos de Docker Compose cuando
    una variable es declarada pero llega vacía al contenedor.
    """

    value = os.getenv(variable_name)

    if value is None:
        return default

    value = value.strip()

    if not value:
        return default

    return value


def _get_env_int(
    variable_name: str,
    default: int,
    *,
    minimum: int = 1,
) -> int:
    """
    Obtiene una variable de entorno numérica de forma segura.

    Evita errores como:

        ValueError: invalid literal for int() with base 10: ''

    que ocurre cuando Docker envía una variable vacía.
    """

    raw_value = os.getenv(variable_name)

    if raw_value is None:
        return default

    raw_value = raw_value.strip()

    if not raw_value:
        return default

    try:

        value = int(raw_value)

    except ValueError as exc:

        raise RuntimeError(
            f"La variable {variable_name} debe ser un número entero. "
            f"Valor recibido: {raw_value!r}"
        ) from exc

    if value < minimum:

        raise RuntimeError(
            f"La variable {variable_name} debe ser mayor o igual "
            f"a {minimum}. Valor recibido: {value}"
        )

    return value


# ==========================================================
# CONFIGURACIÓN JWT
# ==========================================================

ALGORITHM = _get_env_string(
    "JWT_ALGORITHM",
    "HS256",
)


ACCESS_TOKEN_EXPIRE_MINUTES = _get_env_int(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    60,
    minimum=1,
)


# ==========================================================
# JWT SECRET
# ==========================================================

def _get_secret_key() -> str:
    """
    Obtiene la clave utilizada para firmar los JWT.

    La clave nunca se almacena directamente en el código.
    Debe provenir de una variable de entorno.
    """

    value = os.getenv(
        "JWT_SECRET_KEY"
    )

    if value is None:

        raise RuntimeError(
            "JWT_SECRET_KEY no está configurada. "
            "Defínala en el archivo .env utilizado por Docker."
        )

    value = value.strip()

    if not value:

        raise RuntimeError(
            "JWT_SECRET_KEY está vacía. "
            "Defínala en el archivo .env."
        )

    if len(value) < 32:

        raise RuntimeError(
            "JWT_SECRET_KEY debe tener al menos "
            "32 caracteres."
        )

    return value


# ==========================================================
# PASSWORD
# ==========================================================

def hash_password(
    password: str,
) -> str:
    """
    Genera un hash BCrypt.

    Nunca almacena passwords en texto plano.
    """

    if not password:

        raise ValueError(
            "La contraseña no puede estar vacía"
        )

    encoded = password.encode(
        "utf-8"
    )

    # BCrypt procesa como máximo 72 bytes.
    if len(encoded) > 72:

        raise ValueError(
            "La contraseña excede el máximo "
            "de 72 bytes permitido por bcrypt"
        )

    hashed = bcrypt.hashpw(
        encoded,
        bcrypt.gensalt(),
    )

    return hashed.decode(
        "utf-8"
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verifica una contraseña exclusivamente mediante BCrypt.

    Por seguridad NO se compara nunca:

        plain_password == hashed_password
    """

    if (
        not plain_password
        or not hashed_password
    ):
        return False

    try:

        return bcrypt.checkpw(
            plain_password.encode(
                "utf-8"
            ),
            hashed_password.encode(
                "utf-8"
            ),
        )

    except (
        ValueError,
        TypeError,
    ):

        return False


# ==========================================================
# JWT
# ==========================================================

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Genera el token JWT.
    """

    now = datetime.now(
        timezone.utc
    )

    expire = now + (
        expires_delta
        or timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode = data.copy()

    to_encode.update(
        {
            "iat": now,
            "exp": expire,
        }
    )

    return jwt.encode(
        to_encode,
        _get_secret_key(),
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict[str, Any]:
    """
    Valida:

    - Firma JWT.
    - Fecha de expiración.
    - Algoritmo permitido.

    Si el token no es válido, PyJWT genera la excepción
    correspondiente y dependencies.py la convierte a HTTP 401.
    """

    return jwt.decode(
        token,
        _get_secret_key(),
        algorithms=[
            ALGORITHM
        ],
    )