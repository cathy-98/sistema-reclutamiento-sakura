from __future__ import annotations

import os
from typing import Any

from sqlalchemy import func, inspect, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth.utils import hash_password
from app.auth.password_reset_service import revoke_all_pending_tokens_for_user
from app.usuarios import models, schemas


DELETED_USER_STATUS_NAME = os.getenv("DELETED_USER_STATUS_NAME", "Eliminado")


class UserModuleError(Exception):
    def __init__(self, message: str, *, constraint: str | None = None):
        super().__init__(message)
        self.message = message
        self.constraint = constraint


class NotFoundError(UserModuleError):
    pass


class ConflictError(UserModuleError):
    pass


class ValidationError(UserModuleError):
    pass


def _constraint_name(exc: IntegrityError) -> str | None:
    original = getattr(exc, "orig", None)
    diagnostic = getattr(original, "diag", None)
    return getattr(diagnostic, "constraint_name", None) if diagnostic else None


def _translate_integrity(exc: IntegrityError, *, deleting: bool = False) -> ConflictError:
    constraint = _constraint_name(exc)
    if deleting:
        message = "No se puede eliminar el registro porque está siendo utilizado por otros datos"
    elif constraint == "uq_tbl_usuario_email":
        message = "El correo electrónico ya está registrado"
    elif constraint == "uq_tbl_usuario_rut":
        message = "El RUT ya está registrado"
    else:
        message = "La operación viola una restricción de integridad o unicidad"
    return ConflictError(message, constraint=constraint)


def _commit(db: Session, *, deleting: bool = False) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _translate_integrity(exc, deleting=deleting) from exc


def _usuario_stmt():
    return select(models.Usuario).options(
        selectinload(models.Usuario.rol).selectinload(models.Rol.permisos),
        selectinload(models.Usuario.estado),
        selectinload(models.Usuario.area),
    )


def get_usuario(db: Session, usuario_id: int) -> models.Usuario:
    usuario = db.scalar(_usuario_stmt().where(models.Usuario.usr_id == usuario_id))
    if usuario is None:
        raise NotFoundError(f"Usuario con ID {usuario_id} no encontrado")
    return usuario


def list_usuarios(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    rol_id: int | None = None,
    estado_id: int | None = None,
    area_id: int | None = None,
) -> list[models.Usuario]:
    stmt = _usuario_stmt()
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                models.Usuario.usr_nombres.ilike(term),
                models.Usuario.usr_apellido_paterno.ilike(term),
                models.Usuario.usr_apellido_materno.ilike(term),
                models.Usuario.usr_email.ilike(term),
                models.Usuario.usr_rut_sin_dv.ilike(term),
            )
        )
    if rol_id is not None:
        stmt = stmt.where(models.Usuario.usr_rol_id == rol_id)
    if estado_id is not None:
        stmt = stmt.where(models.Usuario.usr_estado_usuario_id == estado_id)
    if area_id is not None:
        stmt = stmt.where(models.Usuario.usr_area_id == area_id)

    stmt = stmt.order_by(models.Usuario.usr_id.asc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).unique().all())


def _validate_refs(
    db: Session,
    *,
    rol_id: int | None,
    estado_id: int | None,
    area_id: int | None,
) -> None:
    if rol_id is not None and db.get(models.Rol, rol_id) is None:
        raise ValidationError(f"Rol {rol_id} no existe")
    if estado_id is not None and db.get(models.EstadoUsuario, estado_id) is None:
        raise ValidationError(f"Estado de usuario {estado_id} no existe")
    if area_id is not None and db.get(models.Area, area_id) is None:
        raise ValidationError(f"Área {area_id} no existe")


def _validate_rut_pair(rut: str | None, dv: str | None) -> None:
    if (rut is None) != (dv is None):
        raise ValidationError("usr_rut_sin_dv y usr_dv deben informarse juntos")




def _validate_email_not_candidate(db: Session, email: str | None) -> None:
    if not email or not inspect(db.get_bind()).has_table("tbl_candidato"):
        return
    from app.candidatos.models import Candidato
    exists = db.scalar(
        select(Candidato.cand_id)
        .where(func.lower(Candidato.cand_email) == email.strip().lower())
        .limit(1)
    )
    if exists is not None:
        raise ConflictError("El correo pertenece a un candidato y no puede utilizarse como usuario interno")

def create_usuario(db: Session, payload: schemas.UsuarioCreate) -> models.Usuario:
    data = payload.model_dump()
    _validate_email_not_candidate(db, data.get("usr_email"))
    _validate_refs(
        db,
        rol_id=data.get("usr_rol_id"),
        estado_id=data.get("usr_estado_usuario_id"),
        area_id=data.get("usr_area_id"),
    )
    _validate_rut_pair(data.get("usr_rut_sin_dv"), data.get("usr_dv"))
    data["usr_contrasena"] = hash_password(data["usr_contrasena"])
    usuario = models.Usuario(**data)
    db.add(usuario)
    _commit(db)
    db.refresh(usuario)
    return get_usuario(db, usuario.usr_id)


def replace_usuario(
    db: Session,
    usuario: models.Usuario,
    payload: schemas.UsuarioReplace,
) -> models.Usuario:
    data = payload.model_dump()
    _validate_email_not_candidate(db, data.get("usr_email"))
    _validate_refs(
        db,
        rol_id=data.get("usr_rol_id"),
        estado_id=data.get("usr_estado_usuario_id"),
        area_id=data.get("usr_area_id"),
    )
    _validate_rut_pair(data.get("usr_rut_sin_dv"), data.get("usr_dv"))
    for field, value in data.items():
        setattr(usuario, field, value)
    _commit(db)
    return get_usuario(db, usuario.usr_id)


def update_usuario(
    db: Session,
    usuario: models.Usuario,
    payload: schemas.UsuarioUpdate,
) -> models.Usuario:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo para actualizar")
    if "usr_email" in data:
        _validate_email_not_candidate(db, data.get("usr_email"))

    rol_id = data.get("usr_rol_id", usuario.usr_rol_id)
    estado_id = data.get("usr_estado_usuario_id", usuario.usr_estado_usuario_id)
    area_id = data.get("usr_area_id", usuario.usr_area_id)
    _validate_refs(db, rol_id=rol_id, estado_id=estado_id, area_id=area_id)

    final_rut = data.get("usr_rut_sin_dv", usuario.usr_rut_sin_dv)
    final_dv = data.get("usr_dv", usuario.usr_dv)
    _validate_rut_pair(final_rut, final_dv)

    for field, value in data.items():
        setattr(usuario, field, value)
    _commit(db)
    return get_usuario(db, usuario.usr_id)


def reset_password(db: Session, usuario: models.Usuario, new_password: str) -> None:
    usuario.usr_contrasena = hash_password(new_password)
    revoke_all_pending_tokens_for_user(db, usuario.usr_id, commit=False)
    _commit(db)


def soft_delete_usuario(db: Session, usuario: models.Usuario) -> None:
    estado = db.scalar(
        select(models.EstadoUsuario).where(
            models.EstadoUsuario.esusr_nombre.ilike(DELETED_USER_STATUS_NAME)
        )
    )
    if estado is None:
        raise ValidationError(
            f"No existe el estado '{DELETED_USER_STATUS_NAME}'. Cárguelo en tbl_estado_usuario"
        )
    usuario.usr_estado_usuario_id = estado.esusr_id
    _commit(db)


# ==========================================================
# CRUD GENÉRICO DE ROLES/PERMISOS/ÁREAS/ESTADOS
# ==========================================================

def list_roles(db: Session) -> list[models.Rol]:
    stmt = select(models.Rol).options(selectinload(models.Rol.permisos)).order_by(models.Rol.rol_id)
    return list(db.scalars(stmt).unique().all())


def get_rol(db: Session, rol_id: int) -> models.Rol:
    rol = db.scalar(
        select(models.Rol)
        .options(selectinload(models.Rol.permisos))
        .where(models.Rol.rol_id == rol_id)
    )
    if rol is None:
        raise NotFoundError(f"Rol con ID {rol_id} no encontrado")
    return rol


def create_rol(db: Session, payload: schemas.RolCreate) -> models.Rol:
    rol = models.Rol(**payload.model_dump())
    db.add(rol)
    _commit(db)
    return get_rol(db, rol.rol_id)


def update_rol(db: Session, rol: models.Rol, payload: schemas.RolUpdate) -> models.Rol:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo")
    for field, value in data.items():
        setattr(rol, field, value)
    _commit(db)
    return get_rol(db, rol.rol_id)


def delete_rol(db: Session, rol: models.Rol) -> None:
    # No se elimina un rol asignado a usuarios porque rompería la FK.
    usuario_asignado = db.scalar(
        select(models.Usuario.usr_id).where(models.Usuario.usr_rol_id == rol.rol_id).limit(1)
    )
    if usuario_asignado is not None:
        raise ConflictError("No se puede eliminar el rol porque está asignado a uno o más usuarios")

    # Las filas de tbl_rol_permiso son configuración del rol y pueden limpiarse antes del DELETE.
    rol.permisos = []
    _commit(db)
    db.delete(rol)
    _commit(db, deleting=True)


def list_permisos(db: Session) -> list[models.Permiso]:
    return list(db.scalars(select(models.Permiso).order_by(models.Permiso.per_id)).all())


def get_permiso(db: Session, permiso_id: int) -> models.Permiso:
    permiso = db.get(models.Permiso, permiso_id)
    if permiso is None:
        raise NotFoundError(f"Permiso con ID {permiso_id} no encontrado")
    return permiso


def create_permiso(db: Session, payload: schemas.PermisoCreate) -> models.Permiso:
    permiso = models.Permiso(**payload.model_dump())
    db.add(permiso)
    _commit(db)
    db.refresh(permiso)
    return permiso


def update_permiso(db: Session, permiso: models.Permiso, payload: schemas.PermisoUpdate) -> models.Permiso:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo")
    for field, value in data.items():
        setattr(permiso, field, value)
    _commit(db)
    db.refresh(permiso)
    return permiso


def delete_permiso(db: Session, permiso: models.Permiso) -> None:
    db.delete(permiso)
    _commit(db, deleting=True)


def replace_role_permissions(
    db: Session,
    rol: models.Rol,
    permiso_ids: list[int],
) -> models.Rol:
    if permiso_ids:
        permisos = list(
            db.scalars(select(models.Permiso).where(models.Permiso.per_id.in_(permiso_ids))).all()
        )
        found_ids = {p.per_id for p in permisos}
        missing = sorted(set(permiso_ids) - found_ids)
        if missing:
            raise ValidationError(f"Permisos inexistentes: {missing}")
    else:
        permisos = []

    rol.permisos = permisos
    _commit(db)
    return get_rol(db, rol.rol_id)


def add_role_permission(db: Session, rol: models.Rol, permiso: models.Permiso) -> models.Rol:
    if permiso not in rol.permisos:
        rol.permisos.append(permiso)
        _commit(db)
    return get_rol(db, rol.rol_id)


def remove_role_permission(db: Session, rol: models.Rol, permiso: models.Permiso) -> models.Rol:
    if permiso not in rol.permisos:
        raise NotFoundError("El permiso no está asignado al rol")
    rol.permisos.remove(permiso)
    _commit(db)
    return get_rol(db, rol.rol_id)


def _simple_create(db: Session, model, payload):
    obj = model(**payload.model_dump())
    db.add(obj)
    _commit(db)
    db.refresh(obj)
    return obj


def _simple_update(db: Session, obj, payload):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo")
    for field, value in data.items():
        setattr(obj, field, value)
    _commit(db)
    db.refresh(obj)
    return obj


def list_areas(db: Session) -> list[models.Area]:
    return list(db.scalars(select(models.Area).order_by(models.Area.area_id)).all())


def get_area(db: Session, area_id: int) -> models.Area:
    obj = db.get(models.Area, area_id)
    if obj is None:
        raise NotFoundError(f"Área con ID {area_id} no encontrada")
    return obj


def create_area(db: Session, payload: schemas.AreaCreate) -> models.Area:
    return _simple_create(db, models.Area, payload)


def update_area(db: Session, obj: models.Area, payload: schemas.AreaUpdate) -> models.Area:
    return _simple_update(db, obj, payload)


def delete_area(db: Session, obj: models.Area) -> None:
    """
    Elimina un área únicamente si no está asignada a ningún usuario.

    La validación se realiza explícitamente antes del DELETE para que el
    comportamiento sea consistente tanto en PostgreSQL como en SQLite de
    pruebas. No dependemos de que la FK o SQLAlchemy intenten poner el valor
    en NULL de manera implícita.
    """
    usuario_asignado = db.scalar(
        select(models.Usuario.usr_id)
        .where(models.Usuario.usr_area_id == obj.area_id)
        .limit(1)
    )

    if usuario_asignado is not None:
        raise ConflictError(
            "No se puede eliminar el área porque está asignada a uno o más usuarios"
        )

    db.delete(obj)
    _commit(db, deleting=True)


def list_estados(db: Session) -> list[models.EstadoUsuario]:
    return list(db.scalars(select(models.EstadoUsuario).order_by(models.EstadoUsuario.esusr_id)).all())


def get_estado(db: Session, estado_id: int) -> models.EstadoUsuario:
    obj = db.get(models.EstadoUsuario, estado_id)
    if obj is None:
        raise NotFoundError(f"Estado de usuario con ID {estado_id} no encontrado")
    return obj


def create_estado(db: Session, payload: schemas.EstadoUsuarioCreate) -> models.EstadoUsuario:
    return _simple_create(db, models.EstadoUsuario, payload)


def update_estado(db: Session, obj: models.EstadoUsuario, payload: schemas.EstadoUsuarioUpdate) -> models.EstadoUsuario:
    return _simple_update(db, obj, payload)


def delete_estado(db: Session, obj: models.EstadoUsuario) -> None:
    """
    Elimina un estado de usuario únicamente si no está asignado a ningún
    usuario. Esto protege los estados operacionales del sistema y devuelve un
    conflicto controlado (HTTP 409 desde el router) en lugar de permitir una
    eliminación inconsistente.
    """
    usuario_asignado = db.scalar(
        select(models.Usuario.usr_id)
        .where(models.Usuario.usr_estado_usuario_id == obj.esusr_id)
        .limit(1)
    )

    if usuario_asignado is not None:
        raise ConflictError(
            "No se puede eliminar el estado porque está asignado a uno o más usuarios"
        )

    db.delete(obj)
    _commit(db, deleting=True)
