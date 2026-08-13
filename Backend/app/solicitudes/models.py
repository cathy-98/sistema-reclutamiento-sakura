from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Time

from app.database import Base


class SolicitudHabilidad(Base):
    __tablename__ = "tbl_solicitud_habilidad"
    __table_args__ = (
        UniqueConstraint(
            "solhb_solicitud_id",
            "solhb_habilidad_id",
            name="uq_tbl_solicitud_habilidad",
        ),
        CheckConstraint(
            "solhb_anios_experiencia_req >= 0",
            name="chk_tbl_solicitud_habilidad_anios",
        ),
    )

    solhb_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    solhb_solicitud_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_solicitud.sol_id"),
        nullable=True,
    )
    solhb_habilidad_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_habilidad.hab_id"),
        nullable=True,
    )
    solhb_nivel_habilidad_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_nivel_habilidad.nvhb_id"),
        nullable=True,
    )
    solhb_anios_experiencia_req: Mapped[int | None] = mapped_column(Integer, nullable=True)
    solhb_es_excluyente: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)

    solicitud: Mapped["Solicitud | None"] = relationship(
        "Solicitud",
        back_populates="habilidades",
    )
    habilidad: Mapped["Habilidad | None"] = relationship("Habilidad")
    nivel_habilidad: Mapped["NivelHabilidad | None"] = relationship("NivelHabilidad")


class Solicitud(Base):
    __tablename__ = "tbl_solicitud"
    __table_args__ = (
        CheckConstraint(
            "sol_codigo ~ '^SOL-[0-9]{6}$'",
            name="chk_tbl_solicitud_codigo",
        ).ddl_if(dialect="postgresql"),
        CheckConstraint(
            "sol_cantidad_vacantes > 0",
            name="chk_tbl_solicitud_vacantes",
        ),
        CheckConstraint(
            "sol_salario_min IS NULL OR sol_salario_max IS NULL OR sol_salario_min <= sol_salario_max",
            name="chk_tbl_solicitud_salarios",
        ),
        CheckConstraint(
            "sol_hora_inicio_jornada IS NULL OR sol_hora_fin_jornada IS NULL OR sol_hora_inicio_jornada < sol_hora_fin_jornada",
            name="chk_tbl_solicitud_horario",
        ),
    )

    sol_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sol_codigo: Mapped[str | None] = mapped_column(String(10), unique=True, nullable=True)
    sol_titulo: Mapped[str | None] = mapped_column(String(300), nullable=True)
    sol_descripcion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    sol_observacion: Mapped[str | None] = mapped_column(String(300), nullable=True)

    sol_cantidad_vacantes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sol_salario_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sol_salario_max: Mapped[int | None] = mapped_column(Integer, nullable=True)

    sol_fecha_creacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sol_fecha_inicio_busqueda: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sol_fecha_cierre_busqueda: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sol_fecha_inicio_cliente: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sol_hora_inicio_jornada: Mapped[time | None] = mapped_column(Time, nullable=True)
    sol_hora_fin_jornada: Mapped[time | None] = mapped_column(Time, nullable=True)

    sol_cargo_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_cargo.crgo_id"),
        nullable=True,
    )
    sol_prioridad_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_prioridad_solicitud.prsol_id"),
        nullable=True,
    )
    sol_cliente_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_cliente.cli_id"),
        nullable=True,
    )
    sol_usuario_creador_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_usuario.usr_id"),
        nullable=True,
    )
    sol_usuario_asignado_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_usuario.usr_id"),
        nullable=True,
    )
    sol_modalidad_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_modalidad.mdld_id"),
        nullable=True,
    )
    sol_estado_solicitud_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_estado_solicitud.essl_id"),
        nullable=True,
    )
    sol_tipo_contrato_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_tipo_contrato.tpct_id"),
        nullable=True,
    )

    habilidades: Mapped[list[SolicitudHabilidad]] = relationship(
        "SolicitudHabilidad",
        back_populates="solicitud",
        cascade="all, delete-orphan",
    )
    historial: Mapped[list["HistorialSolicitud"]] = relationship(
        "HistorialSolicitud",
        back_populates="solicitud",
        order_by="HistorialSolicitud.hsol_fecha_cambio",
    )
    cliente: Mapped["Cliente | None"] = relationship("Cliente")
    usuario_creador: Mapped["Usuario | None"] = relationship(
        "Usuario",
        foreign_keys=[sol_usuario_creador_id],
    )
    usuario_asignado: Mapped["Usuario | None"] = relationship(
        "Usuario",
        foreign_keys=[sol_usuario_asignado_id],
    )
    estado: Mapped["EstadoSolicitud | None"] = relationship("EstadoSolicitud")
    prioridad: Mapped["PrioridadSolicitud | None"] = relationship("PrioridadSolicitud")
    cargo: Mapped["Cargo | None"] = relationship("Cargo")
    modalidad: Mapped["Modalidad | None"] = relationship("Modalidad")
    tipo_contrato: Mapped["TipoContrato | None"] = relationship("TipoContrato")

    @property
    def habilidades_excluyentes(self) -> list[SolicitudHabilidad]:
        return [h for h in self.habilidades if h.solhb_es_excluyente is True]

    @property
    def habilidades_deseables(self) -> list[SolicitudHabilidad]:
        return [h for h in self.habilidades if not h.solhb_es_excluyente]


class HistorialSolicitud(Base):
    __tablename__ = "tbl_historial_solicitud"
    __table_args__ = (
        CheckConstraint(
            "hsol_comentario IS NULL OR TRIM(hsol_comentario) <> ''",
            name="chk_tbl_historial_solicitud_comentario_vacio",
        ),
        CheckConstraint(
            "hsol_estado_anterior_id IS NULL OR hsol_estado_actual_id IS NULL OR hsol_estado_anterior_id <> hsol_estado_actual_id",
            name="chk_tbl_historial_solicitud_estados_diferentes",
        ),
    )

    hsol_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hsol_solicitud_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_solicitud.sol_id"),
        nullable=True,
    )
    hsol_estado_anterior_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_estado_solicitud.essl_id"),
        nullable=True,
    )
    hsol_estado_actual_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_estado_solicitud.essl_id"),
        nullable=True,
    )
    hsol_fecha_cambio: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    hsol_usuario_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("tbl_usuario.usr_id"),
        nullable=True,
    )
    hsol_comentario: Mapped[str | None] = mapped_column(String(300), nullable=True)

    solicitud: Mapped[Solicitud | None] = relationship("Solicitud", back_populates="historial")
    usuario: Mapped["Usuario | None"] = relationship("Usuario")


# Módulo 3: relación física completa entre solicitud y candidato.
                                                                                
                                                                       
class SolicitudCandidato(Base):
    __tablename__ = "tbl_solicitud_candidato"

    slcd_id = Column(Integer, primary_key=True, index=True)
                                                                           
    slcd_candidato_id = Column(Integer, ForeignKey("tbl_candidato.cand_id"))
    slcd_solicitud_id = Column(Integer, ForeignKey("tbl_solicitud.sol_id"))
    slcd_pretension_renta = Column(Integer)
    slcd_puntaje_compatibilidad = Column(Numeric(5, 2))
    slcd_estado_solicitud_candidato_id = Column(
        Integer, ForeignKey("tbl_estado_solicitud_candidato.essc_id")
    )
    slcd_fecha_postulacion = Column(DateTime)
    slcd_observaciones = Column(String(300))
    slcd_motivo_rechazo_id = Column(Integer, ForeignKey("tbl_motivo_rechazo.mtrc_id"))
