from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permissions
from app.database import get_db
from app.informes import services
from app.informes.schemas import (
    CVOverrides,
    CandidateListResponse,
    CategoriaHabilidadItem,
    DirectivosPrepareRequest,
    DirectivosPreview,
    DirectivosSendRequest,
    DocumentoResponse,
    HabilidadCategoriaUpdate,
    IdiomasReplaceRequest,
    MasivoDocumentoResponse,
    MasivoRequest,
    NotificationDetailResponse,
    NotificationResponse,
    PlantillaResponse,
    PlantillaUpdate,
    RechazosPrepareRequest,
    RechazosPreview,
    RechazosSendRequest,
)
from app.usuarios.models import Usuario


router = APIRouter(prefix="/informes", tags=["Informes / Cierre M6"])
report_user = require_permissions("REP_VIEW")


@router.get("/candidatos", response_model=CandidateListResponse)
def candidatos(
    clasificacion: Literal["APROBADO", "PENDIENTE", "NO_APROBADO"] | None = None,
    solicitud_id: int | None = Query(default=None, gt=0),
    cargo_id: int | None = Query(default=None, gt=0),
    habilidad_id: int | None = Query(default=None, gt=0, description="Filtro de Tecnología/Habilidad"),
    estado_postulacion_id: int | None = Query(default=None, gt=0),
    disponibilidad_id: int | None = Query(default=None, gt=0),
    match_min: float | None = Query(default=None, ge=0, le=100),
    match_max: float | None = Query(default=None, ge=0, le=100),
    nombre: str | None = Query(default=None, min_length=1, max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: Usuario = Depends(report_user),
):
    if match_min is not None and match_max is not None and match_min > match_max:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="match_min no puede ser mayor que match_max")
    return services.list_candidates(
        db,
        clasificacion=clasificacion,
        solicitud_id=solicitud_id,
        cargo_id=cargo_id,
        habilidad_id=habilidad_id,
        estado_postulacion_id=estado_postulacion_id,
        disponibilidad_id=disponibilidad_id,
        match_min=match_min,
        match_max=match_max,
        nombre=nombre,
        skip=skip,
        limit=limit,
    )


@router.get("/candidatos/{solicitud_candidato_id}")
def candidato_detalle(
    solicitud_candidato_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(report_user),
):
    return services.candidate_report_item(db, solicitud_candidato_id)


@router.get("/catalogos/categorias-habilidad", response_model=list[CategoriaHabilidadItem])
def categorias_habilidad(db: Session = Depends(get_db), _: Usuario = Depends(report_user)):
    return services.list_categories(db)


@router.get("/catalogos/idiomas")
def idiomas(db: Session = Depends(get_db), _: Usuario = Depends(report_user)):
    return services.list_languages(db)


@router.patch("/catalogos/habilidades/{habilidad_id}/categoria")
def asignar_categoria_habilidad(
    habilidad_id: int,
    payload: HabilidadCategoriaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    return services.update_skill_category(db, habilidad_id, payload.categoria_id)


@router.get("/candidatos-perfil/{candidato_id}/idiomas")
def candidato_idiomas(
    candidato_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_VIEW")),
):
    return services.get_candidate_languages(db, candidato_id)


@router.put("/candidatos-perfil/{candidato_id}/idiomas")
def reemplazar_candidato_idiomas(
    candidato_id: int,
    payload: IdiomasReplaceRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_UPDATE")),
):
    return services.replace_candidate_languages(db, candidato_id, payload.idiomas)


@router.post("/candidatos/{solicitud_candidato_id}/resumen", response_model=DocumentoResponse, status_code=201)
def generar_resumen(
    solicitud_candidato_id: int,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    return services.generate_summary_document(db, solicitud_candidato_id, user.usr_id)


@router.post("/candidatos/resumen-masivo", response_model=MasivoDocumentoResponse, status_code=201)
def generar_resumen_masivo(
    payload: MasivoRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    result, _ = services.generate_bulk(db, payload.solicitud_candidato_ids, user.usr_id, "RESUMEN")
    return result


@router.post("/candidatos/{solicitud_candidato_id}/cv-corporativo", response_model=DocumentoResponse, status_code=201)
def generar_cv_corporativo(
    solicitud_candidato_id: int,
    payload: CVOverrides | None = Body(default=None),
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    return services.generate_corporate_document(db, solicitud_candidato_id, user.usr_id, payload)


@router.post("/candidatos/cv-corporativo-masivo", response_model=MasivoDocumentoResponse, status_code=201)
def generar_cv_corporativo_masivo(
    payload: MasivoRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    result, _ = services.generate_bulk(db, payload.solicitud_candidato_ids, user.usr_id, "CV_CORPORATIVO")
    return result


@router.post("/candidatos/resumen-masivo/descargar")
def descargar_resumen_masivo(
    payload: MasivoRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    result, path = services.generate_bulk(db, payload.solicitud_candidato_ids, user.usr_id, "RESUMEN")
    return FileResponse(path, filename=result["nombre_archivo"], media_type="application/zip")


@router.post("/candidatos/cv-corporativo-masivo/descargar")
def descargar_cv_masivo(
    payload: MasivoRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    result, path = services.generate_bulk(db, payload.solicitud_candidato_ids, user.usr_id, "CV_CORPORATIVO")
    return FileResponse(path, filename=result["nombre_archivo"], media_type="application/zip")


@router.get("/documentos", response_model=list[DocumentoResponse])
def documentos(
    solicitud_candidato_id: int | None = Query(default=None, gt=0),
    tipo: Literal["RESUMEN", "CV_CORPORATIVO"] | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(report_user),
):
    return services.list_documents(db, solicitud_candidato_id, tipo, limit)


@router.get("/documentos/{documento_id}", response_model=DocumentoResponse)
def documento(documento_id: int, db: Session = Depends(get_db), _: Usuario = Depends(report_user)):
    x = services.get_document(db, documento_id)
    return {
        "documento_id": x.drcp_id,
        "solicitud_candidato_id": x.drcp_solicitud_candidato_id,
        "tipo_documento": x.drcp_tipo_documento,
        "nombre_archivo": x.drcp_nombre_archivo,
        "fecha_generacion": x.drcp_fecha_generacion,
        "hash_sha256": x.drcp_hash_sha256,
    }


@router.get("/documentos/{documento_id}/descargar")
def descargar_documento(documento_id: int, db: Session = Depends(get_db), _: Usuario = Depends(report_user)):
    doc = services.get_document(db, documento_id)
    path = services.document_path(db, documento_id)
    return FileResponse(path, filename=doc.drcp_nombre_archivo, media_type="application/pdf")


@router.post("/directivos/preparar", response_model=DirectivosPreview)
def preparar_directivos(
    payload: DirectivosPrepareRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    return services.prepare_directors(
        db,
        payload.solicitud_candidato_ids,
        [str(x) for x in payload.destinatarios],
        [str(x) for x in payload.cc],
        payload.asunto,
        payload.cuerpo,
        user.usr_id,
    )


@router.post("/directivos/enviar", response_model=list[NotificationResponse])
def enviar_directivos(
    payload: DirectivosSendRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    return services.send_to_directors(
        db,
        payload.solicitud_candidato_ids,
        [str(x) for x in payload.destinatarios],
        [str(x) for x in payload.cc],
        payload.asunto,
        payload.cuerpo,
        user.usr_id,
    )


@router.post("/rechazos/preparar", response_model=RechazosPreview)
def preparar_rechazos(
    payload: RechazosPrepareRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(report_user),
):
    return {"items": services.prepare_rejections(db, payload.solicitud_candidato_ids, payload.tipo, payload.asunto_plantilla, payload.cuerpo_plantilla)}


@router.post("/rechazos/enviar", response_model=list[NotificationResponse])
def enviar_rechazos(
    payload: RechazosSendRequest,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    return services.send_rejections(db, payload.items, user.usr_id)


@router.get("/notificaciones", response_model=list[NotificationResponse])
def notificaciones(
    solicitud_candidato_id: int | None = Query(default=None, gt=0),
    tipo: Literal["RECHAZO", "AGRADECIMIENTO", "DIRECTIVOS"] | None = None,
    estado: Literal["BORRADOR", "ENVIADO", "ERROR"] | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(report_user),
):
    return services.list_notifications(db, solicitud_candidato_id, tipo, estado, limit)


@router.get("/notificaciones/{notificacion_id}", response_model=NotificationDetailResponse)
def notificacion_detalle(notificacion_id: int, db: Session = Depends(get_db), _: Usuario = Depends(report_user)):
    return services.get_notification(db, notificacion_id)


@router.get("/plantillas", response_model=list[PlantillaResponse])
def plantillas(db: Session = Depends(get_db), _: Usuario = Depends(report_user)):
    return services.list_templates(db)


@router.patch("/plantillas/{plantilla_id}", response_model=PlantillaResponse)
def modificar_plantilla(
    plantilla_id: int,
    payload: PlantillaUpdate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(report_user),
):
    return services.update_template(db, plantilla_id, payload, user.usr_id)
