from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt


def _get_env_string(variable_name: str, default: str) -> str:
    value = os.getenv(variable_name)
    if value is None or not value.strip():
        return default
    return value.strip()


def _get_env_int(variable_name: str, default: int, minimum: int = 1) -> int:
    raw_value = os.getenv(variable_name)
    if raw_value is None or not raw_value.strip():
        return default
    try:
        value = int(raw_value.strip())
    except ValueError as exc:
        raise RuntimeError(
            f"La variable {variable_name} debe ser un número entero"
        ) from exc
    if value < minimum:
        raise RuntimeError(
            f"La variable {variable_name} debe ser mayor o igual a {minimum}"
        )
    return value


ALGORITHM = _get_env_string("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = _get_env_int(
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    60,
)


def _get_secret_key() -> str:
    value = os.getenv("JWT_SECRET_KEY")
    if value is None or not value.strip():
        raise RuntimeError(
            "JWT_SECRET_KEY no está configurada. "
            "Defínala como variable de entorno antes de iniciar la API."
        )

    value = value.strip()
    if len(value) < 32:
        raise RuntimeError("JWT_SECRET_KEY debe tener al menos 32 caracteres")
    return value


def validate_jwt_configuration() -> None:
    """Permite validar explícitamente la configuración durante startup."""
    _get_secret_key()
    _ = ALGORITHM
    _ = ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("La contraseña no puede estar vacía")

    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        raise ValueError(
            "La contraseña excede el máximo de 72 bytes permitido por bcrypt"
        )

    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode = data.copy()
    to_encode.update({"iat": now, "exp": expire})

    return jwt.encode(
        to_encode,
        _get_secret_key(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        _get_secret_key(),
        algorithms=[ALGORITHM],
    )
