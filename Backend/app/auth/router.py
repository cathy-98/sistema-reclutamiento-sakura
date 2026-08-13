from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session, selectinload

from app.auth import schemas, utils
from app.auth.dependencies import ACTIVE_USER_STATUS_NAME, AuthenticatedPrincipal, get_current_principal
from app.auth.email_service import EmailConfigurationError, EmailDeliveryError, send_password_reset_email
                            
                       
                              
 
from app.auth.password_reset_service import (
    GENERIC_FORGOT_PASSWORD_MESSAGE, ExpiredPasswordResetTokenError,
                                   
    InvalidPasswordResetTokenError, PasswordResetError, create_password_reset_token,
                       
                                
    find_active_user_by_email, reset_password_with_token,
                              
                                       
    revoke_all_pending_tokens_for_user, revoke_token_after_delivery_failure,
)
from app.database import get_db
from app.usuarios.models import Usuario

logger=logging.getLogger(__name__)
router=APIRouter(prefix="/auth",tags=["Autenticación"])

                                    

def _active(entity)->bool:
    name=entity.estado.esusr_nombre if getattr(entity,"estado",None) else None
    return bool(name and name.casefold()==ACTIVE_USER_STATUS_NAME.casefold())

@router.post("/login",response_model=schemas.TokenResponse)
def login(payload:schemas.LoginRequest,db:Session=Depends(get_db)):
    email=str(payload.email).strip().lower()
    user=db.scalar(select(Usuario).options(selectinload(Usuario.estado),selectinload(Usuario.rol)).where(func.lower(Usuario.usr_email)==email))
    if user is not None:
        if not utils.verify_password(payload.password,user.usr_contrasena):
            raise HTTPException(status_code=401,detail="Credenciales incorrectas",headers={"WWW-Authenticate":"Bearer"})
        if not _active(user): raise HTTPException(status_code=403,detail="Usuario inactivo, bloqueado o eliminado")
        token=utils.create_access_token({"sub":str(user.usr_id),"email":user.usr_email,"principal_type":"usuario"})
        return {"access_token":token,"token_type":"bearer","expires_in":utils.ACCESS_TOKEN_EXPIRE_MINUTES*60,"principal_type":"usuario"}

    # Compatibilidad con las suites M1: si el esquema candidato no está presente, no se consulta.
    if inspect(db.get_bind()).has_table("tbl_candidato"):
        from app.candidatos.models import Candidato
                                  
  
        candidate=db.scalar(select(Candidato).options(selectinload(Candidato.estado)).where(func.lower(Candidato.cand_email)==email))
        if candidate is not None:
            if not utils.verify_password(payload.password,candidate.cand_password):
                raise HTTPException(status_code=401,detail="Credenciales incorrectas",headers={"WWW-Authenticate":"Bearer"})
            if not _active(candidate): raise HTTPException(status_code=403,detail="Candidato inactivo, bloqueado o eliminado")
            token=utils.create_access_token({"sub":str(candidate.cand_id),"email":candidate.cand_email,"principal_type":"candidato"})
            return {"access_token":token,"token_type":"bearer","expires_in":utils.ACCESS_TOKEN_EXPIRE_MINUTES*60,"principal_type":"candidato"}
    raise HTTPException(status_code=401,detail="Credenciales incorrectas",headers={"WWW-Authenticate":"Bearer"})

@router.get("/me")
def me(principal:AuthenticatedPrincipal=Depends(get_current_principal)):
    if principal.principal_type=="usuario":
        return schemas.AuthMeResponse.model_validate(principal.usuario)
    from app.candidatos.schemas import CandidatoPerfilResponse
    return {"principal_type":"candidato","candidato":CandidatoPerfilResponse.model_validate(principal.candidato)}
                                              
                                                   
         

@router.post("/change-password",status_code=204)
def change_password(payload:schemas.ChangePasswordRequest,principal:AuthenticatedPrincipal=Depends(get_current_principal),db:Session=Depends(get_db)):
    if principal.principal_type=="usuario":
        entity=principal.usuario; current_hash=entity.usr_contrasena
    else:
        entity=principal.candidato; current_hash=entity.cand_password
    if not utils.verify_password(payload.password_actual,current_hash):
        raise HTTPException(status_code=400,detail="La contraseña actual no es correcta")
    if payload.password_actual==payload.password_nueva:
        raise HTTPException(status_code=400,detail="La nueva contraseña debe ser distinta de la actual")
    new_hash=utils.hash_password(payload.password_nueva)
    if principal.principal_type=="usuario":
        entity.usr_contrasena=new_hash
        revoke_all_pending_tokens_for_user(db,entity.usr_id,commit=False)
    else:
        entity.cand_password=new_hash
    db.commit(); return None

@router.post("/forgot-password",response_model=schemas.ForgotPasswordResponse,status_code=202)
def forgot_password(payload:schemas.ForgotPasswordRequest,db:Session=Depends(get_db)):
    # Por ahora M1 mantiene la recuperación por correo solo para usuarios internos.
    user=find_active_user_by_email(db,str(payload.email))
    if user is None:return {"message":GENERIC_FORGOT_PASSWORD_MESSAGE}
    raw_token,minutes=create_password_reset_token(db,user)
    try: send_password_reset_email(to_email=user.usr_email,token=raw_token,expiration_minutes=minutes)
    except (EmailConfigurationError,EmailDeliveryError):
        revoke_token_after_delivery_failure(db,raw_token); logger.exception("Falló el envío del correo de recuperación")
    return {"message":GENERIC_FORGOT_PASSWORD_MESSAGE}


@router.post("/reset-password",status_code=204)
def reset_password(payload:schemas.ResetPasswordRequest,db:Session=Depends(get_db)):
    try: reset_password_with_token(db,token=payload.token,nueva_contrasena=payload.nueva_contrasena)
    except ExpiredPasswordResetTokenError as exc: raise HTTPException(status_code=410,detail="El enlace de recuperación expiró. Solicita uno nuevo.") from exc
    except InvalidPasswordResetTokenError as exc: raise HTTPException(status_code=400,detail="El enlace de recuperación no es válido o ya fue utilizado.") from exc
    except PasswordResetError as exc: raise HTTPException(status_code=400,detail=str(exc)) from exc
              
    return None
