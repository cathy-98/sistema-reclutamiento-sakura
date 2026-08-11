from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin, get_current_user, require_permissions
from app.database import get_db
from app.usuarios import models, schemas, service


router = APIRouter(prefix="/usuarios", tags=["Usuarios y Accesos"])


def _translate_error(exc: service.UserModuleError) -> HTTPException:
    if isinstance(exc, service.NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, service.ConflictError):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_422_UNPROCESSABLE_CONTENT

    detail: dict[str, object] = {"message": exc.message}
    if exc.constraint:
        detail["constraint"] = exc.constraint
    return HTTPException(status_code=code, detail=detail)


# ============================================================================
# IMPORTANTE SOBRE EL ORDEN DE RUTAS
# ============================================================================
# Las rutas estáticas (/roles, /permisos, /areas, /estados) se registran ANTES
# de /{usuario_id}. Así FastAPI no intenta interpretar "roles" como un entero.
# ============================================================================


# ==========================================================
# ROLES - ADMINISTRACIÓN
# ==========================================================

@router.get("/roles", response_model=list[schemas.RolRead])
def listar_roles(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    return service.list_roles(db)


@router.post("/roles", response_model=schemas.RolRead, status_code=status.HTTP_201_CREATED)
def crear_rol(
    payload: schemas.RolCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.create_rol(db, payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.get("/roles/{rol_id}", response_model=schemas.RolRead)
def obtener_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    try:
        return service.get_rol(db, rol_id)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/roles/{rol_id}", response_model=schemas.RolRead)
def reemplazar_rol(
    rol_id: int,
    payload: schemas.RolCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.update_rol(db, service.get_rol(db, rol_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/roles/{rol_id}", response_model=schemas.RolRead)
def actualizar_rol(
    rol_id: int,
    payload: schemas.RolUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.update_rol(db, service.get_rol(db, rol_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete("/roles/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        service.delete_rol(db, service.get_rol(db, rol_id))
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/roles/{rol_id}/permisos", response_model=list[schemas.PermisoRead])
def listar_permisos_rol(
    rol_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    try:
        return service.get_rol(db, rol_id).permisos
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/roles/{rol_id}/permisos", response_model=schemas.RolRead)
def reemplazar_permisos_rol(
    rol_id: int,
    payload: schemas.RolPermisosReplace,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.replace_role_permissions(
            db,
            service.get_rol(db, rol_id),
            payload.permiso_ids,
        )
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.post("/roles/{rol_id}/permisos/{permiso_id}", response_model=schemas.RolRead)
def agregar_permiso_rol(
    rol_id: int,
    permiso_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.add_role_permission(
            db,
            service.get_rol(db, rol_id),
            service.get_permiso(db, permiso_id),
        )
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete("/roles/{rol_id}/permisos/{permiso_id}", response_model=schemas.RolRead)
def quitar_permiso_rol(
    rol_id: int,
    permiso_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.remove_role_permission(
            db,
            service.get_rol(db, rol_id),
            service.get_permiso(db, permiso_id),
        )
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


# ==========================================================
# PERMISOS - ADMINISTRACIÓN
# ==========================================================

@router.get("/permisos", response_model=list[schemas.PermisoRead])
def listar_permisos(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    return service.list_permisos(db)


@router.post("/permisos", response_model=schemas.PermisoRead, status_code=status.HTTP_201_CREATED)
def crear_permiso(
    payload: schemas.PermisoCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.create_permiso(db, payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.get("/permisos/{permiso_id}", response_model=schemas.PermisoRead)
def obtener_permiso(
    permiso_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    try:
        return service.get_permiso(db, permiso_id)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/permisos/{permiso_id}", response_model=schemas.PermisoRead)
def reemplazar_permiso(
    permiso_id: int,
    payload: schemas.PermisoCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.update_permiso(db, service.get_permiso(db, permiso_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/permisos/{permiso_id}", response_model=schemas.PermisoRead)
def actualizar_permiso(
    permiso_id: int,
    payload: schemas.PermisoUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.update_permiso(db, service.get_permiso(db, permiso_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete("/permisos/{permiso_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_permiso(
    permiso_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        service.delete_permiso(db, service.get_permiso(db, permiso_id))
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================================
# ÁREAS
# ==========================================================

@router.get("/areas", response_model=list[schemas.AreaRead])
def listar_areas(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    return service.list_areas(db)


@router.post("/areas", response_model=schemas.AreaRead, status_code=status.HTTP_201_CREATED)
def crear_area(
    payload: schemas.AreaCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.create_area(db, payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.get("/areas/{area_id}", response_model=schemas.AreaRead)
def obtener_area(
    area_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    try:
        return service.get_area(db, area_id)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/areas/{area_id}", response_model=schemas.AreaRead)
def reemplazar_area(
    area_id: int,
    payload: schemas.AreaCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.update_area(db, service.get_area(db, area_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/areas/{area_id}", response_model=schemas.AreaRead)
def actualizar_area(
    area_id: int,
    payload: schemas.AreaUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.update_area(db, service.get_area(db, area_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_area(
    area_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        service.delete_area(db, service.get_area(db, area_id))
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================================
# ESTADOS DE USUARIO
# ==========================================================

@router.get("/estados", response_model=list[schemas.EstadoUsuarioRead])
def listar_estados(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    return service.list_estados(db)


@router.post("/estados", response_model=schemas.EstadoUsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_estado(
    payload: schemas.EstadoUsuarioCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.create_estado(db, payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.get("/estados/{estado_id}", response_model=schemas.EstadoUsuarioRead)
def obtener_estado(
    estado_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user),
):
    try:
        return service.get_estado(db, estado_id)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/estados/{estado_id}", response_model=schemas.EstadoUsuarioRead)
def reemplazar_estado(
    estado_id: int,
    payload: schemas.EstadoUsuarioCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.update_estado(db, service.get_estado(db, estado_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/estados/{estado_id}", response_model=schemas.EstadoUsuarioRead)
def actualizar_estado(
    estado_id: int,
    payload: schemas.EstadoUsuarioUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        return service.update_estado(db, service.get_estado(db, estado_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete("/estados/{estado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_estado(
    estado_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_admin),
):
    try:
        service.delete_estado(db, service.get_estado(db, estado_id))
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================================
# USUARIOS - COLECCIÓN
# ==========================================================

@router.get("/", response_model=list[schemas.UsuarioRead])
def listar_usuarios(
    q: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    rol_id: int | None = Query(default=None, ge=1),
    estado_id: int | None = Query(default=None, ge=1),
    area_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_permissions("USR_VIEW")),
):
    return service.list_usuarios(
        db,
        skip=skip,
        limit=limit,
        q=q,
        rol_id=rol_id,
        estado_id=estado_id,
        area_id=area_id,
    )


@router.post("/", response_model=schemas.UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    payload: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_permissions("USR_CREATE")),
):
    try:
        return service.create_usuario(db, payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


# ==========================================================
# USUARIOS - DETALLE
# ==========================================================

@router.get("/{usuario_id}/permisos", response_model=list[str])
def obtener_permisos_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_permissions("USR_VIEW")),
):
    try:
        usuario = service.get_usuario(db, usuario_id)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc
    return [p.per_nombre for p in (usuario.rol.permisos if usuario.rol else [])]


@router.post("/{usuario_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password_usuario(
    usuario_id: int,
    payload: schemas.UsuarioPasswordReset,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_permissions("USR_UPDATE")),
):
    try:
        service.reset_password(
            db,
            service.get_usuario(db, usuario_id),
            payload.nueva_contrasena,
        )
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{usuario_id}", response_model=schemas.UsuarioRead)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_permissions("USR_VIEW")),
):
    try:
        return service.get_usuario(db, usuario_id)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/{usuario_id}", response_model=schemas.UsuarioRead)
def reemplazar_usuario(
    usuario_id: int,
    payload: schemas.UsuarioReplace,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_permissions("USR_UPDATE")),
):
    try:
        return service.replace_usuario(db, service.get_usuario(db, usuario_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/{usuario_id}", response_model=schemas.UsuarioRead)
def actualizar_usuario(
    usuario_id: int,
    payload: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_permissions("USR_UPDATE")),
):
    try:
        return service.update_usuario(db, service.get_usuario(db, usuario_id), payload)
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_permissions("USR_DELETE")),
):
    if current_user.usr_id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No puede darse de baja a sí mismo",
        )
    try:
        service.soft_delete_usuario(db, service.get_usuario(db, usuario_id))
    except service.UserModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
