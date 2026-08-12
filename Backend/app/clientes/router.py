from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_permissions
from app.database import get_db
from app.clientes import models, schemas, service
from app.usuarios.models import Usuario


router = APIRouter(prefix="/clientes", tags=["Clientes y Empresas"])


def _translate_error(exc: service.ClientModuleError) -> HTTPException:
    if isinstance(exc, service.NotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, service.ConflictError):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_422_UNPROCESSABLE_CONTENT

    detail: dict[str, object] = {"message": exc.message}
    if exc.constraint:
        detail["constraint"] = exc.constraint
    return HTTPException(status_code=code, detail=detail)


# Las rutas /empresas deben declararse antes de /{cliente_id}.

@router.get("/empresas", response_model=list[schemas.EmpresaRead])
def listar_empresas(
    q: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    return service.list_empresas(db, skip=skip, limit=limit, q=q)


@router.post("/empresas", response_model=schemas.EmpresaRead, status_code=status.HTTP_201_CREATED)
def crear_empresa(
    payload: schemas.EmpresaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        return service.create_empresa(db, payload)
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc


@router.get("/empresas/{empresa_id}", response_model=schemas.EmpresaRead)
def obtener_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        return service.get_empresa(db, empresa_id)
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/empresas/{empresa_id}", response_model=schemas.EmpresaRead)
def reemplazar_empresa(
    empresa_id: int,
    payload: schemas.EmpresaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        return service.replace_empresa(db, service.get_empresa(db, empresa_id), payload)
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/empresas/{empresa_id}", response_model=schemas.EmpresaRead)
def actualizar_empresa(
    empresa_id: int,
    payload: schemas.EmpresaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        return service.update_empresa(db, service.get_empresa(db, empresa_id), payload)
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete("/empresas/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        service.delete_empresa(db, service.get_empresa(db, empresa_id))
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("", response_model=list[schemas.ClienteRead])
@router.get("/", response_model=list[schemas.ClienteRead], include_in_schema=False)
def listar_clientes(
    q: str | None = Query(default=None),
    empresa_id: int | None = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    return service.list_clientes(
        db,
        skip=skip,
        limit=limit,
        q=q,
        empresa_id=empresa_id,
    )


@router.post("", response_model=schemas.ClienteRead, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=schemas.ClienteRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_cliente(
    payload: schemas.ClienteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        return service.create_cliente(db, payload)
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc


@router.get("/{cliente_id}", response_model=schemas.ClienteRead)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        return service.get_cliente(db, cliente_id)
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc


@router.put("/{cliente_id}", response_model=schemas.ClienteRead)
def reemplazar_cliente(
    cliente_id: int,
    payload: schemas.ClienteReplace,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        return service.replace_cliente(db, service.get_cliente(db, cliente_id), payload)
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc


@router.patch("/{cliente_id}", response_model=schemas.ClienteRead)
def actualizar_cliente(
    cliente_id: int,
    payload: schemas.ClienteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        return service.update_cliente(db, service.get_cliente(db, cliente_id), payload)
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("CAT_ADMIN")),
):
    try:
        service.delete_cliente(db, service.get_cliente(db, cliente_id))
    except service.ClientModuleError as exc:
        raise _translate_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
