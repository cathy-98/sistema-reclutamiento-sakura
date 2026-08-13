from __future__ import annotations

import importlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permissions
from app.database import get_db
from app.solicitudes import schemas, services
from app.usuarios.models import Usuario


# Asegura el registro de listeners SQLAlchemy una sola vez al importar el router.
importlib.import_module("app.listeners.solicitud_listeners")

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


def _translate_error(exc: services.SolicitudModuleError) -> HTTPException:
    if isinstance(exc, services.NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, services.ConflictError):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_422_UNPROCESSABLE_CONTENT

    detail: dict[str, object] = {"message": exc.message}
    if exc.constraint:
        detail["constraint"] = exc.constraint
    return HTTPException(status_code=code, detail=detail)


def _permission_names(user: Usuario) -> set[str]:
    return {
        permiso.per_nombre
        for permiso in (user.rol.permisos if user.rol else [])
    }


def _ensure_state_permission(
    db: Session,
    target_state_id: int,
    user: Usuario,
) -> None:
    try:
        required = services.get_target_state_permission(db, target_state_id)
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc

    if required not in _permission_names(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Permisos insuficientes para realizar la transición",
                "required": [required],
            },
        )


@router.get("", response_model=list[schemas.SolicitudResponse])
@router.get("/", response_model=list[schemas.SolicitudResponse], include_in_schema=False)
def listar_solicitudes(
    q: str | None = Query(default=None),
    estado_id: int | None = Query(default=None, gt=0),
    prioridad_id: int | None = Query(default=None, gt=0),
    cargo_id: int | None = Query(default=None, gt=0),
    cliente_id: int | None = Query(default=None, gt=0),
    usuario_asignado_id: int | None = Query(default=None, gt=0),
    modalidad_id: int | None = Query(default=None, gt=0),
    tipo_contrato_id: int | None = Query(default=None, gt=0),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_VIEW")),
):
    return services.list_solicitudes(
        db,
        skip=skip,
        limit=limit,
        q=q,
        estado_id=estado_id,
        prioridad_id=prioridad_id,
        cargo_id=cargo_id,
        cliente_id=cliente_id,
        usuario_asignado_id=usuario_asignado_id,
        modalidad_id=modalidad_id,
        tipo_contrato_id=tipo_contrato_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.post("", response_model=schemas.SolicitudResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.SolicitudResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_solicitud(
    payload: schemas.SolicitudCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permissions("SOL_CREATE")),
):
    try:
        return services.create_solicitud(
            db,
            payload,
            creator_user_id=current_user.usr_id,
        )
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.get("/{solicitud_id}", response_model=schemas.SolicitudResponse)
def obtener_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_VIEW")),
):
    try:
        return services.get_solicitud(db, solicitud_id)
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/{solicitud_id}", response_model=schemas.SolicitudResponse)
def reemplazar_solicitud(
    solicitud_id: int,
    payload: schemas.SolicitudReplace,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_UPDATE")),
):
    try:
        return services.replace_solicitud(
            db,
            services.get_solicitud(db, solicitud_id),
            payload,
        )
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/{solicitud_id}", response_model=schemas.SolicitudResponse)
def actualizar_solicitud(
    solicitud_id: int,
    payload: schemas.SolicitudUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_UPDATE")),
):
    try:
        return services.update_solicitud(
            db,
            services.get_solicitud(db, solicitud_id),
            payload,
        )
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/{solicitud_id}/estado", response_model=schemas.SolicitudResponse)
def cambiar_estado_solicitud(
    solicitud_id: int,
    payload: schemas.SolicitudEstadoUpdate,
    response: Response,                       
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_permissions("SOL_UPDATE", "SOL_DELETE", match_all=False)
    ),
):
    _ensure_state_permission(db, payload.sol_estado_solicitud_id, current_user)
    try:
        result = services.change_state(
            db,
            services.get_solicitud(db, solicitud_id),
            payload,
            actor_user_id=current_user.usr_id,
        )
        warning = getattr(result, "_closure_warning", None)
        if warning:
            response.headers["X-Sakura-Warning"] = warning
        return result                    
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.get(
    "/{solicitud_id}/habilidades",
    response_model=list[schemas.SolicitudHabilidadResponse],
)
def listar_habilidades_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_VIEW")),
):
    try:
        return services.list_habilidades(db, solicitud_id)
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.post(
    "/{solicitud_id}/habilidades",
    response_model=list[schemas.SolicitudHabilidadResponse],
    status_code=status.HTTP_201_CREATED,
)
def agregar_habilidades_solicitud(
    solicitud_id: int,
    payload: list[schemas.SolicitudHabilidadCreate],
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_UPDATE")),
):
    try:
        solicitud = services.get_solicitud(db, solicitud_id)
        return services.add_habilidades(db, solicitud, payload)
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch(
    "/{solicitud_id}/habilidades/{habilidad_id}",
    response_model=schemas.SolicitudHabilidadResponse,
)
def actualizar_habilidad_solicitud(
    solicitud_id: int,
    habilidad_id: int,
    payload: schemas.SolicitudHabilidadUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_UPDATE")),
):
    try:
        solicitud = services.get_solicitud(db, solicitud_id)
        relation = services.get_habilidad_relacion(db, solicitud_id, habilidad_id)
        return services.update_habilidad(db, solicitud, relation, payload)
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete(
    "/{solicitud_id}/habilidades/{habilidad_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_habilidad_solicitud(
    solicitud_id: int,
    habilidad_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_UPDATE")),
):
    try:
        solicitud = services.get_solicitud(db, solicitud_id)
        relation = services.get_habilidad_relacion(db, solicitud_id, habilidad_id)
        services.delete_habilidad(db, solicitud, relation)
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{solicitud_id}/historial",
    response_model=list[schemas.HistorialSolicitudResponse],
)
def historial_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_VIEW")),
):
    try:
        return services.list_historial(db, solicitud_id)
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


@router.post("/{solicitud_id}/evaluar-candidato")
def evaluar_candidato_solicitud(
    solicitud_id: int,
    payload: list[schemas.HabilidadCandidatoInput],
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("SOL_VIEW")),
):
    try:
        data = [item.model_dump() for item in payload]
        return services.evaluar_candidato_cumple_excluyentes(db, solicitud_id, data)
    except services.SolicitudModuleError as exc:
        raise _translate_error(exc) from exc


# No se expone DELETE físico de solicitudes.
# Cancelado y Cerrado son estados terminales y requieren SOL_DELETE.
# La relación SolicitudCandidato se completará en el Módulo 3.
