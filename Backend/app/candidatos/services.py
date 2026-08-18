from __future__ import annotations

import os
import re
import secrets
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.auth.utils import hash_password
from app.catalogos.models import (
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


def derive_nested_from_cv(db: Session, text: str) -> tuple[dict, list[str]]:
    """
    Mapea datos del CV a catálogos existentes sin crear catálogos nuevos.
    Es conservador: solo persiste asociaciones cuando encuentra coincidencias
    textuales razonables con registros ya existentes.
    """
    import re
    lines = [" ".join(x.split()) for x in text.splitlines() if x.strip()]
    folded_lines = [_fold(x) for x in lines]
    folded_text = "\n".join(folded_lines)
    warnings: list[str] = []

    # Habilidades: una coincidencia del nombre del catálogo en el texto genera
    # la habilidad. Intenta además detectar años y nivel en una ventana cercana.
    skills_payload: list[dict] = []
    levels = list(db.scalars(select(NivelHabilidad)).all())
    for skill in db.scalars(select(Habilidad).order_by(Habilidad.hab_id)).all():
        name = (skill.hab_nombre or "").strip()
        if not name:
            continue
        fname = _fold(name)
        pos = folded_text.find(fname)
        if pos < 0:
            continue
        window = folded_text[max(0, pos - 80): pos + len(fname) + 100]
        years = 0
        m = re.search(r"(\d{1,2})\s*(?:anos|ano|years?|yrs?)", window)
        if m:
            years = int(m.group(1))
        level_id = None
        for level in levels:
            lname = _fold(level.nvhb_nombre or "")
            if lname and lname in window:
                level_id = level.nvhb_id
                break
        skills_payload.append({
            "cdhb_habilidad_id": skill.hab_id,
            "cdhb_nivel_habilidad_id": level_id,
            "cdhb_anios_experiencia": years,
        })

    # Educación: combina institución + carrera cuando aparecen en una misma línea.
    institutions = list(db.scalars(select(Institucion)).all())
    careers = list(db.scalars(select(Carrera)).all())
    education_levels = list(db.scalars(select(NivelEducacional)).all())
    studies: list[dict] = []
    seen_studies: set[tuple] = set()
    for line, fline in zip(lines, folded_lines):
        inst = next((x for x in institutions if x.inst_nombre and _fold(x.inst_nombre) in fline), None)
        career = next((x for x in careers if x.crra_nombre and _fold(x.crra_nombre) in fline), None)
        if not inst and not career:
            continue
        level = next((x for x in education_levels if x.nved_nombre and _fold(x.nved_nombre) in fline), None)
        key = (getattr(inst, "inst_id", None), getattr(career, "crra_id", None), getattr(level, "nved_id", None))
        if key in seen_studies:
            continue
        seen_studies.add(key)
        studies.append({
            "etcd_nivel_educacional_id": getattr(level, "nved_id", None),
            "etcd_institucion_id": getattr(inst, "inst_id", None),
            "etcd_carrera_id": getattr(career, "crra_id", None),
            "etcd_fecha_inicio": None,
            "etcd_fecha_fin": None,
        })

    # Experiencia laboral: el esquema físico exige empresa/cargo de catálogo.
    # Solo crea una experiencia si ambos aparecen en la misma línea o líneas muy próximas.
    from app.catalogos.models import Cargo
    companies = list(db.scalars(select(Empresa)).all())
    cargos = list(db.scalars(select(Cargo)).all())
    experiences: list[dict] = []
    seen_exp: set[tuple] = set()
    for idx, (line, fline) in enumerate(zip(lines, folded_lines)):
        context = " ".join(folded_lines[max(0, idx - 1): min(len(lines), idx + 2)])
        company = next((x for x in companies if x.emp_nombre and _fold(x.emp_nombre) in context), None)
        cargo = next((x for x in cargos if x.crgo_nombre and _fold(x.crgo_nombre) in context), None)
        if not company or not cargo:
            continue
        key = (company.emp_id, cargo.crgo_id)
        if key in seen_exp:
            continue
        seen_exp.add(key)
        experiences.append({
            "expl_empresa_id": company.emp_id,
            "expl_cargo_id": cargo.crgo_id,
            "expl_descripcion_funciones": line[:300] if line else "Información extraída desde CV",
            "expl_fecha_inicio": None,
            "expl_fecha_fin": None,
            "habilidades_ids": [],
        })

    # Cursos/certificaciones: el nombre textual se conserva; institución se mapea
    # solo si está reconocida por el catálogo.
    courses: list[dict] = []
    seen_courses: set[str] = set()
    for line, fline in zip(lines, folded_lines):
        if not any(k in fline for k in ("curso", "certificacion", "certificado", "diplomado")):
            continue
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

    # Idiomas: usa exclusivamente idiomas existentes en catálogo y requiere nivel detectable.
    language_payload: list[dict] = []
    seen_language_ids: set[int] = set()
    level_by_code = {x.nvid_codigo.upper(): x for x in db.scalars(select(NivelIdioma).where(NivelIdioma.nvid_activo.is_(True))).all()}
    language_lines = cv_parser.candidate_language_lines(text)
    folded_language_lines = [cv_parser.fold_text(x) for x in language_lines]
    for language in db.scalars(select(Idioma).order_by(Idioma.idio_id)).all():
        aliases = cv_parser.language_aliases(language.idio_nombre)
        detected_level_code = None
        for idx, fline in enumerate(folded_language_lines):
            if not any(re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", fline) for alias in aliases):
                continue
            # Prioriza la misma línea; si no hay nivel, permite la siguiente línea
            # cuando parece ser un valor corto de sección.
            detected_level_code = cv_parser.detect_language_level_code(language_lines[idx])
            if detected_level_code is None and idx + 1 < len(language_lines) and len(language_lines[idx + 1]) <= 80:
                detected_level_code = cv_parser.detect_language_level_code(language_lines[idx + 1])
            if detected_level_code:
                break
        if detected_level_code is None:
            continue
        level = level_by_code.get(detected_level_code.upper())
        if level is None:
            warnings.append(
                f"Se detectó {language.idio_nombre} con nivel {detected_level_code}, pero ese nivel no existe o está inactivo en el catálogo."
            )
            continue
        if language.idio_id not in seen_language_ids:
            language_payload.append({
                "cdio_idioma_id": language.idio_id,
                "cdio_nivel_idioma_id": level.nvid_id,
            })
            seen_language_ids.add(language.idio_id)

    if not skills_payload:
        warnings.append("No se mapearon habilidades contra el catálogo existente; revisar manualmente.")
    if not studies:
        warnings.append("No se mapearon estudios con suficiente certeza contra los catálogos existentes.")
    if not experiences:
        warnings.append("No se mapearon experiencias laborales: el esquema exige empresa y cargo existentes en catálogo.")
    if any(x in folded_text for x in ("idioma", "languages", "language")) and not language_payload:
        warnings.append("Se detectó una sección de idiomas, pero no fue posible mapear idioma y nivel contra los catálogos existentes.")

    return {
        "habilidades": skills_payload,
        "estudios": studies,
        "experiencias": experiences,
        "cursos": courses,
        "idiomas": language_payload,
    }, warnings


def merge_imported_nested(db: Session, candidate: models.Candidato, nested: dict) -> None:
    """Agrega datos CV nuevos sin duplicar los ya existentes."""
    existing_skill_ids = {x.cdhb_habilidad_id for x in candidate.habilidades}
    for item in nested.get("habilidades", []):
        if item["cdhb_habilidad_id"] not in existing_skill_ids:
            candidate.habilidades.append(models.CandidatoHabilidad(**item))
            existing_skill_ids.add(item["cdhb_habilidad_id"])

    existing_studies = {
        (x.etcd_nivel_educacional_id, x.etcd_institucion_id, x.etcd_carrera_id)
        for x in candidate.estudios
    }
    for item in nested.get("estudios", []):
        key = (item.get("etcd_nivel_educacional_id"), item.get("etcd_institucion_id"), item.get("etcd_carrera_id"))
        if key not in existing_studies:
            candidate.estudios.append(models.EstudioCandidato(**item)); existing_studies.add(key)

    existing_exps = {(x.expl_empresa_id, x.expl_cargo_id) for x in candidate.experiencias}
    for item in nested.get("experiencias", []):
        hids = item.pop("habilidades_ids", [])
        key = (item.get("expl_empresa_id"), item.get("expl_cargo_id"))
        if key not in existing_exps:
            exp = models.ExperienciaLaboral(**item)
            exp.habilidades_asociadas = [models.ExperienciaLaboralHabilidad(exph_habilidad_id=h) for h in hids]
            candidate.experiencias.append(exp); existing_exps.add(key)

    existing_courses = {(x.curs_nombre_curso or "").casefold() for x in candidate.cursos}
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


def change_application_state(db:Session,obj:SolicitudCandidato,payload:schemas.PostulacionEstadoUpdate):
    current=db.get(EstadoSolicitudCandidato,obj.slcd_estado_solicitud_candidato_id)
    target=db.get(EstadoSolicitudCandidato,payload.estado_id)
    if target is None: raise ValidationError("Estado de postulación no existe")
    current_name=(current.essc_nombre if current else "").casefold()
    target_name=target.essc_nombre.casefold()
    if target_name==current_name: return obj
    allowed=STATE_TRANSITIONS.get(current_name,set())
    if target_name not in allowed: raise ConflictError(f"Transición no permitida: {current.essc_nombre if current else '?'} -> {target.essc_nombre}")
    if target_name in {"inhabilitado","descartado"}:
        if payload.motivo_rechazo_id is None: raise ValidationError("Inhabilitado y Descartado requieren motivo_rechazo_id")
        if db.get(MotivoRechazo,payload.motivo_rechazo_id) is None: raise ValidationError("Motivo de rechazo no existe")
    else:
        if payload.motivo_rechazo_id is not None: raise ValidationError("motivo_rechazo_id solo corresponde a Inhabilitado o Descartado")
    obj.slcd_estado_solicitud_candidato_id=target.essc_id
    obj.slcd_motivo_rechazo_id=payload.motivo_rechazo_id
    if payload.observaciones is not None: obj.slcd_observaciones=payload.observaciones
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
