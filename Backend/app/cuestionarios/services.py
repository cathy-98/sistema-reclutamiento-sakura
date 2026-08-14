from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import delete, func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


class Module4Error(Exception):
    status_code = 422

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(Module4Error):
    status_code = 404


class ConflictError(Module4Error):
    status_code = 409


def now_utc_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _row(db: Session, sql: str, **params):
    return db.execute(text(sql), params).mappings().first()


def _rows(db: Session, sql: str, **params):
    return list(db.execute(text(sql), params).mappings().all())


def _state_id(db: Session, name: str) -> int:
    row = _row(
        db,
        "SELECT escc_id FROM tbl_estado_cuestionario_candidato WHERE LOWER(escc_nombre)=LOWER(:name)",
        name=name,
    )
    if not row:
        raise Module4Error(f"No existe el estado de cuestionario '{name}'")
    return int(row["escc_id"])


def _state_name(db: Session, state_id: int) -> str:
    row = _row(
        db,
        "SELECT escc_nombre FROM tbl_estado_cuestionario_candidato WHERE escc_id=:id",
        id=state_id,
    )
    return str(row["escc_nombre"]) if row else "Desconocido"


def _validate_habilidad_nivel(db: Session, habilidad_id: int, nivel_id: int) -> None:
    if not _row(db, "SELECT hab_id FROM tbl_habilidad WHERE hab_id=:id", id=habilidad_id):
        raise Module4Error("La habilidad indicada no existe")
    nivel = _row(
        db,
        """
        SELECT nvhb_id, nvhb_puntaje_base, nvhb_duracion
          FROM tbl_nivel_habilidad
         WHERE nvhb_id=:id
        """,
        id=nivel_id,
    )
    if not nivel:
        raise Module4Error("El nivel de habilidad indicado no existe")
    if nivel["nvhb_puntaje_base"] is None or int(nivel["nvhb_puntaje_base"]) < 0:
        raise Module4Error("El nivel no tiene un puntaje base válido")
    if nivel["nvhb_duracion"] is None or int(nivel["nvhb_duracion"]) < 0:
        raise Module4Error("El nivel no tiene una duración válida")


def _cuestionario_metrics(db: Session, cuestionario_id: int) -> dict[str, int]:
    row = _row(
        db,
        """
        SELECT COUNT(pc.prcu_id) cantidad,
               COALESCE(SUM(n.nvhb_puntaje_base),0) puntaje,
               COALESCE(SUM(n.nvhb_duracion),0) duracion
          FROM tbl_pregunta_cuestionario pc
          JOIN tbl_pregunta p ON p.preg_id=pc.prcu_pregunta_id
          JOIN tbl_nivel_habilidad n ON n.nvhb_id=p.preg_nivel_habilidad_id
         WHERE pc.prcu_cuestionario_id=:id
        """,
        id=cuestionario_id,
    )
    return {
        "cantidad_preguntas": int(row["cantidad"] or 0),
        "puntaje_maximo": int(row["puntaje"] or 0),
        "duracion_minutos": int(row["duracion"] or 0),
    }


def _validate_simple_question(db: Session, pregunta_id: int) -> None:
    row = _row(
        db,
        """
        SELECT COUNT(*) total,
               SUM(CASE WHEN opcr_es_correcta THEN 1 ELSE 0 END) correctas
          FROM tbl_opcion_respuesta
         WHERE opcr_pregunta_id=:id
        """,
        id=pregunta_id,
    )
    total = int(row["total"] or 0)
    correctas = int(row["correctas"] or 0)
    if total < 2:
        raise ConflictError("La pregunta debe tener al menos dos opciones")
    if correctas != 1:
        raise ConflictError("La pregunta debe tener exactamente una opción correcta")


def _question_in_questionnaire(db: Session, pregunta_id: int) -> bool:
    return bool(
        db.scalar(
            select(func.count(models.PreguntaCuestionario.prcu_id)).where(
                models.PreguntaCuestionario.prcu_pregunta_id == pregunta_id
            )
        )
    )


def _question_has_assignments(db: Session, pregunta_id: int) -> bool:
    row = _row(
        db,
        """
        SELECT 1
          FROM tbl_pregunta_cuestionario pc
          JOIN tbl_candidato_cuestionario cc
            ON cc.cdcu_cuestionario_id=pc.prcu_cuestionario_id
         WHERE pc.prcu_pregunta_id=:pid
         LIMIT 1
        """,
        pid=pregunta_id,
    )
    return bool(row)


def _questionnaire_has_assignments(db: Session, questionnaire_id: int) -> bool:
    return bool(
        db.scalar(
            select(func.count(models.CandidatoCuestionario.cdcu_id)).where(
                models.CandidatoCuestionario.cdcu_cuestionario_id == questionnaire_id
            )
        )
    )


def question_read(db: Session, question: models.Pregunta) -> schemas.PreguntaAdminRead:
    meta = _row(
        db,
        """
        SELECT h.hab_nombre, n.nvhb_nombre, n.nvhb_puntaje_base, n.nvhb_duracion
          FROM tbl_habilidad h, tbl_nivel_habilidad n
         WHERE h.hab_id=:hid AND n.nvhb_id=:nid
        """,
        hid=question.preg_habilidad_id,
        nid=question.preg_nivel_habilidad_id,
    ) or {}
    options = list(
        db.scalars(
            select(models.OpcionRespuesta)
            .where(models.OpcionRespuesta.opcr_pregunta_id == question.preg_id)
            .order_by(models.OpcionRespuesta.opcr_id)
        )
    )
    return schemas.PreguntaAdminRead(
        preg_id=question.preg_id,
        preg_texto_pregunta=question.preg_texto_pregunta,
        preg_habilidad_id=question.preg_habilidad_id,
        habilidad_nombre=meta.get("hab_nombre"),
        preg_nivel_habilidad_id=question.preg_nivel_habilidad_id,
        nivel_nombre=meta.get("nvhb_nombre"),
        puntaje_base=int(meta.get("nvhb_puntaje_base") or 0),
        duracion_minutos=int(meta.get("nvhb_duracion") or 0),
        preg_fecha_creacion=question.preg_fecha_creacion,
        opciones=options,
    )


def list_questions(db: Session, q=None, habilidad_id=None, nivel_id=None, skip=0, limit=100):
    stmt = select(models.Pregunta)
    if q:
        stmt = stmt.where(models.Pregunta.preg_texto_pregunta.ilike(f"%{q.strip()}%"))
    if habilidad_id:
        stmt = stmt.where(models.Pregunta.preg_habilidad_id == habilidad_id)
    if nivel_id:
        stmt = stmt.where(models.Pregunta.preg_nivel_habilidad_id == nivel_id)
    stmt = stmt.order_by(models.Pregunta.preg_id.desc()).offset(skip).limit(limit)
    return [question_read(db, x) for x in db.scalars(stmt)]


def get_question(db: Session, question_id: int) -> models.Pregunta:
    obj = db.get(models.Pregunta, question_id)
    if not obj:
        raise NotFoundError("Pregunta no encontrada")
    return obj


def create_question(db: Session, payload: schemas.PreguntaCreate):
    _validate_habilidad_nivel(db, payload.preg_habilidad_id, payload.preg_nivel_habilidad_id)
    obj = models.Pregunta(**payload.model_dump(), preg_fecha_creacion=now_utc_naive())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return question_read(db, obj)


def update_question(db: Session, obj: models.Pregunta, payload: schemas.PreguntaUpdate):
    if _question_has_assignments(db, obj.preg_id):
        raise ConflictError("No puede modificar una pregunta que ya forma parte de una evaluación asignada")
    data = payload.model_dump(exclude_unset=True)
    hid = data.get("preg_habilidad_id", obj.preg_habilidad_id)
    nid = data.get("preg_nivel_habilidad_id", obj.preg_nivel_habilidad_id)
    _validate_habilidad_nivel(db, hid, nid)
    for key, value in data.items():
        setattr(obj, key, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(obj)
    return question_read(db, obj)


def replace_question(db: Session, obj: models.Pregunta, payload: schemas.PreguntaCreate):
    update = schemas.PreguntaUpdate(**payload.model_dump())
    return update_question(db, obj, update)


def delete_question(db: Session, obj: models.Pregunta):
    if _question_in_questionnaire(db, obj.preg_id):
        raise ConflictError("No puede eliminar una pregunta utilizada por cuestionarios")
    db.execute(delete(models.OpcionRespuesta).where(models.OpcionRespuesta.opcr_pregunta_id == obj.preg_id))
    db.delete(obj)
    db.commit()


def create_option(db: Session, question_id: int, payload: schemas.OpcionCreate):
    get_question(db, question_id)
    if _question_has_assignments(db, question_id):
        raise ConflictError("No puede modificar opciones de una pregunta con evaluaciones asignadas")
    if payload.opcr_es_correcta:
        existing = db.scalar(
            select(func.count(models.OpcionRespuesta.opcr_id)).where(
                models.OpcionRespuesta.opcr_pregunta_id == question_id,
                models.OpcionRespuesta.opcr_es_correcta.is_(True),
            )
        )
        if existing:
            raise ConflictError("La pregunta ya posee una opción correcta")
    obj = models.OpcionRespuesta(
        opcr_pregunta_id=question_id,
        opcr_texto_opcion=payload.opcr_texto_opcion.strip(),
        opcr_es_correcta=payload.opcr_es_correcta,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_option(db: Session, question_id: int, option_id: int, payload: schemas.OpcionUpdate):
    obj = db.get(models.OpcionRespuesta, option_id)
    if not obj or obj.opcr_pregunta_id != question_id:
        raise NotFoundError("Opción no encontrada")
    if _question_has_assignments(db, question_id):
        raise ConflictError("No puede modificar opciones de una pregunta con evaluaciones asignadas")
    data = payload.model_dump(exclude_unset=True)
    if data.get("opcr_es_correcta") is True and not obj.opcr_es_correcta:
        existing = db.scalar(
            select(func.count(models.OpcionRespuesta.opcr_id)).where(
                models.OpcionRespuesta.opcr_pregunta_id == question_id,
                models.OpcionRespuesta.opcr_es_correcta.is_(True),
                models.OpcionRespuesta.opcr_id != option_id,
            )
        )
        if existing:
            raise ConflictError("La pregunta ya posee una opción correcta")
    for key, value in data.items():
        setattr(obj, key, value.strip() if isinstance(value, str) else value)
    db.flush()
    if _question_in_questionnaire(db, question_id):
        try:
            _validate_simple_question(db, question_id)
        except Exception:
            db.rollback()
            raise
    db.commit()
    db.refresh(obj)
    return obj


def replace_option(db: Session, question_id: int, option_id: int, payload: schemas.OpcionCreate):
    update = schemas.OpcionUpdate(**payload.model_dump())
    return update_option(db, question_id, option_id, update)


def delete_option(db: Session, question_id: int, option_id: int):
    obj = db.get(models.OpcionRespuesta, option_id)
    if not obj or obj.opcr_pregunta_id != question_id:
        raise NotFoundError("Opción no encontrada")
    if _question_has_assignments(db, question_id):
        raise ConflictError("No puede modificar opciones de una pregunta con evaluaciones asignadas")
    if _question_in_questionnaire(db, question_id):
        total = db.scalar(
            select(func.count(models.OpcionRespuesta.opcr_id)).where(
                models.OpcionRespuesta.opcr_pregunta_id == question_id
            )
        )
        if int(total or 0) <= 2:
            raise ConflictError("No puede dejar una pregunta utilizada con menos de dos opciones")
        if obj.opcr_es_correcta:
            raise ConflictError("No puede eliminar la única opción correcta de una pregunta utilizada")
    db.delete(obj)
    db.commit()


def get_questionnaire(db: Session, questionnaire_id: int) -> models.Cuestionario:
    obj = db.get(models.Cuestionario, questionnaire_id)
    if not obj:
        raise NotFoundError("Cuestionario no encontrado")
    return obj


def questionnaire_read(db: Session, obj: models.Cuestionario):
    metrics = _cuestionario_metrics(db, obj.cues_id)
    solicitud = _row(db, "SELECT sol_codigo FROM tbl_solicitud WHERE sol_id=:id", id=obj.cues_solicitud_id)
    return schemas.CuestionarioRead(
        cues_id=obj.cues_id,
        cues_nombre=obj.cues_nombre,
        cues_descripcion=obj.cues_descripcion,
        cues_porcentaje_aprobacion=obj.cues_porcentaje_aprobacion,
        cues_solicitud_id=obj.cues_solicitud_id,
        solicitud_codigo=solicitud["sol_codigo"] if solicitud else None,
        **metrics,
    )


def list_questionnaires(db: Session, q=None, solicitud_id=None, skip=0, limit=100):
    stmt = select(models.Cuestionario)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(models.Cuestionario.cues_nombre.ilike(like), models.Cuestionario.cues_descripcion.ilike(like)))
    if solicitud_id:
        stmt = stmt.where(models.Cuestionario.cues_solicitud_id == solicitud_id)
    stmt = stmt.order_by(models.Cuestionario.cues_id.desc()).offset(skip).limit(limit)
    return [questionnaire_read(db, x) for x in db.scalars(stmt)]


def create_questionnaire(db: Session, payload: schemas.CuestionarioCreate):
    if not _row(db, "SELECT sol_id FROM tbl_solicitud WHERE sol_id=:id", id=payload.cues_solicitud_id):
        raise Module4Error("La solicitud indicada no existe")
    obj = models.Cuestionario(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return questionnaire_read(db, obj)


def update_questionnaire(db: Session, obj: models.Cuestionario, payload: schemas.CuestionarioUpdate):
    data = payload.model_dump(exclude_unset=True)
    if _questionnaire_has_assignments(db, obj.cues_id) and "cues_solicitud_id" in data:
        if data["cues_solicitud_id"] != obj.cues_solicitud_id:
            raise ConflictError("No puede cambiar la solicitud de un cuestionario ya asignado")
    if "cues_solicitud_id" in data:
        if not _row(db, "SELECT sol_id FROM tbl_solicitud WHERE sol_id=:id", id=data["cues_solicitud_id"]):
            raise Module4Error("La solicitud indicada no existe")
    for key, value in data.items():
        setattr(obj, key, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(obj)
    return questionnaire_read(db, obj)


def replace_questionnaire(db: Session, obj: models.Cuestionario, payload: schemas.CuestionarioCreate):
    return update_questionnaire(db, obj, schemas.CuestionarioUpdate(**payload.model_dump()))


def delete_questionnaire(db: Session, obj: models.Cuestionario):
    if _questionnaire_has_assignments(db, obj.cues_id):
        raise ConflictError("No puede eliminar un cuestionario que posee asignaciones")
    db.execute(delete(models.PreguntaCuestionario).where(models.PreguntaCuestionario.prcu_cuestionario_id == obj.cues_id))
    db.delete(obj)
    db.commit()


def list_questionnaire_questions(db: Session, questionnaire_id: int):
    get_questionnaire(db, questionnaire_id)
    ids = list(
        db.scalars(
            select(models.PreguntaCuestionario.prcu_pregunta_id)
            .where(models.PreguntaCuestionario.prcu_cuestionario_id == questionnaire_id)
            .order_by(models.PreguntaCuestionario.prcu_id)
        )
    )
    return [question_read(db, get_question(db, qid)) for qid in ids]


def add_question_to_questionnaire(db: Session, questionnaire_id: int, question_id: int):
    get_questionnaire(db, questionnaire_id)
    get_question(db, question_id)
    if _questionnaire_has_assignments(db, questionnaire_id):
        raise ConflictError("No puede modificar preguntas de un cuestionario que ya fue asignado")
    _validate_simple_question(db, question_id)
    exists = db.scalar(
        select(func.count(models.PreguntaCuestionario.prcu_id)).where(
            models.PreguntaCuestionario.prcu_cuestionario_id == questionnaire_id,
            models.PreguntaCuestionario.prcu_pregunta_id == question_id,
        )
    )
    if exists:
        raise ConflictError("La pregunta ya pertenece al cuestionario")
    obj = models.PreguntaCuestionario(prcu_cuestionario_id=questionnaire_id, prcu_pregunta_id=question_id)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("La pregunta ya pertenece al cuestionario")
    return list_questionnaire_questions(db, questionnaire_id)


def remove_question_from_questionnaire(db: Session, questionnaire_id: int, question_id: int):
    get_questionnaire(db, questionnaire_id)
    if _questionnaire_has_assignments(db, questionnaire_id):
        raise ConflictError("No puede modificar preguntas de un cuestionario que ya fue asignado")
    obj = db.scalar(
        select(models.PreguntaCuestionario).where(
            models.PreguntaCuestionario.prcu_cuestionario_id == questionnaire_id,
            models.PreguntaCuestionario.prcu_pregunta_id == question_id,
        )
    )
    if not obj:
        raise NotFoundError("La pregunta no pertenece al cuestionario")
    db.delete(obj)
    db.commit()


def _validate_questionnaire_for_assignment(db: Session, questionnaire_id: int):
    metrics = _cuestionario_metrics(db, questionnaire_id)
    if metrics["cantidad_preguntas"] <= 0:
        raise ConflictError("No puede asignar un cuestionario sin preguntas")
    if metrics["puntaje_maximo"] <= 0:
        raise ConflictError("El cuestionario debe tener puntaje máximo mayor que cero")
    if metrics["duracion_minutos"] <= 0:
        raise ConflictError("El cuestionario debe tener duración mayor que cero")
    qids = list(
        db.scalars(
            select(models.PreguntaCuestionario.prcu_pregunta_id).where(
                models.PreguntaCuestionario.prcu_cuestionario_id == questionnaire_id
            )
        )
    )
    for qid in qids:
        _validate_simple_question(db, qid)
    return metrics


def get_assignment(db: Session, assignment_id: int) -> models.CandidatoCuestionario:
    obj = db.get(models.CandidatoCuestionario, assignment_id)
    if not obj:
        raise NotFoundError("Asignación de cuestionario no encontrada")
    return obj


def _finalize(db: Session, assignment: models.CandidatoCuestionario, forced_time_limit: bool = False):
    questionnaire = get_questionnaire(db, assignment.cdcu_cuestionario_id)
    metrics = _cuestionario_metrics(db, questionnaire.cues_id)
    total_score = int(
        db.scalar(
            select(func.coalesce(func.sum(models.RespuestaPregunta.rspr_puntaje_obtenido), 0)).where(
                models.RespuestaPregunta.rspr_candidato_cuestionario_id == assignment.cdcu_id
            )
        ) or 0
    )
    max_score = metrics["puntaje_maximo"]
    if max_score <= 0:
        raise ConflictError("El cuestionario no posee puntaje máximo válido")
    percent = (Decimal(total_score) * Decimal("100") / Decimal(max_score)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    approved = percent >= Decimal(questionnaire.cues_porcentaje_aprobacion)
    finish = now_utc_naive()
    start = assignment.cdcu_fecha_inicio or finish
    elapsed_seconds = max(0, int((finish - start).total_seconds()))
    elapsed_minutes = int(math.ceil(elapsed_seconds / 60)) if elapsed_seconds else 0
    if forced_time_limit:
        elapsed_minutes = metrics["duracion_minutos"]
    answered = int(
        db.scalar(
            select(func.count(models.RespuestaPregunta.rspr_id)).where(
                models.RespuestaPregunta.rspr_candidato_cuestionario_id == assignment.cdcu_id
            )
        ) or 0
    )

    assignment.cdcu_fecha_resolucion = finish
    assignment.cdcu_porcentaje_obtenido = percent
    assignment.cdcu_tiempo_utilizado = elapsed_minutes
    assignment.cdcu_aprobado = approved
    assignment.cdcu_estado_cuestionario_candidato_id = _state_id(db, "Finalizado")
    db.commit()
    db.refresh(assignment)

    return schemas.FinalizarRead(
        asignacion_id=assignment.cdcu_id,
        estado="Finalizado",
        puntaje_obtenido=total_score,
        puntaje_maximo=max_score,
        porcentaje_obtenido=percent,
        porcentaje_aprobacion=questionnaire.cues_porcentaje_aprobacion,
        aprobado=approved,
        tiempo_utilizado=elapsed_minutes,
        respondidas=answered,
        preguntas_totales=metrics["cantidad_preguntas"],
    )


def _expire_if_needed(db: Session, assignment: models.CandidatoCuestionario) -> None:
    state = _state_name(db, assignment.cdcu_estado_cuestionario_candidato_id)
    now = now_utc_naive()
    if state == "Asignado" and assignment.cdcu_fecha_vencimiento and now > assignment.cdcu_fecha_vencimiento:
        assignment.cdcu_estado_cuestionario_candidato_id = _state_id(db, "Vencido")
        db.commit()
        return
    if state == "En Progreso" and assignment.cdcu_fecha_inicio:
        duration = _cuestionario_metrics(db, assignment.cdcu_cuestionario_id)["duracion_minutos"]
        if now >= assignment.cdcu_fecha_inicio + timedelta(minutes=duration):
            _finalize(db, assignment, forced_time_limit=True)


def assignment_read(db: Session, assignment: models.CandidatoCuestionario) -> schemas.AsignacionRead:
    _expire_if_needed(db, assignment)
    questionnaire = get_questionnaire(db, assignment.cdcu_cuestionario_id)
    metrics = _cuestionario_metrics(db, questionnaire.cues_id)
    candidate = _row(db, "SELECT cand_email FROM tbl_candidato WHERE cand_id=:id", id=assignment.cdcu_candidato_id)
    return schemas.AsignacionRead(
        cdcu_id=assignment.cdcu_id,
        cdcu_candidato_id=assignment.cdcu_candidato_id,
        candidato_email=candidate["cand_email"] if candidate else None,
        cdcu_cuestionario_id=assignment.cdcu_cuestionario_id,
        cuestionario_nombre=questionnaire.cues_nombre,
        cdcu_fecha_asignacion=assignment.cdcu_fecha_asignacion,
        cdcu_fecha_inicio=assignment.cdcu_fecha_inicio,
        cdcu_fecha_vencimiento=assignment.cdcu_fecha_vencimiento,
        cdcu_fecha_resolucion=assignment.cdcu_fecha_resolucion,
        cdcu_porcentaje_obtenido=assignment.cdcu_porcentaje_obtenido,
        estado_id=assignment.cdcu_estado_cuestionario_candidato_id,
        estado_nombre=_state_name(db, assignment.cdcu_estado_cuestionario_candidato_id),
        cdcu_tiempo_utilizado=assignment.cdcu_tiempo_utilizado,
        cdcu_permitir_reintento=bool(assignment.cdcu_permitir_reintento),
        cdcu_aprobado=assignment.cdcu_aprobado,
        **metrics,
    )


def assign_questionnaire(db: Session, questionnaire_id: int, payload: schemas.AsignacionCreate):
    questionnaire = get_questionnaire(db, questionnaire_id)
    _validate_questionnaire_for_assignment(db, questionnaire_id)
    expiry = _naive(payload.fecha_vencimiento)
    if expiry <= now_utc_naive():
        raise Module4Error("La fecha de vencimiento debe ser futura")
    if not _row(db, "SELECT cand_id FROM tbl_candidato WHERE cand_id=:id", id=payload.candidato_id):
        raise Module4Error("El candidato indicado no existe")
    linked = _row(
        db,
        """
        SELECT slcd_id
          FROM tbl_solicitud_candidato
         WHERE slcd_candidato_id=:cid
           AND slcd_solicitud_id=:sid
        """,
        cid=payload.candidato_id,
        sid=questionnaire.cues_solicitud_id,
    )
    if not linked:
        raise ConflictError("El candidato no está asociado a la solicitud del cuestionario")
    exists = db.scalar(
        select(func.count(models.CandidatoCuestionario.cdcu_id)).where(
            models.CandidatoCuestionario.cdcu_candidato_id == payload.candidato_id,
            models.CandidatoCuestionario.cdcu_cuestionario_id == questionnaire_id,
        )
    )
    if exists:
        raise ConflictError("El candidato ya posee una asignación para este cuestionario")
    obj = models.CandidatoCuestionario(
        cdcu_candidato_id=payload.candidato_id,
        cdcu_cuestionario_id=questionnaire_id,
        cdcu_fecha_asignacion=now_utc_naive(),
        cdcu_fecha_inicio=None,
        cdcu_fecha_vencimiento=expiry,
        cdcu_fecha_resolucion=None,
        cdcu_porcentaje_obtenido=None,
        cdcu_estado_cuestionario_candidato_id=_state_id(db, "Asignado"),
        cdcu_tiempo_utilizado=None,
        cdcu_permitir_reintento=False,
        cdcu_aprobado=None,
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("El candidato ya posee una asignación para este cuestionario")
    db.refresh(obj)
    return assignment_read(db, obj)


def list_assignments(db: Session, questionnaire_id=None, candidato_id=None, estado_id=None, aprobado=None, skip=0, limit=100):
    stmt = select(models.CandidatoCuestionario)
    if questionnaire_id:
        stmt = stmt.where(models.CandidatoCuestionario.cdcu_cuestionario_id == questionnaire_id)
    if candidato_id:
        stmt = stmt.where(models.CandidatoCuestionario.cdcu_candidato_id == candidato_id)
    if estado_id:
        stmt = stmt.where(models.CandidatoCuestionario.cdcu_estado_cuestionario_candidato_id == estado_id)
    if aprobado is not None:
        stmt = stmt.where(models.CandidatoCuestionario.cdcu_aprobado == aprobado)
    stmt = stmt.order_by(models.CandidatoCuestionario.cdcu_id.desc()).offset(skip).limit(limit)
    return [assignment_read(db, x) for x in db.scalars(stmt)]


def cancel_assignment(db: Session, assignment: models.CandidatoCuestionario):
    _expire_if_needed(db, assignment)
    state = _state_name(db, assignment.cdcu_estado_cuestionario_candidato_id)
    if state in {"Finalizado", "Vencido", "Cancelado"}:
        raise ConflictError(f"No puede cancelar una asignación en estado {state}")
    assignment.cdcu_estado_cuestionario_candidato_id = _state_id(db, "Cancelado")
    db.commit()
    db.refresh(assignment)
    return assignment_read(db, assignment)


def mark_technical_error(db: Session, assignment: models.CandidatoCuestionario):
    _expire_if_needed(db, assignment)
    state = _state_name(db, assignment.cdcu_estado_cuestionario_candidato_id)
    if state not in {"Asignado", "En Progreso"}:
        raise ConflictError("El error técnico solo puede declararse en una evaluación pendiente o en curso")
    assignment.cdcu_estado_cuestionario_candidato_id = _state_id(db, "Error Tecnico")
    assignment.cdcu_permitir_reintento = False
    db.commit()
    db.refresh(assignment)
    return assignment_read(db, assignment)


def enable_retry(db: Session, assignment: models.CandidatoCuestionario, payload: schemas.ReintentoEnable):
    state = _state_name(db, assignment.cdcu_estado_cuestionario_candidato_id)
    if state != "Error Tecnico":
        raise ConflictError("Solo puede habilitar reintento cuando el estado es Error Tecnico")
    expiry = _naive(payload.fecha_vencimiento)
    if expiry <= now_utc_naive():
        raise Module4Error("La nueva fecha de vencimiento debe ser futura")
    db.execute(
        delete(models.RespuestaPregunta).where(
            models.RespuestaPregunta.rspr_candidato_cuestionario_id == assignment.cdcu_id
        )
    )
    assignment.cdcu_fecha_inicio = None
    assignment.cdcu_fecha_vencimiento = expiry
    assignment.cdcu_fecha_resolucion = None
    assignment.cdcu_porcentaje_obtenido = None
    assignment.cdcu_tiempo_utilizado = None
    assignment.cdcu_aprobado = None
    assignment.cdcu_permitir_reintento = True
    assignment.cdcu_estado_cuestionario_candidato_id = _state_id(db, "Asignado")
    db.commit()
    db.refresh(assignment)
    return assignment_read(db, assignment)


def candidate_assignment_read(db: Session, assignment: models.CandidatoCuestionario):
    _expire_if_needed(db, assignment)
    questionnaire = get_questionnaire(db, assignment.cdcu_cuestionario_id)
    metrics = _cuestionario_metrics(db, questionnaire.cues_id)
    solicitud = _row(db, "SELECT sol_codigo FROM tbl_solicitud WHERE sol_id=:id", id=questionnaire.cues_solicitud_id)
    return schemas.AsignacionCandidateRead(
        cdcu_id=assignment.cdcu_id,
        cuestionario_id=questionnaire.cues_id,
        cuestionario_nombre=questionnaire.cues_nombre,
        cuestionario_descripcion=questionnaire.cues_descripcion,
        porcentaje_aprobacion=questionnaire.cues_porcentaje_aprobacion,
        solicitud_id=questionnaire.cues_solicitud_id,
        solicitud_codigo=solicitud["sol_codigo"] if solicitud else None,
        fecha_asignacion=assignment.cdcu_fecha_asignacion,
        fecha_inicio=assignment.cdcu_fecha_inicio,
        fecha_vencimiento=assignment.cdcu_fecha_vencimiento,
        fecha_resolucion=assignment.cdcu_fecha_resolucion,
        estado=_state_name(db, assignment.cdcu_estado_cuestionario_candidato_id),
        porcentaje_obtenido=assignment.cdcu_porcentaje_obtenido,
        aprobado=assignment.cdcu_aprobado,
        tiempo_utilizado=assignment.cdcu_tiempo_utilizado,
        **metrics,
    )


def list_candidate_assignments(db: Session, candidate_id: int, estado_id=None, skip=0, limit=100):
    stmt = select(models.CandidatoCuestionario).where(models.CandidatoCuestionario.cdcu_candidato_id == candidate_id)
    if estado_id:
        stmt = stmt.where(models.CandidatoCuestionario.cdcu_estado_cuestionario_candidato_id == estado_id)
    stmt = stmt.order_by(models.CandidatoCuestionario.cdcu_id.desc()).offset(skip).limit(limit)
    return [candidate_assignment_read(db, x) for x in db.scalars(stmt)]


def get_candidate_assignment(db: Session, candidate_id: int, assignment_id: int):
    obj = get_assignment(db, assignment_id)
    if obj.cdcu_candidato_id != candidate_id:
        raise NotFoundError("Asignación no encontrada")
    _expire_if_needed(db, obj)
    return obj


def start_assignment(db: Session, candidate_id: int, assignment_id: int):
    obj = get_candidate_assignment(db, candidate_id, assignment_id)
    state = _state_name(db, obj.cdcu_estado_cuestionario_candidato_id)
    if state == "Vencido":
        raise ConflictError("El cuestionario se encuentra vencido")
    if state != "Asignado":
        raise ConflictError(f"No puede iniciar un cuestionario en estado {state}")
    if now_utc_naive() > obj.cdcu_fecha_vencimiento:
        obj.cdcu_estado_cuestionario_candidato_id = _state_id(db, "Vencido")
        db.commit()
        raise ConflictError("El cuestionario se encuentra vencido")
    obj.cdcu_fecha_inicio = now_utc_naive()
    obj.cdcu_estado_cuestionario_candidato_id = _state_id(db, "En Progreso")
    db.commit()
    db.refresh(obj)
    return candidate_assignment_read(db, obj)


def candidate_questions(db: Session, candidate_id: int, assignment_id: int):
    obj = get_candidate_assignment(db, candidate_id, assignment_id)
    _expire_if_needed(db, obj)
    state = _state_name(db, obj.cdcu_estado_cuestionario_candidato_id)
    if state != "En Progreso":
        raise ConflictError("Las preguntas solo están disponibles mientras el cuestionario está En Progreso")
    rows = _rows(
        db,
        """
        SELECT pc.prcu_id,
               p.preg_id,
               p.preg_texto_pregunta,
               h.hab_nombre,
               n.nvhb_nombre,
               n.nvhb_puntaje_base
          FROM tbl_pregunta_cuestionario pc
          JOIN tbl_pregunta p ON p.preg_id=pc.prcu_pregunta_id
          JOIN tbl_habilidad h ON h.hab_id=p.preg_habilidad_id
          JOIN tbl_nivel_habilidad n ON n.nvhb_id=p.preg_nivel_habilidad_id
         WHERE pc.prcu_cuestionario_id=:qid
         ORDER BY pc.prcu_id
        """,
        qid=obj.cdcu_cuestionario_id,
    )
    answer_map = {
        int(r["rspr_pregunta_cuestionario_id"]): int(r["rspr_opcion_respuesta_id"])
        for r in _rows(
            db,
            """
            SELECT rspr_pregunta_cuestionario_id, rspr_opcion_respuesta_id
              FROM tbl_respuesta_pregunta
             WHERE rspr_candidato_cuestionario_id=:aid
            """,
            aid=obj.cdcu_id,
        )
    }
    result = []
    for row in rows:
        options = _rows(
            db,
            """
            SELECT opcr_id, opcr_texto_opcion
              FROM tbl_opcion_respuesta
             WHERE opcr_pregunta_id=:pid
             ORDER BY opcr_id
            """,
            pid=row["preg_id"],
        )
        result.append(
            schemas.PreguntaCandidateRead(
                prcu_id=row["prcu_id"],
                preg_id=row["preg_id"],
                preg_texto_pregunta=row["preg_texto_pregunta"],
                habilidad_nombre=row["hab_nombre"],
                nivel_nombre=row["nvhb_nombre"],
                puntaje_base=int(row["nvhb_puntaje_base"] or 0),
                opciones=[schemas.OpcionCandidateRead(opcr_id=o["opcr_id"], opcr_texto_opcion=o["opcr_texto_opcion"]) for o in options],
                respuesta_seleccionada_id=answer_map.get(int(row["prcu_id"])),
            )
        )
    return result


def save_answer(db: Session, candidate_id: int, assignment_id: int, payload: schemas.RespuestaSave):
    assignment = get_candidate_assignment(db, candidate_id, assignment_id)
    _expire_if_needed(db, assignment)
    state = _state_name(db, assignment.cdcu_estado_cuestionario_candidato_id)
    if state != "En Progreso":
        raise ConflictError("Solo puede responder un cuestionario En Progreso")
    question = _row(
        db,
        """
        SELECT pc.prcu_id, p.preg_id, n.nvhb_puntaje_base
          FROM tbl_pregunta_cuestionario pc
          JOIN tbl_pregunta p ON p.preg_id=pc.prcu_pregunta_id
          JOIN tbl_nivel_habilidad n ON n.nvhb_id=p.preg_nivel_habilidad_id
         WHERE pc.prcu_id=:prcu_id
           AND pc.prcu_cuestionario_id=:qid
        """,
        prcu_id=payload.pregunta_cuestionario_id,
        qid=assignment.cdcu_cuestionario_id,
    )
    if not question:
        raise Module4Error("La pregunta no pertenece al cuestionario asignado")
    option = _row(
        db,
        """
        SELECT opcr_id, opcr_es_correcta
          FROM tbl_opcion_respuesta
         WHERE opcr_id=:oid AND opcr_pregunta_id=:pid
        """,
        oid=payload.opcion_respuesta_id,
        pid=question["preg_id"],
    )
    if not option:
        raise Module4Error("La opción no pertenece a la pregunta")
    correct = bool(option["opcr_es_correcta"])
    score = int(question["nvhb_puntaje_base"] or 0) if correct else 0
    obj = db.scalar(
        select(models.RespuestaPregunta).where(
            models.RespuestaPregunta.rspr_candidato_cuestionario_id == assignment.cdcu_id,
            models.RespuestaPregunta.rspr_pregunta_cuestionario_id == payload.pregunta_cuestionario_id,
        )
    )
    if obj:
        obj.rspr_opcion_respuesta_id = payload.opcion_respuesta_id
        obj.rspr_es_correcta = correct
        obj.rspr_puntaje_obtenido = score
    else:
        obj = models.RespuestaPregunta(
            rspr_candidato_cuestionario_id=assignment.cdcu_id,
            rspr_es_correcta=correct,
            rspr_puntaje_obtenido=score,
            rspr_opcion_respuesta_id=payload.opcion_respuesta_id,
            rspr_pregunta_cuestionario_id=payload.pregunta_cuestionario_id,
        )
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return schemas.RespuestaRead(
        rspr_id=obj.rspr_id,
        pregunta_cuestionario_id=obj.rspr_pregunta_cuestionario_id,
        opcion_respuesta_id=obj.rspr_opcion_respuesta_id,
    )


def finalize_assignment(db: Session, candidate_id: int, assignment_id: int):
    assignment = get_candidate_assignment(db, candidate_id, assignment_id)
    _expire_if_needed(db, assignment)
    state = _state_name(db, assignment.cdcu_estado_cuestionario_candidato_id)
    if state == "Finalizado":
        raise ConflictError("El cuestionario ya fue finalizado")
    if state != "En Progreso":
        raise ConflictError("Solo puede finalizar un cuestionario En Progreso")
    return _finalize(db, assignment)


def internal_result(db: Session, assignment_id: int):
    assignment = get_assignment(db, assignment_id)
    _expire_if_needed(db, assignment)
    base = assignment_read(db, assignment)
    responses = _rows(
        db,
        """
        SELECT p.preg_texto_pregunta,
               osel.opcr_texto_opcion seleccionada,
               ocor.opcr_texto_opcion correcta,
               r.rspr_es_correcta,
               r.rspr_puntaje_obtenido,
               n.nvhb_puntaje_base
          FROM tbl_respuesta_pregunta r
          JOIN tbl_pregunta_cuestionario pc ON pc.prcu_id=r.rspr_pregunta_cuestionario_id
          JOIN tbl_pregunta p ON p.preg_id=pc.prcu_pregunta_id
          JOIN tbl_nivel_habilidad n ON n.nvhb_id=p.preg_nivel_habilidad_id
          JOIN tbl_opcion_respuesta osel ON osel.opcr_id=r.rspr_opcion_respuesta_id
          JOIN tbl_opcion_respuesta ocor ON ocor.opcr_pregunta_id=p.preg_id AND ocor.opcr_es_correcta=TRUE
         WHERE r.rspr_candidato_cuestionario_id=:aid
         ORDER BY pc.prcu_id
        """,
        aid=assignment_id,
    )
    return schemas.ResultadoInternoRead(
        asignacion=base,
        respuestas=[
            schemas.RespuestaResultadoInterno(
                pregunta=r["preg_texto_pregunta"],
                opcion_seleccionada=r["seleccionada"],
                opcion_correcta=r["correcta"],
                es_correcta=bool(r["rspr_es_correcta"]),
                puntaje_obtenido=int(r["rspr_puntaje_obtenido"] or 0),
                puntaje_maximo=int(r["nvhb_puntaje_base"] or 0),
            )
            for r in responses
        ],
    )


# =============================================================================
# ASIGNACION MASIVA POR SOLICITUD
# =============================================================================

def _validate_future_expiration(fecha_vencimiento: datetime) -> datetime:
    value = _naive(fecha_vencimiento)
    if value <= now_utc_naive():
        raise Module4Error("La fecha de vencimiento debe ser futura")
    return value


def _candidate_ids_for_request(db: Session, solicitud_id: int) -> list[int]:
    rows = _rows(
        db,
        """
        SELECT DISTINCT slcd_candidato_id AS cand_id
          FROM tbl_solicitud_candidato
         WHERE slcd_solicitud_id=:sid
         ORDER BY slcd_candidato_id
        """,
        sid=solicitud_id,
    )
    return [int(row["cand_id"]) for row in rows]


def _already_assigned_candidate_ids(
    db: Session,
    cuestionario_id: int,
    candidate_ids: list[int] | None = None,
) -> set[int]:
    stmt = select(models.CandidatoCuestionario.cdcu_candidato_id).where(
        models.CandidatoCuestionario.cdcu_cuestionario_id == cuestionario_id
    )
    if candidate_ids is not None:
        if not candidate_ids:
            return set()
        stmt = stmt.where(
            models.CandidatoCuestionario.cdcu_candidato_id.in_(candidate_ids)
        )
    return {int(value) for value in db.scalars(stmt)}


def list_available_candidates(
    db: Session,
    questionnaire_id: int,
) -> list[schemas.CandidatoDisponibleRead]:
    questionnaire = get_questionnaire(db, questionnaire_id)

    rows = _rows(
        db,
        """
        SELECT
            c.cand_id,
            c.cand_email,
            c.cand_nombres,
            c.cand_apellido_paterno,
            c.cand_apellido_materno,
            sc.slcd_id,
            sc.slcd_estado_solicitud_candidato_id,
            esc.essc_nombre AS estado_postulacion_nombre,
            cc.cdcu_id AS asignacion_id,
            ecc.escc_nombre AS estado_cuestionario
        FROM tbl_solicitud_candidato sc
        JOIN tbl_candidato c
          ON c.cand_id = sc.slcd_candidato_id
        LEFT JOIN tbl_estado_solicitud_candidato esc
          ON esc.essc_id = sc.slcd_estado_solicitud_candidato_id
        LEFT JOIN tbl_candidato_cuestionario cc
          ON cc.cdcu_candidato_id = c.cand_id
         AND cc.cdcu_cuestionario_id = :qid
        LEFT JOIN tbl_estado_cuestionario_candidato ecc
          ON ecc.escc_id = cc.cdcu_estado_cuestionario_candidato_id
        WHERE sc.slcd_solicitud_id = :sid
        ORDER BY
            c.cand_apellido_paterno,
            c.cand_apellido_materno,
            c.cand_nombres,
            c.cand_id
        """,
        qid=questionnaire_id,
        sid=questionnaire.cues_solicitud_id,
    )

    return [
        schemas.CandidatoDisponibleRead(
            cand_id=int(row["cand_id"]),
            cand_email=row["cand_email"],
            cand_nombres=row["cand_nombres"],
            cand_apellido_paterno=row["cand_apellido_paterno"],
            cand_apellido_materno=row["cand_apellido_materno"],
            solicitud_candidato_id=int(row["slcd_id"]),
            estado_postulacion_id=(
                int(row["slcd_estado_solicitud_candidato_id"])
                if row["slcd_estado_solicitud_candidato_id"] is not None
                else None
            ),
            estado_postulacion_nombre=row["estado_postulacion_nombre"],
            cuestionario_asignado=row["asignacion_id"] is not None,
            asignacion_id=(
                int(row["asignacion_id"])
                if row["asignacion_id"] is not None
                else None
            ),
            estado_cuestionario=row["estado_cuestionario"],
        )
        for row in rows
    ]


def _bulk_create_assignments(
    db: Session,
    questionnaire: models.Cuestionario,
    candidate_ids: list[int],
    fecha_vencimiento: datetime,
) -> list[models.CandidatoCuestionario]:
    if not candidate_ids:
        return []

    state_id = _state_id(db, "Asignado")
    assigned_at = now_utc_naive()

    objects = [
        models.CandidatoCuestionario(
            cdcu_candidato_id=candidate_id,
            cdcu_cuestionario_id=questionnaire.cues_id,
            cdcu_fecha_asignacion=assigned_at,
            cdcu_fecha_inicio=None,
            cdcu_fecha_vencimiento=fecha_vencimiento,
            cdcu_fecha_resolucion=None,
            cdcu_porcentaje_obtenido=None,
            cdcu_estado_cuestionario_candidato_id=state_id,
            cdcu_tiempo_utilizado=None,
            cdcu_permitir_reintento=False,
            cdcu_aprobado=None,
        )
        for candidate_id in candidate_ids
    ]

    db.add_all(objects)
    try:
        # Una sola transaccion: si una fila falla, no se persiste ninguna.
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(
            "No fue posible completar la asignacion masiva; no se creo ninguna asignacion"
        )

    for obj in objects:
        db.refresh(obj)
    return objects


def assign_questionnaire_bulk(
    db: Session,
    questionnaire_id: int,
    payload: schemas.AsignacionMasivaCreate,
) -> schemas.AsignacionMasivaRead:
    questionnaire = get_questionnaire(db, questionnaire_id)
    _validate_questionnaire_for_assignment(db, questionnaire_id)
    expiration = _validate_future_expiration(payload.fecha_vencimiento)

    request_candidate_ids = set(
        _candidate_ids_for_request(db, questionnaire.cues_solicitud_id)
    )
    requested_ids = list(payload.candidato_ids)

    not_linked = sorted(set(requested_ids) - request_candidate_ids)
    if not_linked:
        raise ConflictError(
            "Los siguientes candidatos no estan asociados a la solicitud "
            f"{questionnaire.cues_solicitud_id}: {not_linked}. "
            "No se creo ninguna asignacion."
        )

    already_assigned = sorted(
        _already_assigned_candidate_ids(db, questionnaire_id, requested_ids)
    )
    if already_assigned:
        raise ConflictError(
            "Los siguientes candidatos ya tienen asignado este cuestionario: "
            f"{already_assigned}. No se creo ninguna asignacion."
        )

    objects = _bulk_create_assignments(
        db,
        questionnaire,
        requested_ids,
        expiration,
    )

    return schemas.AsignacionMasivaRead(
        cuestionario_id=questionnaire.cues_id,
        solicitud_id=questionnaire.cues_solicitud_id,
        fecha_vencimiento=expiration,
        total_candidatos_solicitud=len(request_candidate_ids),
        total_solicitados=len(requested_ids),
        total_asignados=len(objects),
        total_omitidos_ya_asignados=0,
        asignaciones=[assignment_read(db, obj) for obj in objects],
    )


def assign_questionnaire_to_all(
    db: Session,
    questionnaire_id: int,
    payload: schemas.AsignarTodosCreate,
) -> schemas.AsignacionMasivaRead:
    questionnaire = get_questionnaire(db, questionnaire_id)
    _validate_questionnaire_for_assignment(db, questionnaire_id)
    expiration = _validate_future_expiration(payload.fecha_vencimiento)

    all_candidate_ids = _candidate_ids_for_request(
        db,
        questionnaire.cues_solicitud_id,
    )
    if not all_candidate_ids:
        raise ConflictError(
            "La solicitud asociada al cuestionario no tiene candidatos"
        )

    already_assigned = _already_assigned_candidate_ids(
        db,
        questionnaire_id,
        all_candidate_ids,
    )
    pending_ids = [
        candidate_id
        for candidate_id in all_candidate_ids
        if candidate_id not in already_assigned
    ]

    objects = _bulk_create_assignments(
        db,
        questionnaire,
        pending_ids,
        expiration,
    )

    return schemas.AsignacionMasivaRead(
        cuestionario_id=questionnaire.cues_id,
        solicitud_id=questionnaire.cues_solicitud_id,
        fecha_vencimiento=expiration,
        total_candidatos_solicitud=len(all_candidate_ids),
        total_solicitados=len(all_candidate_ids),
        total_asignados=len(objects),
        total_omitidos_ya_asignados=len(already_assigned),
        asignaciones=[assignment_read(db, obj) for obj in objects],
    )
