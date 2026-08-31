from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Candidato(Base):
    __tablename__ = "tbl_candidato"
    __table_args__ = (
        UniqueConstraint("cand_email", name="uq_tbl_candidato_email"),
        UniqueConstraint("cand_rut_sin_dv", name="uq_tbl_candidato_rut"),
        CheckConstraint("TRIM(cand_email) <> ''", name="chk_tbl_candidato_email_vacio"),
        CheckConstraint("TRIM(cand_nombres) <> ''", name="chk_tbl_candidato_nombres_vacio"),
        CheckConstraint(
            "TRIM(cand_apellido_paterno) <> ''",
            name="chk_tbl_candidato_apellido_paterno_vacio",
        ),
        CheckConstraint(
            "cand_fecha_nacimiento IS NULL OR cand_fecha_nacimiento <= CURRENT_DATE",
            name="chk_tbl_candidato_fecha_nacimiento",
        ),
        CheckConstraint(
            "cand_rut_sin_dv IS NULL OR cand_rut_sin_dv > 0",
            name="chk_tbl_candidato_rut",
        ),
        CheckConstraint(
            "cand_dv IS NULL OR (cand_dv >= 0 AND cand_dv <= 10)",
            name="chk_tbl_candidato_dv",
        ),
    )

    cand_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cand_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    cand_password: Mapped[str] = mapped_column(String(255), nullable=False)
    cand_nombres: Mapped[str] = mapped_column(String(20), nullable=False)
    cand_apellido_paterno: Mapped[str] = mapped_column(String(20), nullable=False)
    cand_apellido_materno: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cand_fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    cand_telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cand_rut_sin_dv: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    # En el diseño físico 10 representa K.
    cand_dv: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cand_disponibilidad_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_disponibilidad.disp_id"),
        nullable=True,
    )
    cand_resumen_profesional: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cand_fecha_creacion: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=True,
    )
    # URLs profesionales: LinkedIn, GitHub, portafolio, etc. separadas por ';'.
    cand_url_1: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cand_titulo: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cand_estado_usuario_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_estado_usuario.esusr_id"),
        nullable=True,
    )
    # M3: una o varias rutas/URLs de CV, normalizadas y separadas por ';'.
    cand_cv_urls: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    disponibilidad = relationship("Disponibilidad", lazy="joined")
    estado = relationship("EstadoUsuario", lazy="joined")
    direccion = relationship(
        "DireccionCandidato",
        back_populates="candidato",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    habilidades = relationship(
        "CandidatoHabilidad",
        back_populates="candidato",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    experiencias = relationship(
        "ExperienciaLaboral",
        back_populates="candidato",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    estudios = relationship(
        "EstudioCandidato",
        back_populates="candidato",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    cursos = relationship(
        "Curso",
        back_populates="candidato",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    idiomas = relationship(
        "CandidatoIdioma",
        back_populates="candidato",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class CandidatoIdioma(Base):
    __tablename__ = "tbl_candidato_idioma"
    __table_args__ = (
        UniqueConstraint(
            "cdio_candidato_id",
            "cdio_idioma_id",
            name="uq_tbl_candidato_idioma",
        ),
    )

    cdio_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cdio_candidato_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_candidato.cand_id"), nullable=False
    )
    cdio_idioma_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_idioma.idio_id"), nullable=False
    )
    cdio_nivel_idioma_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_nivel_idioma.nvid_id"), nullable=False
    )

    candidato = relationship("Candidato", back_populates="idiomas")
    idioma = relationship("Idioma", lazy="joined")
    nivel_idioma = relationship("NivelIdioma", lazy="joined")


class DireccionCandidato(Base):
    __tablename__ = "tbl_direccion_candidato"
    __table_args__ = (
        UniqueConstraint("drcd_candidato_id", name="uq_tbl_direccion_candidato_candidato"),
        CheckConstraint(
            "drcd_calle IS NULL OR TRIM(drcd_calle) <> ''",
            name="chk_tbl_direccion_candidato_calle",
        ),
        CheckConstraint(
            "drcd_numero IS NULL OR drcd_numero > 0",
            name="chk_tbl_direccion_candidato_numero",
        ),
    )

    drcd_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drcd_candidato_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_candidato.cand_id"),
        nullable=True,
    )
    drcd_comuna_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_comuna.com_id"),
        nullable=True,
    )
    drcd_calle: Mapped[str | None] = mapped_column(String(40), nullable=True)
    drcd_numero: Mapped[int | None] = mapped_column(Integer, nullable=True)
    drcd_dpto_oficina: Mapped[str | None] = mapped_column(String(10), nullable=True)

    candidato = relationship("Candidato", back_populates="direccion")
    comuna = relationship("Comuna", lazy="joined")


class CandidatoHabilidad(Base):
    __tablename__ = "tbl_candidato_habilidad"
    __table_args__ = (
        UniqueConstraint(
            "cdhb_candidato_id",
            "cdhb_habilidad_id",
            name="uq_tbl_candidato_habilidad",
        ),
        CheckConstraint(
            "cdhb_anios_experiencia IS NULL OR cdhb_anios_experiencia >= 0",
            name="chk_tbl_candidato_habilidad_anios",
        ),
    )

    cdhb_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cdhb_candidato_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_candidato.cand_id"),
        nullable=True,
    )
    cdhb_habilidad_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_habilidad.hab_id"),
        nullable=True,
    )
    cdhb_nivel_habilidad_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_nivel_habilidad.nvhb_id"),
        nullable=True,
    )
    cdhb_anios_experiencia: Mapped[int | None] = mapped_column(Integer, nullable=True)

    candidato = relationship("Candidato", back_populates="habilidades")
    habilidad = relationship("Habilidad", lazy="joined")
    nivel_habilidad = relationship("NivelHabilidad", lazy="joined")


class ExperienciaLaboral(Base):
    __tablename__ = "tbl_experiencia_laboral"
    __table_args__ = (
        CheckConstraint(
            "expl_descripcion_funciones IS NULL OR TRIM(expl_descripcion_funciones) <> ''",
            name="chk_tbl_experiencia_laboral_descripcion",
        ),
        CheckConstraint(
            "expl_fecha_fin IS NULL OR expl_fecha_inicio IS NULL OR expl_fecha_inicio <= expl_fecha_fin",
            name="chk_tbl_experiencia_laboral_fechas",
        ),
    )

    expl_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    expl_candidato_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_candidato.cand_id"),
        nullable=True,
    )
    expl_empresa_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_empresa.emp_id"),
        nullable=True,
    )
    expl_cargo_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_cargo.crgo_id"),
        nullable=True,
    )
    expl_descripcion_funciones: Mapped[str | None] = mapped_column(String(300), nullable=True)
    expl_fecha_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    expl_fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)

    candidato = relationship("Candidato", back_populates="experiencias")
    empresa = relationship("Empresa", lazy="joined")
    cargo = relationship("Cargo", lazy="joined")
    habilidades_asociadas = relationship(
        "ExperienciaLaboralHabilidad",
        back_populates="experiencia",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ExperienciaLaboralHabilidad(Base):
    __tablename__ = "tbl_experiencia_laboral_habilidad"

    exph_experiencia_laboral_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tbl_experiencia_laboral.expl_id"),
        primary_key=True,
    )
    exph_habilidad_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tbl_habilidad.hab_id"),
        primary_key=True,
    )

    experiencia = relationship("ExperienciaLaboral", back_populates="habilidades_asociadas")
    habilidad = relationship("Habilidad", lazy="joined")
                                                                                                                      


class EstudioCandidato(Base):
    __tablename__ = "tbl_estudio_candidato"
    __table_args__ = (
        CheckConstraint(
            "etcd_fecha_fin IS NULL OR etcd_fecha_inicio IS NULL OR etcd_fecha_inicio <= etcd_fecha_fin",
            name="chk_tbl_estudio_candidato_fechas",
        ),
    )

    etcd_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    etcd_candidato_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_candidato.cand_id"),
        nullable=True,
    )
    etcd_nivel_educacional_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_nivel_educacional.nved_id"),
        nullable=True,
    )
    etcd_institucion_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_institucion.inst_id"),
        nullable=True,
    )
    etcd_carrera_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_carrera.crra_id"),
        nullable=True,
    )
    etcd_fecha_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    etcd_fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)

    candidato = relationship("Candidato", back_populates="estudios")
    nivel_educacional = relationship("NivelEducacional", lazy="joined")
    institucion = relationship("Institucion", lazy="joined")
    carrera = relationship("Carrera", lazy="joined")
                                                               
                                                                 


class Curso(Base):
    __tablename__ = "tbl_curso"
    __table_args__ = (
        CheckConstraint(
            "curs_nombre_curso IS NULL OR TRIM(curs_nombre_curso) <> ''",
            name="chk_tbl_curso_nombre_vacio",
        ),
        CheckConstraint(
            "curs_anio_curso IS NULL OR curs_anio_curso >= 1900",
            name="chk_tbl_curso_anio_min",
        ),
    )

    curs_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    curs_candidato_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_candidato.cand_id"),
        nullable=True,
    )
    curs_nombre_curso: Mapped[str | None] = mapped_column(String(40), nullable=True)
    curs_institucion_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_institucion.inst_id"),
        nullable=True,
    )
    curs_es_certificado: Mapped[bool | None] = mapped_column(nullable=True)
    curs_anio_curso: Mapped[int | None] = mapped_column(Integer, nullable=True)

    candidato = relationship("Candidato", back_populates="cursos")
    institucion = relationship("Institucion", lazy="joined")
