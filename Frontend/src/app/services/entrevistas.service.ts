import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, throwError } from 'rxjs';

export type EstadoEntrevista = string;
export type TipoEntrevista = string;

// Modelo físico/API esperado para citas de entrevista.
// Backend/BD usa ctev_*; este tipo se debe usar cuando exista el endpoint real.
export interface CitaEntrevistaApi {
  ctev_id: number;
  ctev_solicitud_candidato_id: number | null;
  ctev_tipo_entrevista_id: number | null;
  ctev_estado_entrevista_id: number | null;
  ctev_fecha_hora_inicio: string | null;
  ctev_fecha_hora_fin: string | null;
  ctev_fecha_creacion?: string | null;
  ctev_enlace_reunion?: string | null;
  ctev_comentarios_convocatoria?: string | null;
  ctev_titulo_evento?: string | null;
}

export interface CitaEntrevistaPayload {
  ctev_solicitud_candidato_id: number;
  ctev_tipo_entrevista_id: number;
  ctev_estado_entrevista_id?: number | null;
  ctev_fecha_hora_inicio: string;
  ctev_fecha_hora_fin: string;
  ctev_enlace_reunion?: string | null;
  ctev_comentarios_convocatoria?: string | null;
  ctev_titulo_evento: string;
}

export interface EntrevistaApi {
  entrevista_id: number;
  solicitud_candidato_id: number;
  solicitud_id: number;
  solicitud_codigo?: string | null;
  candidato_id?: number;
  candidato_nombre?: string;
  candidato_email?: string;
  estado_id?: number;
  estado_nombre?: string;
  estado?: string;
  fecha_hora_inicio: string;
  fecha_hora_fin: string;
  fecha_creacion?: string;
  fecha_actualizacion?: string | null;
  titulo_evento: string;
  enlace_reunion?: string | null;
  comentarios_convocatoria?: string | null;
  motivo_estado?: string | null;
  usuario_creador_id?: number | null;
  tipos?: {
    tipo_entrevista_id: number;
    nombre: string;
    descripcion?: string | null;
    entrevistadores?: {
      usuario_id: number;
      nombres: string;
      apellido_paterno: string;
      email: string;
    }[];
  }[];
  evaluaciones?: EvaluacionEntrevistaApi[];
}

export interface EvaluacionEntrevistaApi {
  evaluacion_id: number;
  entrevista_id: number;
  tipo_entrevista_id?: number | null;
  tipo_entrevista_nombre?: string | null;
  usuario_id?: number | null;
  usuario_nombre?: string | null;
  resultado_id: number;
  resultado_nombre: string;
  observacion?: string | null;
  fecha_creacion?: string | null;
  fecha_actualizacion?: string | null;
}

// Modelo de pantalla: nombres legibles para tablas, filtros y formularios.
export interface EntrevistaResumen {
  id: string;
  solicitudCandidatoId?: number;
  candidatoId?: number;
  idSolicitud: string;
  candidato: string;
  candidatoCorreo?: string;
  estado: EstadoEntrevista;
  tipo: TipoEntrevista;
  resultadoEntrevista: string;
  asunto: string;
  cargo: string;
  fecha: string;
  horaInicio: string;
  horaFin: string;
  entrevistador: string;
  linkReunion?: string;
  observacion?: string;
}

export interface EntrevistaPayload {
  solicitudCandidatoId?: number;
  solicitudesCandidatosIds?: number[];
  tipoEntrevistaId?: number;
  entrevistadorIds?: number[];
  idSolicitud: string;
  candidato: string;
  tipo: TipoEntrevista;
  asunto: string;
  cargo: string;
  fecha: string;
  horaInicio: string;
  horaFin: string;
  entrevistador: string;
  linkReunion?: string;
  observacion?: string;
}

interface EntrevistaCreateRequest {
  solicitud_candidato_id: number;
  fecha_hora_inicio: string;
  fecha_hora_fin: string;
  titulo_evento: string;
  enlace_reunion?: string | null;
  comentarios_convocatoria?: string | null;
  tipos: {
    tipo_entrevista_id: number;
    usuarios_ids: number[];
  }[];
}

interface EntrevistaMasivaCreateRequest extends Omit<EntrevistaCreateRequest, 'solicitud_candidato_id'> {
  solicitudes_candidatos_ids: number[];
}

@Injectable({ providedIn: 'root' })
export class EntrevistasService {
  private readonly apiUrl = '/api';

  constructor(private http: HttpClient) {}

  listar() {
    // M5: listado real de entrevistas. El backend incluye tipos asignados y evaluaciones
    // con tipo_entrevista_nombre / resultado_nombre para ver el resultado por área.
    return this.http.get<EntrevistaApi[]>(`${this.apiUrl}/entrevistas`).pipe(
      map((entrevistas) => entrevistas.map((entrevista) => this.mapearResumen(entrevista))),
    );
  }

  listarEvaluaciones(entrevistaId: string | number) {
    return this.http.get<EvaluacionEntrevistaApi[]>(
      `${this.apiUrl}/entrevistas/${entrevistaId}/evaluaciones`,
    );
  }

  listarPorCandidato(candidatoId: string) {
    return this.http.get<EntrevistaApi[]>(
      `${this.apiUrl}/candidatos/${candidatoId}/entrevistas`,
    );
  }

  listarMisEntrevistas() {
    return this.http.get<EntrevistaApi[]>(
      `${this.apiUrl}/candidatos/me/entrevistas`,
    );
  }

  crear(payload: EntrevistaPayload) {
    const body = this.crearPayloadApi(payload);

    if (!body) {
      return throwError(() => new Error('Faltan IDs reales de postulación, tipo de entrevista o entrevistador.'));
    }

    return this.http.post<EntrevistaApi>(`${this.apiUrl}/entrevistas`, body).pipe(
      map((entrevista) => this.mapearResumen(entrevista)),
    );
  }

  crearMasiva(payloads: EntrevistaPayload[]) {
    const primero = payloads[0];
    const solicitudesCandidatosIds = payloads
      .map((payload) => payload.solicitudCandidatoId)
      .filter((id): id is number => typeof id === 'number' && id > 0);

    if (!primero || solicitudesCandidatosIds.length !== payloads.length) {
      return throwError(() => new Error('Faltan IDs reales de postulación para la agenda masiva.'));
    }

    const base = this.crearPayloadApi(primero);

    if (!base) {
      return throwError(() => new Error('Faltan IDs reales de tipo de entrevista o entrevistador.'));
    }

    const body: EntrevistaMasivaCreateRequest = {
      solicitudes_candidatos_ids: solicitudesCandidatosIds,
      fecha_hora_inicio: base.fecha_hora_inicio,
      fecha_hora_fin: base.fecha_hora_fin,
      titulo_evento: base.titulo_evento,
      enlace_reunion: base.enlace_reunion,
      comentarios_convocatoria: base.comentarios_convocatoria,
      tipos: base.tipos,
    };

    return this.http.post<{ entrevistas: EntrevistaApi[] }>(`${this.apiUrl}/entrevistas/agendar-masivo`, body).pipe(
      map((respuesta) => respuesta.entrevistas.map((entrevista) => this.mapearResumen(entrevista))),
    );
  }

  actualizarEntrevista(
    entrevistaId: string | number,
    payload: {
      titulo_evento?: string;
      enlace_reunion?: string | null;
      comentarios_convocatoria?: string | null;
    },
  ) {
    return this.http.patch<EntrevistaApi>(
      `${this.apiUrl}/entrevistas/${entrevistaId}`,
      payload,
    );
  }

  crearEvaluacion(
    entrevistaId: string | number,
    tipoId: string | number,
    payload: {
      nombre_resultado_id: number;
      observacion?: string | null;
    },
  ) {
    return this.http.post<EvaluacionEntrevistaApi>(
      `${this.apiUrl}/entrevistas/${entrevistaId}/tipos/${tipoId}/evaluar`,
      payload,
    );
  }

  actualizarEvaluacion(
    entrevistaId: string | number,
    tipoId: string | number,
    payload: {
      nombre_resultado_id?: number;
      observacion?: string | null;
    },
  ) {
    return this.http.patch<EvaluacionEntrevistaApi>(
      `${this.apiUrl}/entrevistas/${entrevistaId}/tipos/${tipoId}/evaluacion`,
      payload,
    );
  }

  reprogramar(id: string, fecha: string, horaInicio: string, horaFin: string, observacion: string) {
    return this.http.post<EntrevistaApi>(
      `${this.apiUrl}/entrevistas/${id}/reprogramar`,
      {
        fecha_hora_inicio: this.unirFechaHora(fecha, horaInicio),
        fecha_hora_fin: this.unirFechaHora(fecha, horaFin),
        motivo: observacion,
      },
    ).pipe(map((entrevista) => this.mapearResumen(entrevista)));
  }

  cancelar(id: string, observacion: string) {
    return this.http.post<EntrevistaApi>(
      `${this.apiUrl}/entrevistas/${id}/cancelar`,
      { motivo: observacion },
    ).pipe(map((entrevista) => this.mapearResumen(entrevista)));
  }

  confirmar(id: string) {
    return this.http.post<EntrevistaApi>(
      `${this.apiUrl}/entrevistas/${id}/confirmar`,
      {},
    ).pipe(map((entrevista) => this.mapearResumen(entrevista)));
  }

  noAsistio(id: string, motivo: string) {
    return this.http.post<EntrevistaApi>(
      `${this.apiUrl}/entrevistas/${id}/no-asistio`,
      { motivo },
    ).pipe(map((entrevista) => this.mapearResumen(entrevista)));
  }

  realizar(id: string) {
    return this.http.post<EntrevistaApi>(
      `${this.apiUrl}/entrevistas/${id}/realizar`,
      {},
    ).pipe(map((entrevista) => this.mapearResumen(entrevista)));
  }

  private mapearResumen(entrevista: EntrevistaApi): EntrevistaResumen {
    const inicio = this.separarFechaHora(entrevista.fecha_hora_inicio);
    const fin = this.separarFechaHora(entrevista.fecha_hora_fin);
    const tipos = this.nombresTipos(entrevista);

    return {
      id: String(entrevista.entrevista_id),
      solicitudCandidatoId: entrevista.solicitud_candidato_id,
      candidatoId: entrevista.candidato_id,
      idSolicitud: entrevista.solicitud_codigo ?? `SOL-${String(entrevista.solicitud_id).padStart(6, '0')}`,
      candidato: entrevista.candidato_nombre ?? entrevista.candidato_email ?? 'Candidato sin nombre',
      candidatoCorreo: entrevista.candidato_email ?? undefined,
      estado: entrevista.estado_nombre ?? entrevista.estado ?? 'Sin estado',
      tipo: tipos || 'Sin tipo',
      resultadoEntrevista: this.formatearResultados(entrevista),
      asunto: entrevista.titulo_evento || 'Entrevista',
      cargo: 'Sin cargo',
      fecha: inicio.fecha,
      horaInicio: inicio.hora,
      horaFin: fin.hora,
      entrevistador: this.formatearEntrevistadores(entrevista) || 'Sin entrevistador',
      linkReunion: entrevista.enlace_reunion ?? undefined,
      observacion: entrevista.comentarios_convocatoria ?? undefined,
    };
  }

  private nombresTipos(entrevista: EntrevistaApi) {
    const nombres = [
      ...(entrevista.tipos?.map((tipo) => tipo.nombre).filter(Boolean) ?? []),
      ...(entrevista.evaluaciones?.map((evaluacion) => evaluacion.tipo_entrevista_nombre).filter(Boolean) ?? []),
    ];

    return Array.from(new Set(nombres)).join(', ');
  }

  private formatearEntrevistadores(entrevista: EntrevistaApi) {
    const nombres = entrevista.tipos
      ?.flatMap((tipo) => tipo.entrevistadores ?? [])
      .map((entrevistador) =>
        [entrevistador.nombres, entrevistador.apellido_paterno].filter(Boolean).join(' '),
      )
      .filter(Boolean);

    return Array.from(new Set(nombres)).join(', ');
  }

  private formatearResultados(entrevista: EntrevistaApi) {
    const evaluaciones = entrevista.evaluaciones ?? [];

    if (evaluaciones.length === 0) {
      return 'Sin resultado';
    }

    return evaluaciones
      .map((evaluacion) => {
        const tipo = evaluacion.tipo_entrevista_nombre || 'Sin tipo';
        const usuario = evaluacion.usuario_nombre ? ` - ${evaluacion.usuario_nombre}` : '';
        return `${tipo}: ${evaluacion.resultado_nombre}${usuario}`;
      })
      .join(' | ');
  }

  private separarFechaHora(valor?: string | null) {
    if (!valor) {
      return { fecha: 'Sin fecha', hora: 'Sin hora' };
    }

    const fecha = new Date(valor);
    if (Number.isNaN(fecha.getTime())) {
      const [soloFecha, soloHora = 'Sin hora'] = valor.split('T');
      return { fecha: soloFecha || 'Sin fecha', hora: soloHora.slice(0, 5) || 'Sin hora' };
    }

    return {
      fecha: fecha.toISOString().slice(0, 10),
      hora: fecha.toTimeString().slice(0, 5),
    };
  }

  private unirFechaHora(fecha: string, hora: string) {
    return `${fecha}T${hora}:00`;
  }

  private crearPayloadApi(payload: EntrevistaPayload): EntrevistaCreateRequest | null {
    const solicitudCandidatoId = payload.solicitudCandidatoId;
    const tipoEntrevistaId = payload.tipoEntrevistaId;
    const entrevistadorIds = payload.entrevistadorIds ?? [];

    if (!solicitudCandidatoId || !tipoEntrevistaId || entrevistadorIds.length === 0) {
      return null;
    }

    return {
      solicitud_candidato_id: solicitudCandidatoId,
      fecha_hora_inicio: this.unirFechaHora(payload.fecha, payload.horaInicio),
      fecha_hora_fin: this.unirFechaHora(payload.fecha, payload.horaFin),
      titulo_evento: payload.asunto,
      enlace_reunion: payload.linkReunion || null,
      comentarios_convocatoria: payload.observacion || null,
      tipos: [
        {
          tipo_entrevista_id: tipoEntrevistaId,
          usuarios_ids: entrevistadorIds,
        },
      ],
    };
  }
}
