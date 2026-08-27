import {
  EstadoSolicitud,
  PrioridadSolicitud,
  SolicitudApi,
  SolicitudResumen,
} from '../models/solicitud.model';

export interface SolicitudResumenCatalogos {
  cargosPorId: Map<number, string>;
  clientesPorId: Map<number, string>;
  empresasPorClienteId: Map<number, string>;
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
  descripcion: 'sol_descripcion',
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
    empresaCliente: obtenerNombre(catalogos.empresasPorClienteId, solicitud.sol_cliente_id, 'Sin empresa cliente'),
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
    estado: presentarEstadoSolicitud(
      obtenerNombre(catalogos.estadosPorId, solicitud.sol_estado_solicitud_id, 'Sin estado'),
    ),
    descripcion: obtenerTextoSolicitud(solicitud.sol_descripcion, 'Sin descripción'),
  };
}

export function presentarEstadoSolicitud(estado: string) {
  const estadoNormalizado = estado.trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  if (estadoNormalizado === 'en curso' || estadoNormalizado === 'en_curso') {
    return 'En publicación';
  }

  return estado;
}

function obtenerTextoSolicitud(...valores: Array<string | null | undefined>) {
  const texto = valores
    .map((valor) => valor?.trim())
    .find((valor) => Boolean(valor));

  return texto ?? 'Sin descripción';
}

function obtenerNombre(catalogo: Map<number, string>, id: number | null | undefined, fallback: string) {
  const idNormalizado = normalizarId(id);

  if (idNormalizado == null) {
    return fallback;
  }

  return catalogo.get(idNormalizado) || fallback;
}

function normalizarId(id: number | string | null | undefined) {
  if (id == null || id === '') {
    return null;
  }

  const numero = Number(id);
  return Number.isFinite(numero) ? numero : null;
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
