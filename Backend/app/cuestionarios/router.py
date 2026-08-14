from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permissions
from app.database import get_db
from app.usuarios.models import Usuario

from . import schemas, services
from .dependencies import get_current_candidate_id


router = APIRouter(tags=["Cuestionarios y Evaluaciones"])


def _translate(exc: services.Module4Error) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.message)


# ===========================================================================
# BANCO DE PREGUNTAS Y OPCIONES - CUEST_CREATE
# ===========================================================================

@router.get("/preguntas", response_model=list[schemas.PreguntaAdminRead])
def listar_preguntas(
    q: str | None = None,
    habilidad_id: int | None = Query(default=None, ge=1),
    nivel_id: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    return services.list_questions(db, q, habilidad_id, nivel_id, skip, limit)


@router.post("/preguntas", response_model=schemas.PreguntaAdminRead, status_code=201)
def crear_pregunta(
    payload: schemas.PreguntaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.create_question(db, payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.get("/preguntas/{pregunta_id}", response_model=schemas.PreguntaAdminRead)
def obtener_pregunta(
    pregunta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.question_read(db, services.get_question(db, pregunta_id))
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.put("/preguntas/{pregunta_id}", response_model=schemas.PreguntaAdminRead)
def reemplazar_pregunta(
    pregunta_id: int,
    payload: schemas.PreguntaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.replace_question(db, services.get_question(db, pregunta_id), payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.patch("/preguntas/{pregunta_id}", response_model=schemas.PreguntaAdminRead)
def editar_pregunta(
    pregunta_id: int,
    payload: schemas.PreguntaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.update_question(db, services.get_question(db, pregunta_id), payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.delete("/preguntas/{pregunta_id}", status_code=204)
def eliminar_pregunta(
    pregunta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        services.delete_question(db, services.get_question(db, pregunta_id))
    except services.Module4Error as exc:
        raise _translate(exc) from exc
    return Response(status_code=204)


@router.get("/preguntas/{pregunta_id}/opciones", response_model=list[schemas.OpcionAdminRead])
def listar_opciones(
    pregunta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.question_read(db, services.get_question(db, pregunta_id)).opciones
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post("/preguntas/{pregunta_id}/opciones", response_model=schemas.OpcionAdminRead, status_code=201)
def crear_opcion(
    pregunta_id: int,
    payload: schemas.OpcionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.create_option(db, pregunta_id, payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.put("/preguntas/{pregunta_id}/opciones/{opcion_id}", response_model=schemas.OpcionAdminRead)
def reemplazar_opcion(
    pregunta_id: int,
    opcion_id: int,
    payload: schemas.OpcionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.replace_option(db, pregunta_id, opcion_id, payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.patch("/preguntas/{pregunta_id}/opciones/{opcion_id}", response_model=schemas.OpcionAdminRead)
def editar_opcion(
    pregunta_id: int,
    opcion_id: int,
    payload: schemas.OpcionUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.update_option(db, pregunta_id, opcion_id, payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.delete("/preguntas/{pregunta_id}/opciones/{opcion_id}", status_code=204)
def eliminar_opcion(
    pregunta_id: int,
    opcion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        services.delete_option(db, pregunta_id, opcion_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc
    return Response(status_code=204)


# ===========================================================================
# COLECCION CUESTIONARIOS
# ===========================================================================

@router.get("/cuestionarios", response_model=list[schemas.CuestionarioRead])
def listar_cuestionarios(
    q: str | None = None,
    solicitud_id: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_VIEW", "CUEST_CREATE", match_all=False)),
):
    return services.list_questionnaires(db, q, solicitud_id, skip, limit)


@router.post("/cuestionarios", response_model=schemas.CuestionarioRead, status_code=201)
def crear_cuestionario(
    payload: schemas.CuestionarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.create_questionnaire(db, payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


# IMPORTANTE: rutas /me ANTES de /cuestionarios/{cuestionario_id}.


# ---------------------------------------------------------------------------
# ASIGNACION MASIVA POR SOLICITUD
# ---------------------------------------------------------------------------

@router.get(
    "/cuestionarios/{cuestionario_id}/candidatos-disponibles",
    response_model=list[schemas.CandidatoDisponibleRead],
)
def candidatos_disponibles_cuestionario(
    cuestionario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(
        require_permissions("CUEST_ASSIGN", "CUEST_VIEW", match_all=False)
    ),
):
    try:
        return services.list_available_candidates(db, cuestionario_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post(
    "/cuestionarios/{cuestionario_id}/asignar-masivo",
    response_model=schemas.AsignacionMasivaRead,
    status_code=201,
)
def asignar_cuestionario_masivo(
    cuestionario_id: int,
    payload: schemas.AsignacionMasivaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_ASSIGN")),
):
    try:
        return services.assign_questionnaire_bulk(
            db,
            cuestionario_id,
            payload,
        )
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post(
    "/cuestionarios/{cuestionario_id}/asignar-todos",
    response_model=schemas.AsignacionMasivaRead,
    status_code=201,
)
def asignar_cuestionario_a_todos(
    cuestionario_id: int,
    payload: schemas.AsignarTodosCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_ASSIGN")),
):
    try:
        return services.assign_questionnaire_to_all(
            db,
            cuestionario_id,
            payload,
        )
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.get("/cuestionarios/me", response_model=list[schemas.AsignacionCandidateRead])
def mis_cuestionarios(
    estado_id: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    candidato_id: int = Depends(get_current_candidate_id),
):
    return services.list_candidate_assignments(db, candidato_id, estado_id, skip, limit)


@router.get("/cuestionarios/me/{asignacion_id}", response_model=schemas.AsignacionCandidateRead)
def mi_cuestionario(
    asignacion_id: int,
    db: Session = Depends(get_db),
    candidato_id: int = Depends(get_current_candidate_id),
):
    try:
        obj = services.get_candidate_assignment(db, candidato_id, asignacion_id)
        return services.candidate_assignment_read(db, obj)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post("/cuestionarios/me/{asignacion_id}/iniciar", response_model=schemas.AsignacionCandidateRead)
def iniciar_mi_cuestionario(
    asignacion_id: int,
    db: Session = Depends(get_db),
    candidato_id: int = Depends(get_current_candidate_id),
):
    try:
        return services.start_assignment(db, candidato_id, asignacion_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.get("/cuestionarios/me/{asignacion_id}/preguntas", response_model=list[schemas.PreguntaCandidateRead])
def mis_preguntas(
    asignacion_id: int,
    db: Session = Depends(get_db),
    candidato_id: int = Depends(get_current_candidate_id),
):
    try:
        return services.candidate_questions(db, candidato_id, asignacion_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.put("/cuestionarios/me/{asignacion_id}/respuesta", response_model=schemas.RespuestaRead)
def guardar_respuesta(
    asignacion_id: int,
    payload: schemas.RespuestaSave,
    db: Session = Depends(get_db),
    candidato_id: int = Depends(get_current_candidate_id),
):
    try:
        return services.save_answer(db, candidato_id, asignacion_id, payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post("/cuestionarios/me/{asignacion_id}/finalizar", response_model=schemas.FinalizarRead)
def finalizar_mi_cuestionario(
    asignacion_id: int,
    db: Session = Depends(get_db),
    candidato_id: int = Depends(get_current_candidate_id),
):
    try:
        return services.finalize_assignment(db, candidato_id, asignacion_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


# ===========================================================================
# DETALLE / COMPOSICION DE CUESTIONARIO
# ===========================================================================

@router.get("/cuestionarios/{cuestionario_id}", response_model=schemas.CuestionarioRead)
def obtener_cuestionario(
    cuestionario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_VIEW", "CUEST_CREATE", match_all=False)),
):
    try:
        return services.questionnaire_read(db, services.get_questionnaire(db, cuestionario_id))
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.put("/cuestionarios/{cuestionario_id}", response_model=schemas.CuestionarioRead)
def reemplazar_cuestionario(
    cuestionario_id: int,
    payload: schemas.CuestionarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.replace_questionnaire(db, services.get_questionnaire(db, cuestionario_id), payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.patch("/cuestionarios/{cuestionario_id}", response_model=schemas.CuestionarioRead)
def editar_cuestionario(
    cuestionario_id: int,
    payload: schemas.CuestionarioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.update_questionnaire(db, services.get_questionnaire(db, cuestionario_id), payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.delete("/cuestionarios/{cuestionario_id}", status_code=204)
def eliminar_cuestionario(
    cuestionario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        services.delete_questionnaire(db, services.get_questionnaire(db, cuestionario_id))
    except services.Module4Error as exc:
        raise _translate(exc) from exc
    return Response(status_code=204)


@router.get("/cuestionarios/{cuestionario_id}/preguntas", response_model=list[schemas.PreguntaAdminRead])
def preguntas_cuestionario(
    cuestionario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_VIEW", "CUEST_CREATE", match_all=False)),
):
    try:
        return services.list_questionnaire_questions(db, cuestionario_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post("/cuestionarios/{cuestionario_id}/preguntas/{pregunta_id}", response_model=list[schemas.PreguntaAdminRead])
def agregar_pregunta(
    cuestionario_id: int,
    pregunta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        return services.add_question_to_questionnaire(db, cuestionario_id, pregunta_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.delete("/cuestionarios/{cuestionario_id}/preguntas/{pregunta_id}", status_code=204)
def quitar_pregunta(
    cuestionario_id: int,
    pregunta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_CREATE")),
):
    try:
        services.remove_question_from_questionnaire(db, cuestionario_id, pregunta_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc
    return Response(status_code=204)


@router.post("/cuestionarios/{cuestionario_id}/asignar", response_model=schemas.AsignacionRead, status_code=201)
def asignar_cuestionario(
    cuestionario_id: int,
    payload: schemas.AsignacionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_ASSIGN")),
):
    try:
        return services.assign_questionnaire(db, cuestionario_id, payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.get("/cuestionarios/{cuestionario_id}/resultados", response_model=list[schemas.AsignacionRead])
def resultados_cuestionario(
    cuestionario_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_VIEW")),
):
    try:
        services.get_questionnaire(db, cuestionario_id)
        return services.list_assignments(db, questionnaire_id=cuestionario_id, skip=skip, limit=limit)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


# ===========================================================================
# ASIGNACIONES / RESULTADOS INTERNOS
# ===========================================================================

@router.get("/asignaciones-cuestionario", response_model=list[schemas.AsignacionRead])
def listar_asignaciones(
    cuestionario_id: int | None = Query(default=None, ge=1),
    candidato_id: int | None = Query(default=None, ge=1),
    estado_id: int | None = Query(default=None, ge=1),
    aprobado: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_VIEW")),
):
    return services.list_assignments(db, cuestionario_id, candidato_id, estado_id, aprobado, skip, limit)


@router.get("/candidatos/{candidato_id}/cuestionarios", response_model=list[schemas.AsignacionRead])
def cuestionarios_candidato_interno(
    candidato_id: int,
    estado_id: int | None = Query(default=None, ge=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_VIEW")),
):
    return services.list_assignments(db, candidato_id=candidato_id, estado_id=estado_id, skip=skip, limit=limit)


@router.get("/asignaciones-cuestionario/{asignacion_id}", response_model=schemas.AsignacionRead)
def obtener_asignacion(
    asignacion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_VIEW")),
):
    try:
        return services.assignment_read(db, services.get_assignment(db, asignacion_id))
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post("/asignaciones-cuestionario/{asignacion_id}/cancelar", response_model=schemas.AsignacionRead)
def cancelar_asignacion(
    asignacion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_ASSIGN")),
):
    try:
        return services.cancel_assignment(db, services.get_assignment(db, asignacion_id))
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post("/asignaciones-cuestionario/{asignacion_id}/error-tecnico", response_model=schemas.AsignacionRead)
def declarar_error_tecnico(
    asignacion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_ASSIGN")),
):
    try:
        return services.mark_technical_error(db, services.get_assignment(db, asignacion_id))
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.post("/asignaciones-cuestionario/{asignacion_id}/habilitar-reintento", response_model=schemas.AsignacionRead)
def habilitar_reintento(
    asignacion_id: int,
    payload: schemas.ReintentoEnable,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_ASSIGN")),
):
    try:
        return services.enable_retry(db, services.get_assignment(db, asignacion_id), payload)
    except services.Module4Error as exc:
        raise _translate(exc) from exc


@router.get("/asignaciones-cuestionario/{asignacion_id}/resultado", response_model=schemas.ResultadoInternoRead)
def resultado_asignacion(
    asignacion_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CUEST_VIEW")),
):
    try:
        return services.internal_result(db, asignacion_id)
    except services.Module4Error as exc:
        raise _translate(exc) from exc
