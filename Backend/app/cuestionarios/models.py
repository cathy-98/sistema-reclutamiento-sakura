from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Cuestionario(Base):
    __tablename__ = "tbl_cuestionario"

    cues_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cues_nombre: Mapped[str] = mapped_column(String(300), nullable=False)
    cues_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    cues_porcentaje_aprobacion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    cues_solicitud_id: Mapped[int] = mapped_column(Integer, nullable=False)


class Pregunta(Base):
    __tablename__ = "tbl_pregunta"

    preg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    preg_texto_pregunta: Mapped[str] = mapped_column(String(300), nullable=False)
    preg_habilidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    preg_nivel_habilidad_id: Mapped[int] = mapped_column(Integer, nullable=False)
    preg_fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class OpcionRespuesta(Base):
    __tablename__ = "tbl_opcion_respuesta"

    opcr_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opcr_pregunta_id: Mapped[int] = mapped_column(Integer, nullable=False)
    opcr_texto_opcion: Mapped[str] = mapped_column(String(300), nullable=False)
    opcr_es_correcta: Mapped[bool] = mapped_column(Boolean, nullable=False)


class PreguntaCuestionario(Base):
    __tablename__ = "tbl_pregunta_cuestionario"
    __table_args__ = (
        UniqueConstraint("prcu_cuestionario_id", "prcu_pregunta_id", name="uq_tbl_pregunta_cuestionario"),
    )

    prcu_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prcu_pregunta_id: Mapped[int] = mapped_column(Integer, nullable=False)
    prcu_cuestionario_id: Mapped[int] = mapped_column(Integer, nullable=False)


class CandidatoCuestionario(Base):
    __tablename__ = "tbl_candidato_cuestionario"
    __table_args__ = (
        UniqueConstraint(
            "cdcu_candidato_id", "cdcu_cuestionario_id",
            name="uq_tbl_candidato_cuestionario_candidato_cuestionario",
        ),
    )

    cdcu_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cdcu_candidato_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cdcu_cuestionario_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cdcu_fecha_asignacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cdcu_fecha_inicio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cdcu_fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cdcu_fecha_resolucion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cdcu_porcentaje_obtenido: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    cdcu_estado_cuestionario_candidato_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cdcu_tiempo_utilizado: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cdcu_permitir_reintento: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cdcu_aprobado: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


class RespuestaPregunta(Base):
    __tablename__ = "tbl_respuesta_pregunta"
    __table_args__ = (
        UniqueConstraint(
            "rspr_candidato_cuestionario_id", "rspr_pregunta_cuestionario_id",
            name="uq_tbl_respuesta_asignacion_pregunta",
        ),
    )

    rspr_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rspr_candidato_cuestionario_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rspr_es_correcta: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rspr_puntaje_obtenido: Mapped[int] = mapped_column(Integer, nullable=False)
    rspr_opcion_respuesta_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rspr_pregunta_cuestionario_id: Mapped[int] = mapped_column(Integer, nullable=False)
