# app/clientes/models.py
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importamos la clase Base de la configuración de tu base de datos
from app.database import Base

class Empresa(Base):
    __tablename__ = "tbl_empresa"

    # Mapeo de columnas según DDL físico
    emp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_nombre: Mapped[Optional[str]] = mapped_column(String(30), unique=True, nullable=True)
    emp_identificacion: Mapped[Optional[str]] = mapped_column(String(15), unique=True, nullable=True)

    # Relación inversa bidireccional hacia Cliente
    clientes: Mapped[List["Cliente"]] = relationship("Cliente", back_populates="empresa")

    def __repr__(self) -> str:
        return f"<Empresa(id={self.emp_id}, nombre='{self.emp_nombre}')>" 

class Cliente(Base):
    __tablename__ = "tbl_cliente"

    # Mapeo de columnas según DDL físico
    cli_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cli_nombre: Mapped[str] = mapped_column(String(30), nullable=False)
    
    # Llaves Foráneas
    cli_cargo_empresa_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_cargo.crgo_id"), nullable=True)
    cli_area_empresa_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_area.area_id"), nullable=True)
    cli_empresa_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_empresa.emp_id"), nullable=True)

    # Datos de contacto
    cli_email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    cli_email2: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    cli_telefono1: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    cli_telefono2: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)

    # Relaciones ORM
    empresa: Mapped[Optional["Empresa"]] = relationship("Empresa", back_populates="clientes")
    cargo: Mapped[Optional["Cargo"]] = relationship("Cargo")
    area: Mapped[Optional["Area"]] = relationship("Area")

    def __repr__(self) -> str:
        return f"<Cliente(id={self.cli_id}, nombre='{self.cli_nombre}', email='{self.cli_email}')>"