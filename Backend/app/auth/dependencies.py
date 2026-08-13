from __future__ import annotations

import os
from dataclasses import dataclass
from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session, selectinload

from app.auth.utils import decode_access_token
from app.database import get_db
from app.usuarios.models import Rol, Usuario


bearer_scheme = HTTPBearer(auto_error=False)

ACTIVE_USER_STATUS_NAME = os.getenv("ACTIVE_USER_STATUS_NAME", "Activo")
ADMIN_ROLE_NAME = os.getenv("ADMIN_ROLE_NAME", "Administrador")


def _unauthorized(detail: str = "Token inválido o expirado") -> HTTPException:
    return HTTPException(status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def _decode(credentials: HTTPAuthorizationCredentials | None) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Autenticación requerida")
    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("sub") is None:
            raise ValueError("Token sin subject")
        return payload
    except (jwt.PyJWTError, ValueError, TypeError) as exc:
        raise _unauthorized() from exc


def _load_user(db: Session, user_id: int) -> Usuario | None:
    return db.scalar(
        select(Usuario)
        .options(
            selectinload(Usuario.rol).selectinload(Rol.permisos),
            selectinload(Usuario.estado),
            selectinload(Usuario.area),
        )
        .where(Usuario.usr_id == user_id)
    )
                          


def _load_candidate(db: Session, candidate_id: int):
    if not inspect(db.get_bind()).has_table("tbl_candidato"):
        return None
    from app.candidatos.models import Candidato
    from app.candidatos.services import _candidate_stmt
    return db.scalar(_candidate_stmt().where(Candidato.cand_id == candidate_id))


def _ensure_active(entity, principal_type: str) -> None:
    estado = getattr(entity, "estado", None)
    name = getattr(estado, "esusr_nombre", None)
    if not name or name.casefold() != ACTIVE_USER_STATUS_NAME.casefold():
        label = "Usuario" if principal_type == "usuario" else "Candidato"
        raise HTTPException(status_code=403, detail=f"{label} inactivo, bloqueado o eliminado")


@dataclass
class AuthenticatedPrincipal:
    principal_type: str
    usuario: Usuario | None = None
    candidato: object | None = None


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthenticatedPrincipal:
    payload = _decode(credentials)
    principal_type = str(payload.get("principal_type") or "usuario").casefold()
    entity_id = int(payload["sub"])
    if principal_type == "usuario":
        user = _load_user(db, entity_id)
        if user is None:
            raise _unauthorized("Usuario asociado al token no existe")
        _ensure_active(user, "usuario")
        return AuthenticatedPrincipal("usuario", usuario=user)
    if principal_type == "candidato":
        candidate = _load_candidate(db, entity_id)
        if candidate is None:
            raise _unauthorized("Candidato asociado al token no existe")
        _ensure_active(candidate, "candidato")
        return AuthenticatedPrincipal("candidato", candidato=candidate)
    raise _unauthorized("Tipo de identidad no reconocido")

        
                                                              
                                    
                           
                                                 
                              
                                                   
                            
                                                     
                                                
                                                   
         

def get_current_user(principal: AuthenticatedPrincipal = Depends(get_current_principal)) -> Usuario:
    if principal.principal_type != "usuario" or principal.usuario is None:
        raise HTTPException(status_code=403, detail="Este recurso requiere una cuenta de usuario interno")
    return principal.usuario
                                                         
                                                   
         

                                                                     
                                                                           
                                                                                           
                            
                                                  
                                                             
         

def get_current_candidate(principal: AuthenticatedPrincipal = Depends(get_current_principal)):
    if principal.principal_type != "candidato" or principal.candidato is None:
        raise HTTPException(status_code=403, detail="Este recurso requiere una cuenta de candidato")
    return principal.candidato


                      
def get_current_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
             
    role_name = current_user.rol.rol_nombre if current_user.rol else None
    if not role_name or role_name.casefold() != ADMIN_ROLE_NAME.casefold():
                            
                                                  
        raise HTTPException(status_code=403, detail="Se requiere rol Administrador")
         
    return current_user


def require_permissions(*required_permissions: str, match_all: bool = True) -> Callable:
       
                 

            
                                                
                                                                                 
       
    required = {p.strip() for p in required_permissions if p.strip()}

    def dependency(current_user: Usuario = Depends(get_current_user)) -> Usuario:
                  
                              
        actual = {p.per_nombre for p in (current_user.rol.permisos if current_user.rol else [])}
         

                        
                               

        allowed = required.issubset(actual) if match_all else bool(required & actual)
        if required and not allowed:
            raise HTTPException(status_code=403, detail={"message":"Permisos insuficientes","required":sorted(required)})
                                                      
                        
                                                        
                                                 
                  
             
        return current_user

    return dependency
