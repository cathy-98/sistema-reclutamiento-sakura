from __future__ import annotations

from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ==========================================================
# UBICACIÓN GEOGRÁFICA
# ==========================================================

class Pais(Base):
    __tablename__ = "tbl_pais"
    __table_args__ = (
        UniqueConstraint("pais_nombre", name="uq_tbl_pais_nombre"),
        CheckConstraint("TRIM(pais_nombre) <> ''", name="chk_tbl_pais_nombre_vacio"),
    )

    pais_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pais_nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    regiones: Mapped[list["Region"]] = relationship("Region", back_populates="pais")


class Region(Base):
    __tablename__ = "tbl_region"
    __table_args__ = (
        UniqueConstraint("reg_pais_id", "reg_nombre", name="uq_tbl_region_pais_nombre"),
        CheckConstraint("TRIM(reg_nombre) <> ''", name="chk_tbl_region_nombre_vacio"),
    )

    reg_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reg_pais_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tbl_pais.pais_id"), nullable=True
    )
    reg_nombre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # joined evita una consulta adicional al serializar el país de una región.
    pais: Mapped[Optional["Pais"]] = relationship(
        "Pais", back_populates="regiones", lazy="joined"
    )
    comunas: Mapped[list["Comuna"]] = relationship("Comuna", back_populates="region")


class Comuna(Base):
    __tablename__ = "tbl_comuna"

    com_id = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # CORRECCIÓN:
    # La comuna depende directamente de Región.
    com_region_id = mapped_column(
        Integer,
        ForeignKey("tbl_region.reg_id"),
        nullable=True,
    )

    com_nombre = mapped_column(
        String(100),
        nullable=True,
    )

    region = relationship(
        "Region",
        back_populates="comunas",
        lazy="joined",
    )


# ==========================================================
# EDUCACIÓN E INSTITUCIONES
# ==========================================================

class TipoInstitucion(Base):
    __tablename__ = "tbl_tipo_institucion"
    __table_args__ = (
        UniqueConstraint("tint_tipo_institucion", name="uq_tbl_tipo_institucion_nombre"),
        CheckConstraint(
            "TRIM(tint_tipo_institucion) <> ''",
            name="chk_tbl_tipo_institucion_nombre_vacio",
        ),
    )

    tint_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tint_tipo_institucion: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    instituciones: Mapped[list["Institucion"]] = relationship(
        "Institucion", back_populates="tipo_institucion"
    )


class Institucion(Base):
    __tablename__ = "tbl_institucion"
    __table_args__ = (
        UniqueConstraint("inst_nombre", name="uq_tbl_institucion_nombre"),
        CheckConstraint("TRIM(inst_nombre) <> ''", name="chk_tbl_institucion_nombre_vacio"),
    )

    inst_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inst_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    inst_tipo_institucion_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tbl_tipo_institucion.tint_id"), nullable=True
    )

    tipo_institucion: Mapped[Optional["TipoInstitucion"]] = relationship(
        "TipoInstitucion", back_populates="instituciones", lazy="joined"
    )


class Carrera(Base):
    __tablename__ = "tbl_carrera"
    __table_args__ = (
        UniqueConstraint("crra_nombre", name="uq_tbl_carrera_nombre"),
        CheckConstraint("TRIM(crra_nombre) <> ''", name="chk_tbl_carrera_nombre_vacio"),
    )

    crra_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crra_nombre: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class NivelEducacional(Base):
    __tablename__ = "tbl_nivel_educacional"
    __table_args__ = (
        UniqueConstraint("nved_nombre", name="uq_tbl_nivel_educacional_nombre"),
        CheckConstraint(
            "TRIM(nved_nombre) <> ''", name="chk_tbl_nivel_educacional_nombre_vacio"
        ),
    )

    nved_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nved_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)


# ==========================================================
# PUESTO, EXPERIENCIA Y CONDICIONES DE TRABAJO
# ==========================================================


class CategoriaHabilidad(Base):
    __tablename__ = "tbl_categoria_habilidad"
    __table_args__ = (
        UniqueConstraint("cthb_nombre", name="uq_tbl_categoria_habilidad_nombre"),
        CheckConstraint("TRIM(cthb_nombre) <> ''", name="chk_tbl_categoria_habilidad_nombre_vacio"),
        CheckConstraint(
            "cthb_descripcion IS NULL OR TRIM(cthb_descripcion) <> ''",
            name="chk_tbl_categoria_habilidad_descripcion_vacia",
        ),
    )

    cthb_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cthb_nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    cthb_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    habilidades: Mapped[list["Habilidad"]] = relationship(
        "Habilidad", back_populates="categoria", passive_deletes=True
    )


class Idioma(Base):
    __tablename__ = "tbl_idioma"
    __table_args__ = (
        UniqueConstraint("idio_nombre", name="uq_tbl_idioma_nombre"),
        CheckConstraint("TRIM(idio_nombre) <> ''", name="chk_tbl_idioma_nombre_vacio"),
    )

    idio_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idio_nombre: Mapped[str] = mapped_column(String(100), nullable=False)


class Habilidad(Base):
    __tablename__ = "tbl_habilidad"
    __table_args__ = (
        UniqueConstraint("hab_nombre", name="uq_tbl_habilidad_nombre"),
        CheckConstraint("TRIM(hab_nombre) <> ''", name="chk_tbl_habilidad_nombre_vacio"),
    )

    hab_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hab_nombre: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hab_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    hab_categoria_habilidad_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tbl_categoria_habilidad.cthb_id", ondelete="RESTRICT"),
        nullable=True,
    )

    categoria: Mapped[Optional["CategoriaHabilidad"]] = relationship(
        "CategoriaHabilidad", back_populates="habilidades", lazy="joined"
    )


class NivelHabilidad(Base):
    __tablename__ = "tbl_nivel_habilidad"
    __table_args__ = (
        UniqueConstraint("nvhb_nombre", name="uq_tbl_nivel_habilidad_nombre"),
        CheckConstraint(
            "TRIM(nvhb_nombre) <> ''", name="chk_tbl_nivel_habilidad_nombre_vacio"
        ),
        CheckConstraint(
            "nvhb_puntaje_base >= 0", name="chk_tbl_nivel_habilidad_puntaje"
        ),
        CheckConstraint("nvhb_duracion >= 0", name="chk_tbl_nivel_habilidad_duracion"),
    )

    nvhb_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nvhb_nombre: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nvhb_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    nvhb_puntaje_base: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    nvhb_duracion: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class Cargo(Base):
    __tablename__ = "tbl_cargo"
    __table_args__ = (
        UniqueConstraint("crgo_nombre", name="uq_tbl_cargo_nombre"),
        CheckConstraint("TRIM(crgo_nombre) <> ''", name="chk_tbl_cargo_nombre_vacio"),
        CheckConstraint(
            "crgo_descripcion IS NULL OR TRIM(crgo_descripcion) <> ''",
            name="chk_tbl_cargo_descripcion_vacia",
        ),
    )

    crgo_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crgo_nombre: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    crgo_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class Modalidad(Base):
    __tablename__ = "tbl_modalidad"
    __table_args__ = (
        UniqueConstraint("mdld_nombre", name="uq_tbl_modalidad_nombre"),
        CheckConstraint("TRIM(mdld_nombre) <> ''", name="chk_tbl_modalidad_nombre_vacio"),
        CheckConstraint(
            "mdld_descripcion IS NULL OR TRIM(mdld_descripcion) <> ''",
            name="chk_tbl_modalidad_descripcion_vacia",
        ),
    )

    mdld_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mdld_nombre: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mdld_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class TipoContrato(Base):
    __tablename__ = "tbl_tipo_contrato"
    __table_args__ = (
        UniqueConstraint("tpct_nombre", name="uq_tbl_tipo_contrato_nombre"),
        CheckConstraint("TRIM(tpct_nombre) <> ''", name="chk_tbl_tipo_contrato_nombre_vacio"),
        CheckConstraint(
            "tpct_descripcion IS NULL OR TRIM(tpct_descripcion) <> ''",
            name="chk_tbl_tipo_contrato_descripcion_vacia",
        ),
    )

    tpct_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tpct_nombre: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tpct_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class Disponibilidad(Base):
    __tablename__ = "tbl_disponibilidad"
    __table_args__ = (
        UniqueConstraint("disp_nombre", name="uq_tbl_disponibilidad_nombre"),
        CheckConstraint(
            "TRIM(disp_nombre) <> ''", name="chk_tbl_disponibilidad_nombre_vacio"
        ),
    )

    disp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disp_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)


# ==========================================================
# RECLUTAMIENTO, RESULTADOS Y ESTADOS
# ==========================================================

class EstadoSolicitud(Base):
    __tablename__ = "tbl_estado_solicitud"
    __table_args__ = (
        UniqueConstraint("essl_nombre", name="uq_tbl_estado_solicitud_nombre"),
        CheckConstraint("TRIM(essl_nombre) <> ''", name="chk_tbl_estado_solicitud_nombre_vacio"),
        CheckConstraint(
            "essl_descripcion IS NULL OR TRIM(essl_descripcion) <> ''",
            name="chk_tbl_estado_solicitud_descripcion_vacia",
        ),
    )

    essl_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    essl_nombre: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    essl_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class PrioridadSolicitud(Base):
    __tablename__ = "tbl_prioridad_solicitud"
    __table_args__ = (
        UniqueConstraint("prsol_nombre", name="uq_tbl_prioridad_solicitud_nombre"),
        CheckConstraint(
            "TRIM(prsol_nombre) <> ''", name="chk_tbl_prioridad_nombre_vacio"
        ),
        CheckConstraint(
            "prsol_descripcion IS NULL OR TRIM(prsol_descripcion) <> ''",
            name="chk_tbl_prioridad_descripcion_vacia",
        ),
    )

    prsol_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prsol_nombre: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    prsol_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class EstadoSolicitudCandidato(Base):
    __tablename__ = "tbl_estado_solicitud_candidato"
    __table_args__ = (
        UniqueConstraint(
            "essc_nombre", name="uq_tbl_estado_solicitud_candidato_nombre"
        ),
        CheckConstraint(
            "TRIM(essc_nombre) <> ''", name="chk_tbl_estado_solicitud_candidato_nombre"
        ),
    )

    essc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    essc_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    essc_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class MotivoRechazo(Base):
    __tablename__ = "tbl_motivo_rechazo"
    __table_args__ = (
        UniqueConstraint("mtrc_nombre", name="uq_tbl_motivo_rechazo_nombre"),
        CheckConstraint("TRIM(mtrc_nombre) <> ''", name="chk_tbl_motivo_rechazo_nombre"),
    )

    mtrc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mtrc_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    mtrc_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class EstadoCuestionarioCandidato(Base):
    __tablename__ = "tbl_estado_cuestionario_candidato"
    __table_args__ = (
        UniqueConstraint(
            "escc_nombre", name="uq_tbl_estado_cuestionario_candidato_nombre"
        ),
        CheckConstraint(
            "TRIM(escc_nombre) <> ''",
            name="chk_tbl_estado_cuestionario_candidato_nombre",
        ),
    )

    escc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    escc_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)


class EstadoEntrevista(Base):
    __tablename__ = "tbl_estado_entrevista"
    __table_args__ = (
        UniqueConstraint("esev_nombre", name="uq_tbl_estado_entrevista_nombre"),
        CheckConstraint("TRIM(esev_nombre) <> ''", name="chk_tbl_estado_entrevista_nombre"),
    )

    esev_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    esev_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    esev_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class TipoEntrevista(Base):
    __tablename__ = "tbl_tipo_entrevista"
    __table_args__ = (
        UniqueConstraint("tpet_nombre", name="uq_tbl_tipo_entrevista_nombre"),
        CheckConstraint("TRIM(tpet_nombre) <> ''", name="chk_tbl_tipo_entrevista_nombre"),
    )

    tpet_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tpet_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    tpet_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)


class NombreResultado(Base):
    __tablename__ = "tbl_nombre_resultado"
    __table_args__ = (
        UniqueConstraint("nore_nombre", name="uq_tbl_nombre_resultado_nombre"),
        CheckConstraint("TRIM(nore_nombre) <> ''", name="chk_tbl_nombre_resultado_nombre"),
    )

    nore_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nore_nombre: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
