import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, delay, of, throwError } from 'rxjs';

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
  idSolicitud: string;
  candidato: string;
  estado: EstadoEntrevista;
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

export interface EntrevistaPayload {
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

@Injectable({ providedIn: 'root' })
export class EntrevistasService {
  private readonly apiUrl = '/api';

  // Temporal/mock para pantallas que aún no migran al contrato M5.
  private readonly entrevistas = new BehaviorSubject<EntrevistaResumen[]>([
    {
      id: 'ENT-001',
      idSolicitud: 'SOL-021',
      candidato: 'Macarena Lopez',
      estado: 'Confirmada',
      tipo: 'RRHH',
      asunto: 'Entrevista 1',
      cargo: 'Backend',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '18:45',
      entrevistador: 'María Fernanda López',
      linkReunion: 'https://meet.example.com/ent-001',
    },
    {
      id: 'ENT-002',
      idSolicitud: 'SOL-022',
      candidato: 'Valentina Rojas',
      estado: 'Pendiente',
      tipo: 'Tecnica',
      asunto: 'Entrevista 1',
      cargo: 'QA',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '19:00',
      entrevistador: 'Diego Salazar',
    },
    {
      id: 'ENT-003',
      idSolicitud: 'SOL-023',
      candidato: 'Diego Martinez',
      estado: 'Realizada',
      tipo: 'RRHH',
      asunto: 'Entrevista 1',
      cargo: 'Diseñadora',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '18:30',
      entrevistador: 'María Fernanda López',
    },
    {
      id: 'ENT-004',
      idSolicitud: 'SOL-024',
      candidato: 'Camila Fuentes',
      estado: 'Realizada',
      tipo: 'Tecnica',
      asunto: 'Entrevista 1',
      cargo: 'QA',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '18:45',
      entrevistador: 'Carlos Rojas',
    },
    {
      id: 'ENT-005',
      idSolicitud: 'SOL-025',
      candidato: 'Sebastian Araya',
      estado: 'Realizada',
      tipo: 'Cliente',
      asunto: 'Entrevista 1',
      cargo: 'Backend',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '18:30',
      entrevistador: 'María Fernanda López',
    },
    {
      id: 'ENT-006',
      idSolicitud: 'SOL-026',
      candidato: 'Juan Perez Gonzalez',
      estado: 'Realizada',
      tipo: 'Tecnica',
      asunto: 'Entrevista 1',
      cargo: 'Frontend',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '19:00',
      entrevistador: 'Diego Salazar',
    },
  ]);

  constructor(private http: HttpClient) {}

  listar() {
    // Integración pendiente: aquí debería consumirse el endpoint real de entrevistas.
    return this.entrevistas.asObservable().pipe(delay(150));
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
    // Integración pendiente: antes de enviar al backend, adaptar payload a la nomenclatura real de BD/API.
    const nuevaEntrevista: EntrevistaResumen = {
      ...payload,
      id: `ENT-${String(this.entrevistas.value.length + 1).padStart(3, '0')}`,
      estado: 'Pendiente',
    };

    this.entrevistas.next([nuevaEntrevista, ...this.entrevistas.value]);
    return of(nuevaEntrevista).pipe(delay(150));
  }

  crearMasiva(payloads: EntrevistaPayload[]) {
    const inicio = this.entrevistas.value.length;
    const nuevasEntrevistas: EntrevistaResumen[] = payloads.map((payload, index) => ({
      ...payload,
      id: `ENT-${String(inicio + index + 1).padStart(3, '0')}`,
      estado: 'Pendiente',
    }));

    this.entrevistas.next([...nuevasEntrevistas, ...this.entrevistas.value]);
    return of(nuevasEntrevistas).pipe(delay(150));
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
    // Integración pendiente: reprogramar debe actualizar ctev_fecha_hora_inicio/ctev_fecha_hora_fin.
    if (!this.entrevistas.value.some((entrevista) => entrevista.id === id)) {
      return throwError(() => ({ status: 404 }));
    }

    const actualizadas = this.entrevistas.value.map((entrevista) =>
      entrevista.id === id
        ? { ...entrevista, fecha, horaInicio, horaFin, observacion, estado: 'Reprogramada' as EstadoEntrevista }
        : entrevista,
    );

    this.entrevistas.next(actualizadas);
    return of(actualizadas.find((entrevista) => entrevista.id === id)).pipe(delay(150));
  }

  cancelar(id: string, observacion: string) {
    // Integración pendiente: cancelar debe actualizar ctev_estado_entrevista_id y comentario/auditoría.
    if (!this.entrevistas.value.some((entrevista) => entrevista.id === id)) {
      return throwError(() => ({ status: 404 }));
    }

    const actualizadas = this.entrevistas.value.map((entrevista) =>
      entrevista.id === id ? { ...entrevista, estado: 'Cancelada' as EstadoEntrevista, observacion } : entrevista,
    );

    this.entrevistas.next(actualizadas);
    return of(actualizadas.find((entrevista) => entrevista.id === id)).pipe(delay(150));
  }
}
