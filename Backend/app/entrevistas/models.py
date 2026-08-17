from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CitaEntrevista(Base):
    __tablename__ = "tbl_cita_entrevista"
    __table_args__ = (
        CheckConstraint(
            "ctev_fecha_hora_fin IS NULL OR ctev_fecha_hora_inicio < ctev_fecha_hora_fin",
            name="chk_tbl_cita_entrevista_fechas",
        ),
        CheckConstraint(
            "ctev_enlace_reunion IS NULL OR length(trim(ctev_enlace_reunion)) > 0",
            name="chk_tbl_cita_entrevista_enlace",
        ),
        CheckConstraint(
            "trim(ctev_titulo_evento) <> ''",
            name="chk_tbl_cita_entrevista_titulo",
        ),
    )

    ctev_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ctev_solicitud_candidato_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_solicitud_candidato.slcd_id"), nullable=False
    )
    # Campo legado. M5 usa tbl_cita_tipo_entrevista como fuente de verdad y
    # conserva aquí el primer tipo para compatibilidad con frontend/datos previos.
    ctev_tipo_entrevista_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tbl_tipo_entrevista.tpet_id"), nullable=True
    )
    ctev_estado_entrevista_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_estado_entrevista.esev_id"), nullable=False
    )
    ctev_fecha_hora_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ctev_fecha_hora_fin: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ctev_fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ctev_enlace_reunion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ctev_comentarios_convocatoria: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ctev_titulo_evento: Mapped[str] = mapped_column(String(300), nullable=False)

    # Campos M5 añadidos por migración 006.
    ctev_usuario_creador_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tbl_usuario.usr_id"), nullable=True
    )
    ctev_fecha_actualizacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ctev_motivo_estado: Mapped[str | None] = mapped_column(String(300), nullable=True)

    tipos: Mapped[list["CitaTipoEntrevista"]] = relationship(
        "CitaTipoEntrevista", cascade="all, delete-orphan", lazy="selectin"
    )
    entrevistadores: Mapped[list["UsuarioCitaEntrevista"]] = relationship(
        "UsuarioCitaEntrevista", cascade="all, delete-orphan", lazy="selectin"
    )
    evaluaciones: Mapped[list["EvaluacionEntrevista"]] = relationship(
        "EvaluacionEntrevista", cascade="all, delete-orphan", lazy="selectin"
    )


class CitaTipoEntrevista(Base):
    __tablename__ = "tbl_cita_tipo_entrevista"

    cten_tipo_entrevista_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_tipo_entrevista.tpet_id"), primary_key=True
    )
    cten_cita_entrevista_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_cita_entrevista.ctev_id"), primary_key=True
    )


class UsuarioCitaEntrevista(Base):
    __tablename__ = "tbl_usuario_cita_entrevista"

    usrce_cita_entrevista_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_cita_entrevista.ctev_id"), primary_key=True
    )
    usrce_usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_usuario.usr_id"), primary_key=True
    )
    usrce_tipo_entrevista_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_tipo_entrevista.tpet_id"), primary_key=True
    )


class EvaluacionEntrevista(Base):
    __tablename__ = "tbl_evaluacion_entrevista"
    __table_args__ = (
        CheckConstraint(
            "even_observacion IS NULL OR length(trim(even_observacion)) > 0",
            name="chk_tbl_evaluacion_entrevista_observacion",
        ),
    )

    even_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    even_nombre_resultado_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_nombre_resultado.nore_id"), nullable=False
    )
    even_observacion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    even_cita_entrevista_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_cita_entrevista.ctev_id"), nullable=False
    )
    # Nullable únicamente para permitir registros históricos previos a M5.
    # Toda evaluación creada por M5 siempre informa ambos campos.
    even_usuario_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tbl_usuario.usr_id"), nullable=True
    )
    even_tipo_entrevista_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tbl_tipo_entrevista.tpet_id"), nullable=True
    )
    even_fecha_creacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    even_fecha_actualizacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
