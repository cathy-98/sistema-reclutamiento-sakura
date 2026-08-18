from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.catalogos.models import CategoriaHabilidad, Idioma

                               
                                             

                                                                                       
                                                                                      
                                                                                    


                   
                                

                                                                                       
                                                                                      


class CandidatoIdioma(Base):
    __tablename__ = "tbl_candidato_idioma"
    __table_args__ = (
        UniqueConstraint("cdio_candidato_id", "cdio_idioma_id", name="uq_tbl_candidato_idioma"),
    )

    cdio_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cdio_candidato_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_candidato.cand_id"), nullable=False)
    cdio_idioma_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_idioma.idio_id"), nullable=False)
    cdio_nivel: Mapped[str] = mapped_column(String(30), nullable=False)


class DocumentoReporteCandidato(Base):
    __tablename__ = "tbl_documento_reporte_candidato"

    drcp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drcp_solicitud_candidato_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_solicitud_candidato.slcd_id"), nullable=False, index=True
    )
    drcp_tipo_documento: Mapped[str] = mapped_column(String(30), nullable=False)
    drcp_nombre_archivo: Mapped[str] = mapped_column(String(255), nullable=False)
    drcp_ruta_archivo: Mapped[str] = mapped_column(String(1000), nullable=False)
    drcp_fecha_generacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    drcp_usuario_generador_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_usuario.usr_id"), nullable=False)
    drcp_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    drcp_snapshot_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class PlantillaNotificacion(Base):
    __tablename__ = "tbl_plantilla_notificacion"

    plnt_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plnt_tipo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    plnt_nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    plnt_asunto: Mapped[str] = mapped_column(String(300), nullable=False)
    plnt_cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    plnt_activa: Mapped[bool] = mapped_column(nullable=False, default=True)
    plnt_fecha_actualizacion: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    plnt_usuario_actualizacion_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("tbl_usuario.usr_id"), nullable=True)


class NotificacionReclutamiento(Base):
    __tablename__ = "tbl_notificacion_reclutamiento"

    ntfr_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ntfr_solicitud_candidato_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tbl_solicitud_candidato.slcd_id"), nullable=False, index=True
    )
    ntfr_tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    ntfr_destinatario: Mapped[str] = mapped_column(String(2000), nullable=False)
    ntfr_cc: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    ntfr_asunto: Mapped[str] = mapped_column(String(300), nullable=False)
    ntfr_cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    ntfr_estado: Mapped[str] = mapped_column(String(20), nullable=False)
    ntfr_usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_usuario.usr_id"), nullable=False)
    ntfr_fecha_creacion: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ntfr_fecha_envio: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ntfr_error: Mapped[str | None] = mapped_column(Text, nullable=True)
