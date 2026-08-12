from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.catalogos.models import Cargo
from app.clientes import models, schemas
from app.solicitudes.models import Solicitud
from app.usuarios.models import Area


class ClientModuleError(Exception):
    def __init__(self, message: str, *, constraint: str | None = None):
        super().__init__(message)
        self.message = message
        self.constraint = constraint


class NotFoundError(ClientModuleError):
    pass


class ConflictError(ClientModuleError):
    pass


class ValidationError(ClientModuleError):
    pass


def _constraint_name(exc: IntegrityError) -> str | None:
    original = getattr(exc, "orig", None)
    diagnostic = getattr(original, "diag", None)
    return getattr(diagnostic, "constraint_name", None) if diagnostic else None


def _translate_integrity(exc: IntegrityError, *, deleting: bool = False) -> ConflictError:
    constraint = _constraint_name(exc)
    messages = {
        "uq_tbl_empresa_nombre": "Ya existe una empresa con ese nombre",
        "uq_tbl_empresa_identificacion": "Ya existe una empresa con esa identificación",
        "uq_tbl_cliente_email": "El correo principal del cliente ya está registrado",
        "uq_tbl_cliente_email2": "El correo secundario del cliente ya está registrado",
    }
    if deleting:
        message = "No se puede eliminar el registro porque está siendo utilizado por otros datos"
    else:
        message = messages.get(constraint, "La operación viola una restricción de integridad o unicidad")
    return ConflictError(message, constraint=constraint)


def _commit(db: Session, *, deleting: bool = False) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _translate_integrity(exc, deleting=deleting) from exc


def list_empresas(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
) -> list[models.Empresa]:
    stmt = select(models.Empresa)
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                models.Empresa.emp_nombre.ilike(term),
                models.Empresa.emp_identificacion.ilike(term),
            )
        )
    stmt = stmt.order_by(models.Empresa.emp_id.asc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_empresa(db: Session, empresa_id: int) -> models.Empresa:
    empresa = db.get(models.Empresa, empresa_id)
    if empresa is None:
        raise NotFoundError(f"Empresa con ID {empresa_id} no encontrada")
    return empresa


def create_empresa(db: Session, payload: schemas.EmpresaCreate) -> models.Empresa:
    empresa = models.Empresa(**payload.model_dump())
    db.add(empresa)
    _commit(db)
    db.refresh(empresa)
    return empresa


def replace_empresa(
    db: Session,
    empresa: models.Empresa,
    payload: schemas.EmpresaCreate,
) -> models.Empresa:
    for field, value in payload.model_dump().items():
        setattr(empresa, field, value)
    _commit(db)
    db.refresh(empresa)
    return empresa


def update_empresa(
    db: Session,
    empresa: models.Empresa,
    payload: schemas.EmpresaUpdate,
) -> models.Empresa:
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise ValidationError("Debe enviar al menos un campo para actualizar")
    for field, value in data.items():
        setattr(empresa, field, value)
    _commit(db)
    db.refresh(empresa)
    return empresa


def delete_empresa(db: Session, empresa: models.Empresa) -> None:
    cliente_id = db.scalar(
        select(models.Cliente.cli_id)
        .where(models.Cliente.cli_empresa_id == empresa.emp_id)
        .limit(1)
    )
    if cliente_id is not None:
        raise ConflictError("No se puede eliminar la empresa porque posee clientes asociados")
    db.delete(empresa)
    _commit(db, deleting=True)


def _cliente_stmt():
    return select(models.Cliente).options(
        selectinload(models.Cliente.empresa),
        selectinload(models.Cliente.cargo),
        selectinload(models.Cliente.area),
    )


def list_clientes(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    empresa_id: int | None = None,
) -> list[models.Cliente]:
    stmt = _cliente_stmt()
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                models.Cliente.cli_nombre.ilike(term),
                models.Cliente.cli_email.ilike(term),
                models.Cliente.cli_email2.ilike(term),
                models.Cliente.cli_telefono1.ilike(term),
                models.Cliente.cli_telefono2.ilike(term),
            )
        )
    if empresa_id is not None:
        stmt = stmt.where(models.Cliente.cli_empresa_id == empresa_id)
    stmt = stmt.order_by(models.Cliente.cli_id.asc()).offset(skip).limit(limit)
    return list(db.scalars(stmt).unique().all())


def get_cliente(db: Session, cliente_id: int) -> models.Cliente:
    cliente = db.scalar(_cliente_stmt().where(models.Cliente.cli_id == cliente_id))
    if cliente is None:
        raise NotFoundError(f"Cliente con ID {cliente_id} no encontrado")
    return cliente


def _validate_cliente_refs(
    db: Session,
    *,
    empresa_id: int | None,
    cargo_id: int | None,
    area_id: int | None,
) -> None:
    if empresa_id is None or db.get(models.Empresa, empresa_id) is None:
        raise ValidationError(f"Empresa {empresa_id} no existe")
    if cargo_id is not None and db.get(Cargo, cargo_id) is None:
        raise ValidationError(f"Cargo {cargo_id} no existe")
    if area_id is not None and db.get(Area, area_id) is None:
        raise ValidationError(f"Área {area_id} no existe")


def _validate_cliente_contactos(
    *,
    email1: str | None,
    email2: str | None,
    telefono1: str | None,
    telefono2: str | None,
) -> None:
    if email1 and email2 and email1.casefold() == email2.casefold():
        raise ValidationError("cli_email y cli_email2 deben ser diferentes")
    if telefono1 and telefono2 and telefono1 == telefono2:
        raise ValidationError("cli_telefono1 y cli_telefono2 deben ser diferentes")


def create_cliente(db: Session, payload: schemas.ClienteCreate) -> models.Cliente:
    data = payload.model_dump(mode="json")
    _validate_cliente_refs(
        db,
        empresa_id=data.get("cli_empresa_id"),
        cargo_id=data.get("cli_cargo_empresa_id"),
        area_id=data.get("cli_area_empresa_id"),
    )
    _validate_cliente_contactos(
        email1=data.get("cli_email"),
        email2=data.get("cli_email2"),
        telefono1=data.get("cli_telefono1"),
        telefono2=data.get("cli_telefono2"),
    )
    cliente = models.Cliente(**data)
    db.add(cliente)
    _commit(db)
    return get_cliente(db, cliente.cli_id)


def replace_cliente(
    db: Session,
    cliente: models.Cliente,
    payload: schemas.ClienteReplace,
) -> models.Cliente:
    data = payload.model_dump(mode="json")
    _validate_cliente_refs(
        db,
        empresa_id=data.get("cli_empresa_id"),
        cargo_id=data.get("cli_cargo_empresa_id"),
        area_id=data.get("cli_area_empresa_id"),
    )
    _validate_cliente_contactos(
        email1=data.get("cli_email"),
        email2=data.get("cli_email2"),
        telefono1=data.get("cli_telefono1"),
        telefono2=data.get("cli_telefono2"),
    )
    for field, value in data.items():
        setattr(cliente, field, value)
    _commit(db)
    return get_cliente(db, cliente.cli_id)


def update_cliente(
    db: Session,
    cliente: models.Cliente,
    payload: schemas.ClienteUpdate,
) -> models.Cliente:
    data = payload.model_dump(exclude_unset=True, mode="json")
    if not data:
        raise ValidationError("Debe enviar al menos un campo para actualizar")

    empresa_id = data.get("cli_empresa_id", cliente.cli_empresa_id)
    cargo_id = data.get("cli_cargo_empresa_id", cliente.cli_cargo_empresa_id)
    area_id = data.get("cli_area_empresa_id", cliente.cli_area_empresa_id)
    _validate_cliente_refs(
        db,
        empresa_id=empresa_id,
        cargo_id=cargo_id,
        area_id=area_id,
    )

    email1 = data.get("cli_email", cliente.cli_email)
    email2 = data.get("cli_email2", cliente.cli_email2)
    telefono1 = data.get("cli_telefono1", cliente.cli_telefono1)
    telefono2 = data.get("cli_telefono2", cliente.cli_telefono2)
    _validate_cliente_contactos(
        email1=email1,
        email2=email2,
        telefono1=telefono1,
        telefono2=telefono2,
    )

    for field, value in data.items():
        setattr(cliente, field, value)
    _commit(db)
    return get_cliente(db, cliente.cli_id)


def delete_cliente(db: Session, cliente: models.Cliente) -> None:
    solicitud_id = db.scalar(
        select(Solicitud.sol_id)
        .where(Solicitud.sol_cliente_id == cliente.cli_id)
        .limit(1)
    )
    if solicitud_id is not None:
        raise ConflictError("No se puede eliminar el cliente porque posee solicitudes asociadas")
    db.delete(cliente)
    _commit(db, deleting=True)
