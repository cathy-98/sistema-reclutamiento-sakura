from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import event, inspect

from app.solicitudes.models import HistorialSolicitud, Solicitud


TZ_CHILE = ZoneInfo("America/Santiago")


def obtener_fecha_local() -> datetime:
    return datetime.now(TZ_CHILE).replace(tzinfo=None)


@event.listens_for(Solicitud, "after_insert")
def audit_creacion_solicitud(mapper, connection, target: Solicitud):
    comentario = target.sol_observacion or "Creación e ingreso inicial de la solicitud"
    connection.execute(
        HistorialSolicitud.__table__.insert().values(
            hsol_solicitud_id=target.sol_id,
            hsol_estado_anterior_id=None,
            hsol_estado_actual_id=target.sol_estado_solicitud_id,
            hsol_fecha_cambio=obtener_fecha_local(),
            hsol_usuario_id=target.sol_usuario_creador_id,
            hsol_comentario=comentario,
        )
    )


@event.listens_for(Solicitud, "before_update")
def audit_cambio_estado_solicitud(mapper, connection, target: Solicitud):
    state = inspect(target)
    history = state.attrs.sol_estado_solicitud_id.history
    if not history.has_changes():
        return

    anterior = history.deleted[0] if history.deleted else None
    actual = history.added[0] if history.added else target.sol_estado_solicitud_id
    if anterior is None or anterior == actual:
        return

    usuario_id = getattr(target, "_audit_user_id", None)
    comentario = getattr(
        target,
        "_audit_comment",
        f"Cambio de estado: {anterior} -> {actual}",
    )

    connection.execute(
        HistorialSolicitud.__table__.insert().values(
            hsol_solicitud_id=target.sol_id,
            hsol_estado_anterior_id=anterior,
            hsol_estado_actual_id=actual,
            hsol_fecha_cambio=obtener_fecha_local(),
            hsol_usuario_id=usuario_id,
            hsol_comentario=comentario,
        )
    )
