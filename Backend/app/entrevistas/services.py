from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.candidatos.models import Candidato
from app.catalogos.models import (
    EstadoEntrevista,
    EstadoSolicitud,
    EstadoSolicitudCandidato,
    NombreResultado,
    TipoEntrevista,
)
from app.solicitudes.models import Solicitud, SolicitudCandidato
from app.usuarios.models import EstadoUsuario, Permiso, Rol, Usuario

from . import models, schemas


class Module5Error(Exception):
    status_code = 422
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(Module5Error):
    status_code = 404


class ConflictError(Module5Error):
    status_code = 409


def now_utc_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _state(db: Session, name: str) -> EstadoEntrevista:
    obj = db.scalar(select(EstadoEntrevista).where(func.lower(EstadoEntrevista.esev_nombre) == name.lower()))
    if obj is None:
        raise Module5Error(f"No existe el estado de entrevista '{name}'")
    return obj


def _postulation(db: Session, slcd_id: int) -> SolicitudCandidato:
    obj = db.get(SolicitudCandidato, slcd_id)
    if obj is None:
        raise NotFoundError("La postulación indicada no existe")
    return obj


def _postulation_state_name(db: Session, post: SolicitudCandidato) -> str:
    st = db.get(EstadoSolicitudCandidato, post.slcd_estado_solicitud_candidato_id)
    return st.essc_nombre if st and st.essc_nombre else "Desconocido"


def _require_interview_stage(db: Session, post: SolicitudCandidato) -> None:
    candidate_state = _postulation_state_name(db, post)
    if candidate_state.casefold() != "En entrevista".casefold():
        raise ConflictError(
            "Solo se permiten entrevistas y evaluaciones cuando la postulación está en estado 'En entrevista'. "
            f"Estado actual de la postulación: '{candidate_state}'"
        )

    request = db.get(Solicitud, post.slcd_solicitud_id)
    if request is None:
        raise NotFoundError("La solicitud asociada a la postulación no existe")
    request_state = db.get(EstadoSolicitud, request.sol_estado_solicitud_id)
    request_state_name = request_state.essl_nombre if request_state and request_state.essl_nombre else "Desconocido"
    if request_state_name.casefold() != "En Entrevistas".casefold():
        raise ConflictError(
            "Solo se permiten entrevistas y evaluaciones cuando la solicitud está en estado 'En Entrevistas'. "
            f"Estado actual de la solicitud: '{request_state_name}'"
        )


def _validate_future_dates(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    start = _naive(start); end = _naive(end)
    if start >= end:
        raise Module5Error("La fecha/hora de inicio debe ser anterior a la fecha/hora de fin")
    if start <= now_utc_naive():
        raise Module5Error("La fecha/hora de inicio debe ser futura")
    return start, end


def _validate_types_and_users(db: Session, tipos: list[schemas.TipoEntrevistaAsignacion]) -> None:
    type_ids = {x.tipo_entrevista_id for x in tipos}
    existing_types = set(db.scalars(select(TipoEntrevista.tpet_id).where(TipoEntrevista.tpet_id.in_(type_ids))))
    missing_types = sorted(type_ids - existing_types)
    if missing_types:
        raise Module5Error(f"Tipos de entrevista inexistentes: {missing_types}")

    user_ids = {uid for item in tipos for uid in item.usuarios_ids}
    rows = db.execute(
        select(Usuario.usr_id, EstadoUsuario.esusr_nombre)
        .join(EstadoUsuario, EstadoUsuario.esusr_id == Usuario.usr_estado_usuario_id)
        .where(Usuario.usr_id.in_(user_ids))
    ).all()
    found = {int(r[0]) for r in rows}
    missing_users = sorted(user_ids - found)
    if missing_users:
        raise Module5Error(f"Usuarios entrevistadores inexistentes: {missing_users}")
    inactive = sorted(int(uid) for uid, state in rows if not state or state.casefold() != "Activo".casefold())
    if inactive:
        raise ConflictError(f"Usuarios entrevistadores inactivos: {inactive}")

    users_with_permission = set(
        db.scalars(
            select(Usuario.usr_id)
            .join(Rol, Rol.rol_id == Usuario.usr_rol_id)
            .join(Rol.permisos)
            .where(Usuario.usr_id.in_(user_ids), Permiso.per_nombre == "INT_EVALUATE")
        )
    )
    without = sorted(user_ids - {int(x) for x in users_with_permission})
    if without:
        raise ConflictError(
            "Todo entrevistador debe poseer INT_EVALUATE. Usuarios sin permiso: " + str(without)
        )


def get_interview(db: Session, interview_id: int) -> models.CitaEntrevista:
    obj = db.get(models.CitaEntrevista, interview_id)
    if obj is None:
        raise NotFoundError("La entrevista no existe")
    return obj


def _state_name(db: Session, state_id: int) -> str:
    st = db.get(EstadoEntrevista, state_id)
    return st.esev_nombre if st and st.esev_nombre else "Desconocido"


def _candidate_and_request(db: Session, slcd_id: int):
    row = db.execute(
        select(SolicitudCandidato, Candidato, Solicitud)
        .join(Candidato, Candidato.cand_id == SolicitudCandidato.slcd_candidato_id)
        .join(Solicitud, Solicitud.sol_id == SolicitudCandidato.slcd_solicitud_id)
        .where(SolicitudCandidato.slcd_id == slcd_id)
    ).first()
    if not row:
        raise NotFoundError("La postulación no existe")
    return row


def evaluation_read(db: Session, ev: models.EvaluacionEntrevista) -> schemas.EvaluacionRead:
    result = db.get(NombreResultado, ev.even_nombre_resultado_id)
    typ = db.get(TipoEntrevista, ev.even_tipo_entrevista_id) if ev.even_tipo_entrevista_id else None
    user = db.get(Usuario, ev.even_usuario_id) if ev.even_usuario_id else None
    return schemas.EvaluacionRead(
        evaluacion_id=ev.even_id,
        entrevista_id=ev.even_cita_entrevista_id,
        tipo_entrevista_id=ev.even_tipo_entrevista_id,
        tipo_entrevista_nombre=typ.tpet_nombre if typ else None,
        usuario_id=ev.even_usuario_id,
        usuario_nombre=(f"{user.usr_nombres} {user.usr_apellido_paterno}" if user else None),
        resultado_id=ev.even_nombre_resultado_id,
        resultado_nombre=result.nore_nombre if result and result.nore_nombre else "Desconocido",
        observacion=ev.even_observacion,
        fecha_creacion=ev.even_fecha_creacion,
        fecha_actualizacion=ev.even_fecha_actualizacion,
    )


def _types_read(db: Session, interview_id: int, only_user_id: int | None = None) -> list[schemas.TipoEntrevistaRead]:
    type_ids = list(db.scalars(
        select(models.CitaTipoEntrevista.cten_tipo_entrevista_id)
        .where(models.CitaTipoEntrevista.cten_cita_entrevista_id == interview_id)
        .order_by(models.CitaTipoEntrevista.cten_tipo_entrevista_id)
    ))
    output = []
    for tid in type_ids:
        typ = db.get(TipoEntrevista, tid)
        stmt = (
            select(Usuario)
            .join(models.UsuarioCitaEntrevista, models.UsuarioCitaEntrevista.usrce_usuario_id == Usuario.usr_id)
            .where(
                models.UsuarioCitaEntrevista.usrce_cita_entrevista_id == interview_id,
                models.UsuarioCitaEntrevista.usrce_tipo_entrevista_id == tid,
            )
            .order_by(Usuario.usr_apellido_paterno, Usuario.usr_nombres)
        )
        if only_user_id is not None:
            stmt = stmt.where(Usuario.usr_id == only_user_id)
        users = list(db.scalars(stmt))
        if only_user_id is not None and not users:
            continue
        output.append(schemas.TipoEntrevistaRead(
            tipo_entrevista_id=int(tid),
            nombre=typ.tpet_nombre if typ and typ.tpet_nombre else "Desconocido",
            descripcion=typ.tpet_descripcion if typ else None,
            entrevistadores=[schemas.EntrevistadorRead(
                usuario_id=u.usr_id,
                nombres=u.usr_nombres,
                apellido_paterno=u.usr_apellido_paterno,
                email=u.usr_email,
            ) for u in users],
        ))
    return output


def interview_read(db: Session, obj: models.CitaEntrevista, include_evaluations: bool = True) -> schemas.EntrevistaRead:
    post, candidate, request = _candidate_and_request(db, obj.ctev_solicitud_candidato_id)
    evaluations = []
    if include_evaluations:
        evaluations = [evaluation_read(db, ev) for ev in db.scalars(
            select(models.EvaluacionEntrevista)
            .where(models.EvaluacionEntrevista.even_cita_entrevista_id == obj.ctev_id)
            .order_by(models.EvaluacionEntrevista.even_id)
        )]
    full_name = " ".join(x for x in [candidate.cand_nombres, candidate.cand_apellido_paterno, candidate.cand_apellido_materno] if x)
    return schemas.EntrevistaRead(
        entrevista_id=obj.ctev_id,
        solicitud_candidato_id=obj.ctev_solicitud_candidato_id,
        solicitud_id=request.sol_id,
        solicitud_codigo=request.sol_codigo,
        candidato_id=candidate.cand_id,
        candidato_nombre=full_name,
        candidato_email=candidate.cand_email,
        estado_id=obj.ctev_estado_entrevista_id,
        estado_nombre=_state_name(db, obj.ctev_estado_entrevista_id),
        fecha_hora_inicio=obj.ctev_fecha_hora_inicio,
        fecha_hora_fin=obj.ctev_fecha_hora_fin,
        fecha_creacion=obj.ctev_fecha_creacion,
        fecha_actualizacion=obj.ctev_fecha_actualizacion,
        titulo_evento=obj.ctev_titulo_evento,
        enlace_reunion=obj.ctev_enlace_reunion,
        comentarios_convocatoria=obj.ctev_comentarios_convocatoria,
        motivo_estado=obj.ctev_motivo_estado,
        usuario_creador_id=obj.ctev_usuario_creador_id,
        tipos=_types_read(db, obj.ctev_id),
        evaluaciones=evaluations,
    )


def _attach_types(db: Session, interview_id: int, tipos: list[schemas.TipoEntrevistaAsignacion]) -> None:
    for item in tipos:
        db.add(models.CitaTipoEntrevista(
            cten_tipo_entrevista_id=item.tipo_entrevista_id,
            cten_cita_entrevista_id=interview_id,
        ))
        for uid in item.usuarios_ids:
            db.add(models.UsuarioCitaEntrevista(
                usrce_cita_entrevista_id=interview_id,
                usrce_usuario_id=uid,
                usrce_tipo_entrevista_id=item.tipo_entrevista_id,
            ))


def _new_interview(db: Session, slcd_id: int, start: datetime, end: datetime, title: str,
                   link: str | None, comments: str | None,
                   tipos: list[schemas.TipoEntrevistaAsignacion], creator_id: int) -> models.CitaEntrevista:
    post = _postulation(db, slcd_id)
    _require_interview_stage(db, post)
    pending = _state(db, "Pendiente")
    obj = models.CitaEntrevista(
        ctev_solicitud_candidato_id=slcd_id,
        ctev_tipo_entrevista_id=tipos[0].tipo_entrevista_id,
        ctev_estado_entrevista_id=pending.esev_id,
        ctev_fecha_hora_inicio=start,
        ctev_fecha_hora_fin=end,
        ctev_fecha_creacion=now_utc_naive(),
        ctev_enlace_reunion=link,
        ctev_comentarios_convocatoria=comments,
        ctev_titulo_evento=title,
        ctev_usuario_creador_id=creator_id,
        ctev_fecha_actualizacion=now_utc_naive(),
    )
    db.add(obj); db.flush()
    _attach_types(db, obj.ctev_id, tipos)
    return obj


def create_interview(db: Session, payload: schemas.EntrevistaCreate, creator_id: int) -> schemas.EntrevistaRead:
    start, end = _validate_future_dates(payload.fecha_hora_inicio, payload.fecha_hora_fin)
    _validate_types_and_users(db, payload.tipos)
    try:
        obj = _new_interview(db, payload.solicitud_candidato_id, start, end,
                             payload.titulo_evento, payload.enlace_reunion,
                             payload.comentarios_convocatoria, payload.tipos, creator_id)
        db.commit(); db.refresh(obj)
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("La entrevista entra en conflicto con un registro existente") from exc
    return interview_read(db, obj)


def create_interviews_bulk(db: Session, payload: schemas.EntrevistaMasivaCreate, creator_id: int) -> schemas.EntrevistaMasivaRead:
    start, end = _validate_future_dates(payload.fecha_hora_inicio, payload.fecha_hora_fin)
    _validate_types_and_users(db, payload.tipos)
    # Validar todo antes de escribir: operación atómica.
    posts = [_postulation(db, sid) for sid in payload.solicitudes_candidatos_ids]
    for post in posts: _require_interview_stage(db, post)
    created = []
    try:
        for sid in payload.solicitudes_candidatos_ids:
            created.append(_new_interview(db, sid, start, end, payload.titulo_evento,
                                          payload.enlace_reunion, payload.comentarios_convocatoria,
                                          payload.tipos, creator_id))
        db.commit()
        for obj in created: db.refresh(obj)
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("No fue posible completar el agendamiento masivo; no se creó ninguna entrevista") from exc
    return schemas.EntrevistaMasivaRead(
        total_solicitados=len(payload.solicitudes_candidatos_ids),
        total_creados=len(created),
        entrevistas=[interview_read(db, x) for x in created],
    )


def list_interviews(db: Session, solicitud_id: int | None = None, candidato_id: int | None = None,
                    solicitud_candidato_id: int | None = None, usuario_id: int | None = None,
                    estado_id: int | None = None, tipo_id: int | None = None,
                    fecha_desde: datetime | None = None, fecha_hasta: datetime | None = None,
                    skip: int = 0, limit: int = 100) -> list[schemas.EntrevistaRead]:
    stmt = select(models.CitaEntrevista).join(
        SolicitudCandidato, SolicitudCandidato.slcd_id == models.CitaEntrevista.ctev_solicitud_candidato_id
    )
    if solicitud_id is not None: stmt = stmt.where(SolicitudCandidato.slcd_solicitud_id == solicitud_id)
    if candidato_id is not None: stmt = stmt.where(SolicitudCandidato.slcd_candidato_id == candidato_id)
    if solicitud_candidato_id is not None: stmt = stmt.where(models.CitaEntrevista.ctev_solicitud_candidato_id == solicitud_candidato_id)
    if estado_id is not None: stmt = stmt.where(models.CitaEntrevista.ctev_estado_entrevista_id == estado_id)
    if fecha_desde is not None: stmt = stmt.where(models.CitaEntrevista.ctev_fecha_hora_inicio >= _naive(fecha_desde))
    if fecha_hasta is not None: stmt = stmt.where(models.CitaEntrevista.ctev_fecha_hora_inicio <= _naive(fecha_hasta))
    if usuario_id is not None:
        stmt = stmt.join(models.UsuarioCitaEntrevista, models.UsuarioCitaEntrevista.usrce_cita_entrevista_id == models.CitaEntrevista.ctev_id).where(models.UsuarioCitaEntrevista.usrce_usuario_id == usuario_id)
    if tipo_id is not None:
        stmt = stmt.join(models.CitaTipoEntrevista, models.CitaTipoEntrevista.cten_cita_entrevista_id == models.CitaEntrevista.ctev_id).where(models.CitaTipoEntrevista.cten_tipo_entrevista_id == tipo_id)
    stmt = stmt.distinct().order_by(models.CitaEntrevista.ctev_fecha_hora_inicio.desc()).offset(skip).limit(limit)
    return [interview_read(db, x) for x in db.scalars(stmt)]


def update_interview(db: Session, obj: models.CitaEntrevista, payload: schemas.EntrevistaUpdate) -> schemas.EntrevistaRead:
    post = _postulation(db, obj.ctev_solicitud_candidato_id); _require_interview_stage(db, post)
    if _state_name(db, obj.ctev_estado_entrevista_id).casefold() in {"realizada", "cancelada", "no asistio"}:
        raise ConflictError("La entrevista está en un estado terminal y no puede modificarse")
    mapping = {
        "titulo_evento": "ctev_titulo_evento",
        "enlace_reunion": "ctev_enlace_reunion",
        "comentarios_convocatoria": "ctev_comentarios_convocatoria",
    }
    for field in payload.model_fields_set:
        setattr(obj, mapping[field], getattr(payload, field))
    obj.ctev_fecha_actualizacion = now_utc_naive()
    db.commit(); db.refresh(obj)
    return interview_read(db, obj)


def replace_participants(db: Session, obj: models.CitaEntrevista, payload: schemas.ParticipantesUpdate) -> schemas.EntrevistaRead:
    post = _postulation(db, obj.ctev_solicitud_candidato_id); _require_interview_stage(db, post)
    state = _state_name(db, obj.ctev_estado_entrevista_id).casefold()
    if state in {"realizada", "cancelada", "no asistio"}:
        raise ConflictError("No puede modificar participantes de una entrevista terminal")
    if db.scalar(select(func.count(models.EvaluacionEntrevista.even_id)).where(models.EvaluacionEntrevista.even_cita_entrevista_id == obj.ctev_id)):
        raise ConflictError("No puede modificar tipos/entrevistadores cuando ya existen evaluaciones")
    _validate_types_and_users(db, payload.tipos)
    db.execute(delete(models.UsuarioCitaEntrevista).where(models.UsuarioCitaEntrevista.usrce_cita_entrevista_id == obj.ctev_id))
    db.execute(delete(models.CitaTipoEntrevista).where(models.CitaTipoEntrevista.cten_cita_entrevista_id == obj.ctev_id))
    obj.ctev_tipo_entrevista_id = payload.tipos[0].tipo_entrevista_id
    _attach_types(db, obj.ctev_id, payload.tipos)
    obj.ctev_fecha_actualizacion = now_utc_naive()
    db.commit(); db.refresh(obj)
    return interview_read(db, obj)


def _change_state(db: Session, obj: models.CitaEntrevista, target: str, allowed: set[str], motivo: str | None = None) -> schemas.EntrevistaRead:
    post = _postulation(db, obj.ctev_solicitud_candidato_id); _require_interview_stage(db, post)
    current = _state_name(db, obj.ctev_estado_entrevista_id)
    if current.casefold() not in {x.casefold() for x in allowed}:
        raise ConflictError(f"No se permite transición desde '{current}' hacia '{target}'")
    obj.ctev_estado_entrevista_id = _state(db, target).esev_id
    obj.ctev_motivo_estado = motivo
    obj.ctev_fecha_actualizacion = now_utc_naive()
    db.commit(); db.refresh(obj)
    return interview_read(db, obj)


def confirm_interview(db: Session, obj: models.CitaEntrevista) -> schemas.EntrevistaRead:
    return _change_state(db, obj, "Confirmada", {"Pendiente", "Reprogramada"})


def reprogram_interview(db: Session, obj: models.CitaEntrevista, payload: schemas.ReprogramarRequest) -> schemas.EntrevistaRead:
    post = _postulation(db, obj.ctev_solicitud_candidato_id); _require_interview_stage(db, post)
    current = _state_name(db, obj.ctev_estado_entrevista_id)
    if current.casefold() not in {"pendiente", "confirmada", "reprogramada"}:
        raise ConflictError(f"No se puede reprogramar una entrevista en estado '{current}'")
    start, end = _validate_future_dates(payload.fecha_hora_inicio, payload.fecha_hora_fin)
    obj.ctev_fecha_hora_inicio = start; obj.ctev_fecha_hora_fin = end
    obj.ctev_estado_entrevista_id = _state(db, "Reprogramada").esev_id
    obj.ctev_motivo_estado = payload.motivo
    obj.ctev_fecha_actualizacion = now_utc_naive()
    try: db.commit(); db.refresh(obj)
    except IntegrityError as exc:
        db.rollback(); raise ConflictError("La nueva fecha entra en conflicto con otra entrevista") from exc
    return interview_read(db, obj)


def cancel_interview(db: Session, obj: models.CitaEntrevista, motivo: str) -> schemas.EntrevistaRead:
    return _change_state(db, obj, "Cancelada", {"Pendiente", "Confirmada", "Reprogramada"}, motivo)


def mark_no_show(db: Session, obj: models.CitaEntrevista, motivo: str) -> schemas.EntrevistaRead:
    return _change_state(db, obj, "No Asistio", {"Pendiente", "Confirmada", "Reprogramada"}, motivo)


def realize_interview(db: Session, obj: models.CitaEntrevista) -> schemas.EntrevistaRead:
    return _change_state(db, obj, "Realizada", {"Pendiente", "Confirmada", "Reprogramada"})


def _ensure_evaluator_assignment(db: Session, interview_id: int, type_id: int, user_id: int) -> None:
    if db.get(TipoEntrevista, type_id) is None:
        raise NotFoundError("El tipo de entrevista no existe")
    exists = db.scalar(select(func.count()).select_from(models.UsuarioCitaEntrevista).where(
        models.UsuarioCitaEntrevista.usrce_cita_entrevista_id == interview_id,
        models.UsuarioCitaEntrevista.usrce_tipo_entrevista_id == type_id,
        models.UsuarioCitaEntrevista.usrce_usuario_id == user_id,
    ))
    if not exists:
        raise ConflictError("El usuario autenticado no está asignado como entrevistador para ese tipo de entrevista")


def create_evaluation(db: Session, obj: models.CitaEntrevista, type_id: int, user_id: int, payload: schemas.EvaluacionCreate) -> schemas.EvaluacionRead:
    post = _postulation(db, obj.ctev_solicitud_candidato_id); _require_interview_stage(db, post)
    if _state_name(db, obj.ctev_estado_entrevista_id).casefold() != "realizada":
        raise ConflictError("Solo una entrevista 'Realizada' puede ser evaluada")
    _ensure_evaluator_assignment(db, obj.ctev_id, type_id, user_id)
    if db.get(NombreResultado, payload.nombre_resultado_id) is None:
        raise Module5Error("El resultado indicado no existe")
    existing = db.scalar(select(models.EvaluacionEntrevista).where(
        models.EvaluacionEntrevista.even_cita_entrevista_id == obj.ctev_id,
        models.EvaluacionEntrevista.even_tipo_entrevista_id == type_id,
        models.EvaluacionEntrevista.even_usuario_id == user_id,
    ))
    if existing:
        raise ConflictError("El entrevistador ya registró una evaluación para este tipo")
    ev = models.EvaluacionEntrevista(
        even_nombre_resultado_id=payload.nombre_resultado_id,
        even_observacion=payload.observacion,
        even_cita_entrevista_id=obj.ctev_id,
        even_usuario_id=user_id,
        even_tipo_entrevista_id=type_id,
        even_fecha_creacion=now_utc_naive(),
        even_fecha_actualizacion=now_utc_naive(),
    )
    db.add(ev)
    try: db.commit(); db.refresh(ev)
    except IntegrityError as exc:
        db.rollback(); raise ConflictError("Ya existe una evaluación del usuario para ese tipo") from exc
    return evaluation_read(db, ev)


def update_evaluation(db: Session, obj: models.CitaEntrevista, type_id: int, user_id: int, payload: schemas.EvaluacionUpdate) -> schemas.EvaluacionRead:
    post = _postulation(db, obj.ctev_solicitud_candidato_id); _require_interview_stage(db, post)
    if _state_name(db, obj.ctev_estado_entrevista_id).casefold() != "realizada":
        raise ConflictError("Solo puede modificar evaluaciones mientras la entrevista permanezca 'Realizada'")
    _ensure_evaluator_assignment(db, obj.ctev_id, type_id, user_id)
    ev = db.scalar(select(models.EvaluacionEntrevista).where(
        models.EvaluacionEntrevista.even_cita_entrevista_id == obj.ctev_id,
        models.EvaluacionEntrevista.even_tipo_entrevista_id == type_id,
        models.EvaluacionEntrevista.even_usuario_id == user_id,
    ))
    if ev is None: raise NotFoundError("El usuario aún no ha registrado una evaluación para ese tipo")
    if "nombre_resultado_id" in payload.model_fields_set:
        if db.get(NombreResultado, payload.nombre_resultado_id) is None:
            raise Module5Error("El resultado indicado no existe")
        ev.even_nombre_resultado_id = payload.nombre_resultado_id
    if "observacion" in payload.model_fields_set: ev.even_observacion = payload.observacion
    ev.even_fecha_actualizacion = now_utc_naive()
    db.commit(); db.refresh(ev)
    return evaluation_read(db, ev)


def list_evaluations(db: Session, interview_id: int) -> list[schemas.EvaluacionRead]:
    get_interview(db, interview_id)
    return [evaluation_read(db, x) for x in db.scalars(
        select(models.EvaluacionEntrevista).where(models.EvaluacionEntrevista.even_cita_entrevista_id == interview_id).order_by(models.EvaluacionEntrevista.even_id)
    )]


def my_interviews(db: Session, user_id: int) -> list[schemas.MiEntrevistaRead]:
    objs = list(db.scalars(
        select(models.CitaEntrevista)
        .join(models.UsuarioCitaEntrevista, models.UsuarioCitaEntrevista.usrce_cita_entrevista_id == models.CitaEntrevista.ctev_id)
        .where(models.UsuarioCitaEntrevista.usrce_usuario_id == user_id)
        .distinct().order_by(models.CitaEntrevista.ctev_fecha_hora_inicio)
    ))
    result = []
    for obj in objs:
        post, candidate, request = _candidate_and_request(db, obj.ctev_solicitud_candidato_id)
        full = " ".join(x for x in [candidate.cand_nombres, candidate.cand_apellido_paterno, candidate.cand_apellido_materno] if x)
        result.append(schemas.MiEntrevistaRead(
            entrevista_id=obj.ctev_id, solicitud_candidato_id=obj.ctev_solicitud_candidato_id,
            candidato_id=candidate.cand_id, candidato_nombre=full, solicitud_id=request.sol_id,
            solicitud_codigo=request.sol_codigo, estado=_state_name(db, obj.ctev_estado_entrevista_id),
            fecha_hora_inicio=obj.ctev_fecha_hora_inicio, fecha_hora_fin=obj.ctev_fecha_hora_fin,
            titulo_evento=obj.ctev_titulo_evento, enlace_reunion=obj.ctev_enlace_reunion,
            tipos_asignados=_types_read(db, obj.ctev_id, only_user_id=user_id),
        ))
    return result


def candidate_agenda(db: Session, candidate_id: int) -> list[schemas.EntrevistaCandidatoRead]:
    objs = list(db.scalars(
        select(models.CitaEntrevista)
        .join(SolicitudCandidato, SolicitudCandidato.slcd_id == models.CitaEntrevista.ctev_solicitud_candidato_id)
        .where(SolicitudCandidato.slcd_candidato_id == candidate_id)
        .order_by(models.CitaEntrevista.ctev_fecha_hora_inicio.desc())
    ))
    out = []
    for obj in objs:
        _, _, request = _candidate_and_request(db, obj.ctev_solicitud_candidato_id)
        names = [x.nombre for x in _types_read(db, obj.ctev_id)]
        out.append(schemas.EntrevistaCandidatoRead(
            entrevista_id=obj.ctev_id, solicitud_id=request.sol_id, solicitud_codigo=request.sol_codigo,
            estado=_state_name(db, obj.ctev_estado_entrevista_id), fecha_hora_inicio=obj.ctev_fecha_hora_inicio,
            fecha_hora_fin=obj.ctev_fecha_hora_fin, titulo_evento=obj.ctev_titulo_evento,
            enlace_reunion=obj.ctev_enlace_reunion, comentarios_convocatoria=obj.ctev_comentarios_convocatoria,
            tipos=names,
        ))
    return out


def candidate_interview(db: Session, candidate_id: int, interview_id: int) -> schemas.EntrevistaCandidatoRead:
    items = [x for x in candidate_agenda(db, candidate_id) if x.entrevista_id == interview_id]
    if not items: raise NotFoundError("La entrevista no existe o no pertenece al candidato autenticado")
    return items[0]
