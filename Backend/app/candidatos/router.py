from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_candidate, require_permissions
from app.database import get_db
from app.usuarios.models import Usuario

from . import cv_parser, schemas, services

router = APIRouter(tags=["Candidatos"])


def _http(exc: Exception) -> HTTPException:
    if isinstance(exc, services.NotFoundError): code=404
    elif isinstance(exc, services.ConflictError): code=409
    elif isinstance(exc, services.ValidationError): code=422
    else: code=400
    return HTTPException(status_code=code, detail=str(exc))


def _profile(candidate):
    data=schemas.CandidatoPerfilResponse.model_validate(candidate).model_dump()
    for i,exp in enumerate(candidate.experiencias):
        if i < len(data["experiencias"]):
            data["experiencias"][i]["habilidades_ids"]=[x.exph_habilidad_id for x in exp.habilidades_asociadas]
    return data


@router.get("/candidatos/me", response_model=schemas.PrincipalTypeResponse)
def candidate_me(candidate=Depends(get_current_candidate)):
    return {"principal_type":"candidato","candidato":_profile(candidate)}



# =============================================================================
# AUTOSERVICIO DEL CANDIDATO
# Estas rutas deben declararse antes de /candidatos/{candidate_id}.
# El candidate_id siempre se obtiene del JWT; nunca del cliente.
# =============================================================================

@router.get(
    "/candidatos/me/perfil-completo",
    response_model=schemas.CandidatoPerfilCompletoResponse,
)
def candidate_my_full_profile(candidate=Depends(get_current_candidate)):
    return _profile(candidate)


@router.patch(
    "/candidatos/me",
    response_model=schemas.CandidatoPerfilResponse,
)
def candidate_update_me(
    payload: schemas.CandidatoSelfUpdate,
    db: Session = Depends(get_db),
    candidate=Depends(get_current_candidate),
):
    try:
        return _profile(services.update_candidate_self(db, candidate, payload))
    except services.CandidateModuleError as exc:
        raise _http(exc) from exc


@router.get("/candidatos/me/habilidades", response_model=list[schemas.HabilidadResponse])
def candidate_my_skills(candidate=Depends(get_current_candidate), db: Session=Depends(get_db)):
    return services.list_candidate_skills(db, candidate.cand_id)


@router.post("/candidatos/me/habilidades", response_model=schemas.HabilidadResponse, status_code=201)
def candidate_add_my_skill(payload:schemas.HabilidadCreate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.add_skill(db, candidate.cand_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.patch("/candidatos/me/habilidades/{item_id}", response_model=schemas.HabilidadResponse)
def candidate_patch_my_skill(item_id:int, payload:schemas.HabilidadUpdate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.update_skill(db, candidate.cand_id, item_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.delete("/candidatos/me/habilidades/{item_id}", status_code=204)
def candidate_delete_my_skill(item_id:int, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: services.delete_skill(db, candidate.cand_id, item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.get("/candidatos/me/estudios", response_model=list[schemas.EstudioResponse])
def candidate_my_studies(candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    return services.list_candidate_studies(db, candidate.cand_id)


@router.post("/candidatos/me/estudios", response_model=schemas.EstudioResponse, status_code=201)
def candidate_add_my_study(payload:schemas.EstudioCreate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.add_study(db, candidate.cand_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.patch("/candidatos/me/estudios/{item_id}", response_model=schemas.EstudioResponse)
def candidate_patch_my_study(item_id:int, payload:schemas.EstudioUpdate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.update_study(db, candidate.cand_id, item_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.delete("/candidatos/me/estudios/{item_id}", status_code=204)
def candidate_delete_my_study(item_id:int, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: services.delete_study(db, candidate.cand_id, item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.get("/candidatos/me/experiencias", response_model=list[schemas.ExperienciaResponse])
def candidate_my_experiences(candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    return services.list_candidate_experiences(db, candidate.cand_id)


@router.post("/candidatos/me/experiencias", response_model=schemas.ExperienciaResponse, status_code=201)
def candidate_add_my_experience(payload:schemas.ExperienciaCreate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.add_experience(db, candidate.cand_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.patch("/candidatos/me/experiencias/{item_id}", response_model=schemas.ExperienciaResponse)
def candidate_patch_my_experience(item_id:int, payload:schemas.ExperienciaUpdate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.update_experience(db, candidate.cand_id, item_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.delete("/candidatos/me/experiencias/{item_id}", status_code=204)
def candidate_delete_my_experience(item_id:int, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: services.delete_experience(db, candidate.cand_id, item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.get("/candidatos/me/cursos", response_model=list[schemas.CursoResponse])
def candidate_my_courses(candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    return services.list_candidate_courses(db, candidate.cand_id)


@router.post("/candidatos/me/cursos", response_model=schemas.CursoResponse, status_code=201)
def candidate_add_my_course(payload:schemas.CursoCreate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.add_course(db, candidate.cand_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.patch("/candidatos/me/cursos/{item_id}", response_model=schemas.CursoResponse)
def candidate_patch_my_course(item_id:int, payload:schemas.CursoUpdate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.update_course(db, candidate.cand_id, item_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.delete("/candidatos/me/cursos/{item_id}", status_code=204)
def candidate_delete_my_course(item_id:int, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: services.delete_course(db, candidate.cand_id, item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.get("/candidatos/me/idiomas", response_model=list[schemas.IdiomaCandidatoResponse])
def my_languages(db:Session=Depends(get_db), candidate=Depends(get_current_candidate)):
    return services.list_candidate_languages(db, candidate.cand_id)

@router.post("/candidatos/me/idiomas", response_model=schemas.IdiomaCandidatoResponse, status_code=201)
def my_add_language(payload:schemas.IdiomaCandidatoCreate, db:Session=Depends(get_db), candidate=Depends(get_current_candidate)):
    try:return services.add_language(db, candidate.cand_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.patch("/candidatos/me/idiomas/{item_id}", response_model=schemas.IdiomaCandidatoResponse)
def my_patch_language(item_id:int, payload:schemas.IdiomaCandidatoUpdate, db:Session=Depends(get_db), candidate=Depends(get_current_candidate)):
    try:return services.update_language(db, candidate.cand_id, item_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.delete("/candidatos/me/idiomas/{item_id}", status_code=204)
def my_delete_language(item_id:int, db:Session=Depends(get_db), candidate=Depends(get_current_candidate)):
    try:services.delete_language(db, candidate.cand_id, item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.get("/candidatos/me/direcciones", response_model=list[schemas.DireccionResponse])
def candidate_my_addresses(candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    return services.list_candidate_addresses(db, candidate.cand_id)


@router.put("/candidatos/me/direccion", response_model=schemas.DireccionResponse)
def candidate_upsert_my_address(payload:schemas.DireccionUpdate, candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: return services.upsert_candidate_address(db, candidate.cand_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.delete("/candidatos/me/direccion", status_code=204)
def candidate_delete_my_address(candidate=Depends(get_current_candidate), db:Session=Depends(get_db)):
    try: services.delete_candidate_address(db, candidate.cand_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.get("/candidatos/me/solicitudes", response_model=list[schemas.PostulacionResponse])
def candidate_my_requests(
    estado_id:int|None=None,
    skip:int=0,
    limit:int=100,
    candidate=Depends(get_current_candidate),
    db:Session=Depends(get_db),
):
    return services.list_candidate_applications(
        db,
        candidate.cand_id,
        estado_id=estado_id,
        skip=skip,
        limit=limit,
    )


@router.get("/candidatos", response_model=list[schemas.CandidatoResponse])
def list_candidates(q:str|None=None,estado_id:int|None=None,disponibilidad_id:int|None=None,habilidad_id:int|None=None,skip:int=0,limit:int=100,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_VIEW"))):
    return services.list_candidates(db,q=q,estado_id=estado_id,disponibilidad_id=disponibilidad_id,habilidad_id=habilidad_id,skip=skip,limit=min(limit,500))


@router.post("/candidatos", response_model=schemas.CandidatoCreationResponse, status_code=201)
def create_candidate(payload:schemas.CandidatoCreate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:
        obj,pwd=services.create_candidate(db,payload); return {"candidato":_profile(obj),"password_temporal":pwd}
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.get("/candidatos/{candidate_id}", response_model=schemas.CandidatoPerfilResponse)
def get_candidate(candidate_id:int,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_VIEW"))):
    try: return _profile(services.get_candidate(db,candidate_id))
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.put("/candidatos/{candidate_id}", response_model=schemas.CandidatoPerfilResponse)
def replace_candidate(candidate_id:int,payload:schemas.CandidatoReplace,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return _profile(services.replace_candidate(db,services.get_candidate(db,candidate_id),payload))
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.patch("/candidatos/{candidate_id}", response_model=schemas.CandidatoPerfilResponse)
def update_candidate(candidate_id:int,payload:schemas.CandidatoUpdate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return _profile(services.update_candidate(db,services.get_candidate(db,candidate_id),payload))
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.delete("/candidatos/{candidate_id}", status_code=204)
def delete_candidate(candidate_id:int,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_DELETE"))):
    try:services.soft_delete_candidate(db,services.get_candidate(db,candidate_id)); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc


def _save_upload(file: UploadFile, content: bytes) -> str:
    base=Path(os.getenv("CANDIDATE_CV_STORAGE_DIR","storage/cv")); base.mkdir(parents=True,exist_ok=True)
    suffix=Path(file.filename or "cv.pdf").suffix.lower() or ".pdf"
    name=f"{uuid.uuid4().hex}{suffix}"; path=base/name; path.write_bytes(content); return str(path).replace("\\","/")


def _import_one(file:UploadFile,db:Session):
    content=file.file.read()
    try:
        text=cv_parser.extract_text(file.filename or "cv.pdf",content)
        core,warnings=cv_parser.parse_core(text)
        nested,nested_warnings=services.derive_nested_from_cv(db,text)
        warnings.extend(nested_warnings)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    path=_save_upload(file,content)
    existing=services.get_candidate_by_email(db,core["cand_email"])
    if existing:
        # Si el correo pertenece a candidato existente: complementa campos vacíos y agrega CV sin tocar password.
        for field,value in core.items():
            if value and not getattr(existing,field,None): setattr(existing,field,value)
        existing.cand_url_1=services.merge_semicolon(existing.cand_url_1,core.get("cand_url_1"))
        existing.cand_cv_urls=services.merge_semicolon(existing.cand_cv_urls,path)
        services.merge_imported_nested(db,existing,nested)
        services._commit(db)
        obj=services.get_candidate(db,existing.cand_id)
        return {"candidato":_profile(obj),"creado":False,"actualizado":True,"password_temporal":None,"cv_ruta_guardada":path,"advertencias":warnings}
    payload=schemas.CandidatoCreate(**core,cand_cv_urls=path,**nested)
    try:obj,pwd=services.create_candidate(db,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc
    return {"candidato":_profile(obj),"creado":True,"actualizado":False,"password_temporal":pwd,"cv_ruta_guardada":path,"advertencias":warnings}


@router.post("/candidatos/importar-cv", response_model=schemas.ImportCvResponse)
def import_cv(file:UploadFile=File(...),db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    return _import_one(file,db)


@router.post("/candidatos/importar-cvs", response_model=list[schemas.ImportCvResponse])
def import_cvs(files:list[UploadFile]=File(...),db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    return [_import_one(file,db) for file in files]


@router.get(
    "/candidatos/{candidate_id}/perfil-completo",
    response_model=schemas.CandidatoPerfilCompletoResponse,
)
def get_candidate_full_profile(
    candidate_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_VIEW")),
):
    try:
        return _profile(services.get_candidate(db, candidate_id))
    except services.CandidateModuleError as exc:
        raise _http(exc) from exc


@router.get(
    "/candidatos/{candidate_id}/habilidades",
    response_model=list[schemas.HabilidadResponse],
)
def get_candidate_skills(
    candidate_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_VIEW")),
):
    try:
        return services.list_candidate_skills(db, candidate_id)
    except services.CandidateModuleError as exc:
        raise _http(exc) from exc


@router.get(
    "/candidatos/{candidate_id}/estudios",
    response_model=list[schemas.EstudioResponse],
)
def get_candidate_studies(
    candidate_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_VIEW")),
):
    try:
        return services.list_candidate_studies(db, candidate_id)
    except services.CandidateModuleError as exc:
        raise _http(exc) from exc


@router.get(
    "/candidatos/{candidate_id}/experiencias",
    response_model=list[schemas.ExperienciaResponse],
)
def get_candidate_experiences(
    candidate_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_VIEW")),
):
    try:
        return services.list_candidate_experiences(db, candidate_id)
    except services.CandidateModuleError as exc:
        raise _http(exc) from exc


@router.get(
    "/candidatos/{candidate_id}/cursos",
    response_model=list[schemas.CursoResponse],
)
def get_candidate_courses(
    candidate_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_VIEW")),
):
    try:
        return services.list_candidate_courses(db, candidate_id)
    except services.CandidateModuleError as exc:
        raise _http(exc) from exc


@router.get(
    "/candidatos/{candidate_id}/direcciones",
    response_model=list[schemas.DireccionResponse],
)
def get_candidate_addresses(
    candidate_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_VIEW")),
):
    try:
        return services.list_candidate_addresses(db, candidate_id)
    except services.CandidateModuleError as exc:
        raise _http(exc) from exc


@router.get("/candidatos/{candidate_id}/idiomas", response_model=list[schemas.IdiomaCandidatoResponse])
def candidate_languages(candidate_id:int, db:Session=Depends(get_db), _:Usuario=Depends(require_permissions("CAN_VIEW"))):
    try:return services.list_candidate_languages(db, candidate_id)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.post("/candidatos/{candidate_id}/idiomas", response_model=schemas.IdiomaCandidatoResponse, status_code=201)
def add_candidate_language(candidate_id:int, payload:schemas.IdiomaCandidatoCreate, db:Session=Depends(get_db), _:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.add_language(db, candidate_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.patch("/candidatos/{candidate_id}/idiomas/{item_id}", response_model=schemas.IdiomaCandidatoResponse)
def patch_candidate_language(candidate_id:int, item_id:int, payload:schemas.IdiomaCandidatoUpdate, db:Session=Depends(get_db), _:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.update_language(db, candidate_id, item_id, payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.delete("/candidatos/{candidate_id}/idiomas/{item_id}", status_code=204)
def delete_candidate_language(candidate_id:int, item_id:int, db:Session=Depends(get_db), _:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:services.delete_language(db, candidate_id, item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.post("/candidatos/{candidate_id}/habilidades",response_model=schemas.HabilidadResponse,status_code=201)
def add_skill(candidate_id:int,payload:schemas.HabilidadCreate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.add_skill(db,candidate_id,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.patch("/candidatos/{candidate_id}/habilidades/{item_id}",response_model=schemas.HabilidadResponse)
def patch_skill(candidate_id:int,item_id:int,payload:schemas.HabilidadUpdate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.update_skill(db,candidate_id,item_id,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.delete("/candidatos/{candidate_id}/habilidades/{item_id}",status_code=204)
def del_skill(candidate_id:int,item_id:int,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:services.delete_skill(db,candidate_id,item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.post("/candidatos/{candidate_id}/estudios",response_model=schemas.EstudioResponse,status_code=201)
def add_study(candidate_id:int,payload:schemas.EstudioCreate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.add_study(db,candidate_id,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.patch("/candidatos/{candidate_id}/estudios/{item_id}",response_model=schemas.EstudioResponse)
def patch_study(candidate_id:int,item_id:int,payload:schemas.EstudioUpdate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.update_study(db,candidate_id,item_id,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.delete("/candidatos/{candidate_id}/estudios/{item_id}",status_code=204)
def del_study(candidate_id:int,item_id:int,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:services.delete_study(db,candidate_id,item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.post("/candidatos/{candidate_id}/cursos",response_model=schemas.CursoResponse,status_code=201)
def add_course(candidate_id:int,payload:schemas.CursoCreate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.add_course(db,candidate_id,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.patch("/candidatos/{candidate_id}/cursos/{item_id}",response_model=schemas.CursoResponse)
def patch_course(candidate_id:int,item_id:int,payload:schemas.CursoUpdate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.update_course(db,candidate_id,item_id,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.delete("/candidatos/{candidate_id}/cursos/{item_id}",status_code=204)
def del_course(candidate_id:int,item_id:int,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:services.delete_course(db,candidate_id,item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.post("/candidatos/{candidate_id}/experiencias",response_model=schemas.ExperienciaResponse,status_code=201)
def add_exp(candidate_id:int,payload:schemas.ExperienciaCreate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.add_experience(db,candidate_id,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.patch("/candidatos/{candidate_id}/experiencias/{item_id}",response_model=schemas.ExperienciaResponse)
def patch_exp(candidate_id:int,item_id:int,payload:schemas.ExperienciaUpdate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.update_experience(db,candidate_id,item_id,payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.delete("/candidatos/{candidate_id}/experiencias/{item_id}",status_code=204)
def del_exp(candidate_id:int,item_id:int,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:services.delete_experience(db,candidate_id,item_id); return None
    except services.CandidateModuleError as exc: raise _http(exc) from exc


@router.post("/solicitudes/{solicitud_id}/candidatos/{candidate_id}",response_model=schemas.PostulacionConEvaluacionResponse,status_code=201)
def associate(solicitud_id:int,candidate_id:int,payload:schemas.PostulacionCreate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:obj,evaluation=services.create_application(db,solicitud_id,candidate_id,payload); return {"postulacion":obj,"evaluacion":evaluation}
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.get("/solicitudes/{solicitud_id}/candidatos",response_model=list[schemas.PostulacionResponse])
def request_candidates(solicitud_id:int,estado_id:int|None=None,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_VIEW"))):
    try:return services.list_request_applications(db,solicitud_id,estado_id)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.get(
    "/candidatos/{candidate_id}/solicitudes",
    response_model=list[schemas.PostulacionResponse],
)
def candidate_requests(
    candidate_id: int,
    estado_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAN_VIEW")),
):
    try:
        return services.list_candidate_applications(
            db,
            candidate_id,
            estado_id=estado_id,
            skip=skip,
            limit=limit,
        )
    except services.CandidateModuleError as exc:
        raise _http(exc) from exc

@router.patch("/postulaciones/{application_id}",response_model=schemas.PostulacionResponse)
def patch_application(application_id:int,payload:schemas.PostulacionUpdate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.update_application(db,services.get_application(db,application_id),payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc

@router.patch("/postulaciones/{application_id}/estado",response_model=schemas.PostulacionResponse)
def application_state(application_id:int,payload:schemas.PostulacionEstadoUpdate,db:Session=Depends(get_db),_:Usuario=Depends(require_permissions("CAN_UPDATE"))):
    try:return services.change_application_state(db,services.get_application(db,application_id),payload)
    except services.CandidateModuleError as exc: raise _http(exc) from exc
