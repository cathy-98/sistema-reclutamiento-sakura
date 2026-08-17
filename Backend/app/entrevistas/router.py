from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_candidate, require_permissions
from app.database import get_db
from app.usuarios.models import Usuario

from . import schemas, services

router = APIRouter(tags=["Entrevistas"])


def _translate(exc: services.Module5Error) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.message)


# Rutas estáticas antes de /entrevistas/{id} para evitar colisiones.
@router.get("/entrevistas/me", response_model=list[schemas.MiEntrevistaRead])
def mis_entrevistas(
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permissions("INT_VIEW")),
):
    return services.my_interviews(db, user.usr_id)


@router.get("/candidatos/me/entrevistas", response_model=list[schemas.EntrevistaCandidatoRead])
def agenda_candidato(
    db: Session = Depends(get_db),
    candidate=Depends(get_current_candidate),
):
    return services.candidate_agenda(db, candidate.cand_id)


@router.get("/candidatos/me/entrevistas/{entrevista_id}", response_model=schemas.EntrevistaCandidatoRead)
def detalle_agenda_candidato(
    entrevista_id: int,
    db: Session = Depends(get_db),
    candidate=Depends(get_current_candidate),
):
    try:
        return services.candidate_interview(db, candidate.cand_id, entrevista_id)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.post("/entrevistas", response_model=schemas.EntrevistaRead, status_code=201)
def crear_entrevista(
    payload: schemas.EntrevistaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permissions("INT_CREATE")),
):
    try:
        return services.create_interview(db, payload, user.usr_id)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.post("/entrevistas/agendar-masivo", response_model=schemas.EntrevistaMasivaRead, status_code=201)
def agendar_masivo(
    payload: schemas.EntrevistaMasivaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permissions("INT_CREATE")),
):
    try:
        return services.create_interviews_bulk(db, payload, user.usr_id)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.get("/entrevistas", response_model=list[schemas.EntrevistaRead])
def listar_entrevistas(
    solicitud_id: int | None = Query(default=None, ge=1),
    candidato_id: int | None = Query(default=None, ge=1),
    solicitud_candidato_id: int | None = Query(default=None, ge=1),
    usuario_id: int | None = Query(default=None, ge=1),
    estado_id: int | None = Query(default=None, ge=1),
    tipo_id: int | None = Query(default=None, ge=1),
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_VIEW")),
):
    return services.list_interviews(db, solicitud_id, candidato_id, solicitud_candidato_id,
                                    usuario_id, estado_id, tipo_id, fecha_desde, fecha_hasta, skip, limit)


@router.get("/solicitudes/{solicitud_id}/entrevistas", response_model=list[schemas.EntrevistaRead])
def entrevistas_solicitud(
    solicitud_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_VIEW")),
):
    return services.list_interviews(db, solicitud_id=solicitud_id)


@router.get("/candidatos/{candidato_id}/entrevistas", response_model=list[schemas.EntrevistaRead])
def entrevistas_candidato_interno(
    candidato_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_VIEW")),
):
    return services.list_interviews(db, candidato_id=candidato_id)


@router.get("/entrevistas/{entrevista_id}", response_model=schemas.EntrevistaRead)
def obtener_entrevista(
    entrevista_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_VIEW")),
):
    try:
        return services.interview_read(db, services.get_interview(db, entrevista_id))
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.patch("/entrevistas/{entrevista_id}", response_model=schemas.EntrevistaRead)
def editar_entrevista(
    entrevista_id: int,
    payload: schemas.EntrevistaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_UPDATE")),
):
    try:
        return services.update_interview(db, services.get_interview(db, entrevista_id), payload)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.put("/entrevistas/{entrevista_id}/participantes", response_model=schemas.EntrevistaRead)
def reemplazar_participantes(
    entrevista_id: int,
    payload: schemas.ParticipantesUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_UPDATE")),
):
    try:
        return services.replace_participants(db, services.get_interview(db, entrevista_id), payload)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.post("/entrevistas/{entrevista_id}/confirmar", response_model=schemas.EntrevistaRead)
def confirmar(
    entrevista_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_UPDATE")),
):
    try:
        return services.confirm_interview(db, services.get_interview(db, entrevista_id))
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.post("/entrevistas/{entrevista_id}/reprogramar", response_model=schemas.EntrevistaRead)
def reprogramar(
    entrevista_id: int,
    payload: schemas.ReprogramarRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_UPDATE")),
):
    try:
        return services.reprogram_interview(db, services.get_interview(db, entrevista_id), payload)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.post("/entrevistas/{entrevista_id}/cancelar", response_model=schemas.EntrevistaRead)
def cancelar(
    entrevista_id: int,
    payload: schemas.MotivoEstadoRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_UPDATE")),
):
    try:
        return services.cancel_interview(db, services.get_interview(db, entrevista_id), payload.motivo)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.post("/entrevistas/{entrevista_id}/no-asistio", response_model=schemas.EntrevistaRead)
def no_asistio(
    entrevista_id: int,
    payload: schemas.MotivoEstadoRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_UPDATE")),
):
    try:
        return services.mark_no_show(db, services.get_interview(db, entrevista_id), payload.motivo)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.post("/entrevistas/{entrevista_id}/realizar", response_model=schemas.EntrevistaRead)
def realizar(
    entrevista_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_UPDATE")),
):
    try:
        return services.realize_interview(db, services.get_interview(db, entrevista_id))
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.post("/entrevistas/{entrevista_id}/tipos/{tipo_id}/evaluar", response_model=schemas.EvaluacionRead, status_code=201)
def evaluar(
    entrevista_id: int,
    tipo_id: int,
    payload: schemas.EvaluacionCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permissions("INT_EVALUATE")),
):
    try:
        return services.create_evaluation(db, services.get_interview(db, entrevista_id), tipo_id, user.usr_id, payload)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.patch("/entrevistas/{entrevista_id}/tipos/{tipo_id}/evaluacion", response_model=schemas.EvaluacionRead)
def editar_mi_evaluacion(
    entrevista_id: int,
    tipo_id: int,
    payload: schemas.EvaluacionUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_permissions("INT_EVALUATE")),
):
    try:
        return services.update_evaluation(db, services.get_interview(db, entrevista_id), tipo_id, user.usr_id, payload)
    except services.Module5Error as exc:
        raise _translate(exc) from exc


@router.get("/entrevistas/{entrevista_id}/evaluaciones", response_model=list[schemas.EvaluacionRead])
def evaluaciones(
    entrevista_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("INT_VIEW", "INT_EVALUATE", match_all=False)),
):
    try:
        return services.list_evaluations(db, entrevista_id)
    except services.Module5Error as exc:
        raise _translate(exc) from exc
