import { Injectable } from '@angular/core';
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
  // Temporal/mock: este módulo aún no tiene endpoint registrado en backend.
  // Cuando exista la API, reemplazar BehaviorSubject por HttpClient y mapear campos backend/BD a EntrevistaResumen.
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

  listar() {
    // Integración pendiente: aquí debería consumirse el endpoint real de entrevistas.
    return this.entrevistas.asObservable().pipe(delay(150));
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
