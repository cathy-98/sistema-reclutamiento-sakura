from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.usuarios import models, schemas
from app.auth.utils import hash_password

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# ==========================================
# 1. Listar todos los Roles (GET /usuarios/roles)
# ==========================================
@router.get("/roles", response_model=List[schemas.RolWithPermisosResponse])
def listar_roles_con_permisos(db: Session = Depends(get_db)):
    roles = db.query(models.Rol).options(joinedload(models.Rol.permisos)).all()
    return roles


# ==========================================
# 2. Listar todos los Permisos (GET /usuarios/permisos)
# ==========================================
@router.get("/permisos", response_model=List[schemas.PermisoResponse])
def listar_permisos(db: Session = Depends(get_db)):
    permisos = db.query(models.Permiso).all()
    return permisos


# ==========================================
# 3. Listar todos los Estados de Usuario (GET /usuarios/estados)
# ==========================================
@router.get("/estados", response_model=List[schemas.EstadoUsuarioResponse])
def listar_estados_usuario(db: Session = Depends(get_db)):
    estados = db.query(models.EstadoUsuario).all()
    return estados


# ==========================================
# 4. Crear Usuario (POST /usuarios/)
# ==========================================
@router.post("/", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario_in: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    email_existe = db.query(models.Usuario).filter(models.Usuario.usr_email == usuario_in.usr_email).first()
    if email_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )

    datos_usuario = usuario_in.model_dump()
    datos_usuario["usr_contrasena"] = hash_password(datos_usuario["usr_contrasena"])
    
    nuevo_usuario = models.Usuario(**datos_usuario)
    db.add(nuevo_usuario)
    db.commit()
    
    usuario_completo = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos),
        joinedload(models.Usuario.area),
        joinedload(models.Usuario.estado)
    ).filter(models.Usuario.usr_id == nuevo_usuario.usr_id).first()
    
    return usuario_completo


# ==========================================
# 5. Listar todos los Usuarios (GET /usuarios/)
# ==========================================
@router.get("/", response_model=List[schemas.UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos),
        joinedload(models.Usuario.estado),
        joinedload(models.Usuario.area)
    ).offset(skip).limit(limit).all()
    return usuarios


# ==========================================
# 6. Obtener SOLO Permisos de un Usuario (GET /usuarios/{usuario_id}/permisos)
# ==========================================
@router.get("/{usuario_id}/permisos", response_model=List[str])
def obtener_permisos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos)
    ).filter(models.Usuario.usr_id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )
    
    if not usuario.rol:
        return []
        
    return [permiso.per_nombre for permiso in usuario.rol.permisos]


# ==========================================
# 7. Obtener un Usuario por ID (GET /usuarios/{id})
# ==========================================
@router.get("/{usuario_id}", response_model=schemas.UsuarioResponse)
def obtener_usuario_por_id(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos),
        joinedload(models.Usuario.estado),
        joinedload(models.Usuario.area)
    ).filter(models.Usuario.usr_id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )
    return usuario


# ==========================================
# 8. Actualizar Usuario Parcialmente (PATCH /usuarios/{usuario_id})
# ==========================================
@router.patch("/{usuario_id}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(
    usuario_id: int, 
    usuario_update: schemas.UsuarioUpdate, 
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos),
        joinedload(models.Usuario.area),
        joinedload(models.Usuario.estado)
    ).filter(models.Usuario.usr_id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )
    
    datos_actualizados = usuario_update.model_dump(exclude_unset=True)
    
    if "usr_contrasena" in datos_actualizados and datos_actualizados["usr_contrasena"]:
        datos_actualizados["usr_contrasena"] = hash_password(datos_actualizados["usr_contrasena"])
        
    if "usr_email" in datos_actualizados:
        email_existe = db.query(models.Usuario).filter(
            models.Usuario.usr_email == datos_actualizados["usr_email"],
            models.Usuario.usr_id != usuario_id
        ).first()
        if email_existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado por otro usuario."
            )

    for campo, valor in datos_actualizados.items():
        setattr(usuario, campo, valor)
        
    db.commit()
    db.refresh(usuario)
    return usuario


# ==========================================
# 9. Eliminar Usuario - Baja Lógica (DELETE /usuarios/{usuario_id})
# ==========================================
@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.usr_id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )
    
    usuario.usr_estado_usuario_id = 4
    db.commit()
    
    return {
        "ok": True,
        "message": f"Usuario con ID {usuario_id} ha sido dado de baja lógicamente (Estado: Eliminado)."
    }