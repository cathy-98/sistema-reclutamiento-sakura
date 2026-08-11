from __future__ import annotations

import os
from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.utils import decode_access_token
from app.database import get_db
from app.usuarios.models import Rol, Usuario


bearer_scheme = HTTPBearer(auto_error=False)

ACTIVE_USER_STATUS_NAME = os.getenv("ACTIVE_USER_STATUS_NAME", "Activo")
ADMIN_ROLE_NAME = os.getenv("ADMIN_ROLE_NAME", "Administrador")


def _load_user(db: Session, user_id: int) -> Usuario | None:
    stmt = (
        select(Usuario)
        .options(
            selectinload(Usuario.rol).selectinload(Rol.permisos),
            selectinload(Usuario.estado),
            selectinload(Usuario.area),
        )
        .where(Usuario.usr_id == user_id)
    )
    return db.scalar(stmt)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        if subject is None:
            raise ValueError("Token sin subject")
        user_id = int(subject)
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = _load_user(db, user_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario asociado al token no existe",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # La autorización consulta el estado REAL en BD en cada request.
    estado_nombre = usuario.estado.esusr_nombre if usuario.estado else None
    if not estado_nombre or estado_nombre.casefold() != ACTIVE_USER_STATUS_NAME.casefold():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo, bloqueado o eliminado",
        )

    return usuario


def get_current_admin(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    role_name = current_user.rol.rol_nombre if current_user.rol else None
    if not role_name or role_name.casefold() != ADMIN_ROLE_NAME.casefold():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol Administrador",
        )
    return current_user


def require_permissions(*required_permissions: str, match_all: bool = True) -> Callable:
    """
    Factory RBAC.

    Ejemplo:
        Depends(require_permissions("USR_VIEW"))
        Depends(require_permissions("USR_UPDATE", "USR_DELETE", match_all=False))
    """
    required = {permission.strip() for permission in required_permissions if permission.strip()}

    def dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        actual = {
            permiso.per_nombre
            for permiso in (current_user.rol.permisos if current_user.rol else [])
        }

        if not required:
            return current_user

        allowed = required.issubset(actual) if match_all else bool(required & actual)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Permisos insuficientes",
                    "required": sorted(required),
                },
            )
        return current_user

    return dependency
