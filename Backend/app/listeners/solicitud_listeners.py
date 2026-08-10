from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import event, inspect
from app.solicitudes.models import Solicitud, HistorialSolicitud

# Configuración de zona horaria local (Chile / UTC-4)
TZ_CHILE = ZoneInfo("America/Santiago")


def obtener_fecha_local():
    """Retorna la hora actual ajustada a la zona horaria local de Chile."""
    return datetime.now(TZ_CHILE).replace(tzinfo=None)


@event.listens_for(Solicitud, "after_insert")
def audit_creacion_solicitud(mapper, connection, target: Solicitud):
    """
    Escucha la inserción de una nueva vacante e inserta su estado inicial en tbl_historial_solicitud.
    """
    usuario_id = getattr(
        target, 
        "sol_usuario_creador_id", 
        1
    )

    comentario_inicial = getattr(
        target, 
        "sol_observacion", 
        "Creación e ingreso inicial de la solicitud"
    ) or "Creación e ingreso inicial de la solicitud"

    connection.execute(
        HistorialSolicitud.__table__.insert().values(
            hsol_solicitud_id=target.sol_id,
            hsol_estado_anterior_id=None,
            hsol_estado_actual_id=target.sol_estado_solicitud_id,
            hsol_fecha_cambio=obtener_fecha_local(),
            hsol_usuario_id=usuario_id,
            hsol_comentario=comentario_inicial
        )
    )


@event.listens_for(Solicitud, "before_update")
def audit_cambio_estado_solicitud(mapper, connection, target: Solicitud):
    """
    Escucha las actualizaciones de la tabla tbl_solicitud antes de enviar los cambios a la base de datos.
    Si cambia sol_estado_solicitud_id, inserta automáticamente la traza en tbl_historial_solicitud.
    """
    state = inspect(target)
    # Inspeccionar el historial del atributo real sol_estado_solicitud_id
    history = state.get_history("sol_estado_solicitud_id", True)

    if history.has_changes():
        estado_anterior_id = history.deleted[0] if history.deleted else None
        estado_actual_id = history.added[0] if history.added else target.sol_estado_solicitud_id

        # Omitir si no hubo un cambio real de valor o si el estado previo no existe
        if estado_anterior_id is None or estado_anterior_id == estado_actual_id:
            return

        # Capturar la observación dinámica inyectada desde la API o usar un mensaje por defecto
        comentario_final = getattr(
            target, 
            "_observacion", 
            f"Cambio automático de estado: {estado_anterior_id} -> {estado_actual_id}"
        )

		
	 
        # Si el cambio viene desde la Web/API se usará 'sol_usuario_modificador_id'.
        # Si no se identifica un usuario (ej. procesos automáticos internos), por defecto se asigna 1 (Usuario Sistema/Admin)
        usuario_id = getattr(target, "sol_usuario_modificador_id", None) or 1
   

        # Insertar registro inmutable de auditoría
        connection.execute(
            HistorialSolicitud.__table__.insert().values(
                hsol_solicitud_id=target.sol_id,
                hsol_estado_anterior_id=estado_anterior_id,
                hsol_estado_actual_id=estado_actual_id,
                hsol_fecha_cambio=obtener_fecha_local(),
                hsol_usuario_id=usuario_id,
                hsol_comentario=comentario_final
            )
        )