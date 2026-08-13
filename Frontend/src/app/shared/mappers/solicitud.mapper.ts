import {
  EstadoSolicitud,
  PrioridadSolicitud,
  SolicitudApi,
  SolicitudResumen,
} from '../models/solicitud.model';

export interface SolicitudResumenCatalogos {
  cargosPorId: Map<number, string>;
  clientesPorId: Map<number, string>;
  usuariosPorId: Map<number, string>;
  prioridadesPorId: Map<number, string>;
  estadosPorId: Map<number, string>;
}

export const camposSolicitudResumen = {
  id: 'sol_id',
  codigo: 'sol_codigo',
  nombre: 'sol_titulo',
  cargo: 'sol_cargo_id',
  vacantes: 'sol_cantidad_vacantes',
  responsable: 'sol_usuario_asignado_id',
  prioridad: 'sol_prioridad_id',
  estado: 'sol_estado_solicitud_id',
  observacion: 'sol_observacion',
} as const;

// Mapeo API -> pantalla: traduce campos sol_* a nombres usados por la tabla de solicitudes.
export function mapearSolicitudResumen(
  solicitud: SolicitudApi,
  catalogos: SolicitudResumenCatalogos,
): SolicitudResumen {
  return {
    id: String(solicitud.sol_id),
    codigo: solicitud.sol_codigo || `SOL-${String(solicitud.sol_id).padStart(6, '0')}`,
    nombre: solicitud.sol_titulo || 'Sin nombre',
    cliente: obtenerNombre(catalogos.clientesPorId, solicitud.sol_cliente_id, 'Cliente pendiente'),
    cargo: obtenerNombre(catalogos.cargosPorId, solicitud.sol_cargo_id, 'Cargo pendiente'),
    vacantes: solicitud.sol_cantidad_vacantes ?? 0,
    responsable: obtenerNombre(catalogos.usuariosPorId, solicitud.sol_usuario_asignado_id, 'Sin asignar'),
    seleccion: formatearRangoFechas(
      solicitud.sol_fecha_inicio_busqueda,
      solicitud.sol_fecha_cierre_busqueda,
    ),
    inicioEmpleo: formatearFecha(solicitud.sol_fecha_inicio_cliente),
    prioridad: obtenerNombre(
      catalogos.prioridadesPorId,
      solicitud.sol_prioridad_id,
      'Sin prioridad',
    ) as PrioridadSolicitud,
    estado: obtenerNombre(catalogos.estadosPorId, solicitud.sol_estado_solicitud_id, 'Sin estado'),
    observacion: solicitud.sol_observacion || 'Sin observación',
  };
}

function obtenerNombre(catalogo: Map<number, string>, id: number | null | undefined, fallback: string) {
  if (id == null) {
    return fallback;
  }

  return catalogo.get(id) || fallback;
}

function formatearRangoFechas(inicio?: string | null, fin?: string | null) {
  const inicioFormateado = formatearFecha(inicio);
  const finFormateado = formatearFecha(fin);

  if (inicioFormateado === 'Sin fecha' && finFormateado === 'Sin fecha') {
    return 'Sin fechas';
  }

  return `${inicioFormateado} - ${finFormateado}`;
}

function formatearFecha(fecha?: string | null) {
  if (!fecha) {
    return 'Sin fecha';
  }

  const fechaNormalizada = new Date(fecha);

  if (Number.isNaN(fechaNormalizada.getTime())) {
    return 'Sin fecha';
  }

  return new Intl.DateTimeFormat('es-CL').format(fechaNormalizada);
}
