# app/catalogos/models.py

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

# ==========================================================
# CATÁLOGOS GEOGRÁFICOS DE RECLUTAMIENTO Y SELECCIÓN
# ==========================================================

class Pais(Base):
    """Mapea la tabla tbl_pais para la parametrización geográfica global"""
    __tablename__ = "tbl_pais"

    pais_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) 
    pais_nombre: Mapped[str | None] = mapped_column(String(100), nullable=True) # Nombre del país

    # Relación uno a muchos con Region
    regiones: Mapped[list["Region"]] = relationship("Region", back_populates="pais") # Relación uno a muchos con Region


class Region(Base):
    """Mapea la tabla tbl_region conectada a un País"""
    __tablename__ = "tbl_region"

    reg_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID de la región
    reg_pais_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tbl_pais.pais_id"), nullable=True) # ID del país
    reg_nombre: Mapped[str | None] = mapped_column(String(100), nullable=True) # Nombre de la región

    # Relaciones del ORM
    pais: Mapped["Pais"] = relationship("Pais", back_populates="regiones") # Relación uno a muchos con Pais
    ciudades: Mapped[list["Ciudad"]] = relationship("Ciudad", back_populates="region") # Relación uno a muchos con Ciudad


class Ciudad(Base):
    """Mapea la tabla tbl_ciudad conectada a una Región"""
    __tablename__ = "tbl_ciudad"

    ciu_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID de la ciudad
    ciu_region_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tbl_region.reg_id"), nullable=True) # ID de la región
    ciu_nombre: Mapped[str | None] = mapped_column(String(100), nullable=True) # Nombre de la ciudad

    # Relaciones del ORM
    region: Mapped["Region"] = relationship("Region", back_populates="ciudades") # Relación uno a muchos con Region
    comunas: Mapped[list["Comuna"]] = relationship("Comuna", back_populates="ciudad") # Relación uno a muchos con Comuna


class Comuna(Base):
    """Mapea la tabla tbl_comuna conectada a una Ciudad"""
    __tablename__ = "tbl_comuna"

    com_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID de la comuna
    com_ciudad_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tbl_ciudad.ciu_id"), nullable=True) # ID de la ciudad
    com_nombre: Mapped[str | None] = mapped_column(String(100), nullable=True) # Nombre de la comuna

    # Relación del ORM
    ciudad: Mapped["Ciudad"] = relationship("Ciudad", back_populates="comunas") # Relación uno a muchos con Ciudad

# ==========================================================
# CATÁLOGOS TÉCNICOS DE RECLUTAMIENTO Y SELECCIÓN
# ==========================================================

class Habilidad(Base):
    """Mapea la tabla tbl_habilidad (Tecnologías, Idiomas, Metodologías)"""
    __tablename__ = "tbl_habilidad"

    hab_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID de la habilidad
    hab_nombre: Mapped[str | None] = mapped_column(String(20), nullable=True) # Nombre de la habilidad      
    hab_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True) # Descripción de la habilidad


class NivelHabilidad(Base):
    """Mapea la tabla tbl_nivel_habilidad (Junior, Semi Senior, Senior, etc.)"""
    __tablename__ = "tbl_nivel_habilidad"

    nvhb_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID del nivel de habilidad
    nvhb_nombre: Mapped[str | None] = mapped_column(String(20), nullable=True) # Nombre del nivel de habilidad
    nvhb_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True) # Descripción del nivel de habilidad
    nvhb_puntaje_base: Mapped[int | None] = mapped_column(Integer, nullable=True) # Puntaje base del nivel de habilidad
    nvhb_duracion: Mapped[int | None] = mapped_column(Integer, nullable=True) # Duración de pregunta del nivel de habilidad en minutos


class Cargo(Base):
    """Mapea la tabla tbl_cargo (Fullstack, Devops, QA, Product Owner)"""
    __tablename__ = "tbl_cargo"

    crgo_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID del cargo
    crgo_nombre: Mapped[str | None] = mapped_column(String(30), nullable=True) # Nombre del cargo
    crgo_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True) # Descripción del cargo


class Modalidad(Base):
    """Mapea la tabla tbl_modalidad (Remoto, Presencial, Híbrido)"""
    __tablename__ = "tbl_modalidad"

    mdld_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID de la modalidad
    mdld_nombre: Mapped[str | None] = mapped_column(String(20), nullable=True) # Nombre de la modalidad
    mdld_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True) # Descripción de la modalidad


class TipoContrato(Base):
    """Mapea la tabla tbl_tipo_contrato (Indefinido, Por Proyecto, Plazo Fijo)"""
    __tablename__ = "tbl_tipo_contrato"

    tpct_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID del tipo de contrato
    tpct_nombre: Mapped[str | None] = mapped_column(String(20), nullable=True) # Nombre del tipo de contrato
    tpct_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True) # Descripción del tipo de contrato


class Disponibilidad(Base):
    """Mapea la tabla tbl_disponibilidad (Inmediata, De 1 a 2 semanas)"""
    __tablename__ = "tbl_disponibilidad"

    disp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID de la disponibilidad
    disp_nombre: Mapped[str | None] = mapped_column(String(40), nullable=True) # Nombre de la disponibilidad


class EstadoSolicitud(Base):
    """Mapea la tabla tbl_estado_solicitud (Abierta, Pausada, Cerrada)"""
    __tablename__ = "tbl_estado_solicitud"

    essl_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID del estado de solicitud        
    essl_nombre: Mapped[str | None] = mapped_column(String(20), nullable=True) # Nombre del estado de solicitud
    essl_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True) # Descripción del estado de solicitud


class PrioridadSolicitud(Base):
    """Mapea la tabla tbl_prioridad_solicitud (Alta, Media, Baja)"""
    __tablename__ = "tbl_prioridad_solicitud"

    prsol_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # ID de la prioridad de solicitud
    prsol_nombre: Mapped[str | None] = mapped_column(String(15), nullable=True) # Nombre de la prioridad de solicitud
    prsol_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True) # Descripción de la prioridad de solicitud