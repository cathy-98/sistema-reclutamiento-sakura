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
# NOTA: Esta ruta DEBE ir arriba de {usuario_id} para que no se confunda
@router.get("/roles", response_model=List[schemas.RolWithPermisosResponse])
def listar_roles_con_permisos(db: Session = Depends(get_db)):
    # Usamos joinedload para traer la relación muchos a muchos de permisos en una sola consulta limpia
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
# 3. Crear Usuario (POST /usuarios/)
# ==========================================
@router.post("/", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario_in: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Validar si el email ya existe
    email_existe = db.query(models.Usuario).filter(models.Usuario.usr_email == usuario_in.usr_email).first()
    if email_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )

    # Convertir a dict y hashear contraseña
    datos_usuario = usuario_in.model_dump()
    datos_usuario["usr_contrasena"] = hash_password(datos_usuario["usr_contrasena"])
    
    # Crear y guardar el nuevo usuario
    nuevo_usuario = models.Usuario(**datos_usuario)
    db.add(nuevo_usuario)
    db.commit()
    
    # En lugar de solo hacer db.refresh(), consultamos de nuevo el usuario cargando sus relaciones de inmediato
    usuario_completo = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos),
        joinedload(models.Usuario.area)
    ).filter(models.Usuario.usr_id == nuevo_usuario.usr_id).first()
    
    return usuario_completo


# ==========================================
# 4. Listar todos los Usuarios (GET /usuarios/)
# ==========================================
@router.get("/", response_model=List[schemas.UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Usamos joinedload para traer el rol y sus permisos de inmediato evitando queries lentas
    usuarios = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos)
    ).offset(skip).limit(limit).all()
    return usuarios


# ==========================================
# 5. Obtener SOLO Permisos de un Usuario (GET /usuarios/{usuario_id}/permisos)
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
# 6. Obtener un Usuario por ID (GET /usuarios/{id})
# ==========================================
@router.get("/{usuario_id}", response_model=schemas.UsuarioResponse)
def obtener_usuario_por_id(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos)
    ).filter(models.Usuario.usr_id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )
    return usuario

# ==========================================
# 7. Actualizar Usuario Parcialmente (PATCH /usuarios/{usuario_id})
# ==========================================
@router.patch("/{usuario_id}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(
    usuario_id: int, 
    usuario_update: schemas.UsuarioUpdate, 
    db: Session = Depends(get_db)
):
    # Buscamos al usuario con sus relaciones listas para la respuesta final
    usuario = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol).joinedload(models.Rol.permisos),
        joinedload(models.Usuario.area)
    ).filter(models.Usuario.usr_id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )
    
    # Extraemos solo los campos que el frontend envió en la petición (excluyendo los Nulos)
    datos_actualizados = usuario_update.model_dump(exclude_unset=True)
    
    # Si viene contraseña nueva, la hasheamos antes de guardarla
    if "usr_contrasena" in datos_actualizados and datos_actualizados["usr_contrasena"]:
        datos_actualizados["usr_contrasena"] = hash_password(datos_actualizados["usr_contrasena"])
        
    # Si viene un correo nuevo, validamos que no esté duplicado en otra cuenta
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

    # Aplicamos los cambios dinámicamente en el modelo
    for campo, valor in datos_actualizados.items():
        setattr(usuario, campo, valor)
        
    db.commit()
    db.refresh(usuario)
    return usuario


# ==========================================
# 8. Eliminar Usuario - Baja Lógica (DELETE /usuarios/{usuario_id})
# ==========================================
@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.usr_id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado."
        )
    
    # Cambiamos su estado a "Eliminado" (ID 4 de acuerdo a tus estados oficiales)
    usuario.usr_estado_usuario_id = 4
    db.commit()
    
    return {
        "ok": True,
        "message": f"Usuario con ID {usuario_id} ha sido dado de baja lógicamente (Estado: Eliminado)."
    }