# app/solicitudes/models.py
from datetime import datetime, time
from typing import Optional, List
from sqlalchemy import String, Integer, Boolean, DateTime, Time, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

#
class SolicitudHabilidad(Base):
    __tablename__ = "tbl_solicitud_habilidad"

    # 🔒 Constraints explícitos según el esquema DDL físico (base_inicial.sql)
    __table_args__ = (
        UniqueConstraint("solhb_solicitud_id", "solhb_habilidad_id", name="uq_tbl_solicitud_habilidad"),
        CheckConstraint("solhb_anios_experiencia_req >= 0", name="chk_tbl_solicitud_habilidad_anios"),
    )

    solhb_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    solhb_solicitud_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_solicitud.sol_id"), nullable=True)
    solhb_habilidad_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_habilidad.hab_id"), nullable=True)
    solhb_nivel_habilidad_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_nivel_habilidad.nvhb_id"), nullable=True)
    
    solhb_anios_experiencia_req: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 🎯 Cumplimiento de: Boolean, default, nullable
    solhb_es_excluyente: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)

    # 🔗 Relaciones ORM
    solicitud: Mapped[Optional["Solicitud"]] = relationship("Solicitud", back_populates="habilidades")
    habilidad: Mapped[Optional["Habilidad"]] = relationship("Habilidad")
    nivel_habilidad: Mapped[Optional["NivelHabilidad"]] = relationship("NivelHabilidad")

    def __repr__(self) -> str:
        return f"<SolicitudHabilidad(id={self.solhb_id}, habilidad_id={self.solhb_habilidad_id}, excluyente={self.solhb_es_excluyente})>"
# tabla solicitud  
class Solicitud(Base):
    __tablename__ = "tbl_solicitud"

    #  Constraints a nivel de modelo (Igual a la base de datos física)
    __table_args__ = (
        CheckConstraint("sol_codigo ~ '^SOL-[0-9]{3}$'", name="chk_tbl_solicitud_codigo"),
        CheckConstraint("sol_cantidad_vacantes > 0", name="chk_tbl_solicitud_vacantes"),
        CheckConstraint("sol_salario_min IS NULL OR sol_salario_max IS NULL OR sol_salario_min <= sol_salario_max", name="chk_tbl_solicitud_salarios"),
        CheckConstraint("sol_hora_inicio_jornada IS NULL OR sol_hora_fin_jornada IS NULL OR sol_hora_inicio_jornada < sol_hora_fin_jornada", name="chk_tbl_solicitud_horario"),
    )

    sol_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sol_codigo: Mapped[Optional[str]] = mapped_column(String(8), unique=True, nullable=True)
    sol_titulo: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    sol_descripcion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    sol_observacion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    
    sol_cantidad_vacantes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sol_salario_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sol_salario_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Fechas y Horarios
    sol_fecha_creacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sol_fecha_inicio_busqueda: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sol_fecha_cierre_busqueda: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sol_fecha_inicio_cliente: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sol_hora_inicio_jornada: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    sol_hora_fin_jornada: Mapped[Optional[time]] = mapped_column(Time, nullable=True)

    # Llaves Foráneas
    sol_cargo_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_cargo.crgo_id"), nullable=True)
    sol_prioridad_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_prioridad_solicitud.prsol_id"), nullable=True)
    sol_cliente_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_cliente.cli_id"), nullable=True)
    sol_usuario_creador_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_usuario.usr_id"), nullable=True)
    sol_usuario_asignado_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_usuario.usr_id"), nullable=True)
    sol_modalidad_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_modalidad.mdld_id"), nullable=True)
    sol_estado_solicitud_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_estado_solicitud.essl_id"), nullable=True)
    sol_tipo_contrato_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tbl_tipo_contrato.tpct_id"), nullable=True)

    # Relaciones ORM
    habilidades: Mapped[List["SolicitudHabilidad"]] = relationship(
        "SolicitudHabilidad", back_populates="solicitud", cascade="all, delete-orphan"
    )
    cliente: Mapped[Optional["Cliente"]] = relationship("Cliente")
    usuario_creador: Mapped[Optional["Usuario"]] = relationship("Usuario", foreign_keys=[sol_usuario_creador_id])
    usuario_asignado: Mapped[Optional["Usuario"]] = relationship("Usuario", foreign_keys=[sol_usuario_asignado_id])
    estado: Mapped[Optional["EstadoSolicitud"]] = relationship("EstadoSolicitud")
    prioridad: Mapped[Optional["PrioridadSolicitud"]] = relationship("PrioridadSolicitud")

    def __repr__(self) -> str:
        return f"<Solicitud(id={self.sol_id}, codigo='{self.sol_codigo}', titulo='{self.sol_titulo}')>"
    
    # LAS PROPIEDADES (Al final de la clase Solicitud)
    @property
    def habilidades_excluyentes(self) -> List["SolicitudHabilidad"]:
        """Retorna únicamente los requisitos técnicos obligatorios (excluyentes)."""
        return [h for h in self.habilidades if h.solhb_es_excluyente is True]

    @property
    def habilidades_deseables(self) -> List["SolicitudHabilidad"]:
        """Retorna los requisitos técnicos opcionales (no excluyentes)."""
        return [h for h in self.habilidades if not h.solhb_es_excluyente]