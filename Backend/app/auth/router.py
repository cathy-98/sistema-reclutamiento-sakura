from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.usuarios.models import Usuario
from app.auth import schemas, utils

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.usr_email == payload.email).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # 2. Verificar la contraseña con hash
    if not utils.verify_password(payload.password, usuario.usr_contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
        
    # 3. Generar el JWT
    token_data = {
        "sub": usuario.usr_email,
        "usuario_id": usuario.usr_id,
        "rol_id": usuario.usr_role_id if hasattr(usuario, 'usr_role_id') else usuario.usr_rol_id
    }
    token = utils.create_access_token(data=token_data)
    
    return {"access_token": token, "token_type": "bearer"}