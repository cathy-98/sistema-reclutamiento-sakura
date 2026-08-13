# app/clientes/models.py                        
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Empresa(Base):
    __tablename__ = "tbl_empresa"
    __table_args__ = (
        UniqueConstraint("emp_nombre", name="uq_tbl_empresa_nombre"),
        UniqueConstraint("emp_identificacion", name="uq_tbl_empresa_identificacion"),
    )

    emp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_nombre: Mapped[str | None] = mapped_column(String(30), nullable=True)
    emp_identificacion: Mapped[str | None] = mapped_column(String(15), nullable=True)

    clientes: Mapped[list["Cliente"]] = relationship(
        "Cliente",
        back_populates="empresa",
    )

    def __repr__(self) -> str:
        return f"<Empresa(id={self.emp_id}, nombre={self.emp_nombre!r})>"


class Cliente(Base):
    __tablename__ = "tbl_cliente"
    __table_args__ = (
        UniqueConstraint("cli_email", name="uq_tbl_cliente_email"),
        UniqueConstraint("cli_email2", name="uq_tbl_cliente_email2"),
    )

    cli_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cli_nombre: Mapped[str] = mapped_column(String(30), nullable=False)

    cli_cargo_empresa_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_cargo.crgo_id"),
        nullable=True,
    )
    cli_area_empresa_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_area.area_id"),
        nullable=True,
    )
    cli_empresa_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_empresa.emp_id"),
        nullable=True,
    )

    cli_email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cli_email2: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cli_telefono1: Mapped[str | None] = mapped_column(String(12), nullable=True)
    cli_telefono2: Mapped[str | None] = mapped_column(String(12), nullable=True)

    empresa: Mapped[Empresa | None] = relationship("Empresa", back_populates="clientes")
    cargo: Mapped["Cargo | None"] = relationship("Cargo")
    area: Mapped["Area | None"] = relationship("Area")

    def __repr__(self) -> str:
        return f"<Cliente(id={self.cli_id}, nombre={self.cli_nombre!r}, email={self.cli_email!r})>"
