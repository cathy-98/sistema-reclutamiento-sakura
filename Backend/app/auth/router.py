from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import schemas, utils
from app.auth.dependencies import ACTIVE_USER_STATUS_NAME, get_current_user
from app.auth.email_service import (
    EmailConfigurationError,
    EmailDeliveryError,
    send_password_reset_email,
)
from app.auth.password_reset_service import (
    GENERIC_FORGOT_PASSWORD_MESSAGE,
    ExpiredPasswordResetTokenError,
    InvalidPasswordResetTokenError,
    PasswordResetError,
    create_password_reset_token,
    find_active_user_by_email,
    reset_password_with_token,
    revoke_all_pending_tokens_for_user,
    revoke_token_after_delivery_failure,
)
from app.database import get_db
from app.usuarios.models import Usuario


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    payload: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    usuario = db.scalar(
        select(Usuario)
        .options(selectinload(Usuario.estado), selectinload(Usuario.rol))
        .where(Usuario.usr_email == str(payload.email))
    )

    if usuario is None or not utils.verify_password(
        payload.password,
        usuario.usr_contrasena,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    estado_nombre = usuario.estado.esusr_nombre if usuario.estado else None
    if not estado_nombre or estado_nombre.casefold() != ACTIVE_USER_STATUS_NAME.casefold():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo, bloqueado o eliminado",
        )

    token = utils.create_access_token(
        {
            "sub": str(usuario.usr_id),
            "email": usuario.usr_email,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": utils.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/me", response_model=schemas.AuthMeResponse)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: schemas.ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not utils.verify_password(
        payload.password_actual,
        current_user.usr_contrasena,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual no es correcta",
        )

    if payload.password_actual == payload.password_nueva:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser distinta de la actual",
        )

    current_user.usr_contrasena = utils.hash_password(payload.password_nueva)
    revoke_all_pending_tokens_for_user(db, current_user.usr_id, commit=False)
    db.commit()
    return None


@router.post(
    "/forgot-password",
    response_model=schemas.ForgotPasswordResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def forgot_password(
    payload: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Solicita un correo de recuperación.

    Por seguridad, la respuesta es idéntica si el correo no existe,
    si la cuenta no está activa o si el usuario no es recuperable.
    """

    email = str(payload.email)
    usuario = find_active_user_by_email(db, email)

    if usuario is None:
        return {"message": GENERIC_FORGOT_PASSWORD_MESSAGE}

    raw_token, expiration_minutes = create_password_reset_token(db, usuario)

    try:
        send_password_reset_email(
            to_email=usuario.usr_email,
            token=raw_token,
            expiration_minutes=expiration_minutes,
        )
    except (EmailConfigurationError, EmailDeliveryError):
        # Un token cuyo correo no fue entregado no debe quedar utilizable.
        # La respuesta sigue siendo genérica para no permitir enumeración de usuarios.
        revoke_token_after_delivery_failure(db, raw_token)
        logger.exception("Falló el envío del correo de recuperación de contraseña")

    return {"message": GENERIC_FORGOT_PASSWORD_MESSAGE}


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def reset_password(
    payload: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        reset_password_with_token(
            db,
            token=payload.token,
            nueva_contrasena=payload.nueva_contrasena,
        )
    except ExpiredPasswordResetTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="El enlace de recuperación expiró. Solicita uno nuevo.",
        ) from exc
    except InvalidPasswordResetTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace de recuperación no es válido o ya fue utilizado.",
        ) from exc
    except PasswordResetError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return None
