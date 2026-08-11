from __future__ import annotations

from typing import Any, Generic, Iterable, Mapping, TypeVar

from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CatalogIntegrityError(Exception):
    """Error de integridad controlado para exponer un HTTP 409 desde el router."""

    def __init__(self, message: str, constraint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.constraint = constraint


class CatalogValidationError(Exception):
    """Error de negocio previo al acceso a base de datos."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CatalogCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repository/CRUD genérico para catálogos maestros.

    Centraliza paginación, búsqueda, filtros permitidos, transacciones y manejo
    de IntegrityError. De esta forma cada catálogo no duplica la misma lógica.
    """

    def __init__(
        self,
        model: type[ModelType],
        *,
        id_field: str,
        search_fields: Iterable[str],
        allowed_filter_fields: Iterable[str] = (),
        required_fields: Iterable[str] = (),
    ) -> None:
        self.model = model
        self.id_field = id_field
        self.search_fields = tuple(search_fields)
        self.allowed_filter_fields = set(allowed_filter_fields)
        self.required_fields = set(required_fields)

        # Validación temprana de la configuración del repository.
        for field_name in (
            self.id_field,
            *self.search_fields,
            *self.allowed_filter_fields,
            *self.required_fields,
        ):
            if not hasattr(self.model, field_name):
                raise RuntimeError(
                    f"Configuración CRUD inválida: {self.model.__name__} no posee {field_name}"
                )

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        filters: Mapping[str, Any] | None = None,
    ) -> list[ModelType]:
        stmt = select(self.model)

        if search and search.strip():
            term = f"%{search.strip()}%"
            predicates = [
                getattr(self.model, field_name).ilike(term)
                for field_name in self.search_fields
            ]
            if predicates:
                stmt = stmt.where(or_(*predicates))

        if filters:
            for field_name, value in filters.items():
                if value is None:
                    continue
                if field_name not in self.allowed_filter_fields:
                    raise CatalogValidationError(
                        f"El filtro '{field_name}' no está permitido para {self.model.__name__}"
                    )
                stmt = stmt.where(getattr(self.model, field_name) == value)

        stmt = (
            stmt.order_by(getattr(self.model, self.id_field).asc())
            .offset(skip)
            .limit(limit)
        )
        return list(db.scalars(stmt).all())

    def get(self, db: Session, item_id: int) -> ModelType | None:
        stmt = select(self.model).where(
            getattr(self.model, self.id_field) == item_id
        )
        return db.scalar(stmt)

    def create(self, db: Session, payload: CreateSchemaType) -> ModelType:
        data = payload.model_dump()
        self._validate_required_fields(data)
        instance = self.model(**data)
        db.add(instance)

        try:
            db.commit()
            db.refresh(instance)
            return instance
        except IntegrityError as exc:
            db.rollback()
            raise self._translate_integrity_error(exc) from exc

    def replace(
        self,
        db: Session,
        instance: ModelType,
        payload: CreateSchemaType,
    ) -> ModelType:
        """PUT: reemplaza los campos editables usando el schema de creación completo."""
        data = payload.model_dump()
        self._validate_required_fields(data)
        return self._apply_update(db, instance, data)

    def update(
        self,
        db: Session,
        instance: ModelType,
        payload: UpdateSchemaType,
    ) -> ModelType:
        """PATCH: modifica exclusivamente los campos enviados por el cliente."""
        data = payload.model_dump(exclude_unset=True)
        if not data:
            raise CatalogValidationError("Debe enviar al menos un campo para actualizar")
        self._validate_required_fields(data, partial=True)
        return self._apply_update(db, instance, data)

    def delete(self, db: Session, instance: ModelType) -> None:
        db.delete(instance)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise self._translate_integrity_error(exc, deleting=True) from exc

    def _apply_update(
        self,
        db: Session,
        instance: ModelType,
        data: Mapping[str, Any],
    ) -> ModelType:
        for field_name, value in data.items():
            if field_name == self.id_field:
                continue
            if hasattr(instance, field_name):
                setattr(instance, field_name, value)

        try:
            db.commit()
            db.refresh(instance)
            return instance
        except IntegrityError as exc:
            db.rollback()
            raise self._translate_integrity_error(exc) from exc

    def _validate_required_fields(
        self,
        data: Mapping[str, Any],
        *,
        partial: bool = False,
    ) -> None:
        for field_name in self.required_fields:
            if partial and field_name not in data:
                continue
            if data.get(field_name) is None:
                raise CatalogValidationError(
                    f"El campo '{field_name}' no puede quedar nulo"
                )

    @staticmethod
    def _translate_integrity_error(
        exc: IntegrityError,
        *,
        deleting: bool = False,
    ) -> CatalogIntegrityError:
        constraint = None
        original = getattr(exc, "orig", None)
        diagnostic = getattr(original, "diag", None)
        if diagnostic is not None:
            constraint = getattr(diagnostic, "constraint_name", None)

        if deleting:
            message = (
                "No se puede eliminar el registro porque está siendo utilizado "
                "por otros datos del sistema"
            )
        else:
            message = (
                "La operación viola una restricción de integridad. Revise valores "
                "duplicados y referencias a registros relacionados"
            )

        return CatalogIntegrityError(message=message, constraint=constraint)
