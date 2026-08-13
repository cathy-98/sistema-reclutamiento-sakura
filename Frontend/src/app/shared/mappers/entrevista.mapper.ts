import {
  CitaEntrevistaApi,
  CitaEntrevistaPayload,
  EntrevistaPayload,
  EntrevistaResumen,
} from '../../services/entrevistas.service';

export interface EntrevistaResumenCatalogos {
  estadosPorId: Map<number, string>;
  tiposPorId: Map<number, string>;
  solicitudesPorId: Map<number, string>;
  candidatosPorSolicitudCandidatoId: Map<number, string>;
  cargosPorSolicitudCandidatoId: Map<number, string>;
  entrevistadoresPorCitaId: Map<number, string>;
}

// Mapeo API -> pantalla: traduce ctev_* mas relaciones necesarias para agenda/listado.
export function mapearEntrevistaResumen(
  entrevista: CitaEntrevistaApi,
  catalogos: EntrevistaResumenCatalogos,
): EntrevistaResumen {
  const inicio = separarFechaHora(entrevista.ctev_fecha_hora_inicio);
  const fin = separarFechaHora(entrevista.ctev_fecha_hora_fin);
  const solicitudCandidatoId = entrevista.ctev_solicitud_candidato_id;

  return {
    id: String(entrevista.ctev_id),
    idSolicitud: obtenerNombre(catalogos.solicitudesPorId, solicitudCandidatoId, 'Solicitud pendiente'),
    candidato: obtenerNombre(catalogos.candidatosPorSolicitudCandidatoId, solicitudCandidatoId, 'Candidato pendiente'),
    estado: obtenerNombre(catalogos.estadosPorId, entrevista.ctev_estado_entrevista_id, 'Sin estado'),
    tipo: obtenerNombre(catalogos.tiposPorId, entrevista.ctev_tipo_entrevista_id, 'Sin tipo'),
    asunto: entrevista.ctev_titulo_evento ?? 'Entrevista',
    cargo: obtenerNombre(catalogos.cargosPorSolicitudCandidatoId, solicitudCandidatoId, 'Cargo pendiente'),
    fecha: inicio.fecha,
    horaInicio: inicio.hora,
    horaFin: fin.hora,
    entrevistador: obtenerNombre(catalogos.entrevistadoresPorCitaId, entrevista.ctev_id, 'Sin entrevistador'),
    linkReunion: entrevista.ctev_enlace_reunion ?? undefined,
    observacion: entrevista.ctev_comentarios_convocatoria ?? undefined,
  };
}

// Mapeo pantalla -> API: arma timestamps ctev_* desde fecha/hora del modal.
export function mapearEntrevistaPayload(
  payload: EntrevistaPayload,
  ids: {
    solicitudCandidatoId: number;
    tipoEntrevistaId: number;
    estadoEntrevistaId?: number | null;
  },
): CitaEntrevistaPayload {
  return {
    ctev_solicitud_candidato_id: ids.solicitudCandidatoId,
    ctev_tipo_entrevista_id: ids.tipoEntrevistaId,
    ctev_estado_entrevista_id: ids.estadoEntrevistaId ?? null,
    ctev_fecha_hora_inicio: unirFechaHora(payload.fecha, payload.horaInicio),
    ctev_fecha_hora_fin: unirFechaHora(payload.fecha, payload.horaFin),
    ctev_enlace_reunion: payload.linkReunion || null,
    ctev_comentarios_convocatoria: payload.observacion || null,
    ctev_titulo_evento: payload.asunto,
  };
}

function obtenerNombre(catalogo: Map<number, string>, id: number | null | undefined, fallback: string) {
  return id == null ? fallback : catalogo.get(id) || fallback;
}

function separarFechaHora(valor?: string | null) {
  if (!valor) {
    return { fecha: 'Sin fecha', hora: 'Sin hora' };
  }

  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) {
    const [soloFecha, soloHora = 'Sin hora'] = valor.split('T');
    return { fecha: soloFecha || 'Sin fecha', hora: soloHora.slice(0, 5) || 'Sin hora' };
  }

  return {
    fecha: new Intl.DateTimeFormat('es-CL').format(fecha),
    hora: fecha.toTimeString().slice(0, 5),
  };
}

function unirFechaHora(fecha: string, hora: string) {
  return `${fecha}T${hora}:00`;
}
