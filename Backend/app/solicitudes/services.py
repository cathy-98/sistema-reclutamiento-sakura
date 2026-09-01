from __future__ import annotations

import os
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import func, inspect, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.catalogos.models import (
    Cargo,
    EstadoSolicitud,
    EstadoSolicitudCandidato,
    Habilidad,
    Modalidad,
    NivelHabilidad,
    PrioridadSolicitud,
    TipoContrato,
)
from app.clientes.models import Cliente
from app.solicitudes import models, schemas
from app.usuarios.models import Usuario


TZ_CHILE = ZoneInfo("America/Santiago")
ACTIVE_USER_STATUS_NAME = os.getenv("ACTIVE_USER_STATUS_NAME", "Activo")
RECRUITER_ROLE_NAME = "Reclutador"
INITIAL_REQUEST_STATUS_NAME = "Pendiente"

STATE_TRANSITIONS: dict[str, set[str]] = {
    "pendiente": {"en publicacion", "cancelado"},
    "en publicacion": {"en entrevistas", "pausado", "cancelado"},
    "en entrevistas": {"en publicacion", "pausado", "cerrado", "cancelado"},
    "pausado": {"en publicacion", "cancelado"},
    "cerrado": set(),
    "cancelado": set(),
}

TERMINAL_STATE_NAMES = {"cerrado", "cancelado"}
COMMENT_REQUIRED_STATE_NAMES = {"pausado", "cancelado", "cerrado"}


class SolicitudModuleError(Exception):
    def __init__(self, message: str, *, constraint: str | None = None):
        super().__init__(message)
        self.message = message
        self.constraint = constraint


class NotFoundError(SolicitudModuleError):
    pass


class ConflictError(SolicitudModuleError):
    pass


class ValidationError(SolicitudModuleError):
    pass


def now_chile_naive() -> datetime:
    return datetime.now(TZ_CHILE).replace(tzinfo=None)


def _constraint_name(exc: IntegrityError) -> str | None:
    original = getattr(exc, "orig", None)
    diagnostic = getattr(original, "diag", None)
    return getattr(diagnostic, "constraint_name", None) if diagnostic else None


def _translate_integrity(exc: IntegrityError) -> SolicitudModuleError:
    constraint = _constraint_name(exc)
    conflicts = {
        "uq_tbl_solicitud_codigo": "Ya existe una solicitud con ese código",
        "uq_tbl_solicitud_habilidad": "La habilidad ya está asociada a la solicitud",
    }
    validation_constraints = {
        "fk_tbl_solicitud_cargo",
        "fk_tbl_solicitud_cliente",
        "fk_tbl_solicitud_estado",
        "fk_tbl_solicitud_prioridad",
        "fk_tbl_solicitud_usuario_creador",
        "fk_tbl_solicitud_usuario_asignado",
        "fk_tbl_solicitud_modalidad",
        "fk_tbl_solicitud_tipo_contrato",
        "fk_tbl_solicitud_habilidad_habilidad",
        "fk_tbl_solicitud_habilidad_nivel",
        "chk_tbl_solicitud_codigo",
        "chk_tbl_solicitud_vacantes",
        "chk_tbl_solicitud_salarios",
        "chk_tbl_solicitud_horario",
        "chk_tbl_solicitud_habilidad_anios",
    }
    if constraint in conflicts:
        return ConflictError(conflicts[constraint], constraint=constraint)
    if constraint in validation_constraints:
        return ValidationError("La operación contiene referencias o valores no válidos", constraint=constraint)
    return ConflictError("La operación viola una restricción de integridad", constraint=constraint)


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _translate_integrity(exc) from exc


def _solicitud_stmt():
    return select(models.Solicitud).options(
        selectinload(models.Solicitud.habilidades),
        selectinload(models.Solicitud.cliente),
        selectinload(models.Solicitud.usuario_creador),
        selectinload(models.Solicitud.usuario_asignado),
        selectinload(models.Solicitud.estado),
        selectinload(models.Solicitud.prioridad),
        selectinload(models.Solicitud.cargo),
        selectinload(models.Solicitud.modalidad),
        selectinload(models.Solicitud.tipo_contrato),
    )


def get_solicitud(db: Session, solicitud_id: int) -> models.Solicitud:
    solicitud = db.scalar(_solicitud_stmt().where(models.Solicitud.sol_id == solicitud_id))
    if solicitud is None:
        raise NotFoundError(f"Solicitud con ID {solicitud_id} no encontrada")
    return solicitud


def list_solicitudes(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    estado_id: int | None = None,
    prioridad_id: int | None = None,
    cargo_id: int | None = None,
    cliente_id: int | None = None,
    usuario_asignado_id: int | None = None,
    modalidad_id: int | None = None,
    tipo_contrato_id: int | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
) -> list[models.Solicitud]:
    stmt = _solicitud_stmt()
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                models.Solicitud.sol_codigo.ilike(term),
                models.Solicitud.sol_titulo.ilike(term),
                models.Solicitud.sol_descripcion.ilike(term),
                models.Solicitud.sol_observacion.ilike(term),
            )
        )
    if estado_id is not None:
        stmt = stmt.where(models.Solicitud.sol_estado_solicitud_id == estado_id)
    if prioridad_id is not None:
        stmt = stmt.where(models.Solicitud.sol_prioridad_id == prioridad_id)
    if cargo_id is not None:
        stmt = stmt.where(models.Solicitud.sol_cargo_id == cargo_id)
    if cliente_id is not None:
        stmt = stmt.where(models.Solicitud.sol_cliente_id == cliente_id)
    if usuario_asignado_id is not None:
        stmt = stmt.where(models.Solicitud.sol_usuario_asignado_id == usuario_asignado_id)
    if modalidad_id is not None:
        stmt = stmt.where(models.Solicitud.sol_modalidad_id == modalidad_id)
    if tipo_contrato_id is not None:
        stmt = stmt.where(models.Solicitud.sol_tipo_contrato_id == tipo_contrato_id)
    if fecha_desde is not None:
        stmt = stmt.where(models.Solicitud.sol_fecha_creacion >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(models.Solicitud.sol_fecha_creacion <= fecha_hasta)

    stmt = stmt.order_by(models.Solicitud.sol_id.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).unique().all())


def _get_state_by_name(db: Session, name: str) -> EstadoSolicitud:
    state = db.scalar(
        select(EstadoSolicitud).where(EstadoSolicitud.essl_nombre.ilike(name))
    )
    if state is None:
        raise ValidationError(f"No existe el estado de solicitud '{name}' en tbl_estado_solicitud")
    return state


def _get_state(db: Session, state_id: int | None) -> EstadoSolicitud:
    if state_id is None:
        raise ValidationError("La solicitud no posee estado configurado")
    state = db.get(EstadoSolicitud, state_id)
    if state is None:
        raise ValidationError(f"Estado de solicitud {state_id} no existe")
    return state


def _validate_recruiter(db: Session, usuario_id: int | None) -> None:
    if usuario_id is None:
        return
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise ValidationError(f"Usuario asignado {usuario_id} no existe")
    role_name = usuario.rol.rol_nombre if usuario.rol else None
    if not role_name or role_name.casefold() != RECRUITER_ROLE_NAME.casefold():
        raise ValidationError("El usuario asignado debe tener rol Reclutador")
    state_name = usuario.estado.esusr_nombre if usuario.estado else None
    if not state_name or state_name.casefold() != ACTIVE_USER_STATUS_NAME.casefold():
        raise ValidationError("El reclutador asignado debe estar Activo")


def _validate_refs(
    db: Session,
    *,
    cargo_id: int | None,
    prioridad_id: int | None,
    cliente_id: int | None,
    usuario_asignado_id: int | None,
    modalidad_id: int | None,
    tipo_contrato_id: int | None,
) -> None:
    if cliente_id is None or db.get(Cliente, cliente_id) is None:
        raise ValidationError(f"Cliente {cliente_id} no existe")
    if cargo_id is not None and db.get(Cargo, cargo_id) is None:
        raise ValidationError(f"Cargo {cargo_id} no existe")
    if prioridad_id is not None and db.get(PrioridadSolicitud, prioridad_id) is None:
        raise ValidationError(f"Prioridad {prioridad_id} no existe")
    if modalidad_id is not None and db.get(Modalidad, modalidad_id) is None:
        raise ValidationError(f"Modalidad {modalidad_id} no existe")
    if tipo_contrato_id is not None and db.get(TipoContrato, tipo_contrato_id) is None:
        raise ValidationError(f"Tipo de contrato {tipo_contrato_id} no existe")
    _validate_recruiter(db, usuario_asignado_id)


def _validate_ranges(data: dict[str, Any]) -> None:
    salario_min = data.get("sol_salario_min")
    salario_max = data.get("sol_salario_max")
    if salario_min is not None and salario_max is not None and salario_min > salario_max:
        raise ValidationError("sol_salario_min no puede ser mayor que sol_salario_max")

    hora_inicio = data.get("sol_hora_inicio_jornada")
    hora_fin = data.get("sol_hora_fin_jornada")
    if hora_inicio is not None and hora_fin is not None and hora_inicio >= hora_fin:
        raise ValidationError("La hora de inicio de jornada debe ser anterior a la hora de fin")

    fecha_inicio = data.get("sol_fecha_inicio_busqueda")
    fecha_cierre = data.get("sol_fecha_cierre_busqueda")
    if fecha_inicio is not None and fecha_cierre is not None and fecha_cierre < fecha_inicio:
        raise ValidationError("La fecha de cierre de búsqueda no puede ser anterior a la fecha de inicio")


def _validate_habilidad_refs(db: Session, habilidades: list[schemas.SolicitudHabilidadCreate]) -> None:
    ids = [h.solhb_habilidad_id for h in habilidades]
    if len(ids) != len(set(ids)):
        raise ValidationError("No se puede repetir una habilidad dentro de la solicitud")
    for item in habilidades:
        if db.get(Habilidad, item.solhb_habilidad_id) is None:
            raise ValidationError(f"Habilidad {item.solhb_habilidad_id} no existe")
        if item.solhb_nivel_habilidad_id is not None:
            if db.get(NivelHabilidad, item.solhb_nivel_habilidad_id) is None:
                raise ValidationError(f"Nivel de habilidad {item.solhb_nivel_habilidad_id} no existe")


def _ensure_exclusive_skill(items: list[schemas.SolicitudHabilidadCreate]) -> None:
    if not items or not any(item.solhb_es_excluyente for item in items):
        raise ValidationError("Toda solicitud debe tener al menos una habilidad excluyente")


def _codigo_from_id(solicitud_id: int) -> str:
    if solicitud_id > 999999:
        raise ValidationError("Se alcanzó el máximo permitido para códigos SOL-999999")
    return f"SOL-{solicitud_id:06d}"


def create_solicitud(
    db: Session,
    payload: schemas.SolicitudCreate,
    *,
    creator_user_id: int,
) -> models.Solicitud:
    _validate_refs(
        db,
        cargo_id=payload.sol_cargo_id,
        prioridad_id=payload.sol_prioridad_id,
        cliente_id=payload.sol_cliente_id,
        usuario_asignado_id=payload.sol_usuario_asignado_id,
        modalidad_id=payload.sol_modalidad_id,
        tipo_contrato_id=payload.sol_tipo_contrato_id,
    )
    _validate_habilidad_refs(db, payload.habilidades)
    _ensure_exclusive_skill(payload.habilidades)

    initial_state = _get_state_by_name(db, INITIAL_REQUEST_STATUS_NAME)
    data = payload.model_dump(exclude={"habilidades"})
    _validate_ranges(data)
    data.update(
        sol_codigo=None,
        sol_fecha_creacion=now_chile_naive(),
        sol_usuario_creador_id=creator_user_id,
        sol_estado_solicitud_id=initial_state.essl_id,
    )

    solicitud = models.Solicitud(**data)
    db.add(solicitud)
    try:
        db.flush()
        solicitud.sol_codigo = _codigo_from_id(solicitud.sol_id)
        for item in payload.habilidades:
            solicitud.habilidades.append(
                models.SolicitudHabilidad(
                    solhb_habilidad_id=item.solhb_habilidad_id,
                    solhb_nivel_habilidad_id=item.solhb_nivel_habilidad_id,
                    solhb_anios_experiencia_req=item.solhb_anios_experiencia_req,
                    solhb_es_excluyente=item.solhb_es_excluyente,
                )
            )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _translate_integrity(exc) from exc
    except SolicitudModuleError:
        db.rollback()
        raise

    return get_solicitud(db, solicitud.sol_id)


def _final_update_data(solicitud: models.Solicitud, data: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "sol_titulo",
        "sol_descripcion",
        "sol_observacion",
        "sol_cantidad_vacantes",
        "sol_salario_min",
        "sol_salario_max",
        "sol_fecha_inicio_busqueda",
        "sol_fecha_cierre_busqueda",
        "sol_fecha_inicio_cliente",
        "sol_hora_inicio_jornada",
        "sol_hora_fin_jornada",
        "sol_cargo_id",
        "sol_prioridad_id",
        "sol_cliente_id",
        "sol_usuario_asignado_id",
        "sol_modalidad_id",
        "sol_tipo_contrato_id",
    )
    return {field: data.get(field, getattr(solicitud, field)) for field in fields}


def replace_solicitud(
    db: Session,
    solicitud: models.Solicitud,
    payload: schemas.SolicitudReplace,
) -> models.Solicitud:
    data = payload.model_dump()
    _validate_refs(
        db,
        cargo_id=data.get("sol_cargo_id"),
        prioridad_id=data.get("sol_prioridad_id"),
        cliente_id=data.get("sol_cliente_id"),
        usuario_asignado_id=data.get("sol_usuario_asignado_id"),
        modalidad_id=data.get("sol_modalidad_id"),
        tipo_contrato_id=data.get("sol_tipo_contrato_id"),
    )
    _validate_ranges(data)
    for field, value in data.items():
        setattr(solicitud, field, value)
    _commit(db)
    return get_solicitud(db, solicitud.sol_id)


def update_solicitud(
    db: Session,
    solicitud: models.Solicitud,
    payload: schemas.SolicitudUpdate,
) -> models.Solicitud:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo para actualizar")

    final = _final_update_data(solicitud, data)
    _validate_refs(
        db,
        cargo_id=final.get("sol_cargo_id"),
        prioridad_id=final.get("sol_prioridad_id"),
        cliente_id=final.get("sol_cliente_id"),
        usuario_asignado_id=final.get("sol_usuario_asignado_id"),
        modalidad_id=final.get("sol_modalidad_id"),
        tipo_contrato_id=final.get("sol_tipo_contrato_id"),
    )
    _validate_ranges(final)
    for field, value in data.items():
        setattr(solicitud, field, value)
    _commit(db)
    return get_solicitud(db, solicitud.sol_id)


def _assert_ready_for_in_progress(db: Session, solicitud: models.Solicitud) -> None:
    missing: list[str] = []
    if solicitud.sol_cliente_id is None:
        missing.append("cliente")
    if solicitud.sol_cargo_id is None:
        missing.append("cargo")
    if not solicitud.sol_cantidad_vacantes or solicitud.sol_cantidad_vacantes <= 0:
        missing.append("cantidad_vacantes")
    if solicitud.sol_usuario_asignado_id is None:
        missing.append("reclutador_asignado")
    if solicitud.sol_modalidad_id is None:
        missing.append("modalidad")
    if solicitud.sol_tipo_contrato_id is None:
        missing.append("tipo_contrato")
    if not solicitud.habilidades_excluyentes:
        missing.append("habilidad_excluyente")
    if missing:
        raise ValidationError(
            "La solicitud no está completa para pasar a En Publicacion. Faltan: " + ", ".join(missing)
        )
    _validate_recruiter(db, solicitud.sol_usuario_asignado_id)


def get_target_state_permission(db: Session, target_state_id: int) -> str:
    target = _get_state(db, target_state_id)
    target_name = (target.essl_nombre or "").casefold()
    return "SOL_DELETE" if target_name in TERMINAL_STATE_NAMES else "SOL_UPDATE"


def change_state(
    db: Session,
    solicitud: models.Solicitud,
    payload: schemas.SolicitudEstadoUpdate,
    *,
    actor_user_id: int,
) -> models.Solicitud:
    current = _get_state(db, solicitud.sol_estado_solicitud_id)
    target = _get_state(db, payload.sol_estado_solicitud_id)

    current_name = (current.essl_nombre or "").casefold()
    target_name = (target.essl_nombre or "").casefold()

    if current.essl_id == target.essl_id:
        raise ValidationError("La solicitud ya se encuentra en el estado solicitado")

    allowed = STATE_TRANSITIONS.get(current_name)
    if allowed is None:
        raise ValidationError(f"Estado actual no soportado por el flujo: {current.essl_nombre}")
    if target_name not in allowed:
        raise ConflictError(
            f"Transición no permitida: {current.essl_nombre} -> {target.essl_nombre}"
        )

    if target_name in COMMENT_REQUIRED_STATE_NAMES and not payload.observacion:
        raise ValidationError(f"Debe informar una observación para pasar a {target.essl_nombre}")

    if target_name == "en publicacion":
        _assert_ready_for_in_progress(db, solicitud)

    closure_warning = None
    if target_name == "cerrado" and inspect(db.get_bind()).has_table("tbl_solicitud_candidato"):
        contratado = db.scalar(
            select(EstadoSolicitudCandidato).where(
                func.lower(EstadoSolicitudCandidato.essc_nombre) == "contratado"
            )
        )
        if contratado is None:
            raise ValidationError("No existe el estado de postulación Contratado")
        contratados = db.scalar(
            select(func.count(models.SolicitudCandidato.slcd_id)).where(
                models.SolicitudCandidato.slcd_solicitud_id == solicitud.sol_id,
                models.SolicitudCandidato.slcd_estado_solicitud_candidato_id == contratado.essc_id,
            )
        ) or 0
        if contratados == 0:
            raise ConflictError(
                "La solicitud no puede cerrarse porque no existe ningún candidato contratado. "
                "Si el proceso finalizó sin contratación, utilice Cancelado."
            )
        vacantes = solicitud.sol_cantidad_vacantes or 0
        if contratados < vacantes:
            closure_warning = (
                f"La solicitud fue cerrada con {contratados} de {vacantes} vacante(s) cubierta(s)."
            )
    solicitud._audit_user_id = actor_user_id
    solicitud._audit_comment = payload.observacion or (
        f"Cambio de estado: {current.essl_nombre} -> {target.essl_nombre}"
    )
    solicitud.sol_estado_solicitud_id = target.essl_id
    _commit(db)
    result = get_solicitud(db, solicitud.sol_id)
    result._closure_warning = closure_warning
    return result


def list_habilidades(db: Session, solicitud_id: int) -> list[models.SolicitudHabilidad]:
    solicitud = get_solicitud(db, solicitud_id)
    return list(solicitud.habilidades)


def add_habilidades(
    db: Session,
    solicitud: models.Solicitud,
    payload: list[schemas.SolicitudHabilidadCreate],
) -> list[models.SolicitudHabilidad]:
    if not payload:
        raise ValidationError("Debe enviar al menos una habilidad")
    _validate_habilidad_refs(db, payload)
    existing = {item.solhb_habilidad_id for item in solicitud.habilidades}
    incoming = {item.solhb_habilidad_id for item in payload}
    duplicate = existing & incoming
    if duplicate:
        raise ConflictError(f"Las habilidades {sorted(duplicate)} ya están asociadas a la solicitud")

    for item in payload:
        solicitud.habilidades.append(
            models.SolicitudHabilidad(
                solhb_habilidad_id=item.solhb_habilidad_id,
                solhb_nivel_habilidad_id=item.solhb_nivel_habilidad_id,
                solhb_anios_experiencia_req=item.solhb_anios_experiencia_req,
                solhb_es_excluyente=item.solhb_es_excluyente,
            )
        )
    _commit(db)
    return list(get_solicitud(db, solicitud.sol_id).habilidades)


def get_habilidad_relacion(
    db: Session,
    solicitud_id: int,
    habilidad_id: int,
) -> models.SolicitudHabilidad:
    relation = db.scalar(
        select(models.SolicitudHabilidad).where(
            models.SolicitudHabilidad.solhb_solicitud_id == solicitud_id,
            models.SolicitudHabilidad.solhb_habilidad_id == habilidad_id,
        )
    )
    if relation is None:
        raise NotFoundError(
            f"La habilidad {habilidad_id} no está asociada a la solicitud {solicitud_id}"
        )
    return relation


def update_habilidad(
    db: Session,
    solicitud: models.Solicitud,
    relation: models.SolicitudHabilidad,
    payload: schemas.SolicitudHabilidadUpdate,
) -> models.SolicitudHabilidad:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo para actualizar")
    if "solhb_nivel_habilidad_id" in data and data["solhb_nivel_habilidad_id"] is not None:
        if db.get(NivelHabilidad, data["solhb_nivel_habilidad_id"]) is None:
            raise ValidationError(f"Nivel de habilidad {data['solhb_nivel_habilidad_id']} no existe")

    final_exclusive = data.get("solhb_es_excluyente", relation.solhb_es_excluyente)
    if relation.solhb_es_excluyente and not final_exclusive:
        other_exclusive = any(
            item.solhb_es_excluyente
            for item in solicitud.habilidades
            if item.solhb_id != relation.solhb_id
        )
        if not other_exclusive:
            raise ConflictError("No se puede quitar la última habilidad excluyente de la solicitud")

    for field, value in data.items():
        setattr(relation, field, value)
    _commit(db)
    db.refresh(relation)
    return relation


def delete_habilidad(
    db: Session,
    solicitud: models.Solicitud,
    relation: models.SolicitudHabilidad,
) -> None:
    if relation.solhb_es_excluyente:
        other_exclusive = any(
            item.solhb_es_excluyente
            for item in solicitud.habilidades
            if item.solhb_id != relation.solhb_id
        )
        if not other_exclusive:
            raise ConflictError("No se puede eliminar la última habilidad excluyente de la solicitud")
    db.delete(relation)
    _commit(db)


def list_historial(db: Session, solicitud_id: int) -> list[models.HistorialSolicitud]:
    get_solicitud(db, solicitud_id)
    stmt = (
        select(models.HistorialSolicitud)
        .where(models.HistorialSolicitud.hsol_solicitud_id == solicitud_id)
        .order_by(models.HistorialSolicitud.hsol_fecha_cambio.asc(), models.HistorialSolicitud.hsol_id.asc())
    )
    return list(db.scalars(stmt).all())


def evaluar_candidato_cumple_excluyentes(
    db: Session,
    solicitud_id: int,
    habilidades_candidato: list[dict[str, Any]],
) -> dict[str, Any]:
    solicitud = get_solicitud(db, solicitud_id)
    requisitos = solicitud.habilidades_excluyentes
    if not requisitos:
        raise ValidationError("La solicitud no posee habilidades excluyentes; revise la integridad del registro")

    cand_map = {
        int(item["habilidad_id"]): int(item.get("anios_experiencia", 0))
        for item in habilidades_candidato
    }
    faltantes: list[dict[str, Any]] = []
    for req in requisitos:
        habilidad_id = req.solhb_habilidad_id
        anios_req = req.solhb_anios_experiencia_req or 0
        if habilidad_id not in cand_map:
            faltantes.append(
                {
                    "habilidad_id": habilidad_id,
                    "motivo": "Habilidad obligatoria no informada por el candidato",
                }
            )
            continue
        if cand_map[habilidad_id] < anios_req:
            faltantes.append(
                {
                    "habilidad_id": habilidad_id,
                    "motivo": (
                        f"Experiencia insuficiente: {cand_map[habilidad_id]} año(s) "
                        f"informado(s), {anios_req} requerido(s)"
                    ),
                }
            )

    cumple = not faltantes
    return {
        "cumple_excluyentes": cumple,
        "descartado_automaticamente": False,
        "habilidades_faltantes": faltantes,
    }
