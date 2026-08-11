from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Area(Base):
    """Área organizacional asociable a usuarios administrativos."""

    __tablename__ = "tbl_area"
    __table_args__ = (
        UniqueConstraint("area_nombre", name="uq_tbl_area_nombre"),
    )

    area_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # CORRECCIÓN: base_inicial.sql define varchar(50), no varchar(20).
    area_nombre: Mapped[str | None] = mapped_column(String(50), nullable=True)
    area_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    usuarios: Mapped[list["Usuario"]] = relationship(
        "Usuario",
        back_populates="area",
    )


class Permiso(Base):
    """Permiso atómico utilizado por el esquema RBAC."""

    __tablename__ = "tbl_permiso"
    __table_args__ = (
        UniqueConstraint("per_nombre", name="uq_tbl_permiso_nombre"),
    )

    per_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    per_nombre: Mapped[str] = mapped_column(String(20), nullable=False)
    per_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    roles: Mapped[list["Rol"]] = relationship(
        "Rol",
        secondary="tbl_rol_permiso",
        back_populates="permisos",
    )


class RolPermiso(Base):
    """Tabla física de asociación muchos-a-muchos entre rol y permiso."""

    __tablename__ = "tbl_rol_permiso"

    rlpm_rol_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tbl_rol.rol_id"),
        primary_key=True,
    )
    rlpm_permiso_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tbl_permiso.per_id"),
        primary_key=True,
    )


class Rol(Base):
    """Rol administrativo del sistema."""

    __tablename__ = "tbl_rol"
    __table_args__ = (
        UniqueConstraint("rol_nombre", name="uq_tbl_rol_nombre"),
    )

    rol_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rol_nombre: Mapped[str] = mapped_column(String(20), nullable=False)
    rol_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    permisos: Mapped[list[Permiso]] = relationship(
        "Permiso",
        secondary="tbl_rol_permiso",
        back_populates="roles",
    )
    usuarios: Mapped[list["Usuario"]] = relationship(
        "Usuario",
        back_populates="rol",
    )


class EstadoUsuario(Base):
    """Estado operacional de una cuenta: Activo, Inactivo, Bloqueado, Eliminado, etc."""

    __tablename__ = "tbl_estado_usuario"
    __table_args__ = (
        UniqueConstraint("esusr_nombre", name="uq_tbl_estado_usuario_nombre"),
    )

    esusr_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    esusr_nombre: Mapped[str] = mapped_column(String(20), nullable=False)
    esusr_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    usuarios: Mapped[list["Usuario"]] = relationship(
        "Usuario",
        back_populates="estado",
    )


class Usuario(Base):
    """Usuario administrativo/reclutador autenticable mediante JWT."""

    __tablename__ = "tbl_usuario"
    __table_args__ = (
        UniqueConstraint("usr_email", name="uq_tbl_usuario_email"),
        UniqueConstraint("usr_rut_sin_dv", "usr_dv", name="uq_tbl_usuario_rut"),
    )

    # CORRECCIÓN: usr_id es IDENTITY en base_inicial.sql.
    usr_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usr_rol_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_rol.rol_id"),
        nullable=True,
    )
    usr_estado_usuario_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_estado_usuario.esusr_id"),
        nullable=True,
    )
    usr_area_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_area.area_id"),
        nullable=True,
    )

    usr_nombres: Mapped[str] = mapped_column(String(15), nullable=False)
    usr_apellido_paterno: Mapped[str] = mapped_column(String(15), nullable=False)
    usr_apellido_materno: Mapped[str | None] = mapped_column(String(15), nullable=True)
    usr_rut_sin_dv: Mapped[str | None] = mapped_column(String(15), nullable=True)
    usr_dv: Mapped[str | None] = mapped_column(String(1), nullable=True)
    usr_telefono: Mapped[str | None] = mapped_column(String(15), nullable=True)
    usr_email: Mapped[str] = mapped_column(String(30), nullable=False)
    usr_contrasena: Mapped[str] = mapped_column(String(255), nullable=False)

    # joined evita N+1 para relaciones simples consultadas continuamente.
    rol: Mapped[Rol | None] = relationship(
        "Rol",
        back_populates="usuarios",
        lazy="joined",
    )
    estado: Mapped[EstadoUsuario | None] = relationship(
        "EstadoUsuario",
        back_populates="usuarios",
        lazy="joined",
    )
    area: Mapped[Area | None] = relationship(
        "Area",
        back_populates="usuarios",
        lazy="joined",
    )
