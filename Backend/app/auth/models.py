from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PasswordResetToken(Base):
    """Token de recuperación de contraseña almacenado únicamente como hash SHA-256."""

    __tablename__ = "tbl_password_reset_token"
    __table_args__ = (
        Index("ix_password_reset_usuario", "prst_usuario_id"),
        Index("ix_password_reset_expiracion", "prst_fecha_expiracion"),
    )

    prst_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    prst_usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tbl_usuario.usr_id"),
        nullable=False,
    )
    prst_token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )
    prst_fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    prst_fecha_expiracion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    prst_fecha_uso: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    prst_fecha_revocacion: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    usuario = relationship(
        "Usuario",
        lazy="joined",
    )
