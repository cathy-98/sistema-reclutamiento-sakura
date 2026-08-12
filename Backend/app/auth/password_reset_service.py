from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.auth import utils
from app.auth.models import PasswordResetToken
from app.auth.dependencies import ACTIVE_USER_STATUS_NAME
from app.usuarios.models import Usuario


GENERIC_FORGOT_PASSWORD_MESSAGE = (
    "Si el correo corresponde a una cuenta válida, recibirás instrucciones "
    "para restablecer tu contraseña."
)


class PasswordResetError(Exception):
    pass


class InvalidPasswordResetTokenError(PasswordResetError):
    pass


class ExpiredPasswordResetTokenError(PasswordResetError):
    pass


class PasswordResetConfigurationError(RuntimeError):
    pass


def _expiration_minutes() -> int:
    raw = (os.getenv("PASSWORD_RESET_EXPIRE_MINUTES") or "30").strip()
    if not raw:
        raw = "30"
    try:
        minutes = int(raw)
    except ValueError as exc:
        raise PasswordResetConfigurationError(
            "PASSWORD_RESET_EXPIRE_MINUTES debe ser un número entero"
        ) from exc
    if minutes < 5 or minutes > 1440:
        raise PasswordResetConfigurationError(
            "PASSWORD_RESET_EXPIRE_MINUTES debe estar entre 5 y 1440 minutos"
        )
    return minutes


def get_password_reset_expiration_minutes() -> int:
    return _expiration_minutes()


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_reset_token() -> str:
    return secrets.token_urlsafe(48)


def _is_active_user(usuario: Usuario) -> bool:
    estado_nombre = usuario.estado.esusr_nombre if usuario.estado else None
    return bool(
        estado_nombre
        and estado_nombre.casefold() == ACTIVE_USER_STATUS_NAME.casefold()
    )


def find_active_user_by_email(db: Session, email: str) -> Usuario | None:
    usuario = db.scalar(
        select(Usuario)
        .options(selectinload(Usuario.estado))
        .where(Usuario.usr_email == email)
    )
    if usuario is None or not _is_active_user(usuario):
        return None
    return usuario



def revoke_all_pending_tokens_for_user(
    db: Session,
    usuario_id: int,
    *,
    commit: bool = False,
) -> None:
    """Revoca todos los tokens de recuperación todavía utilizables del usuario."""
    now = datetime.now(timezone.utc)
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.prst_usuario_id == usuario_id,
            PasswordResetToken.prst_fecha_uso.is_(None),
            PasswordResetToken.prst_fecha_revocacion.is_(None),
        )
        .values(prst_fecha_revocacion=now)
    )
    if commit:
        db.commit()

def create_password_reset_token(
    db: Session,
    usuario: Usuario,
) -> tuple[str, int]:
    """
    Revoca tokens pendientes previos y crea uno nuevo.

    Retorna el token en texto plano únicamente para su envío por correo.
    La base de datos conserva solo SHA-256(token).
    """

    now = datetime.now(timezone.utc)
    expiration_minutes = _expiration_minutes()

    revoke_all_pending_tokens_for_user(db, usuario.usr_id, commit=False)

    raw_token = generate_reset_token()
    token_hash = hash_reset_token(raw_token)

    reset_record = PasswordResetToken(
        prst_usuario_id=usuario.usr_id,
        prst_token_hash=token_hash,
        prst_fecha_creacion=now,
        prst_fecha_expiracion=now + timedelta(minutes=expiration_minutes),
        prst_fecha_uso=None,
        prst_fecha_revocacion=None,
    )

    db.add(reset_record)
    db.commit()

    return raw_token, expiration_minutes


def revoke_token_after_delivery_failure(
    db: Session,
    token: str,
) -> None:
    token_hash = hash_reset_token(token)
    now = datetime.now(timezone.utc)

    record = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.prst_token_hash == token_hash
        )
    )
    if record is None:
        return

    record.prst_fecha_revocacion = now
    db.commit()


def reset_password_with_token(
    db: Session,
    *,
    token: str,
    nueva_contrasena: str,
) -> None:
    now = datetime.now(timezone.utc)
    token_hash = hash_reset_token(token)

    record = db.scalar(
        select(PasswordResetToken)
        .options(selectinload(PasswordResetToken.usuario))
        .where(PasswordResetToken.prst_token_hash == token_hash)
    )

    if record is None:
        raise InvalidPasswordResetTokenError(
            "El token de recuperación no es válido"
        )

    if record.prst_fecha_uso is not None or record.prst_fecha_revocacion is not None:
        raise InvalidPasswordResetTokenError(
            "El token de recuperación no es válido"
        )

    expiration = record.prst_fecha_expiracion
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)

    if expiration <= now:
        record.prst_fecha_revocacion = now
        db.commit()
        raise ExpiredPasswordResetTokenError(
            "El token de recuperación expiró"
        )

    usuario = record.usuario
    if usuario is None:
        raise InvalidPasswordResetTokenError(
            "El token de recuperación no es válido"
        )

    # Evita cambiar la clave de una cuenta que dejó de estar activa desde
    # que se solicitó el correo de recuperación.
    db.refresh(usuario, attribute_names=["estado"])
    if not _is_active_user(usuario):
        record.prst_fecha_revocacion = now
        db.commit()
        raise InvalidPasswordResetTokenError(
            "El token de recuperación no es válido"
        )

    if utils.verify_password(nueva_contrasena, usuario.usr_contrasena):
        raise PasswordResetError(
            "La nueva contraseña debe ser distinta de la contraseña actual"
        )

    usuario.usr_contrasena = utils.hash_password(nueva_contrasena)
    record.prst_fecha_uso = now

    # Invalida cualquier otro token todavía pendiente del mismo usuario.
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.prst_usuario_id == usuario.usr_id,
            PasswordResetToken.prst_id != record.prst_id,
            PasswordResetToken.prst_fecha_uso.is_(None),
            PasswordResetToken.prst_fecha_revocacion.is_(None),
        )
        .values(prst_fecha_revocacion=now)
    )

    db.commit()
