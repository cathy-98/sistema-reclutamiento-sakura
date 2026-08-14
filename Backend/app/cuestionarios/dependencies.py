from __future__ import annotations

import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.utils import decode_access_token
from app.database import get_db


bearer_scheme_candidate = HTTPBearer(auto_error=False)
ACTIVE_USER_STATUS_NAME = os.getenv("ACTIVE_USER_STATUS_NAME", "Activo")


def get_current_candidate_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme_candidate),
    db: Session = Depends(get_db),
) -> int:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("principal_type") != "candidato":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este recurso requiere autenticación de candidato",
            )
        candidate_id = int(payload["sub"])
    except HTTPException:
        raise
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    row = db.execute(
        text(
            """
            SELECT c.cand_id, eu.esusr_nombre
              FROM tbl_candidato c
              LEFT JOIN tbl_estado_usuario eu
                ON eu.esusr_id = c.cand_estado_usuario_id
             WHERE c.cand_id = :candidate_id
            """
        ),
        {"candidate_id": candidate_id},
    ).mappings().first()

    if not row:
        raise HTTPException(status_code=401, detail="Candidato asociado al token no existe")
    if not row["esusr_nombre"] or row["esusr_nombre"].casefold() != ACTIVE_USER_STATUS_NAME.casefold():
        raise HTTPException(status_code=403, detail="Candidato inactivo, bloqueado o eliminado")

    return candidate_id
