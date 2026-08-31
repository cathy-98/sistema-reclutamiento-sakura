from __future__ import annotations

import hashlib
import os
import re
import tempfile
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.auth.email_service import EmailConfigurationError, EmailDeliveryError, send_email
from app.informes.models import (
    CandidatoIdioma,
    CategoriaHabilidad,
    DocumentoReporteCandidato,
    Idioma,
    NivelIdioma,
    NotificacionReclutamiento,
    PlantillaNotificacion,
)
from app.informes.pdf_service import generate_candidate_summary, generate_corporate_cv
from app.informes.schemas import CVOverrides


APPROVED_RESULTS = {"aprobado", "aprobado con observaciones"}
REJECTED_RESULT = "no aprobado"
PENDING_RESULTS = {"en espera", "requiere segunda entrevista"}
REJECTED_STATES = {"descartado", "inhabilitado"}
APPROVED_STATES = {"seleccionado", "contratado"}
INTERVIEW_STATE = "en entrevista"
REVIEW_STATE = "en revision"


def _norm(value: Any) -> str:
    if value is None:
        return ""
    raw = unicodedata.normalize("NFKD", str(value))
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    return " ".join(raw.casefold().strip().split())


def _rows(db: Session, sql: str, params: dict | None = None) -> list[dict]:
    return [dict(x) for x in db.execute(text(sql), params or {}).mappings().all()]


def _one(db: Session, sql: str, params: dict | None = None) -> dict | None:
    row = db.execute(text(sql), params or {}).mappings().first()
    return dict(row) if row else None


def _storage_root() -> Path:
    configured = (os.getenv("REPORTS_STORAGE_DIR") or "").strip()
    root = Path(configured) if configured else Path.cwd() / "storage" / "informes"
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def _slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return value[:80] or "CANDIDATO"


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _period(start: date | None, end: date | None) -> str:
    def fmt(d: date | None):
        if d is None:
            return None
        months = ["ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sept.", "oct.", "nov.", "dic."]
        return f"{months[d.month - 1]} {d.year}"
    a, b = fmt(start), fmt(end)
    if a and b:
        return f"{a} – {b}"
    if a:
        return f"{a} – actualidad"
    if b:
        return b
    return ""


def _base_candidate(db: Session, slcd_id: int) -> dict:
    row = _one(
        db,
        """
        SELECT sc.slcd_id, sc.slcd_candidato_id, sc.slcd_solicitud_id,
               sc.slcd_pretension_renta, sc.slcd_puntaje_compatibilidad,
               sc.slcd_estado_solicitud_candidato_id,
               esc.essc_nombre AS estado_postulacion,
               c.cand_id, c.cand_email, c.cand_nombres, c.cand_apellido_paterno,
               c.cand_apellido_materno, c.cand_telefono, c.cand_titulo,
               c.cand_resumen_profesional, c.cand_disponibilidad_id,
               d.disp_nombre AS disponibilidad,
               s.sol_id, s.sol_codigo, s.sol_titulo, s.sol_cargo_id,
               ca.crgo_nombre AS cargo
        FROM tbl_solicitud_candidato sc
        JOIN tbl_candidato c ON c.cand_id = sc.slcd_candidato_id
        JOIN tbl_solicitud s ON s.sol_id = sc.slcd_solicitud_id
        LEFT JOIN tbl_estado_solicitud_candidato esc ON esc.essc_id = sc.slcd_estado_solicitud_candidato_id
        LEFT JOIN tbl_disponibilidad d ON d.disp_id = c.cand_disponibilidad_id
        LEFT JOIN tbl_cargo ca ON ca.crgo_id = s.sol_cargo_id
        WHERE sc.slcd_id = :id
        """,
        {"id": slcd_id},
    )
    if not row:
        raise HTTPException(status_code=404, detail="Postulación no encontrada")
    return row


def _candidate_technologies(db: Session, candidate_id: int) -> list[str]:
    return [
        str(x["hab_nombre"])
        for x in _rows(
            db,
            """
            SELECT h.hab_nombre
            FROM tbl_candidato_habilidad ch
            JOIN tbl_habilidad h ON h.hab_id = ch.cdhb_habilidad_id
            WHERE ch.cdhb_candidato_id = :cid
            ORDER BY h.hab_nombre
            """,
            {"cid": candidate_id},
        )
        if x.get("hab_nombre")
    ]


def _technical_evaluations(db: Session, candidate_id: int, solicitud_id: int) -> tuple[list[dict], int]:
    configured = db.execute(
        text("SELECT COUNT(*) FROM tbl_cuestionario WHERE cues_solicitud_id = :sid"),
        {"sid": solicitud_id},
    ).scalar_one()
    rows = _rows(
        db,
        """
        SELECT q.cues_id AS cuestionario_id, q.cues_nombre AS cuestionario,
               cc.cdcu_porcentaje_obtenido AS porcentaje,
               cc.cdcu_aprobado AS aprobado,
               ec.escc_nombre AS estado
        FROM tbl_cuestionario q
        LEFT JOIN tbl_candidato_cuestionario cc
          ON cc.cdcu_cuestionario_id = q.cues_id
         AND cc.cdcu_candidato_id = :cid
        LEFT JOIN tbl_estado_cuestionario_candidato ec
          ON ec.escc_id = cc.cdcu_estado_cuestionario_candidato_id
        WHERE q.cues_solicitud_id = :sid
        ORDER BY q.cues_id
        """,
        {"cid": candidate_id, "sid": solicitud_id},
    )
    for x in rows:
        if x.get("porcentaje") is not None:
            x["porcentaje"] = float(x["porcentaje"])
    return rows, int(configured or 0)


def _interview_evaluations(db: Session, slcd_id: int) -> tuple[list[dict], dict]:
    evaluations = _rows(
        db,
        """
        SELECT ce.ctev_id AS entrevista_id,
               e.even_tipo_entrevista_id AS tipo_id,
               te.tpet_nombre AS tipo,
               e.even_usuario_id AS entrevistador_id,
               trim(coalesce(u.usr_nombres,'') || ' ' || coalesce(u.usr_apellido_paterno,'') || ' ' || coalesce(u.usr_apellido_materno,'')) AS entrevistador,
               nr.nore_nombre AS resultado,
               e.even_observacion AS observacion
        FROM tbl_cita_entrevista ce
        JOIN tbl_evaluacion_entrevista e ON e.even_cita_entrevista_id = ce.ctev_id
        JOIN tbl_nombre_resultado nr ON nr.nore_id = e.even_nombre_resultado_id
        LEFT JOIN tbl_tipo_entrevista te ON te.tpet_id = e.even_tipo_entrevista_id
        LEFT JOIN tbl_usuario u ON u.usr_id = e.even_usuario_id
        WHERE ce.ctev_solicitud_candidato_id = :slcd
        ORDER BY ce.ctev_id, e.even_tipo_entrevista_id, e.even_usuario_id
        """,
        {"slcd": slcd_id},
    )
    status_rows = _rows(
        db,
        """
        SELECT ce.ctev_id, ee.esev_nombre AS estado,
               (SELECT COUNT(*) FROM tbl_usuario_cita_entrevista uce WHERE uce.usrce_cita_entrevista_id=ce.ctev_id) AS asignados,
               (SELECT COUNT(*) FROM tbl_evaluacion_entrevista ev WHERE ev.even_cita_entrevista_id=ce.ctev_id AND ev.even_usuario_id IS NOT NULL AND ev.even_tipo_entrevista_id IS NOT NULL) AS evaluados
        FROM tbl_cita_entrevista ce
        LEFT JOIN tbl_estado_entrevista ee ON ee.esev_id = ce.ctev_estado_entrevista_id
        WHERE ce.ctev_solicitud_candidato_id = :slcd
        ORDER BY ce.ctev_id
        """,
        {"slcd": slcd_id},
    )
    meta = {
        "total": len(status_rows),
        "pending": any(_norm(x.get("estado")) in {"pendiente", "confirmada", "reprogramada"} for x in status_rows),
        "not_final": any(_norm(x.get("estado")) not in {"realizada", "cancelada", "no asistio"} for x in status_rows),
        "missing_evaluations": any(
            _norm(x.get("estado")) == "realizada" and int(x.get("evaluados") or 0) < int(x.get("asignados") or 0)
            for x in status_rows
        ),
    }
    return evaluations, meta


def classify_candidate(base: dict, technical: list[dict], configured_tests: int, interviews: list[dict], interview_meta: dict) -> tuple[str, bool, list[str]]:
    state = _norm(base.get("estado_postulacion"))
    reasons: list[str] = []

    if state in APPROVED_STATES:
        return "APROBADO", False, [f"Estado de postulación: {base.get('estado_postulacion')}"]
    if state in REJECTED_STATES:
        return "NO_APROBADO", False, [f"Estado de postulación: {base.get('estado_postulacion')}"]
    if state == REVIEW_STATE:
        return "PENDIENTE", False, ["El candidato todavía se encuentra en revisión"]
    if state != INTERVIEW_STATE:
        return "PENDIENTE", False, ["La postulación aún no tiene una decisión final de M3"]

    if configured_tests:
        missing_tests = [x for x in technical if x.get("aprobado") is None]
        failed_tests = [x for x in technical if x.get("aprobado") is False]
        if failed_tests:
            reasons.extend(f"Evaluación técnica no aprobada: {x.get('cuestionario')}" for x in failed_tests)
            return "NO_APROBADO", True, reasons
        if missing_tests or len(technical) < configured_tests:
            return "PENDIENTE", False, ["Existen evaluaciones técnicas pendientes"]

    normalized_results = [_norm(x.get("resultado")) for x in interviews]
    if REJECTED_RESULT in normalized_results:
        return "NO_APROBADO", True, ["Existe al menos una entrevista con resultado No Aprobado"]
    if any(x in PENDING_RESULTS for x in normalized_results):
        return "PENDIENTE", False, ["Existen entrevistas En Espera o que requieren segunda entrevista"]
    if interview_meta.get("pending") or interview_meta.get("missing_evaluations"):
        return "PENDIENTE", False, ["Existen entrevistas o evaluaciones de entrevista pendientes"]
    if interview_meta.get("total", 0) == 0:
        return "PENDIENTE", False, ["Aún no se registran entrevistas para la postulación"]
    if interviews and all(x in APPROVED_RESULTS for x in normalized_results):
        return "APROBADO", True, ["Evaluaciones técnicas e entrevistas completadas sin resultados de rechazo"]
    return "PENDIENTE", False, ["El proceso aún no reúne antecedentes suficientes para una clasificación final"]


def candidate_report_item(db: Session, slcd_id: int) -> dict:
    base = _base_candidate(db, slcd_id)
    technical, configured = _technical_evaluations(db, base["cand_id"], base["sol_id"])
    interviews, interview_meta = _interview_evaluations(db, slcd_id)
    classification, suggested, reasons = classify_candidate(base, technical, configured, interviews, interview_meta)
    full_name = " ".join(x for x in [base.get("cand_nombres"), base.get("cand_apellido_paterno"), base.get("cand_apellido_materno")] if x)
    return {
        "solicitud_candidato_id": base["slcd_id"],
        "solicitud_id": base["sol_id"],
        "solicitud_codigo": base.get("sol_codigo"),
        "solicitud_titulo": base.get("sol_titulo"),
        "candidato_id": base["cand_id"],
        "candidato_nombre": full_name,
        "candidato_email": base["cand_email"],
        "candidato_telefono": base.get("cand_telefono"),
        "cargo_id": base.get("sol_cargo_id"),
        "cargo": base.get("cargo"),
        "disponibilidad_id": base.get("cand_disponibilidad_id"),
        "disponibilidad": base.get("disponibilidad"),
        "match": float(base["slcd_puntaje_compatibilidad"]) if base.get("slcd_puntaje_compatibilidad") is not None else None,
        "estado_postulacion": base.get("estado_postulacion"),
        "clasificacion": classification,
        "clasificacion_sugerida": suggested,
        "motivo_clasificacion": reasons,
        "tecnologias": _candidate_technologies(db, base["cand_id"]),
        "tecnicas": technical,
        "entrevistas": interviews,
        "puede_enviar_rechazo": _norm(base.get("estado_postulacion")) in REJECTED_STATES,
        "puede_enviar_directivos": classification == "APROBADO",
    }


def list_candidates(
    db: Session,
    *,
    clasificacion: str | None = None,
    solicitud_id: int | None = None,
    cargo_id: int | None = None,
    habilidad_id: int | None = None,
    estado_postulacion_id: int | None = None,
    disponibilidad_id: int | None = None,
    match_min: float | None = None,
    match_max: float | None = None,
    nombre: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> dict:
    where = ["1=1"]
    params: dict[str, Any] = {}
    if solicitud_id is not None:
        where.append("sc.slcd_solicitud_id = :solicitud_id"); params["solicitud_id"] = solicitud_id
    if cargo_id is not None:
        where.append("s.sol_cargo_id = :cargo_id"); params["cargo_id"] = cargo_id
    if estado_postulacion_id is not None:
        where.append("sc.slcd_estado_solicitud_candidato_id = :estado_id"); params["estado_id"] = estado_postulacion_id
    if disponibilidad_id is not None:
        where.append("c.cand_disponibilidad_id = :disp_id"); params["disp_id"] = disponibilidad_id
    if match_min is not None:
        where.append("sc.slcd_puntaje_compatibilidad >= :match_min"); params["match_min"] = match_min
    if match_max is not None:
        where.append("sc.slcd_puntaje_compatibilidad <= :match_max"); params["match_max"] = match_max
    if habilidad_id is not None:
        where.append("EXISTS (SELECT 1 FROM tbl_candidato_habilidad ch WHERE ch.cdhb_candidato_id=c.cand_id AND ch.cdhb_habilidad_id=:hab_id)"); params["hab_id"] = habilidad_id
    if nombre:
        where.append("lower(coalesce(c.cand_nombres,'') || ' ' || coalesce(c.cand_apellido_paterno,'') || ' ' || coalesce(c.cand_apellido_materno,'')) LIKE :nombre")
        params["nombre"] = f"%{nombre.strip().casefold()}%"
    ids = [
        int(x["slcd_id"])
        for x in _rows(
            db,
            f"""
            SELECT sc.slcd_id
            FROM tbl_solicitud_candidato sc
            JOIN tbl_candidato c ON c.cand_id=sc.slcd_candidato_id
            JOIN tbl_solicitud s ON s.sol_id=sc.slcd_solicitud_id
            WHERE {' AND '.join(where)}
            ORDER BY sc.slcd_id DESC
            """,
            params,
        )
    ]
    items = [candidate_report_item(db, x) for x in ids]
    if clasificacion:
        desired = clasificacion.strip().upper().replace(" ", "_")
        items = [x for x in items if x["clasificacion"] == desired]
    total = len(items)
    return {"total": total, "items": items[skip: skip + limit]}


def list_categories(db: Session) -> list[dict]:
    return [
        {"categoria_id": x.cthb_id, "nombre": x.cthb_nombre, "descripcion": x.cthb_descripcion}
        for x in db.scalars(select(CategoriaHabilidad).order_by(CategoriaHabilidad.cthb_nombre)).all()
    ]


def list_languages(db: Session) -> list[dict]:
    return [{"idioma_id": x.idio_id, "idioma": x.idio_nombre} for x in db.scalars(select(Idioma).order_by(Idioma.idio_nombre)).all()]


def update_skill_category(db: Session, habilidad_id: int, categoria_id: int | None) -> dict:
    if not _one(db, "SELECT hab_id, hab_nombre FROM tbl_habilidad WHERE hab_id=:id", {"id": habilidad_id}):
        raise HTTPException(status_code=404, detail="Habilidad no encontrada")
    if categoria_id is not None and db.get(CategoriaHabilidad, categoria_id) is None:
        raise HTTPException(status_code=422, detail="Categoría de habilidad inexistente")
    db.execute(text("UPDATE tbl_habilidad SET hab_categoria_habilidad_id=:cat WHERE hab_id=:id"), {"cat": categoria_id, "id": habilidad_id})
    db.commit()
    return {"habilidad_id": habilidad_id, "categoria_id": categoria_id}


def get_candidate_languages(db: Session, candidate_id: int) -> list[dict]:
    if not _one(db, "SELECT cand_id FROM tbl_candidato WHERE cand_id=:id", {"id": candidate_id}):
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    return _rows(
        db,
        """
        SELECT ci.cdio_idioma_id AS idioma_id, i.idio_nombre AS idioma,
               ci.cdio_nivel_idioma_id AS nivel_idioma_id,
               ni.nvid_codigo AS nivel_codigo, ni.nvid_nombre AS nivel,
               ni.nvid_grupo AS nivel_grupo
        FROM tbl_candidato_idioma ci
        JOIN tbl_idioma i ON i.idio_id=ci.cdio_idioma_id
        JOIN tbl_nivel_idioma ni ON ni.nvid_id=ci.cdio_nivel_idioma_id
        WHERE ci.cdio_candidato_id=:cid
        ORDER BY i.idio_nombre
        """,
        {"cid": candidate_id},
    )


def replace_candidate_languages(db: Session, candidate_id: int, values: list) -> list[dict]:
    if not _one(db, "SELECT cand_id FROM tbl_candidato WHERE cand_id=:id", {"id": candidate_id}):
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    valid = set(db.scalars(select(Idioma.idio_id).where(Idioma.idio_id.in_([x.idioma_id for x in values]))).all()) if values else set()
    requested = {x.idioma_id for x in values}
    if valid != requested:
        raise HTTPException(status_code=422, detail="Uno o más idiomas no existen")

    legacy_codes = {"Basico": "BAS", "Intermedio": "INT", "Avanzado": "AVA", "Nativo": "NAT"}
    resolved = []
    for x in values:
        level = None
        if x.nivel_idioma_id is not None:
            level = db.get(NivelIdioma, x.nivel_idioma_id)
        elif x.nivel is not None:
            level = db.scalar(select(NivelIdioma).where(NivelIdioma.nvid_codigo == legacy_codes[x.nivel]))
        if level is None or not level.nvid_activo:
            raise HTTPException(status_code=422, detail="Uno o más niveles de idioma no existen o están inactivos")
        resolved.append((x.idioma_id, level.nvid_id))

    try:
        db.execute(text("DELETE FROM tbl_candidato_idioma WHERE cdio_candidato_id=:cid"), {"cid": candidate_id})
        for idioma_id, nivel_id in resolved:
            db.add(CandidatoIdioma(
                cdio_candidato_id=candidate_id,
                cdio_idioma_id=idioma_id,
                cdio_nivel_idioma_id=nivel_id,
            ))
        db.commit()
    except Exception:
        db.rollback(); raise
    return get_candidate_languages(db, candidate_id)


def _corporate_data(db: Session, slcd_id: int, overrides: CVOverrides | None = None) -> dict:
    b = _base_candidate(db, slcd_id)
    name = " ".join(x for x in [b.get("cand_nombres"), b.get("cand_apellido_paterno"), b.get("cand_apellido_materno")] if x)
    country = _one(
        db,
        """
        SELECT p.pais_nombre
        FROM tbl_direccion_candidato dc
        LEFT JOIN tbl_comuna c ON c.com_id=dc.drcd_comuna_id
        LEFT JOIN tbl_region r ON r.reg_id=c.com_region_id
        LEFT JOIN tbl_pais p ON p.pais_id=r.reg_pais_id
        WHERE dc.drcd_candidato_id=:cid
        LIMIT 1
        """,
        {"cid": b["cand_id"]},
    )
    education = _rows(
        db,
        """
        SELECT e.etcd_fecha_inicio, e.etcd_fecha_fin, ne.nved_nombre AS nivel,
               i.inst_nombre AS institucion, c.crra_nombre AS carrera
        FROM tbl_estudio_candidato e
        LEFT JOIN tbl_nivel_educacional ne ON ne.nved_id=e.etcd_nivel_educacional_id
        LEFT JOIN tbl_institucion i ON i.inst_id=e.etcd_institucion_id
        LEFT JOIN tbl_carrera c ON c.crra_id=e.etcd_carrera_id
        WHERE e.etcd_candidato_id=:cid
        ORDER BY e.etcd_fecha_fin DESC, e.etcd_fecha_inicio DESC
        """,
        {"cid": b["cand_id"]},
    )
    for x in education:
        x["periodo"] = _period(x.get("etcd_fecha_inicio"), x.get("etcd_fecha_fin"))
    experience = _rows(
        db,
        """
        SELECT e.expl_fecha_inicio, e.expl_fecha_fin, e.expl_descripcion_funciones AS descripcion,
               em.emp_nombre AS empresa, ca.crgo_nombre AS cargo
        FROM tbl_experiencia_laboral e
        LEFT JOIN tbl_empresa em ON em.emp_id=e.expl_empresa_id
        LEFT JOIN tbl_cargo ca ON ca.crgo_id=e.expl_cargo_id
        WHERE e.expl_candidato_id=:cid
        ORDER BY e.expl_fecha_fin DESC, e.expl_fecha_inicio DESC
        """,
        {"cid": b["cand_id"]},
    )
    for x in experience:
        x["periodo"] = _period(x.get("expl_fecha_inicio"), x.get("expl_fecha_fin"))
    skills = _rows(
        db,
        """
        SELECT h.hab_nombre AS habilidad, nh.nvhb_nombre AS nivel,
               coalesce(chc.cthb_nombre, 'Otros') AS categoria,
               ch.cdhb_anios_experiencia AS anios
        FROM tbl_candidato_habilidad ch
        JOIN tbl_habilidad h ON h.hab_id=ch.cdhb_habilidad_id
        LEFT JOIN tbl_nivel_habilidad nh ON nh.nvhb_id=ch.cdhb_nivel_habilidad_id
        LEFT JOIN tbl_categoria_habilidad chc ON chc.cthb_id=h.hab_categoria_habilidad_id
        WHERE ch.cdhb_candidato_id=:cid
        ORDER BY coalesce(chc.cthb_nombre, 'Otros'), h.hab_nombre
        """,
        {"cid": b["cand_id"]},
    )
    grouped: dict[str, list] = defaultdict(list)
    for x in skills:
        grouped[x["categoria"]].append(x)
    langs = get_candidate_languages(db, b["cand_id"])
    certs = _rows(
        db,
        """
        SELECT curs_nombre_curso AS nombre, curs_anio_curso AS anio
        FROM tbl_curso
        WHERE curs_candidato_id=:cid AND curs_es_certificado IS TRUE
        ORDER BY curs_anio_curso DESC, curs_nombre_curso
        """,
        {"cid": b["cand_id"]},
    )
    profile = (overrides.perfil_profesional if overrides and overrides.perfil_profesional else b.get("cand_resumen_profesional")) or ""
    top_skills = [x["habilidad"] for x in skills[:6] if x.get("habilidad")]
    executive = overrides.resumen_ejecutivo if overrides and overrides.resumen_ejecutivo else profile
    if not executive:
        executive = f"Profesional con experiencia relacionada al cargo {b.get('cargo') or b.get('cand_titulo') or 'postulado'}, con conocimientos en {', '.join(top_skills[:4]) or 'tecnologías y herramientas relevantes'}."
    if overrides and overrides.roles_recomendados is not None:
        roles = overrides.roles_recomendados
    else:
        roles = []
        if b.get("cargo"):
            roles.append(f"{b['cargo']} – por su alineación con la solicitud y experiencia declarada.")
        seen = {_norm(b.get("cargo"))}
        for x in experience:
            role = x.get("cargo")
            if role and _norm(role) not in seen:
                roles.append(f"{role} – por experiencia laboral previa en funciones relacionadas.")
                seen.add(_norm(role))
            if len(roles) >= 3:
                break
    if overrides and overrides.fortalezas is not None:
        strengths = overrides.fortalezas
    else:
        strengths = []
        if top_skills:
            strengths.append("Conocimientos técnicos destacados en " + ", ".join(top_skills[:5]) + ".")
        if experience:
            strengths.append("Experiencia laboral demostrable en distintos contextos y responsabilidades profesionales.")
        if profile:
            strengths.append("Perfil profesional orientado a los objetivos y responsabilidades descritos por el candidato.")
    return {
        "nombre": name,
        "titulo": b.get("cand_titulo") or b.get("cargo"),
        "pais": country.get("pais_nombre") if country else None,
        "educacion": education,
        "perfil_profesional": profile,
        "experiencia": experience,
        "habilidades_por_categoria": dict(grouped),
        "idiomas": langs,
        "certificaciones": certs,
        "resumen_ejecutivo": executive,
        "roles_recomendados": roles[:3],
        "fortalezas": strengths[:6],
    }


def _save_document(db: Session, *, slcd_id: int, kind: str, filename: str, path: Path, user_id: int, snapshot: dict) -> dict:
    doc = DocumentoReporteCandidato(
        drcp_solicitud_candidato_id=slcd_id,
        drcp_tipo_documento=kind,
        drcp_nombre_archivo=filename,
        drcp_ruta_archivo=str(path.resolve()),
        drcp_fecha_generacion=datetime.now(),
        drcp_usuario_generador_id=user_id,
        drcp_hash_sha256=_hash_file(path),
        drcp_snapshot_json=snapshot,
    )
    db.add(doc); db.commit(); db.refresh(doc)
    return {
        "documento_id": doc.drcp_id,
        "solicitud_candidato_id": doc.drcp_solicitud_candidato_id,
        "tipo_documento": doc.drcp_tipo_documento,
        "nombre_archivo": doc.drcp_nombre_archivo,
        "fecha_generacion": doc.drcp_fecha_generacion,
        "hash_sha256": doc.drcp_hash_sha256,
    }


def generate_corporate_document(db: Session, slcd_id: int, user_id: int, overrides: CVOverrides | None = None) -> dict:
    item = candidate_report_item(db, slcd_id)
    if item["clasificacion"] != "APROBADO":
        raise HTTPException(status_code=409, detail="El CV corporativo de cierre solo puede generarse para candidatos clasificados como Aprobado")
    data = _corporate_data(db, slcd_id, overrides)
    filename = f"CV_ELITSOFT_{_slug(item['candidato_nombre'])}_{_slug(item['solicitud_codigo'] or str(item['solicitud_id']))}.pdf"
    path = _storage_root() / "cv_corporativo" / filename
    generate_corporate_cv(str(path), data)
    return _save_document(db, slcd_id=slcd_id, kind="CV_CORPORATIVO", filename=filename, path=path, user_id=user_id, snapshot=data)


def generate_summary_document(db: Session, slcd_id: int, user_id: int) -> dict:
    item = candidate_report_item(db, slcd_id)
    filename = f"RESUMEN_{_slug(item['candidato_nombre'])}_{_slug(item['solicitud_codigo'] or str(item['solicitud_id']))}.pdf"
    path = _storage_root() / "resumen" / filename
    generate_candidate_summary(str(path), item)
    return _save_document(db, slcd_id=slcd_id, kind="RESUMEN", filename=filename, path=path, user_id=user_id, snapshot=item)


def generate_bulk(db: Session, ids: list[int], user_id: int, kind: str) -> tuple[dict, Path]:
    # Prevalidación completa para evitar generar documentos parciales por errores de negocio.
    prevalidated = [candidate_report_item(db, slcd) for slcd in ids]
    if kind == "CV_CORPORATIVO":
        invalid = [x["solicitud_candidato_id"] for x in prevalidated if x["clasificacion"] != "APROBADO"]
        if invalid:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Todos los candidatos deben estar clasificados como Aprobado para generar CVs corporativos masivos",
                    "ids": invalid,
                },
            )
    docs: list[dict] = []
    paths: list[Path] = []
    for slcd in ids:
        doc = generate_corporate_document(db, slcd, user_id) if kind == "CV_CORPORATIVO" else generate_summary_document(db, slcd, user_id)
        stored = db.get(DocumentoReporteCandidato, doc["documento_id"])
        docs.append(doc); paths.append(Path(stored.drcp_ruta_archivo))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"{kind}_MASIVO_{stamp}.zip"
    zip_path = _storage_root() / "masivos" / zip_name
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=p.name)
    return {"nombre_archivo": zip_name, "cantidad": len(docs), "documento_ids": [x["documento_id"] for x in docs]}, zip_path


def get_document(db: Session, document_id: int) -> DocumentoReporteCandidato:
    doc = db.get(DocumentoReporteCandidato, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return doc


def document_path(db: Session, document_id: int) -> Path:
    doc = get_document(db, document_id)
    path = Path(doc.drcp_ruta_archivo).resolve()
    root = _storage_root()
    if root not in path.parents:
        raise HTTPException(status_code=409, detail="Ruta de documento fuera del almacenamiento autorizado")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="El archivo físico ya no está disponible")
    if _hash_file(path) != doc.drcp_hash_sha256:
        raise HTTPException(status_code=409, detail="El documento no supera la verificación de integridad")
    return path


def list_documents(db: Session, slcd_id: int | None = None, kind: str | None = None, limit: int = 100) -> list[dict]:
    stmt = select(DocumentoReporteCandidato).order_by(DocumentoReporteCandidato.drcp_id.desc()).limit(limit)
    if slcd_id is not None:
        stmt = stmt.where(DocumentoReporteCandidato.drcp_solicitud_candidato_id == slcd_id)
    if kind:
        stmt = stmt.where(DocumentoReporteCandidato.drcp_tipo_documento == kind.upper())
    return [
        {
            "documento_id": x.drcp_id,
            "solicitud_candidato_id": x.drcp_solicitud_candidato_id,
            "tipo_documento": x.drcp_tipo_documento,
            "nombre_archivo": x.drcp_nombre_archivo,
            "fecha_generacion": x.drcp_fecha_generacion,
            "hash_sha256": x.drcp_hash_sha256,
        }
        for x in db.scalars(stmt).all()
    ]


def _template(db: Session, kind: str) -> PlantillaNotificacion:
    obj = db.scalar(select(PlantillaNotificacion).where(PlantillaNotificacion.plnt_tipo == kind, PlantillaNotificacion.plnt_activa.is_(True)))
    if obj is None:
        raise HTTPException(status_code=409, detail=f"No existe plantilla activa para {kind}")
    return obj


def _render(template: str, item: dict) -> str:
    values = {
        "{nombre}": item["candidato_nombre"],
        "{cargo}": item.get("cargo") or "el cargo publicado",
        "{codigo_solicitud}": item.get("solicitud_codigo") or str(item["solicitud_id"]),
        "{solicitud}": item.get("solicitud_titulo") or item.get("solicitud_codigo") or "proceso de selección",
    }
    result = template
    for key, val in values.items():
        result = result.replace(key, str(val))
    return result


def prepare_directors(db: Session, ids: list[int], recipients: list[str], cc: list[str], subject: str | None, body: str | None, user_id: int) -> dict:
    items = [candidate_report_item(db, x) for x in ids]
    invalid = [x["solicitud_candidato_id"] for x in items if not x["puede_enviar_directivos"]]
    if invalid:
        raise HTTPException(status_code=409, detail={"message": "Todos los candidatos deben estar clasificados como Aprobado", "ids": invalid})
    tpl = _template(db, "DIRECTIVOS")
    base = items[0]
    final_subject = subject or _render(tpl.plnt_asunto, base)
    final_body = body or _render(tpl.plnt_cuerpo, base)
    docs = [generate_corporate_document(db, x["solicitud_candidato_id"], user_id) for x in items]
    return {"destinatarios": recipients, "cc": cc, "asunto": final_subject, "cuerpo": final_body, "candidatos": items, "adjuntos": docs}


def _record_notifications(db: Session, *, items: list[dict], kind: str, recipients: str, cc: str | None, subject: str, body: str, user_id: int, state: str, error: str | None = None) -> list[NotificacionReclutamiento]:
    now = datetime.now()
    result = []
    for item in items:
        obj = NotificacionReclutamiento(
            ntfr_solicitud_candidato_id=item["solicitud_candidato_id"],
            ntfr_tipo=kind,
            ntfr_destinatario=recipients,
            ntfr_cc=cc,
            ntfr_asunto=subject,
            ntfr_cuerpo=body,
            ntfr_estado=state,
            ntfr_usuario_id=user_id,
            ntfr_fecha_creacion=now,
            ntfr_fecha_envio=now if state == "ENVIADO" else None,
            ntfr_error=error,
        )
        db.add(obj); result.append(obj)
    db.commit()
    return result


def send_to_directors(db: Session, ids: list[int], recipients: list[str], cc: list[str], subject: str | None, body: str | None, user_id: int) -> list[dict]:
    preview = prepare_directors(db, ids, recipients, cc, subject, body, user_id)
    attachments = []
    for d in preview["adjuntos"]:
        doc = get_document(db, d["documento_id"])
        attachments.append((doc.drcp_nombre_archivo, Path(doc.drcp_ruta_archivo)))
    try:
        send_email(to_emails=recipients, cc_emails=cc, subject=preview["asunto"], body_text=preview["cuerpo"], attachments=attachments)
        rows = _record_notifications(db, items=preview["candidatos"], kind="DIRECTIVOS", recipients=";".join(recipients), cc=";".join(cc) or None, subject=preview["asunto"], body=preview["cuerpo"], user_id=user_id, state="ENVIADO")
    except (EmailConfigurationError, EmailDeliveryError) as exc:
        _record_notifications(db, items=preview["candidatos"], kind="DIRECTIVOS", recipients=";".join(recipients), cc=";".join(cc) or None, subject=preview["asunto"], body=preview["cuerpo"], user_id=user_id, state="ERROR", error=str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return [_notification_dict(x) for x in rows]


def prepare_rejections(db: Session, ids: list[int], kind: str = "RECHAZO", subject_template: str | None = None, body_template: str | None = None) -> list[dict]:
    kind = kind.upper()
    if kind not in {"RECHAZO", "AGRADECIMIENTO"}:
        raise HTTPException(status_code=422, detail="Tipo de notificación inválido")
    tpl = _template(db, kind)
    out = []
    for slcd in ids:
        item = candidate_report_item(db, slcd)
        if not item["puede_enviar_rechazo"]:
            raise HTTPException(status_code=409, detail={"message": "El rechazo solo puede notificarse a postulaciones Descartadas o Inhabilitadas", "id": slcd})
        out.append({
            "solicitud_candidato_id": slcd,
            "destinatario": item["candidato_email"],
            "asunto": _render(subject_template or tpl.plnt_asunto, item),
            "cuerpo": _render(body_template or tpl.plnt_cuerpo, item),
        })
    return out


def send_rejections(db: Session, values: list, user_id: int) -> list[dict]:
    responses = []
    for value in values:
        item = candidate_report_item(db, value.solicitud_candidato_id)
        if not item["puede_enviar_rechazo"]:
            raise HTTPException(status_code=409, detail={"message": "El rechazo solo puede notificarse a postulaciones Descartadas o Inhabilitadas", "id": value.solicitud_candidato_id})
        try:
            send_email(to_emails=[item["candidato_email"]], subject=value.asunto, body_text=value.cuerpo)
            state, error = "ENVIADO", None
        except (EmailConfigurationError, EmailDeliveryError) as exc:
            state, error = "ERROR", str(exc)
        rows = _record_notifications(db, items=[item], kind=value.tipo, recipients=item["candidato_email"], cc=None, subject=value.asunto, body=value.cuerpo, user_id=user_id, state=state, error=error)
        responses.append(_notification_dict(rows[0]))
    if any(x["estado"] == "ERROR" for x in responses):
        # No se pierde trazabilidad; el caller recibe todos los resultados.
        return responses
    return responses


def _notification_dict(x: NotificacionReclutamiento) -> dict:
    return {
        "notificacion_id": x.ntfr_id,
        "solicitud_candidato_id": x.ntfr_solicitud_candidato_id,
        "tipo": x.ntfr_tipo,
        "destinatario": x.ntfr_destinatario,
        "cc": x.ntfr_cc,
        "asunto": x.ntfr_asunto,
        "estado": x.ntfr_estado,
        "fecha_creacion": x.ntfr_fecha_creacion,
        "fecha_envio": x.ntfr_fecha_envio,
        "error": x.ntfr_error,
    }


def list_notifications(db: Session, slcd_id: int | None = None, kind: str | None = None, state: str | None = None, limit: int = 100) -> list[dict]:
    stmt = select(NotificacionReclutamiento).order_by(NotificacionReclutamiento.ntfr_id.desc()).limit(limit)
    if slcd_id is not None:
        stmt = stmt.where(NotificacionReclutamiento.ntfr_solicitud_candidato_id == slcd_id)
    if kind:
        stmt = stmt.where(NotificacionReclutamiento.ntfr_tipo == kind.upper())
    if state:
        stmt = stmt.where(NotificacionReclutamiento.ntfr_estado == state.upper())
    return [_notification_dict(x) for x in db.scalars(stmt).all()]


def get_notification(db: Session, notification_id: int) -> dict:
    x = db.get(NotificacionReclutamiento, notification_id)
    if x is None:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    result = _notification_dict(x)
    result["cuerpo"] = x.ntfr_cuerpo
    return result


def list_templates(db: Session) -> list[dict]:
    return [
        {"plantilla_id": x.plnt_id, "tipo": x.plnt_tipo, "nombre": x.plnt_nombre, "asunto": x.plnt_asunto, "cuerpo": x.plnt_cuerpo, "activa": x.plnt_activa}
        for x in db.scalars(select(PlantillaNotificacion).order_by(PlantillaNotificacion.plnt_id)).all()
    ]


def update_template(db: Session, template_id: int, payload, user_id: int) -> dict:
    x = db.get(PlantillaNotificacion, template_id)
    if x is None:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    values = payload.model_dump(exclude_unset=True)
    mapping = {"nombre": "plnt_nombre", "asunto": "plnt_asunto", "cuerpo": "plnt_cuerpo", "activa": "plnt_activa"}
    for key, value in values.items():
        setattr(x, mapping[key], value)
    x.plnt_fecha_actualizacion = datetime.now(); x.plnt_usuario_actualizacion_id = user_id
    db.commit(); db.refresh(x)
    return {"plantilla_id": x.plnt_id, "tipo": x.plnt_tipo, "nombre": x.plnt_nombre, "asunto": x.plnt_asunto, "cuerpo": x.plnt_cuerpo, "activa": x.plnt_activa}
