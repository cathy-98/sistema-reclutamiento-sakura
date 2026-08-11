from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

# ⚠️ IMPORTANTE: Importa las clases de catálogos maestras para que SQLAlchemy las registre
# Ajusta la ruta del import según la carpeta donde tengas definidas Institucion, Comuna, etc.
from app.catalogos.models import (  # <--- Cambia 'app.catalogos.models' por la ruta real
    Comuna,
    Habilidad,
    NivelHabilidad,
    Cargo,
    Disponibilidad,
)



class DireccionCandidato(Base):
    __tablename__ = "tbl_direccion_candidato"

    drcd_id = Column(Integer, primary_key=True, index=True)
    drcd_candidato_id = Column(Integer, ForeignKey("tbl_candidato.cand_id", ondelete="CASCADE"), nullable=False)
    drcd_comuna_id = Column(Integer, ForeignKey("tbl_comuna.com_id"), nullable=True)
    drcd_calle = Column(String(150), nullable=True)
    drcd_numero = Column(String(20), nullable=True)
    drcd_depto_oficina = Column(String(20), nullable=True)

    # Relaciones
    comuna = relationship("Comuna", lazy="joined")


class CandidatoHabilidad(Base):
    __tablename__ = "tbl_candidato_habilidad"

    cdhb_id = Column(Integer, primary_key=True, index=True)
    cdhb_candidato_id = Column(Integer, ForeignKey("tbl_candidato.cand_id", ondelete="CASCADE"), nullable=False)
    cdhb_habilidad_id = Column(Integer, ForeignKey("tbl_habilidad.hab_id"), nullable=False)
    cdhb_nivel_habilidad_id = Column(Integer, ForeignKey("tbl_nivel_habilidad.nvhb_id"), nullable=True)
    cdhb_anios_experiencia = Column(Integer, default=0, nullable=False)

    # Relaciones
    habilidad = relationship("Habilidad", lazy="joined")
    nivel_habilidad = relationship("NivelHabilidad", lazy="joined")


class ExperienciaLaboralHabilidad(Base):
    __tablename__ = "tbl_experiencia_laboral_habilidad"

    exhb_id = Column(Integer, primary_key=True, index=True)
    exhb_experiencia_laboral_id = Column(Integer, ForeignKey("tbl_experiencia_laboral.expl_id", ondelete="CASCADE"), nullable=False)
    exhb_habilidad_id = Column(Integer, ForeignKey("tbl_habilidad.hab_id"), nullable=False)

    habilidad = relationship("Habilidad", lazy="joined")


class ExperienciaLaboral(Base):
    __tablename__ = "tbl_experiencia_laboral"

    expl_id = Column(Integer, primary_key=True, index=True)
    expl_candidato_id = Column(Integer, ForeignKey("tbl_candidato.cand_id", ondelete="CASCADE"), nullable=False)
    expl_empresa = Column(String(150), nullable=False)
    expl_cargo_id = Column(Integer, ForeignKey("tbl_cargo.crgo_id"), nullable=True)
    expl_cargo_nombre_custom = Column(String(150), nullable=True)
    expl_fecha_inicio = Column(Date, nullable=False)
    expl_fecha_fin = Column(Date, nullable=True)
    expl_trabaja_actualmente = Column(Boolean, default=False)
    expl_descripcion_funciones = Column(Text, nullable=True)

    # Relaciones
    cargo = relationship("Cargo", lazy="joined")
    habilidades_asociadas = relationship("ExperienciaLaboralHabilidad", cascade="all, delete-orphan", lazy="selectin")


class EstudioCandidato(Base):
    __tablename__ = "tbl_estudio_candidato"

    estc_id = Column(Integer, primary_key=True, index=True)
    estc_candidato_id = Column(Integer, ForeignKey("tbl_candidato.cand_id", ondelete="CASCADE"), nullable=False)
    estc_institucion_id = Column(Integer, ForeignKey("tbl_institucion.inst_id"), nullable=True)
    estc_carrera_id = Column(Integer, ForeignKey("tbl_carrera.crra_id"), nullable=True)
    estc_nivel_estudio_id = Column(Integer, ForeignKey("tbl_nivel_estudio.nves_id"), nullable=True)
    estc_estado_estudio_id = Column(Integer, ForeignKey("tbl_estado_estudio.eces_id"), nullable=True)
    estc_fecha_inicio = Column(Date, nullable=True)
    estc_fecha_fin = Column(Date, nullable=True)

    # Relaciones
    institucion = relationship("Institucion", lazy="joined")
    carrera = relationship("Carrera", lazy="joined")
    nivel_estudio = relationship("NivelEstudio", lazy="joined")
    estado_estudio = relationship("EstadoEstudio", lazy="joined")


class Curso(Base):
    __tablename__ = "tbl_curso"

    crs_id = Column(Integer, primary_key=True, index=True)
    crs_candidato_id = Column(Integer, ForeignKey("tbl_candidato.cand_id", ondelete="CASCADE"), nullable=False)
    crs_nombre = Column(String(200), nullable=False)
    crs_institucion_id = Column(Integer, ForeignKey("tbl_institucion.inst_id"), nullable=True)
    crs_horas_duracion = Column(Integer, nullable=True)
    crs_fecha_obtencion = Column(Date, nullable=True)
    crs_tiene_certificado = Column(Boolean, default=False)

    institucion = relationship("Institucion", lazy="joined")


class Candidato(Base):
    __tablename__ = "tbl_candidato"

    cand_id = Column(Integer, primary_key=True, index=True)
    cand_rut_sin_dv = Column(Integer, unique=True, nullable=False, index=True)
    cand_dv = Column(String(1), nullable=False)
    cand_nombres = Column(String(100), nullable=False)
    cand_apellidos = Column(String(100), nullable=False)
    cand_email = Column(String(150), unique=True, nullable=False, index=True)
    cand_telefono = Column(String(20), nullable=True)
    cand_fecha_nacimiento = Column(Date, nullable=True)
    cand_resumen_profesional = Column(Text, nullable=True)
    cand_disponibilidad_id = Column(Integer, ForeignKey("tbl_disponibilidad.dsp_id"), nullable=True)

    # Relaciones maestras (Trayectoria y Perfil Anidado)
    disponibilidad = relationship("Disponibilidad", lazy="joined")
    direccion = relationship("DireccionCandidato", uselist=False, cascade="all, delete-orphan", lazy="joined")
    habilidades = relationship("CandidatoHabilidad", cascade="all, delete-orphan", lazy="selectin")
    experiencias = relationship("ExperienciaLaboral", cascade="all, delete-orphan", lazy="selectin")
    estudios = relationship("EstudioCandidato", cascade="all, delete-orphan", lazy="selectin")
    cursos = relationship("Curso", cascade="all, delete-orphan", lazy="selectin")