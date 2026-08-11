from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import schemas, utils
from app.auth.dependencies import ACTIVE_USER_STATUS_NAME, get_current_user
from app.database import get_db
from app.usuarios.models import Rol, Usuario


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.scalar(
        select(Usuario)
        .options(selectinload(Usuario.estado), selectinload(Usuario.rol))
        .where(Usuario.usr_email == str(payload.email))
    )

    if usuario is None or not utils.verify_password(payload.password, usuario.usr_contrasena):
        # Mensaje genérico: evita revelar si el email existe.
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
    if not utils.verify_password(payload.password_actual, current_user.usr_contrasena):
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
    db.commit()
    return None
