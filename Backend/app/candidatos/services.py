from __future__ import annotations

import os
import re
import secrets
import hashlib
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth.utils import hash_password
from app.catalogos.models import (
    Cargo,
    Carrera,
    Comuna,
    Disponibilidad,
    EstadoSolicitudCandidato,
    Habilidad,
    Institucion,
    Idioma,
    MotivoRechazo,
    NivelEducacional,
    NivelHabilidad,
    NivelIdioma,
)
from app.clientes.models import Empresa
from app.solicitudes.models import Solicitud, SolicitudCandidato, SolicitudHabilidad
from app.usuarios.models import EstadoUsuario, Usuario

from . import cv_parser, models, schemas


ACTIVE_STATUS_NAME = os.getenv("ACTIVE_USER_STATUS_NAME", "Activo")
DELETED_STATUS_NAME = os.getenv("DELETED_USER_STATUS_NAME", "Eliminado")


class CandidateModuleError(Exception):
    pass


class NotFoundError(CandidateModuleError):
    pass


class ConflictError(CandidateModuleError):
    pass


class ValidationError(CandidateModuleError):
    pass


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("La operación viola una restricción de integridad o unicidad") from exc


def _candidate_stmt():
    return select(models.Candidato).options(
        selectinload(models.Candidato.direccion),
        selectinload(models.Candidato.habilidades),
        selectinload(models.Candidato.estudios),
        selectinload(models.Candidato.experiencias).selectinload(
            models.ExperienciaLaboral.habilidades_asociadas
        ),
        selectinload(models.Candidato.cursos),
        selectinload(models.Candidato.idiomas),
    )
 
         
                                             

                                
                              
                                                                                             

def get_candidate(db: Session, candidate_id: int) -> models.Candidato:
    obj = db.scalar(_candidate_stmt().where(models.Candidato.cand_id == candidate_id))
    if obj is None:
        raise NotFoundError(f"Candidato con ID {candidate_id} no encontrado")
    return obj


def get_candidate_by_email(db: Session, email: str) -> models.Candidato | None:
    return db.scalar(
        _candidate_stmt().where(func.lower(models.Candidato.cand_email) == email.strip().lower())
    )


def list_candidates(
    db: Session,
    *,
    q: str | None = None,
    estado_id: int | None = None,
    disponibilidad_id: int | None = None,
    habilidad_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Candidato]:
    stmt = _candidate_stmt()
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                models.Candidato.cand_email.ilike(term),
                models.Candidato.cand_nombres.ilike(term),
                models.Candidato.cand_apellido_paterno.ilike(term),
                models.Candidato.cand_apellido_materno.ilike(term),
                models.Candidato.cand_titulo.ilike(term),
            )
        )
    if estado_id is not None:
        stmt = stmt.where(models.Candidato.cand_estado_usuario_id == estado_id)
    if disponibilidad_id is not None:
        stmt = stmt.where(models.Candidato.cand_disponibilidad_id == disponibilidad_id)
    if habilidad_id is not None:
        stmt = stmt.join(models.CandidatoHabilidad).where(
            models.CandidatoHabilidad.cdhb_habilidad_id == habilidad_id
        )
    return list(
        db.scalars(stmt.order_by(models.Candidato.cand_id.desc()).offset(skip).limit(limit))
        .unique()
        .all()
    )

                              
                                     
                                                                             

def _status_id(db: Session, name: str) -> int:
    obj = db.scalar(select(EstadoUsuario).where(EstadoUsuario.esusr_nombre.ilike(name)))
    if obj is None:
        raise ValidationError(f"No existe el estado de usuario '{name}'")
    return obj.esusr_id


def _ensure_email_available(db: Session, email: str, *, candidate_id: int | None = None) -> None:
    normalized = email.strip().lower()
    internal = db.scalar(
        select(Usuario.usr_id).where(func.lower(Usuario.usr_email) == normalized).limit(1)
    )
    if internal is not None:
        raise ConflictError("El correo pertenece a un usuario interno del sistema")

    stmt = select(models.Candidato.cand_id).where(func.lower(models.Candidato.cand_email) == normalized)
    if candidate_id is not None:
        stmt = stmt.where(models.Candidato.cand_id != candidate_id)
    if db.scalar(stmt.limit(1)) is not None:
        raise ConflictError("El correo electrónico ya está registrado como candidato")


def _validate_candidate_refs(db: Session, data: dict) -> None:
    did = data.get("cand_disponibilidad_id")
    if did is not None and db.get(Disponibilidad, did) is None:
        raise ValidationError(f"Disponibilidad {did} no existe")


def _validate_nested_refs(db: Session, payload: schemas.CandidatoCreate) -> None:
    if payload.direccion and payload.direccion.drcd_comuna_id:
        if db.get(Comuna, payload.direccion.drcd_comuna_id) is None:
            raise ValidationError("La comuna indicada no existe")
    for skill in payload.habilidades:
        if db.get(Habilidad, skill.cdhb_habilidad_id) is None:
            raise ValidationError(f"Habilidad {skill.cdhb_habilidad_id} no existe")
        if skill.cdhb_nivel_habilidad_id and db.get(NivelHabilidad, skill.cdhb_nivel_habilidad_id) is None:
            raise ValidationError(f"Nivel de habilidad {skill.cdhb_nivel_habilidad_id} no existe")
    for study in payload.estudios:
        if study.etcd_nivel_educacional_id and db.get(NivelEducacional, study.etcd_nivel_educacional_id) is None:
            raise ValidationError("Nivel educacional no existe")
        if study.etcd_institucion_id and db.get(Institucion, study.etcd_institucion_id) is None:
            raise ValidationError("Institución no existe")
        if study.etcd_carrera_id and db.get(Carrera, study.etcd_carrera_id) is None:
            raise ValidationError("Carrera no existe")
    for exp in payload.experiencias:
        if exp.expl_empresa_id and db.get(Empresa, exp.expl_empresa_id) is None:
            raise ValidationError("Empresa no existe")
        from app.catalogos.models import Cargo
        if exp.expl_cargo_id and db.get(Cargo, exp.expl_cargo_id) is None:
            raise ValidationError("Cargo no existe")
        for hid in exp.habilidades_ids:
            if db.get(Habilidad, hid) is None:
                raise ValidationError(f"Habilidad {hid} no existe")
    for course in payload.cursos:
        if course.curs_institucion_id and db.get(Institucion, course.curs_institucion_id) is None:
            raise ValidationError("Institución del curso no existe")
    seen_idiomas: set[int] = set()
    for item in payload.idiomas:
        if item.cdio_idioma_id in seen_idiomas:
            raise ValidationError("No se puede repetir un idioma para el candidato")
        seen_idiomas.add(item.cdio_idioma_id)
        if db.get(Idioma, item.cdio_idioma_id) is None:
            raise ValidationError(f"Idioma {item.cdio_idioma_id} no existe")
        nivel = db.get(NivelIdioma, item.cdio_nivel_idioma_id)
        if nivel is None or not nivel.nvid_activo:
            raise ValidationError(f"Nivel de idioma {item.cdio_nivel_idioma_id} no existe o está inactivo")


def _temporary_password() -> str:
    # URL-safe, > 8 caracteres y muy por debajo del límite bcrypt de 72 bytes.
    return secrets.token_urlsafe(12)


def _apply_nested_create(db: Session, candidate: models.Candidato, payload: schemas.CandidatoCreate) -> None:
    if payload.direccion:
        candidate.direccion = models.DireccionCandidato(**payload.direccion.model_dump())

    for item in payload.habilidades:
        candidate.habilidades.append(models.CandidatoHabilidad(**item.model_dump()))

    for item in payload.estudios:
        candidate.estudios.append(models.EstudioCandidato(**item.model_dump()))

    for item in payload.experiencias:
        data = item.model_dump(exclude={"habilidades_ids"})
        exp = models.ExperienciaLaboral(**data)
        exp.habilidades_asociadas = [
            models.ExperienciaLaboralHabilidad(exph_habilidad_id=hid)
            for hid in item.habilidades_ids
        ]
        candidate.experiencias.append(exp)

    for item in payload.cursos:
        candidate.cursos.append(models.Curso(**item.model_dump()))

    for item in payload.idiomas:
        candidate.idiomas.append(models.CandidatoIdioma(**item.model_dump()))


def create_candidate(
    db: Session,
    payload: schemas.CandidatoCreate,
    *,
    auto_catalogs: list[object] | None = None,
    commit: bool = True,
) -> tuple[models.Candidato, str | None]:
    email = str(payload.cand_email).strip().lower()
    _ensure_email_available(db, email)
    data = payload.model_dump(
        exclude={"password_inicial", "direccion", "habilidades", "estudios", "experiencias", "cursos", "idiomas"}
    )
    data["cand_email"] = email
    _validate_candidate_refs(db, data)
    _validate_nested_refs(db, payload)

    raw_password = payload.password_inicial or _temporary_password()
    generated = payload.password_inicial is None
    data["cand_password"] = hash_password(raw_password)
    data["cand_fecha_creacion"] = datetime.utcnow()
    data["cand_estado_usuario_id"] = _status_id(db, ACTIVE_STATUS_NAME)

    candidate = models.Candidato(**data)
    _apply_nested_create(db, candidate, payload)
    db.add(candidate)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("La operación viola una restricción de integridad o unicidad") from exc
    # El flush asigna cand_id sin confirmar la transacción; con ese ID se deja
    # trazabilidad del CV que originó cada catálogo nuevo dentro del mismo commit.
    for catalog in auto_catalogs or []:
        if isinstance(catalog, Empresa):
            catalog.emp_origen_candidato_id = candidate.cand_id
        elif isinstance(catalog, Cargo):
            catalog.crgo_origen_candidato_id = candidate.cand_id
        elif isinstance(catalog, Habilidad):
            catalog.hab_origen_candidato_id = candidate.cand_id
        elif isinstance(catalog, Institucion):
            catalog.inst_origen_candidato_id = candidate.cand_id
        elif isinstance(catalog, Carrera):
            catalog.crra_origen_candidato_id = candidate.cand_id
        elif isinstance(catalog, Idioma):
            catalog.idio_origen_candidato_id = candidate.cand_id
    if commit:
        _commit(db)
    return get_candidate(db, candidate.cand_id), (raw_password if generated else None)


def replace_candidate(db: Session, candidate: models.Candidato, payload: schemas.CandidatoReplace) -> models.Candidato:
    data = payload.model_dump()
    email = str(data["cand_email"]).strip().lower()
    _ensure_email_available(db, email, candidate_id=candidate.cand_id)
    data["cand_email"] = email
    _validate_candidate_refs(db, data)
    for key, value in data.items():
        setattr(candidate, key, value)
    _commit(db)
    return get_candidate(db, candidate.cand_id)


def update_candidate(db: Session, candidate: models.Candidato, payload: schemas.CandidatoUpdate) -> models.Candidato:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo para actualizar")
    if "cand_email" in data and data["cand_email"] is not None:
        email = str(data["cand_email"]).strip().lower()
        _ensure_email_available(db, email, candidate_id=candidate.cand_id)
        data["cand_email"] = email
    _validate_candidate_refs(db, data)
    for key, value in data.items():
        setattr(candidate, key, value)
    _commit(db)
    return get_candidate(db, candidate.cand_id)


def update_candidate_self(
    db: Session,
    candidate: models.Candidato,
    payload: schemas.CandidatoSelfUpdate,
) -> models.Candidato:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo para actualizar")
    _validate_candidate_refs(db, data)
    for key, value in data.items():
        setattr(candidate, key, value)
    _commit(db)
    return get_candidate(db, candidate.cand_id)


def soft_delete_candidate(db: Session, candidate: models.Candidato) -> None:
    candidate.cand_estado_usuario_id = _status_id(db, DELETED_STATUS_NAME)
    _commit(db)


def merge_semicolon(existing: str | None, incoming: str | list[str] | None) -> str | None:
    existing_items = existing.split(";") if existing else []
    incoming_items = incoming if isinstance(incoming, list) else ((incoming or "").split(";"))
    return schemas.normalize_semicolon_values(existing_items + list(incoming_items))


def append_cv_url(db: Session, candidate: models.Candidato, cv_path: str) -> models.Candidato:
    candidate.cand_cv_urls = merge_semicolon(candidate.cand_cv_urls, cv_path)
    _commit(db)
    return get_candidate(db, candidate.cand_id)


# --------------------------- consultas de recursos anidados ---------------------------
def list_candidate_skills(db: Session, candidate_id: int) -> list[models.CandidatoHabilidad]:
    candidate = get_candidate(db, candidate_id)
    return sorted(candidate.habilidades, key=lambda x: x.cdhb_id)


def list_candidate_studies(db: Session, candidate_id: int) -> list[models.EstudioCandidato]:
    candidate = get_candidate(db, candidate_id)
    return sorted(
        candidate.estudios,
        key=lambda x: (x.etcd_fecha_inicio is not None, x.etcd_fecha_inicio, x.etcd_id),
        reverse=True,
    )


def list_candidate_experiences(db: Session, candidate_id: int) -> list[dict]:
    candidate = get_candidate(db, candidate_id)
    ordered = sorted(
        candidate.experiencias,
        key=lambda x: (x.expl_fecha_inicio is not None, x.expl_fecha_inicio, x.expl_id),
        reverse=True,
    )
    return [_exp_to_response_data(exp) for exp in ordered]


def list_candidate_courses(db: Session, candidate_id: int) -> list[models.Curso]:
    candidate = get_candidate(db, candidate_id)
    return sorted(
        candidate.cursos,
        key=lambda x: (x.curs_anio_curso is not None, x.curs_anio_curso or 0, x.curs_id),
        reverse=True,
    )


def list_candidate_languages(db: Session, candidate_id: int) -> list[models.CandidatoIdioma]:
    candidate = get_candidate(db, candidate_id)
    return sorted(
        candidate.idiomas,
        key=lambda x: ((x.idioma.idio_nombre if x.idioma else "").casefold(), x.cdio_id),
    )


def list_candidate_addresses(db: Session, candidate_id: int) -> list[models.DireccionCandidato]:
    candidate = get_candidate(db, candidate_id)
    # El modelo físico permite una sola dirección por candidato (UNIQUE drcd_candidato_id).
    return [candidate.direccion] if candidate.direccion is not None else []


def upsert_candidate_address(
    db: Session,
    candidate_id: int,
    payload: schemas.DireccionUpdate,
) -> models.DireccionCandidato:
    candidate = get_candidate(db, candidate_id)
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo de dirección")
    comuna_id = data.get("drcd_comuna_id")
    if comuna_id is not None and db.get(Comuna, comuna_id) is None:
        raise ValidationError("La comuna indicada no existe")
    if candidate.direccion is None:
        obj = models.DireccionCandidato(drcd_candidato_id=candidate_id, **data)
        db.add(obj)
    else:
        obj = candidate.direccion
        for key, value in data.items():
            setattr(obj, key, value)
    _commit(db)
    db.refresh(obj)
    return obj


def delete_candidate_address(db: Session, candidate_id: int) -> None:
    candidate = get_candidate(db, candidate_id)
    if candidate.direccion is None:
        raise NotFoundError("Dirección del candidato no encontrada")
    db.delete(candidate.direccion)
    _commit(db)


# --------------------------- recursos anidados ---------------------------
def add_language(db: Session, candidate_id: int, payload: schemas.IdiomaCandidatoCreate):
    get_candidate(db, candidate_id)
    if db.get(Idioma, payload.cdio_idioma_id) is None:
        raise ValidationError("Idioma no existe")
    nivel = db.get(NivelIdioma, payload.cdio_nivel_idioma_id)
    if nivel is None or not nivel.nvid_activo:
        raise ValidationError("Nivel de idioma no existe o está inactivo")
    exists = db.scalar(select(models.CandidatoIdioma.cdio_id).where(
        models.CandidatoIdioma.cdio_candidato_id == candidate_id,
        models.CandidatoIdioma.cdio_idioma_id == payload.cdio_idioma_id,
    ))
    if exists:
        raise ConflictError("El idioma ya está registrado para el candidato")
    obj = models.CandidatoIdioma(cdio_candidato_id=candidate_id, **payload.model_dump())
    db.add(obj); _commit(db); db.refresh(obj)
    return db.scalar(select(models.CandidatoIdioma).where(models.CandidatoIdioma.cdio_id == obj.cdio_id))


def update_language(db: Session, candidate_id: int, item_id: int, payload: schemas.IdiomaCandidatoUpdate):
    obj = db.scalar(select(models.CandidatoIdioma).where(
        models.CandidatoIdioma.cdio_id == item_id,
        models.CandidatoIdioma.cdio_candidato_id == candidate_id,
    ))
    if obj is None:
        raise NotFoundError("Idioma del candidato no encontrado")
    nivel = db.get(NivelIdioma, payload.cdio_nivel_idioma_id)
    if nivel is None or not nivel.nvid_activo:
        raise ValidationError("Nivel de idioma no existe o está inactivo")
    obj.cdio_nivel_idioma_id = payload.cdio_nivel_idioma_id
    _commit(db); db.refresh(obj)
    return obj


def delete_language(db: Session, candidate_id: int, item_id: int) -> None:
    obj = db.scalar(select(models.CandidatoIdioma).where(
        models.CandidatoIdioma.cdio_id == item_id,
        models.CandidatoIdioma.cdio_candidato_id == candidate_id,
    ))
    if obj is None:
        raise NotFoundError("Idioma del candidato no encontrado")
    db.delete(obj); _commit(db)


def add_skill(db: Session, candidate_id: int, payload: schemas.HabilidadCreate):
    get_candidate(db, candidate_id)
    if db.get(Habilidad, payload.cdhb_habilidad_id) is None:
        raise ValidationError("Habilidad no existe")
    if payload.cdhb_nivel_habilidad_id and db.get(NivelHabilidad, payload.cdhb_nivel_habilidad_id) is None:
        raise ValidationError("Nivel de habilidad no existe")
    exists = db.scalar(select(models.CandidatoHabilidad.cdhb_id).where(
        models.CandidatoHabilidad.cdhb_candidato_id == candidate_id,
        models.CandidatoHabilidad.cdhb_habilidad_id == payload.cdhb_habilidad_id,
    ))
    if exists:
        raise ConflictError("La habilidad ya está registrada para el candidato")
    obj = models.CandidatoHabilidad(cdhb_candidato_id=candidate_id, **payload.model_dump())
    db.add(obj); _commit(db); db.refresh(obj); return obj


def update_skill(db: Session, candidate_id: int, skill_id: int, payload: schemas.HabilidadUpdate):
    obj = db.scalar(select(models.CandidatoHabilidad).where(
        models.CandidatoHabilidad.cdhb_id == skill_id,
        models.CandidatoHabilidad.cdhb_candidato_id == candidate_id,
    ))
    if obj is None: raise NotFoundError("Habilidad del candidato no encontrada")
    data = payload.model_dump(exclude_unset=True)
    if not data: raise ValidationError("Debe enviar al menos un campo")
    if data.get("cdhb_nivel_habilidad_id") and db.get(NivelHabilidad, data["cdhb_nivel_habilidad_id"]) is None:
        raise ValidationError("Nivel de habilidad no existe")
    for k,v in data.items(): setattr(obj,k,v)
    _commit(db); db.refresh(obj); return obj


def delete_skill(db: Session, candidate_id: int, skill_id: int) -> None:
    obj = db.scalar(select(models.CandidatoHabilidad).where(
        models.CandidatoHabilidad.cdhb_id == skill_id,
        models.CandidatoHabilidad.cdhb_candidato_id == candidate_id,
    ))
    if obj is None: raise NotFoundError("Habilidad del candidato no encontrada")
    db.delete(obj); _commit(db)


def add_study(db: Session, candidate_id: int, payload: schemas.EstudioCreate):
    get_candidate(db,candidate_id)
    obj=models.EstudioCandidato(etcd_candidato_id=candidate_id,**payload.model_dump()); db.add(obj); _commit(db); db.refresh(obj); return obj


def update_study(db: Session,candidate_id:int,item_id:int,payload:schemas.EstudioUpdate):
    obj=db.scalar(select(models.EstudioCandidato).where(models.EstudioCandidato.etcd_id==item_id,models.EstudioCandidato.etcd_candidato_id==candidate_id))
    if obj is None: raise NotFoundError("Estudio no encontrado")
    data=payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(obj,k,v)
    _commit(db); db.refresh(obj); return obj


def delete_study(db:Session,candidate_id:int,item_id:int):
    obj=db.scalar(select(models.EstudioCandidato).where(models.EstudioCandidato.etcd_id==item_id,models.EstudioCandidato.etcd_candidato_id==candidate_id))
    if obj is None: raise NotFoundError("Estudio no encontrado")
    db.delete(obj); _commit(db)


def add_course(db: Session,candidate_id:int,payload:schemas.CursoCreate):
    get_candidate(db,candidate_id); obj=models.Curso(curs_candidato_id=candidate_id,**payload.model_dump()); db.add(obj); _commit(db); db.refresh(obj); return obj


def update_course(db:Session,candidate_id:int,item_id:int,payload:schemas.CursoUpdate):
    obj=db.scalar(select(models.Curso).where(models.Curso.curs_id==item_id,models.Curso.curs_candidato_id==candidate_id))
    if obj is None: raise NotFoundError("Curso no encontrado")
    data=payload.model_dump(exclude_unset=True)
    for k,v in data.items(): setattr(obj,k,v)
    _commit(db); db.refresh(obj); return obj


def delete_course(db:Session,candidate_id:int,item_id:int):
    obj=db.scalar(select(models.Curso).where(models.Curso.curs_id==item_id,models.Curso.curs_candidato_id==candidate_id))
    if obj is None: raise NotFoundError("Curso no encontrado")
    db.delete(obj); _commit(db)


def _exp_to_response_data(exp: models.ExperienciaLaboral) -> dict:
    return {
        "expl_id": exp.expl_id, "expl_candidato_id": exp.expl_candidato_id,
        "expl_empresa_id": exp.expl_empresa_id, "expl_cargo_id": exp.expl_cargo_id,
        "expl_descripcion_funciones": exp.expl_descripcion_funciones,
        "expl_fecha_inicio": exp.expl_fecha_inicio, "expl_fecha_fin": exp.expl_fecha_fin,
        "habilidades_ids": [x.exph_habilidad_id for x in exp.habilidades_asociadas],
    }


def add_experience(db:Session,candidate_id:int,payload:schemas.ExperienciaCreate):
    get_candidate(db,candidate_id)
    data=payload.model_dump(exclude={"habilidades_ids"}); obj=models.ExperienciaLaboral(expl_candidato_id=candidate_id,**data)
    obj.habilidades_asociadas=[models.ExperienciaLaboralHabilidad(exph_habilidad_id=x) for x in payload.habilidades_ids]
    db.add(obj); _commit(db); db.refresh(obj); return _exp_to_response_data(obj)


def update_experience(db:Session,candidate_id:int,item_id:int,payload:schemas.ExperienciaUpdate):
    obj=db.scalar(select(models.ExperienciaLaboral).options(selectinload(models.ExperienciaLaboral.habilidades_asociadas)).where(models.ExperienciaLaboral.expl_id==item_id,models.ExperienciaLaboral.expl_candidato_id==candidate_id))
    if obj is None: raise NotFoundError("Experiencia no encontrada")
    data=payload.model_dump(exclude_unset=True)
    hids=data.pop("habilidades_ids",None)
    for k,v in data.items(): setattr(obj,k,v)
    if hids is not None: obj.habilidades_asociadas=[models.ExperienciaLaboralHabilidad(exph_habilidad_id=x) for x in hids]
    _commit(db); return _exp_to_response_data(obj)


def delete_experience(db:Session,candidate_id:int,item_id:int):
    obj=db.scalar(select(models.ExperienciaLaboral).where(models.ExperienciaLaboral.expl_id==item_id,models.ExperienciaLaboral.expl_candidato_id==candidate_id))
    if obj is None: raise NotFoundError("Experiencia no encontrada")
    db.delete(obj); _commit(db)



def _fold(value: str) -> str:
    import unicodedata
    return "".join(
        c for c in unicodedata.normalize("NFD", value.casefold())
        if unicodedata.category(c) != "Mn"
    )


def _normalizar_nombre_para_match(value: str | None) -> str:
    """Normaliza formato sin inventar equivalencias semánticas."""
    if not value:
        return ""
    folded = _fold(value)
    normalized = re.sub(r"[^a-z0-9]+", " ", folded)
    return " ".join(normalized.split())


def _contiene_nombre_normalizado(contexto: str, nombre_catalogo: str) -> bool:
    if not contexto or not nombre_catalogo:
        return False
    pattern = rf"(?<![a-z0-9]){re.escape(nombre_catalogo)}(?![a-z0-9])"
    return re.search(pattern, contexto) is not None


def _buscar_unico_por_nombre_normalizado(items, nombre_attr: str, id_attr: str, contexto: str):
    contexto_normalizado = _normalizar_nombre_para_match(contexto)
    matches = []
    seen_ids: set[int] = set()
    for item in items:
        item_id = getattr(item, id_attr, None)
        nombre = _normalizar_nombre_para_match(getattr(item, nombre_attr, None))
        if item_id is None or not nombre:
            continue
        if not _contiene_nombre_normalizado(contexto_normalizado, nombre):
            continue
        if item_id in seen_ids:
            continue
        matches.append(item)
        seen_ids.add(item_id)
    # Si el texto calza con más de un catálogo, no elegimos por cercanía ni
    # fuzzy matching: persistir un ID incorrecto es peor que dejarlo pendiente.
    return matches[0] if len(matches) == 1 else None


_EXPERIENCE_GENERIC_VALUES = {
    "empresa", "compania", "compania desconocida", "cliente", "organizacion",
    "cargo", "puesto", "posicion", "trabajo", "funciones", "responsabilidades",
}
_ACADEMIC_GENERIC_VALUES = {
    "institucion", "instituto", "universidad", "escuela", "academia", "college",
    "carrera", "titulo", "programa", "grado", "estudios", "educacion", "formacion",
}


def _catalog_value_for_auto_creation(value: str | None, *, max_length: int, kind: str) -> str | None:
    """Valida nombres extraídos antes de convertirlos en datos maestros.

    El importador no puede corregir ni completar nombres fuera del CV: crear un
    catálogo desde una frase laboral o truncar silenciosamente el valor sería
    más dañino que dejar la experiencia pendiente.
    """
    if not value:
        return None
    cleaned = " ".join(value.replace("\u2022", " ").split()).strip(" -|,:;")
    normalized = _normalizar_nombre_para_match(cleaned)
    if kind == "habilidad":
        # Una habilidad nueva solo puede nacer de una lista explícita y breve;
        # no completamos descripciones ni inferimos categorías desde el CV.
        short_tokens = {"c", "r", "go", "c sharp", "c plus plus"}
        if not cleaned or len(cleaned) > max_length or not normalized:
            return None
        if normalized not in short_tokens and len(normalized) < 2:
            return None
        if len(cleaned.split()) > 8 or re.search(r"https?://|@|\d", cleaned):
            return None
        if normalized in _SKILL_GENERIC_VALUES or any(
            token in normalized.split()
            for token in ("experiencia", "responsabilidades", "funciones", "tareas")
        ):
            return None
        return cleaned
    if kind in {"institucion", "carrera"}:
        if not cleaned or len(cleaned) > max_length or not normalized:
            return None
        if len(normalized) < 3 or normalized in _ACADEMIC_GENERIC_VALUES:
            return None
        if re.search(r"https?://|@|\d", cleaned):
            return None
        if len(cleaned.split()) > (12 if kind == "carrera" else 8):
            return None
        if any(
            token in normalized.split()
            for token in (
                "certificacion", "certificado", "curso", "diplomado", "experiencia",
                "responsabilidades", "funciones", "proyecto", "trabajo",
            )
        ):
            return None
        if kind == "carrera" and any(
            token in normalized.split()
            for token in ("estudios", "educacion", "formacion", "institucion", "carrera", "programa", "grado")
        ):
            return None
        return cleaned
    if kind == "idioma":
        # Un idioma nuevo solo puede provenir de una etiqueta explicita y
        # breve; no se crean nombres desde texto libre o descripciones.
        if not cleaned or len(cleaned) > max_length or not normalized:
            return None
        if len(normalized) < 2 or normalized in {"idioma", "idiomas", "language", "languages", "nivel", "niveles"}:
            return None
        if re.search(r"https?://|@|\d", cleaned) or len(cleaned.split()) > 4:
            return None
        return cleaned
    if len(normalized) < 2 or normalized in _EXPERIENCE_GENERIC_VALUES:
        return None
    if len(cleaned) > max_length or any(char.isdigit() for char in cleaned) and len(cleaned) < 4:
        return None
    if any(token in normalized.split() for token in ("responsabilidades", "funciones", "tareas")):
        return None
    return cleaned


def _experience_candidate_lines(lines: list[str]) -> list[str]:
    candidates = []
    for line in lines:
        folded = _normalizar_nombre_para_match(line)
        if not folded or line.lstrip().startswith(("-", "•", "*")):
            continue
        if re.search(r"\b(?:19|20)\d{2}\b", folded):
            continue
        if any(
            token in folded
            for token in (
                "educacion", "formacion", "certificacion", "curso", "estudio",
                "habilidad", "competencia", "tecnologia", "herramienta",
                "lenguaje", "stack", "conocimiento",
            )
        ):
            continue
        if len(line) > 140:
            continue
        candidates.append(line)
    return candidates


def _extract_experience_pair(lines: list[str]) -> tuple[str | None, str | None]:
    """Extrae pares solo desde formatos delimitados o rotulados explícitamente."""
    for line in _experience_candidate_lines(lines):
        labeled = re.search(
            r"(?i)^\s*empresa\s*[:\-]\s*(?P<empresa>[^|;]+?)\s*(?:\||;)\s*"
            r"(?:cargo|puesto|posicion)\s*[:\-]\s*(?P<cargo>.+?)\s*$",
            line,
        )
        if labeled:
            return labeled.group("empresa"), labeled.group("cargo")
        labeled = re.search(
            r"(?i)^\s*(?:cargo|puesto|posicion)\s*[:\-]\s*(?P<cargo>[^|;]+?)\s*(?:\||;)\s*"
            r"empresa\s*[:\-]\s*(?P<empresa>.+?)\s*$",
            line,
        )
        if labeled:
            return labeled.group("empresa"), labeled.group("cargo")
        parts = re.split(r"\s+(?:\||@)\s+|\s+-\s+", line, maxsplit=1)
        if len(parts) == 2:
            return parts[0], parts[1]
    return None, None


def _extract_missing_experience_value(lines: list[str], known_name: str, *, after: bool) -> str | None:
    known = _normalizar_nombre_para_match(known_name)
    if not known:
        return None
    for line in _experience_candidate_lines(lines):
        normalized = _normalizar_nombre_para_match(line)
        if not _contiene_nombre_normalizado(normalized, known):
            continue
        before, separator, tail = normalized.partition(known)
        candidate = tail if after and separator else before
        candidate = re.sub(r"^(?:[-|,:;]|y)\s*|\s*(?:[-|,:;]|y)$", "", candidate).strip()
        if candidate:
            return candidate
    return None


def _catalog_advisory_lock(db: Session, normalized_name: str, kind: str) -> None:
    # El lock transaccional combina tipo y nombre normalizado para serializar
    # altas concurrentes del mismo valor y se libera automáticamente al terminar
    # la transacción; SQLite y dobles de tests no tienen este mecanismo.
    bind = getattr(db, "bind", None)
    if bind is None or getattr(bind.dialect, "name", None) != "postgresql":
        return
    raw_key = hashlib.sha256(f"sakura:{kind}:{normalized_name}".encode("utf-8")).digest()[:8]
    lock_key = int.from_bytes(raw_key, byteorder="big", signed=True)
    db.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})


def _resolve_or_create_experience_catalog(
    db: Session,
    items: list,
    model,
    *,
    id_attr: str,
    name_attr: str,
    raw_value: str | None,
    max_length: int,
    kind: str,
    origin_candidate_id: int | None,
    warnings: list[str],
):
    value = _catalog_value_for_auto_creation(raw_value, max_length=max_length, kind=kind)
    if value is None:
        if raw_value:
            warnings.append(f"No se creó {kind} desde CV: el valor no es válido o está incompleto ({raw_value[:80]}).")
        return None
    normalized = _normalizar_nombre_para_match(value)
    matches = [item for item in items if _normalizar_nombre_para_match(getattr(item, name_attr, None)) == normalized]
    if len(matches) > 1:
        warnings.append(f"No se creó {kind} desde CV: existen coincidencias ambiguas para '{value}'.")
        return None
    if matches:
        return matches[0]

    _catalog_advisory_lock(db, normalized, kind)
    # La consulta posterior al lock permite reutilizar el registro creado por la
    # importación concurrente que ganó la carrera, en vez de insertar otro valor.
    refreshed = list(db.scalars(select(model)).all())
    matches = [item for item in refreshed if _normalizar_nombre_para_match(getattr(item, name_attr, None)) == normalized]
    if len(matches) > 1:
        warnings.append(f"No se creó {kind} desde CV: existen coincidencias ambiguas para '{value}'.")
        return None
    if matches:
        items[:] = refreshed
        return matches[0]

    data = {
        name_attr: value,
        f"{name_attr.split('_')[0]}_creado_automaticamente": True,
        f"{name_attr.split('_')[0]}_origen": "CV",
        f"{name_attr.split('_')[0]}_origen_candidato_id": origin_candidate_id,
    }
    instance = model(**data)
    # Los dobles de parser no exponen persistencia; en producción este camino
    # siempre recibe una Session real y la creación queda dentro de su transacción.
    if not hasattr(db, "add"):
        warnings.append(f"No se pudo crear {kind} desde CV: la sesión de persistencia no está disponible.")
        return None
    db.add(instance)
    try:
        with db.begin_nested():
            db.flush()
    except IntegrityError:
        refreshed = list(db.scalars(select(model)).all())
        matches = [item for item in refreshed if _normalizar_nombre_para_match(getattr(item, name_attr, None)) == normalized]
        if len(matches) == 1:
            items[:] = refreshed
            return matches[0]
        warnings.append(f"No se pudo crear {kind} desde CV por una colisión de integridad para '{value}'.")
        return None
    items.append(instance)
    return instance


def _iter_nombre_normalizado_en_contexto(contexto_normalizado: str, nombre_normalizado: str):
    if not contexto_normalizado or not nombre_normalizado:
        return []
    pattern = rf"(?<![a-z0-9]){re.escape(nombre_normalizado)}(?![a-z0-9])"
    return list(re.finditer(pattern, contexto_normalizado))


def _matches_habilidades_en_linea(skills, line: str) -> list[tuple]:
    contexto_normalizado = _normalizar_nombre_para_match(line)
    candidates = []
    for skill in skills:
        skill_id = getattr(skill, "hab_id", None)
        nombre = _normalizar_nombre_para_match(getattr(skill, "hab_nombre", None))
        if skill_id is None or not nombre:
            continue
        for match in _iter_nombre_normalizado_en_contexto(contexto_normalizado, nombre):
            candidates.append((skill, nombre, match.start(), match.end()))

    ambiguous: set[int] = set()
    for i, first in enumerate(candidates):
        for j, second in enumerate(candidates):
            if i >= j:
                continue
            overlaps = first[2] < second[3] and second[2] < first[3]
            if overlaps:
                ambiguous.update({i, j})
    return [candidate for idx, candidate in enumerate(candidates) if idx not in ambiguous]


_SKILL_GENERIC_VALUES = {
    "habilidad", "habilidades", "competencia", "competencias", "skill", "skills",
    "tecnologia", "tecnologias", "herramienta", "herramientas", "lenguaje", "lenguajes",
    "stack", "conocimiento", "conocimientos", "otros", "ninguno", "n a",
}
_SKILL_SECTION_RE = re.compile(
    r"^\s*(?:habilidades?|competencias?|skills?|tecnolog(?:ia|ía)s?|herramientas?|"
    r"lenguajes?|stack(?:\s+tecnolog(?:ico|ica|icos|icas))?|conocimientos?)"
    r"(?:\s+(?:tecnic[ao]s?|profesionales?|informatic[ao]s?))?\s*(?::|-)?\s*(.*)$",
    re.IGNORECASE,
)
_SKILL_BLOCK_STOP_WORDS = {
    "experiencia", "experiencia laboral", "educacion", "estudios", "formacion",
    "cursos", "certificaciones", "idiomas", "contacto", "perfil", "perfil profesional",
    "proyecto", "proyectos", "responsabilidades", "actividades", "logros", "referencias",
}


def _lineas_de_habilidades_explicitas(lines: list[str]) -> list[str]:
    """Obtiene únicamente contenido dentro de etiquetas/listas de habilidades.

    El texto libre de una experiencia puede mencionar muchas tecnologías sin
    demostrar que sean competencias declaradas; por eso las altas automáticas
    se limitan a secciones con una señal explícita de habilidades.
    """
    result: list[str] = []
    in_skill_block = False
    for line in lines:
        # El prefijo "Habilidades" también puede aparecer al comienzo de un
        # correo como habilidades.persona@dominio; ese contacto no es una sección.
        match = None if "@" in line or re.search(r"https?://", line, re.IGNORECASE) else _SKILL_SECTION_RE.match(line)
        folded = _normalizar_nombre_para_match(line)
        if match:
            in_skill_block = True
            inline = match.group(1).strip()
            if inline:
                result.append(inline)
            continue
        if in_skill_block and (folded in _SKILL_BLOCK_STOP_WORDS or _es_heading_curso(folded)):
            in_skill_block = False
            continue
        if in_skill_block:
            if len(line) <= 120 and not re.search(r"[.!?]\s", line):
                result.append(line)
    return result


def _candidatos_habilidad_desde_linea(line: str) -> list[str]:
    # Las listas explícitas usan delimitadores para separar habilidades; quitar
    # años y niveles deja el nombre maestro sin convertir una frase laboral en
    # una habilidad nueva.
    cleaned_line = re.sub(r"^[\s•·*\-]+", "", line).strip()
    candidates = re.split(r"\s*(?:,|;|\||/|•)\s*", cleaned_line)
    result: list[str] = []
    for candidate in candidates:
        candidate = re.sub(
            r"\s*(?:[-–—:]\s*)?(?:\d{1,2}\s+(?:anos?|years?|yrs?)|"
            r"(?:basico|basica|intermedio|intermedia|avanzado|avanzada|senior|junior))\s*$",
            "",
            candidate,
            flags=re.IGNORECASE,
        ).strip(" .:-–—()[]")
        if candidate:
            result.append(candidate)
    return result


_ACADEMIC_SECTION_HEADINGS = {
    "educacion", "estudios", "formacion academica", "formacion profesional",
    "academic background", "education", "education background",
}
_ACADEMIC_INSTITUTION_SIGNALS = {
    "universidad", "universitario", "universitaria", "instituto", "instituto profesional",
    "escuela", "academia", "college", "school",
}
_ACADEMIC_CAREER_SIGNALS = {
    "ingenieria", "ingeniero", "ingeniera", "licenciatura", "licenciado", "licenciada",
    "magister", "master", "mba", "doctorado", "doctor", "tecnico", "tecnica",
    "tecnologia", "administracion", "ciencias", "diseno", "arquitectura", "informatica",
    "computacion", "programacion", "analista", "contador", "periodismo", "psicologia",
}
_ACADEMIC_STOP_HEADINGS = {
    "experiencia", "experiencia laboral", "proyectos", "cursos", "certificaciones", "idiomas",
    "habilidades", "competencias", "contacto", "referencias", "perfil", "perfil profesional",
}


def _es_encabezado_academico(line: str) -> bool:
    normalized = _normalizar_nombre_para_match(line)
    return normalized in _ACADEMIC_SECTION_HEADINGS


def _lineas_academicas_explicitas(lines: list[str]) -> set[int]:
    # Solo se habilita contexto entre encabezados académicos y la siguiente
    # sección, evitando que una universidad mencionada en experiencia o cursos
    # produzca una institución o carrera por asociación lejana.
    indices: set[int] = set()
    active = False
    for idx, line in enumerate(lines):
        normalized = _normalizar_nombre_para_match(line)
        if _es_encabezado_academico(line):
            active = True
            continue
        if active and normalized in _ACADEMIC_STOP_HEADINGS:
            active = False
            continue
        if active:
            indices.add(idx)
    return indices


def _parece_institucion_academica(value: str) -> bool:
    normalized = _normalizar_nombre_para_match(value)
    return any(signal in normalized.split() for signal in _ACADEMIC_INSTITUTION_SIGNALS)


def _parece_carrera_academica(value: str) -> bool:
    normalized = _normalizar_nombre_para_match(value)
    return any(signal in normalized.split() for signal in _ACADEMIC_CAREER_SIGNALS)


def _componentes_estudio_en_linea(line: str) -> tuple[str | None, str | None]:
    institution: str | None = None
    career: str | None = None
    segments = re.split(r"\s*(?:\||;)\s*", line)
    for segment in segments:
        match = re.match(
            r"(?i)^\s*(?:institucion|institución|universidad|instituto|escuela)\s*[:\-]\s*(.+)$",
            segment,
        )
        if match:
            institution = match.group(1).strip()
            continue
        match = re.match(
            r"(?i)^\s*(?:carrera|titulo|título|programa|grado)\s*[:\-]\s*(.+)$",
            segment,
        )
        if match:
            career = match.group(1).strip()

    if institution or career:
        return institution, career

    parts = re.split(r"\s+(?:@)\s+|\s+-\s+", line, maxsplit=1)
    if len(parts) == 2:
        left, right = (part.strip() for part in parts)
        if _parece_institucion_academica(left):
            return left, right
        if _parece_institucion_academica(right):
            return right, left

    if _parece_institucion_academica(line):
        return line.strip(), None
    if _parece_carrera_academica(line):
        return None, line.strip()
    return None, None


def _componentes_estudio_en_contexto(
    lines: list[str],
    index: int,
    academic_indices: set[int],
) -> tuple[str | None, str | None]:
    # Se permiten líneas académicas inmediatamente vecinas para conservar CVs
    # que separan carrera e institución, pero nunca se salta fuera del bloque.
    # Por eso un estudio puede quedar parcialmente válido sin inventar el dato faltante.
    institution, career = _componentes_estudio_en_linea(lines[index])
    for neighbor in (index - 1, index + 1):
        if neighbor not in academic_indices:
            continue
        adjacent_institution, adjacent_career = _componentes_estudio_en_linea(lines[neighbor])
        institution = institution or adjacent_institution
        career = career or adjacent_career
    return institution, career


def _extraer_anios_habilidad(
    line: str,
    nombre_habilidad_normalizado: str,
    start: int | None = None,
    end: int | None = None,
) -> int | None:
    line_norm = _normalizar_nombre_para_match(line)
    if not line_norm or not nombre_habilidad_normalizado:
        return None
    year_word = r"(?:anos?|years?|yrs?)"
    if start is not None and end is not None:
        before = line_norm[:start].rstrip()
        after = line_norm[end:].lstrip()
        patterns = [
            rf"^(?:experiencia\s+)?(\d{{1,2}})\s+{year_word}(?![a-z0-9])",
            rf"(\d{{1,2}})\s+{year_word}\s+de\s+(?:experiencia\s+)?en$",
            rf"(\d{{1,2}})\s+{year_word}\s+(?:of\s+)?(?:experience\s+)?in$",
        ]
        years = set()
        for match in re.finditer(patterns[0], after):
            years.add(int(match.group(1)))
        for pattern in patterns[1:]:
            match = re.search(pattern, before)
            if match:
                years.add(int(match.group(1)))
        return years.pop() if len(years) == 1 else None

    skill_pattern = re.escape(nombre_habilidad_normalizado)
    patterns = [
        rf"(?<![a-z0-9]){skill_pattern}(?![a-z0-9])\s+(?:experiencia\s+)?(\d{{1,2}})\s+{year_word}",
        rf"(\d{{1,2}})\s+{year_word}\s+(?:de\s+)?(?:experiencia\s+)?(?:en\s+)?(?<![a-z0-9]){skill_pattern}(?![a-z0-9])",
        rf"(\d{{1,2}})\s+{year_word}\s+(?:of\s+)?(?:experience\s+)?(?:in\s+)?(?<![a-z0-9]){skill_pattern}(?![a-z0-9])",
    ]
    years = set()
    for pattern in patterns:
        for match in re.finditer(pattern, line_norm):
            years.add(int(match.group(1)))
    return years.pop() if len(years) == 1 else None


_MONTH_NAMES = {
    "ene": 1,
    "enero": 1,
    "jan": 1,
    "january": 1,
    "feb": 2,
    "febrero": 2,
    "february": 2,
    "mar": 3,
    "marzo": 3,
    "march": 3,
    "abr": 4,
    "abril": 4,
    "apr": 4,
    "april": 4,
    "may": 5,
    "mayo": 5,
    "jun": 6,
    "junio": 6,
    "june": 6,
    "jul": 7,
    "julio": 7,
    "july": 7,
    "ago": 8,
    "agosto": 8,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "septiembre": 9,
    "set": 9,
    "setiembre": 9,
    "september": 9,
    "oct": 10,
    "octubre": 10,
    "october": 10,
    "nov": 11,
    "noviembre": 11,
    "november": 11,
    "dic": 12,
    "diciembre": 12,
    "dec": 12,
    "december": 12,
}

_CURRENT_DATE_WORDS = {"actualidad", "presente", "fecha"}
_EXPERIENCE_DATE_EDUCATION_SIGNALS = {
    "academia",
    "certificacion",
    "colegio",
    "curso",
    "diplomado",
    "educacion",
    "formacion",
    "instituto",
    "universidad",
    "udemy",
}
_STUDY_DATE_CONTEXT_SIGNALS = {
    "academia",
    "college",
    "educacion",
    "education",
    "escuela",
    "formacion",
    "instituto",
    "school",
    "universidad",
}
_STUDY_DATE_BLOCKED_SIGNALS = {
    "capacitacion",
    "certificacion",
    "certificado",
    "curso",
    "diplomado",
    "experiencia",
    "laboral",
    "proyecto",
}
_STUDY_DATE_PROFESSIONAL_CONTEXT_SIGNALS = {
    "actividad",
    "actividades",
    "agente",
    "asistente",
    "ayudante",
    "consultor",
    "corrector",
    "docente",
    "encargado",
    "experiencia",
    "instructor",
    "laboral",
    "proyecto",
    "trabajo",
    "voluntariado",
}
_COURSE_HEADING_WORDS = {
    "curso",
    "cursos",
    "certificacion",
    "certificaciones",
    "certificado",
    "certificados",
    "diplomado",
    "diplomados",
}
_COURSE_SIGNAL_RE = re.compile(
    r"(?<![a-z0-9])(?:cursos?|certificaci(?:on|ones)|certificados?|diplomados?)(?![a-z0-9])"
)
_COURSE_STRONG_START_RE = re.compile(
    r"^(?:"
    r"curso(?:\s+de)?|"
    r"diplomado|"
    r"(?:19\d{2}|20\d{2})(?:\s*-\s*(?:19\d{2}|20\d{2}))?\s+diplomado|"
    r"(?:19\d{2}|20\d{2})\s*:?\s*curso"
    r")(?=\s+\S)"
)
_CERTIFICATION_STRONG_RE = re.compile(
    r"^(?:certificacion|certificado)\s+(?:en|de\s+)?\S+|"
    r"^(?:19\d{2}|20\d{2})\s+(?:certificacion|certificado)\s+\S+|"
    r"^licencias\s+y\s+certificaciones\s*:\s*\S+"
)
_COURSE_LABOR_CONTEXT_SIGNALS = {
    "aplicaciones internas",
    "aplicaciones externas",
    "capa de negocio",
    "definicion de requerimientos",
    "desarrollada",
    "funciones",
    "mejoras a sistemas",
    "recursos",
    "responsabilidades",
    "tareas",
    "validando",
    "web container",
}
_COURSE_TAUGHT_CONTEXT_RE = re.compile(
    r"(?:"
    r"dictad[oa]\s+por\s+(?:el\s+)?candidato|"
    r"(?:escribio\s+y\s+)?dicto\s+curso|"
    r"curso\s+que\s+impartio|"
    r"impartio\s+como\s+(?:docente|instructor)|"
    r"curso\s+que\s+enseno|"
    r"enseno\s+como\s+(?:docente|instructor)|"
    r"como\s+(?:docente|instructor)"
    r")"
)


def _date_for_period(year: int, month: int, *, end: bool) -> date:
    day = monthrange(year, month)[1] if end else 1
    return date(year, month, day)


def _parse_experience_period_endpoint(value: str) -> tuple[int | None, int | None, bool]:
    normalized = _normalizar_nombre_para_match(value)
    if not normalized:
        return None, None, False
    if any(word in normalized.split() for word in _CURRENT_DATE_WORDS):
        return None, None, True

    numeric = re.fullmatch(r"(0?[1-9]|1[0-2])\s*/\s*(19\d{2}|20\d{2})", value.strip())
    if numeric:
        return int(numeric.group(2)), int(numeric.group(1)), False

    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", normalized)
    month = None
    month_source = normalized[:year_match.start()].strip() if year_match else normalized
    for token in reversed(month_source.split()):
        if token in _MONTH_NAMES:
            month = _MONTH_NAMES[token]
            break
    if not year_match:
        return None, month, False
    year = int(year_match.group(1))
    return year, month, False


def _extraer_rango_fechas_mes_anio(line: str, *, allow_current: bool) -> tuple[date, date | None] | None:
    if not line:
        return None

    # Reutilizamos una sola normalización para experiencias y estudios, pero el
    # contrato conservador exige mes+año: los rangos solo-año quedan fuera para
    # no inventar precisión que el CV no entregó.
    clean = " ".join(line.replace("\u2013", "-").replace("\u2014", "-").split())
    month_words = "|".join(sorted(_MONTH_NAMES, key=len, reverse=True))
    endpoint = rf"(?:\d{{1,2}}/\d{{4}}|(?:{month_words})\.?\s+\d{{4}}|\d{{4}}|(?:{month_words})\.?)"
    current = r"(?:actualidad|presente|a\s+la\s+fecha|la\s+fecha)"
    end_pattern = rf"{endpoint}|{current}" if allow_current else endpoint
    pattern = re.compile(rf"(?i)\b({endpoint})\s*(?:-|a)\s*({end_pattern})\b")
    matches = list(pattern.finditer(clean))
    if len(matches) != 1:
        return None

    start_year, start_month, start_current = _parse_experience_period_endpoint(matches[0].group(1))
    end_year, end_month, end_current = _parse_experience_period_endpoint(matches[0].group(2))
    if start_current:
        return None
    if start_year is None and start_month is not None and end_year is not None:
        start_year = end_year
    if start_year is None or start_month is None:
        return None
    if end_year is None and end_month is not None:
        end_year = start_year
    if end_current:
        return _date_for_period(start_year, start_month, end=False), None
    if end_year is None or end_month is None:
        return None

    start = _date_for_period(start_year, start_month, end=False)
    end = _date_for_period(end_year, end_month, end=True)
    if start > end:
        return None
    return start, end


def _extraer_rango_fechas_experiencia(line: str) -> tuple[date, date | None] | None:
    if not line:
        return None
    normalized_line = _normalizar_nombre_para_match(line)
    if any(signal in normalized_line.split() for signal in _EXPERIENCE_DATE_EDUCATION_SIGNALS):
        return None
    return _extraer_rango_fechas_mes_anio(line, allow_current=True)


def _extraer_rango_fechas_experiencia_en_bloque(lines: list[str]) -> tuple[date, date | None] | None:
    ranges = []
    for line in lines:
        parsed = _extraer_rango_fechas_experiencia(line)
        if parsed is not None:
            ranges.append(parsed)
    return ranges[0] if len(ranges) == 1 else None


def _extraer_rango_fechas_estudio(line: str) -> tuple[date, date | None] | None:
    normalized_line = _normalizar_nombre_para_match(line)
    words = normalized_line.split()
    if any(signal in words for signal in _STUDY_DATE_BLOCKED_SIGNALS):
        return None
    # Estudios no aceptan "Actualidad/Presente/En curso" en esta iteración:
    # no hubo evidencia real suficiente y sería fácil confundirlo con trabajo.
    return _extraer_rango_fechas_mes_anio(line, allow_current=False)


def _fecha_estudio_tiene_contexto_profesional(lines: list[str], date_line_index: int) -> bool:
    context = " ".join(
        _normalizar_nombre_para_match(line)
        for line in lines[max(0, date_line_index - 1): min(len(lines), date_line_index + 2)]
    )
    words = set(context.split())
    return any(signal in words for signal in _STUDY_DATE_PROFESSIONAL_CONTEXT_SIGNALS)


def _extraer_rango_fechas_estudio_en_bloque(
    lines: list[str],
    study_line_index: int,
) -> tuple[date, date | None] | None:
    normalized_study_line = _normalizar_nombre_para_match(lines[study_line_index])
    educational_context = any(
        signal in normalized_study_line.split()
        for signal in _STUDY_DATE_CONTEXT_SIGNALS
    )
    ranges = []
    for idx, line in enumerate(lines):
        if abs(idx - study_line_index) > 1:
            continue
        if idx != study_line_index and not educational_context:
            continue
        # Una línea fechada cerca de una universidad puede pertenecer a una
        # ayudantía, trabajo o proyecto; en ese caso no hay evidencia suficiente
        # para tratarla como fecha académica del estudio detectado.
        if idx != study_line_index and _fecha_estudio_tiene_contexto_profesional(lines, idx):
            continue
        parsed = _extraer_rango_fechas_estudio(line)
        if parsed is not None:
            ranges.append(parsed)

    # Cursos, certificaciones, columnas mezcladas o múltiples rangos cercanos
    # se dejan sin fecha: preferimos perder dato antes que contaminar un estudio.
    return ranges[0] if len(ranges) == 1 else None


def _es_heading_curso(folded_line: str) -> bool:
    # Un heading solo nombra la sección del CV; "Cursos", "Certificaciones" o
    # "Diplomados" no describen por sí mismos una formación concreta a persistir.
    heading = re.sub(r"^[\s:;,.·\-–—]+|[\s:;,.·\-–—]+$", "", folded_line)
    return heading in _COURSE_HEADING_WORDS


def _es_linea_curso_conservadora(line: str, folded_line: str) -> bool:
    # La detección por substring contaminaba "recursos" como si fuera "curso";
    # exigimos señales delimitadas y luego evidencia de formación concreta.
    if not _COURSE_SIGNAL_RE.search(folded_line):
        return False
    if _es_heading_curso(folded_line):
        return False

    normalized = " ".join(folded_line.replace(":", " : ").split())
    words = normalized.split()
    if len(words) < 3:
        return False

    # Una mención a curso/certificación/certificado dentro de funciones o
    # responsabilidades no prueba formación realizada; ante ambigüedad,
    # preferimos no persistir antes que guardar una función laboral como curso.
    if any(signal in normalized for signal in _COURSE_LABOR_CONTEXT_SIGNALS):
        return False

    # La colección representa formación obtenida por el candidato. Cuando la
    # propia línea indica que el candidato dictó/impartió el curso, pertenece a
    # trayectoria docente/laboral y no a cursos realizados.
    if _COURSE_TAUGHT_CONTEXT_RE.search(normalized):
        return False

    return bool(
        _COURSE_STRONG_START_RE.search(normalized)
        or _CERTIFICATION_STRONG_RE.search(normalized)
    )


_LANGUAGE_SECTION_HEADINGS = {"idiomas", "languages", "language"}
_LANGUAGE_SECTION_STOP_HEADINGS = {
    "experiencia", "experiencia laboral", "educacion", "estudios", "formacion",
    "habilidades", "competencias", "skills", "tecnologias", "cursos",
    "certificaciones", "contacto", "perfil", "perfil profesional", "proyectos",
    "referencias",
}


def _lineas_idiomas_explicitas(lines: list[str]) -> list[str]:
    """Limita la extracción automática al bloque rotulado de idiomas.

    El mismo nombre de idioma puede aparecer en una experiencia o en una
    descripción; exigir un encabezado explícito evita convertir una mención
    profesional en una asociación de idioma del candidato.
    """
    result: list[str] = []
    in_block = False
    for line in lines:
        folded = cv_parser.fold_text(line).strip(" :;-–—")
        if not in_block:
            heading_match = re.match(r"^\s*(idiomas?|languages?)\s*[:\-–—]?\s*(.*)$", line, re.I)
            if heading_match and cv_parser.fold_text(heading_match.group(1)) in _LANGUAGE_SECTION_HEADINGS:
                in_block = True
                remainder = heading_match.group(2).strip()
                if remainder and cv_parser.fold_text(remainder) not in _LANGUAGE_SECTION_HEADINGS:
                    result.append(remainder)
            continue
        if folded in _LANGUAGE_SECTION_STOP_HEADINGS:
            break
        result.append(line)
    return result


def _idioma_nivel_codes(value: str) -> set[str]:
    """Devuelve todas las señales de nivel para poder rechazar combinaciones ambiguas."""
    folded = cv_parser.fold_text(value)
    codes = {match.upper() for match in re.findall(r"(?<![a-z0-9])([abc][12])(?![a-z0-9])", folded)}
    signals = (
        ("NAT", r"\b(?:nativo|native|native speaker|mother tongue|lengua materna)\b"),
        ("AVA", r"\b(?:avanzado|advanced|fluent|fluido)\b"),
        ("INT", r"\b(?:intermedio|intermediate)\b"),
        ("BAS", r"\b(?:basico|basic|elementary)\b"),
    )
    for code, pattern in signals:
        if re.search(pattern, folded):
            codes.add(code)
    return codes


def _idioma_candidatos_de_linea(line: str) -> list[tuple[str, set[str]]]:
    """Obtiene solo pares nombre/nivel delimitados dentro del bloque de idiomas."""
    candidates: list[tuple[str, set[str]]] = []
    for segment in re.split(r"\s*[|;]\s*", line):
        segment = segment.strip(" -–—:;,•*\t")
        if not segment:
            continue
        codes = _idioma_nivel_codes(segment)
        if not codes:
            continue
        # Se acepta también "Inglés Avanzado"; el nivel se separa únicamente
        # al final y no se intenta adivinar nombres desde texto libre.
        match = re.match(
            r"^(?P<name>.+?)\s*(?:[:\-–—]|\s)(?P<level>"
            r"(?:[abc][12]|nativo|native(?: speaker)?|mother tongue|lengua materna|"
            r"avanzado|advanced|fluent|fluido|intermedio|intermediate|basico|basic|elementary)"
            r"(?:\b.*)?)$",
            segment,
            re.I,
        )
        if match:
            candidates.append((match.group("name").strip(), codes))
    return candidates


def _warning_once(warnings: list[str], message: str) -> None:
    if message not in warnings:
        warnings.append(message)


def derive_nested_from_cv(
    db: Session,
    text: str,
    *,
    origin_candidate_id: int | None = None,
) -> tuple[dict, list[str]]:
    """Deriva asociaciones del CV y altas conservadoras de catálogos seguros.

    Procesa habilidades, estudios, experiencias, cursos e idiomas, reutilizando
    catálogos normalizados y creando solo valores inequívocos en contextos
    explícitos del CV.
    """
    import re
    lines = [" ".join(x.split()) for x in text.splitlines() if x.strip()]
    folded_lines = [_fold(x) for x in lines]
    folded_text = "\n".join(folded_lines)
    warnings: list[str] = []

    # Las coincidencias existentes se pueden reconocer en cualquier línea como
    # antes; las altas nuevas, en cambio, requieren una sección/lista explícita
    # para no convertir frases laborales en habilidades maestras.
    skills_payload: list[dict] = []
    levels = list(db.scalars(select(NivelHabilidad)).all())
    catalog_skills = list(db.scalars(select(Habilidad).order_by(Habilidad.hab_id)).all())
    skills_by_id: dict[int, dict] = {}
    auto_catalogs: list[object] = []
    for line in lines:
        for skill, nombre_normalizado, start, end in _matches_habilidades_en_linea(catalog_skills, line):
            years = _extraer_anios_habilidad(line, nombre_normalizado, start, end)
            level = _buscar_unico_por_nombre_normalizado(levels, "nvhb_nombre", "nvhb_id", line)
            existing = skills_by_id.get(skill.hab_id)
            if existing is None:
                skills_by_id[skill.hab_id] = {
                    "cdhb_habilidad_id": skill.hab_id,
                    "cdhb_nivel_habilidad_id": getattr(level, "nvhb_id", None),
                    "cdhb_anios_experiencia": years,
                }
                continue
            if existing.get("cdhb_anios_experiencia") is None and years is not None:
                existing["cdhb_anios_experiencia"] = years
            if existing.get("cdhb_nivel_habilidad_id") is None and level is not None:
                existing["cdhb_nivel_habilidad_id"] = level.nvhb_id

    explicit_skill_lines = _lineas_de_habilidades_explicitas(lines)
    for skill_line in explicit_skill_lines:
        for raw_skill in _candidatos_habilidad_desde_linea(skill_line):
            value = _catalog_value_for_auto_creation(
                raw_skill,
                max_length=255,
                kind="habilidad",
            )
            if value is None:
                continue
            normalized = _normalizar_nombre_para_match(value)
            matches = [
                skill
                for skill in catalog_skills
                if _iter_nombre_normalizado_en_contexto(
                    normalized,
                    _normalizar_nombre_para_match(getattr(skill, "hab_nombre", None)),
                )
            ]
            if len(matches) > 1:
                warnings.append(f"No se creó habilidad desde CV: coincidencias ambiguas para '{value}'.")
                continue
            skill = matches[0] if matches else _resolve_or_create_experience_catalog(
                db,
                catalog_skills,
                Habilidad,
                id_attr="hab_id",
                name_attr="hab_nombre",
                raw_value=value,
                max_length=255,
                kind="habilidad",
                origin_candidate_id=origin_candidate_id,
                warnings=warnings,
            )
            if skill is None:
                continue
            if getattr(skill, "hab_creado_automaticamente", False) and skill not in auto_catalogs:
                auto_catalogs.append(skill)
            skill_id = getattr(skill, "hab_id", None)
            if skill_id is None or skill_id in skills_by_id:
                continue
            start = _normalizar_nombre_para_match(skill_line).find(normalized)
            end = start + len(normalized) if start >= 0 else None
            years = _extraer_anios_habilidad(skill_line, normalized, start, end)
            level = _buscar_unico_por_nombre_normalizado(levels, "nvhb_nombre", "nvhb_id", skill_line)
            skills_by_id[skill_id] = {
                "cdhb_habilidad_id": skill_id,
                "cdhb_nivel_habilidad_id": getattr(level, "nvhb_id", None),
                "cdhb_anios_experiencia": years,
            }
    skills_payload = list(skills_by_id.values())

    # Educación permite institución O carrera porque ambos son datos valiosos
    # por separado; las fechas siguen reglas propias para no heredar rangos de
    # experiencia, cursos o certificaciones cercanas.
    institutions = list(db.scalars(select(Institucion)).all())
    careers = list(db.scalars(select(Carrera)).all())
    education_levels = list(db.scalars(select(NivelEducacional)).all())
    studies: list[dict] = []
    seen_studies: set[tuple] = set()
    academic_indices = _lineas_academicas_explicitas(lines)
    for idx, (line, fline) in enumerate(zip(lines, folded_lines)):
        inst = _buscar_unico_por_nombre_normalizado(institutions, "inst_nombre", "inst_id", line)
        career = _buscar_unico_por_nombre_normalizado(careers, "crra_nombre", "crra_id", line)
        raw_inst, raw_career = (None, None)
        if idx in academic_indices:
            raw_inst, raw_career = _componentes_estudio_en_contexto(lines, idx, academic_indices)
        if inst is None and raw_inst is not None:
            inst = _resolve_or_create_experience_catalog(
                db,
                institutions,
                Institucion,
                id_attr="inst_id",
                name_attr="inst_nombre",
                raw_value=raw_inst,
                max_length=40,
                kind="institucion",
                origin_candidate_id=origin_candidate_id,
                warnings=warnings,
            )
            if inst is not None and getattr(inst, "inst_creado_automaticamente", False) and inst not in auto_catalogs:
                auto_catalogs.append(inst)
        if career is None and raw_career is not None:
            career = _resolve_or_create_experience_catalog(
                db,
                careers,
                Carrera,
                id_attr="crra_id",
                name_attr="crra_nombre",
                raw_value=raw_career,
                max_length=255,
                kind="carrera",
                origin_candidate_id=origin_candidate_id,
                warnings=warnings,
            )
            if career is not None and getattr(career, "crra_creado_automaticamente", False) and career not in auto_catalogs:
                auto_catalogs.append(career)
        if not inst and not career:
            continue
        level = _buscar_unico_por_nombre_normalizado(education_levels, "nved_nombre", "nved_id", line)
        key = (getattr(inst, "inst_id", None), getattr(career, "crra_id", None), getattr(level, "nved_id", None))
        if key in seen_studies:
            continue
        seen_studies.add(key)
        context_start = max(0, idx - 2)
        context_lines = lines[context_start: min(len(lines), idx + 2)]
        dates = _extraer_rango_fechas_estudio_en_bloque(context_lines, idx - context_start)
        studies.append({
            "etcd_nivel_educacional_id": getattr(level, "nved_id", None),
            "etcd_institucion_id": getattr(inst, "inst_id", None),
            "etcd_carrera_id": getattr(career, "crra_id", None),
            "etcd_fecha_inicio": dates[0] if dates else None,
            "etcd_fecha_fin": dates[1] if dates else None,
        })

    # Experiencia laboral exige empresa + cargo resueltos con certeza: primero
    # reutiliza catálogos y, solo ante nombres delimitados válidos, crea los
    # faltantes; nunca usa fuzzy matching ni convierte funciones en catálogos.
    # Solo crea una experiencia si ambos aparecen en la misma línea o líneas muy próximas.
    from app.catalogos.models import Cargo
    companies = list(db.scalars(select(Empresa)).all())
    cargos = list(db.scalars(select(Cargo)).all())
    experiences: list[dict] = []
    seen_exp: set[tuple] = set()
    for idx, (line, fline) in enumerate(zip(lines, folded_lines)):
        context_lines = lines[max(0, idx - 1): min(len(lines), idx + 2)]
        context = " ".join(context_lines)
        company = _buscar_unico_por_nombre_normalizado(companies, "emp_nombre", "emp_id", context)
        cargo = _buscar_unico_por_nombre_normalizado(cargos, "crgo_nombre", "crgo_id", context)
        pair_company, pair_cargo = _extract_experience_pair(context_lines)
        if company is not None and cargo is None:
            pair_cargo = pair_cargo or _extract_missing_experience_value(
                context_lines,
                company.emp_nombre,
                after=True,
            )
        if cargo is not None and company is None:
            pair_company = pair_company or _extract_missing_experience_value(
                context_lines,
                cargo.crgo_nombre,
                after=False,
            )
        # Una línea de fechas puede tener texto auxiliar entre empresa y cargo;
        # no debemos convertirlo en catálogo antes de evaluar el bloque completo.
        has_date_context = any(re.search(r"\b(?:19|20)\d{2}\b", _normalizar_nombre_para_match(item)) for item in context_lines)
        if company is None and not has_date_context:
            company = _resolve_or_create_experience_catalog(
                db,
                companies,
                Empresa,
                id_attr="emp_id",
                name_attr="emp_nombre",
                raw_value=pair_company,
                max_length=30,
                kind="empresa",
                origin_candidate_id=origin_candidate_id,
                warnings=warnings,
            )
            if company is not None and getattr(company, "emp_creado_automaticamente", False):
                auto_catalogs.append(company)
        if cargo is None and not has_date_context:
            cargo = _resolve_or_create_experience_catalog(
                db,
                cargos,
                Cargo,
                id_attr="crgo_id",
                name_attr="crgo_nombre",
                raw_value=pair_cargo,
                max_length=50,
                kind="cargo",
                origin_candidate_id=origin_candidate_id,
                warnings=warnings,
            )
            if cargo is not None and getattr(cargo, "crgo_creado_automaticamente", False):
                auto_catalogs.append(cargo)
        if not company or not cargo:
            if not company:
                warnings.append("No se creó empresa desde CV: no hubo un nombre laboral válido e inequívoco asociado.")
            if not cargo:
                warnings.append("No se creó cargo desde CV: no hubo un nombre laboral válido e inequívoco asociado.")
            continue
        key = (company.emp_id, cargo.crgo_id)
        if key in seen_exp:
            continue
        seen_exp.add(key)
        dates = _extraer_rango_fechas_experiencia_en_bloque(context_lines)
        experiences.append({
            "expl_empresa_id": company.emp_id,
            "expl_cargo_id": cargo.crgo_id,
            "expl_descripcion_funciones": line[:300] if line else "Información extraída desde CV",
            "expl_fecha_inicio": dates[0] if dates else None,
            "expl_fecha_fin": dates[1] if dates else None,
            "habilidades_ids": [],
        })

    # Cursos/certificaciones: el nombre textual se conserva; institución se mapea
    # solo si está reconocida por el catálogo.
    courses: list[dict] = []
    seen_courses: set[str] = set()
    for line, fline in zip(lines, folded_lines):
        if not _es_linea_curso_conservadora(line, fline):
            continue
        # La decisión se toma con la línea completa; el límite físico de 40
        # caracteres se aplica después para no validar usando texto sin contexto.
        course_name = line[:40].strip()
        if not course_name or course_name.casefold() in seen_courses:
            continue
        seen_courses.add(course_name.casefold())
        inst = next((x for x in institutions if x.inst_nombre and _fold(x.inst_nombre) in fline), None)
        year_match = re.search(r"\b(19\d{2}|20\d{2})\b", line)
        courses.append({
            "curs_nombre_curso": course_name,
            "curs_institucion_id": getattr(inst, "inst_id", None),
            "curs_es_certificado": "cert" in fline,
            "curs_anio_curso": int(year_match.group(1)) if year_match else None,
        })

    # Idiomas: solo se consideran líneas del bloque explícito y niveles únicos
    # ya existentes; no se crean asociaciones parciales ni niveles inventados.
    language_payload: list[dict] = []
    seen_language_ids: set[int] = set()
    level_by_code = {x.nvid_codigo.upper(): x for x in db.scalars(select(NivelIdioma).where(NivelIdioma.nvid_activo.is_(True))).all()}
    language_catalog = list(db.scalars(select(Idioma).order_by(Idioma.idio_id)).all())
    language_lines = _lineas_idiomas_explicitas(lines)
    folded_language_lines = [cv_parser.fold_text(x) for x in language_lines]
    for language in language_catalog:
        aliases = cv_parser.language_aliases(language.idio_nombre)
        matching_indexes = [
            idx for idx, fline in enumerate(folded_language_lines)
            if any(re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", fline) for alias in aliases)
        ]
        evidence_codes: set[str] = set()
        for idx in matching_indexes:
            evidence_codes.update(_idioma_nivel_codes(language_lines[idx]))
            if not evidence_codes and idx + 1 < len(language_lines) and len(language_lines[idx + 1]) <= 80:
                evidence_codes.update(_idioma_nivel_codes(language_lines[idx + 1]))
        if len(evidence_codes) > 1:
            _warning_once(warnings, f"No se asoció {language.idio_nombre}: el nivel detectado es ambiguo.")
            continue
        if not evidence_codes:
            _warning_once(warnings, f"Se detectó el idioma '{language.idio_nombre}', pero no se pudo resolver un nivel válido del catálogo.")
            continue
        detected_level_code = next(iter(evidence_codes))
        level = level_by_code.get(detected_level_code)
        if level is None:
            _warning_once(warnings, f"Se detectó {language.idio_nombre} con nivel {detected_level_code}, pero ese nivel no existe o está inactivo en el catálogo.")
            continue
        if language.idio_id not in seen_language_ids:
            language_payload.append({
                "cdio_idioma_id": language.idio_id,
                "cdio_nivel_idioma_id": level.nvid_id,
            })
            seen_language_ids.add(language.idio_id)

    # El nombre nuevo solo es confiable si aparece delimitado junto a un nivel
    # único. Resolver primero el nivel evita crear catálogos sin asociación útil.
    for line in language_lines:
        for segment in re.split(r"\s*[|;]\s*", line):
            raw_segment = segment.strip(" -–—:;,•*\t")
            if raw_segment and not _idioma_nivel_codes(raw_segment):
                value = _catalog_value_for_auto_creation(raw_segment, max_length=100, kind="idioma")
                if value is not None and not any(
                    _normalizar_nombre_para_match(value) == _normalizar_nombre_para_match(alias)
                    for language in language_catalog
                    for alias in cv_parser.language_aliases(language.idio_nombre)
                ):
                    _warning_once(warnings, f"Se detectó el idioma '{value}', pero no se pudo resolver un nivel válido del catálogo.")
        for raw_name, evidence_codes in _idioma_candidatos_de_linea(line):
            value = _catalog_value_for_auto_creation(raw_name, max_length=100, kind="idioma")
            if value is None:
                continue
            if len(evidence_codes) != 1:
                _warning_once(warnings, f"No se creó idioma desde CV: el nivel de '{value}' es ambiguo.")
                continue
            level = level_by_code.get(next(iter(evidence_codes)))
            if level is None:
                _warning_once(warnings, f"Se detectó el idioma '{value}', pero su nivel no existe o está inactivo en el catálogo.")
                continue
            normalized = _normalizar_nombre_para_match(value)
            matches = [
                language for language in language_catalog
                if _normalizar_nombre_para_match(language.idio_nombre) == normalized
                or any(_normalizar_nombre_para_match(alias) == normalized for alias in cv_parser.language_aliases(language.idio_nombre))
            ]
            if len(matches) > 1:
                _warning_once(warnings, f"No se creó idioma desde CV: coincidencias ambiguas para '{value}'.")
                continue
            language = matches[0] if matches else _resolve_or_create_experience_catalog(
                db,
                language_catalog,
                Idioma,
                id_attr="idio_id",
                name_attr="idio_nombre",
                raw_value=value,
                max_length=100,
                kind="idioma",
                origin_candidate_id=origin_candidate_id,
                warnings=warnings,
            )
            if language is None or language.idio_id in seen_language_ids:
                continue
            if getattr(language, "idio_creado_automaticamente", False) and language not in auto_catalogs:
                auto_catalogs.append(language)
            language_payload.append({
                "cdio_idioma_id": language.idio_id,
                "cdio_nivel_idioma_id": level.nvid_id,
            })
            seen_language_ids.add(language.idio_id)

    if not skills_payload:
        warnings.append("No se detectaron habilidades persistibles: no hubo un valor válido, inequívoco y asociado a un contexto confiable.")
    if not studies:
        warnings.append("No se detectaron estudios persistibles: no hubo institución o carrera válida, inequívoca y asociada a contexto académico.")
    if not experiences:
        warnings.append("No se mapearon experiencias laborales: no hubo empresa y cargo resueltos con suficiente certeza.")
    if any(x in folded_text for x in ("idioma", "languages", "language")) and not language_payload:
        warnings.append("Se detectó una sección de idiomas, pero no fue posible mapear idioma y nivel contra los catálogos existentes.")

    return {
        "habilidades": skills_payload,
        "estudios": studies,
        "experiencias": experiences,
        "cursos": courses,
        "idiomas": language_payload,
        "_catalogos_creados": auto_catalogs,
    }, warnings


def merge_imported_nested(db: Session, candidate: models.Candidato, nested: dict) -> None:
    """Agrega datos CV nuevos sin duplicar los ya existentes."""
    existing_skill_ids = {x.cdhb_habilidad_id for x in candidate.habilidades}
    # La clave de habilidad evita duplicar la asociación en reimportaciones;
    # los valores faltantes no reemplazan una corrección manual existente.
    for item in nested.get("habilidades", []):
        if item["cdhb_habilidad_id"] not in existing_skill_ids:
            candidate.habilidades.append(models.CandidatoHabilidad(**item))
            existing_skill_ids.add(item["cdhb_habilidad_id"])

    existing_studies = {
        (x.etcd_nivel_educacional_id, x.etcd_institucion_id, x.etcd_carrera_id)
        for x in candidate.estudios
    }
    # El merge de importación complementa el perfil, no reemplaza registros
    # corregidos manualmente; por eso deduplica por las claves de catálogo.
    for item in nested.get("estudios", []):
        key = (item.get("etcd_nivel_educacional_id"), item.get("etcd_institucion_id"), item.get("etcd_carrera_id"))
        if key not in existing_studies:
            candidate.estudios.append(models.EstudioCandidato(**item)); existing_studies.add(key)

    existing_exps = {(x.expl_empresa_id, x.expl_cargo_id) for x in candidate.experiencias}
    # Una misma pareja empresa/cargo se considera la misma experiencia para el
    # merge conservador; así la reimportación no crea filas repetidas.
    for item in nested.get("experiencias", []):
        hids = item.pop("habilidades_ids", [])
        key = (item.get("expl_empresa_id"), item.get("expl_cargo_id"))
        if key not in existing_exps:
            exp = models.ExperienciaLaboral(**item)
            exp.habilidades_asociadas = [models.ExperienciaLaboralHabilidad(exph_habilidad_id=h) for h in hids]
            candidate.experiencias.append(exp); existing_exps.add(key)

    existing_courses = {(x.curs_nombre_curso or "").casefold() for x in candidate.cursos}
    # Los cursos carecen de una clave de catálogo propia, por lo que el nombre
    # normalizado es la única deduplicación segura disponible en esta etapa.
    for item in nested.get("cursos", []):
        key = (item.get("curs_nombre_curso") or "").casefold()
        if key and key not in existing_courses:
            candidate.cursos.append(models.Curso(**item)); existing_courses.add(key)

    # Los idiomas importados se agregan solo si no existen. Una reimportación
    # nunca sobrescribe silenciosamente un nivel corregido manualmente.
    existing_language_ids = {x.cdio_idioma_id for x in candidate.idiomas}
    for item in nested.get("idiomas", []):
        if item["cdio_idioma_id"] not in existing_language_ids:
            candidate.idiomas.append(models.CandidatoIdioma(**item))
            existing_language_ids.add(item["cdio_idioma_id"])

# ----------------------------- postulaciones -----------------------------
STATE_TRANSITIONS = {
    "en revision": {"en entrevista", "inhabilitado", "descartado"},
    "en entrevista": {"seleccionado", "descartado", "inhabilitado"},
    "seleccionado": {"contratado", "descartado"},
    "inhabilitado": set(), "descartado": set(), "contratado": set(),
}


def _application_state(db: Session, name: str) -> EstadoSolicitudCandidato:
    obj=db.scalar(select(EstadoSolicitudCandidato).where(EstadoSolicitudCandidato.essc_nombre.ilike(name)))
    if obj is None: raise ValidationError(f"No existe estado de postulación '{name}'")
    return obj


def evaluate_exclusions(db:Session,solicitud_id:int,candidate_id:int) -> schemas.EvaluacionExcluyentes:
    requirements=list(db.scalars(select(SolicitudHabilidad).where(SolicitudHabilidad.solhb_solicitud_id==solicitud_id,SolicitudHabilidad.solhb_es_excluyente.is_(True))).all())
    skills=list(db.scalars(select(models.CandidatoHabilidad).where(models.CandidatoHabilidad.cdhb_candidato_id==candidate_id)).all())
    by_id={x.cdhb_habilidad_id:x for x in skills}
    missing=[]
    for req in requirements:
        got=by_id.get(req.solhb_habilidad_id)
        reason=None
        if got is None: reason="Habilidad no declarada"
        elif (got.cdhb_anios_experiencia or 0) < (req.solhb_anios_experiencia_req or 0): reason="Años de experiencia insuficientes"
        elif req.solhb_nivel_habilidad_id and got.cdhb_nivel_habilidad_id:
            req_lvl=db.get(NivelHabilidad,req.solhb_nivel_habilidad_id); got_lvl=db.get(NivelHabilidad,got.cdhb_nivel_habilidad_id)
            if req_lvl and got_lvl and (got_lvl.nvhb_puntaje_base or 0)<(req_lvl.nvhb_puntaje_base or 0): reason="Nivel de habilidad insuficiente"
        elif req.solhb_nivel_habilidad_id and not got.cdhb_nivel_habilidad_id: reason="Nivel de habilidad no informado"
        if reason:
            hab=db.get(Habilidad,req.solhb_habilidad_id)
            missing.append({"habilidad_id":req.solhb_habilidad_id,"habilidad":hab.hab_nombre if hab else None,"motivo":reason})
    ok=not missing
    return schemas.EvaluacionExcluyentes(cumple_excluyentes=ok,habilidades_faltantes=missing,advertencia=None if ok else "El candidato fue asociado, pero no cumple todos los requisitos excluyentes.")


def create_application(db:Session,solicitud_id:int,candidate_id:int,payload:schemas.PostulacionCreate):
    if db.get(Solicitud,solicitud_id) is None: raise NotFoundError("Solicitud no encontrada")
    get_candidate(db,candidate_id)
    exists=db.scalar(select(SolicitudCandidato.slcd_id).where(SolicitudCandidato.slcd_solicitud_id==solicitud_id,SolicitudCandidato.slcd_candidato_id==candidate_id))
    if exists: raise ConflictError("El candidato ya está asociado a esta solicitud")
    state=_application_state(db,"En revision")
    obj=SolicitudCandidato(slcd_candidato_id=candidate_id,slcd_solicitud_id=solicitud_id,slcd_estado_solicitud_candidato_id=state.essc_id,slcd_fecha_postulacion=datetime.utcnow(),**payload.model_dump())
    db.add(obj); _commit(db); db.refresh(obj)
    return obj,evaluate_exclusions(db,solicitud_id,candidate_id)


def get_application(db:Session,application_id:int)->SolicitudCandidato:
    obj=db.get(SolicitudCandidato,application_id)
    if obj is None: raise NotFoundError("Postulación no encontrada")
    return obj


def update_application(db:Session,obj:SolicitudCandidato,payload:schemas.PostulacionUpdate):
    data=payload.model_dump(exclude_unset=True)
    if not data: raise ValidationError("Debe enviar al menos un campo")
    for k,v in data.items(): setattr(obj,k,v)
    _commit(db); db.refresh(obj); return obj


def validar_cambio_estado_postulacion(
    db: Session,
    obj: SolicitudCandidato,
    payload: schemas.PostulacionEstadoUpdate,
) -> EstadoSolicitudCandidato | None:
    """Valida si la transición de estado de una postulación está permitida.

    Usa las reglas existentes de STATE_TRANSITIONS y valida datos asociados,
    pero no modifica ni guarda la postulación. La separación es:
    validar -> aplicar sin commit -> commit final del flujo que orquesta.
    """
    current=db.get(EstadoSolicitudCandidato,obj.slcd_estado_solicitud_candidato_id)
    target=db.get(EstadoSolicitudCandidato,payload.estado_id)
    if target is None: raise ValidationError("Estado de postulación no existe")
    current_name=(current.essc_nombre if current else "").casefold()
    target_name=target.essc_nombre.casefold()
    if target_name==current_name: return None
    allowed=STATE_TRANSITIONS.get(current_name,set())
    if target_name not in allowed: raise ConflictError(f"Transición no permitida: {current.essc_nombre if current else '?'} -> {target.essc_nombre}")
    if target_name in {"inhabilitado","descartado"}:
        if payload.motivo_rechazo_id is None: raise ValidationError("Inhabilitado y Descartado requieren motivo_rechazo_id")
        if db.get(MotivoRechazo,payload.motivo_rechazo_id) is None: raise ValidationError("Motivo de rechazo no existe")
    else:
        if payload.motivo_rechazo_id is not None: raise ValidationError("motivo_rechazo_id solo corresponde a Inhabilitado o Descartado")
    return target


def aplicar_cambio_estado_postulacion_sin_commit(
    obj: SolicitudCandidato,
    target: EstadoSolicitudCandidato | None,
    payload: schemas.PostulacionEstadoUpdate,
) -> None:
    """Aplica el cambio de estado de la postulación sin realizar commit.

    Deja los cambios en memoria para que formen parte de una transacción mayor
    y se confirmen junto con otras operaciones relacionadas en un commit final.
    """
    if target is None:
        return
    obj.slcd_estado_solicitud_candidato_id=target.essc_id
    obj.slcd_motivo_rechazo_id=payload.motivo_rechazo_id
    if payload.observaciones is not None: obj.slcd_observaciones=payload.observaciones


def change_application_state(db:Session,obj:SolicitudCandidato,payload:schemas.PostulacionEstadoUpdate):
    # El endpoint individual conserva su commit propio, pero usa la misma validación reutilizable.
    target = validar_cambio_estado_postulacion(db, obj, payload)
    aplicar_cambio_estado_postulacion_sin_commit(obj, target, payload)
    if target is None:
        return obj
    _commit(db); db.refresh(obj); return obj


def list_request_applications(db:Session,solicitud_id:int,estado_id:int|None=None):
    if db.get(Solicitud,solicitud_id) is None: raise NotFoundError("Solicitud no encontrada")
    stmt=select(SolicitudCandidato).where(SolicitudCandidato.slcd_solicitud_id==solicitud_id)
    if estado_id: stmt=stmt.where(SolicitudCandidato.slcd_estado_solicitud_candidato_id==estado_id)
    return list(db.scalars(stmt.order_by(SolicitudCandidato.slcd_id.desc())).all())


def list_candidate_applications(
    db: Session,
    candidate_id: int,
    estado_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    get_candidate(db, candidate_id)
    stmt = select(SolicitudCandidato).where(
        SolicitudCandidato.slcd_candidato_id == candidate_id
    )
    if estado_id is not None:
        stmt = stmt.where(
            SolicitudCandidato.slcd_estado_solicitud_candidato_id == estado_id
        )
    stmt = (
        stmt.order_by(SolicitudCandidato.slcd_id.desc())
        .offset(max(skip, 0))
        .limit(min(max(limit, 1), 500))
    )
    return list(db.scalars(stmt).all())
