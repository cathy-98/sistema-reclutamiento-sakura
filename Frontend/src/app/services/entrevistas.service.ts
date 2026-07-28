import { Injectable } from '@angular/core';
import { BehaviorSubject, delay, of, throwError } from 'rxjs';

export type EstadoEntrevista = 'En curso' | 'Pendiente' | 'Cerrada' | 'Cancelada';
export type TipoEntrevista = 'Reclutamiento' | 'Técnica' | 'Operacional';

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
  modalidad: 'Online' | 'Presencial' | 'Híbrida';
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
  modalidad: 'Online' | 'Presencial' | 'Híbrida';
  entrevistador: string;
  linkReunion?: string;
  observacion?: string;
}

@Injectable({ providedIn: 'root' })
export class EntrevistasService {
  private readonly entrevistas = new BehaviorSubject<EntrevistaResumen[]>([
    {
      id: 'ENT-001',
      idSolicitud: 'Req-021',
      candidato: 'Macarena Lopez',
      estado: 'En curso',
      tipo: 'Reclutamiento',
      asunto: 'Entrevista 1',
      cargo: 'Backend',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '18:45',
      modalidad: 'Online',
      entrevistador: 'María Fernanda López',
      linkReunion: 'https://meet.example.com/ent-001',
    },
    {
      id: 'ENT-002',
      idSolicitud: 'Req-022',
      candidato: 'Valentina Rojas',
      estado: 'Pendiente',
      tipo: 'Técnica',
      asunto: 'Entrevista 1',
      cargo: 'QA',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '19:00',
      modalidad: 'Online',
      entrevistador: 'Diego Salazar',
    },
    {
      id: 'ENT-003',
      idSolicitud: 'Req-023',
      candidato: 'Diego Martinez',
      estado: 'Cerrada',
      tipo: 'Reclutamiento',
      asunto: 'Entrevista 1',
      cargo: 'Diseñadora',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '18:30',
      modalidad: 'Híbrida',
      entrevistador: 'María Fernanda López',
    },
    {
      id: 'ENT-004',
      idSolicitud: 'Req-024',
      candidato: 'Camila Fuentes',
      estado: 'Cerrada',
      tipo: 'Técnica',
      asunto: 'Entrevista 1',
      cargo: 'QA',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '18:45',
      modalidad: 'Presencial',
      entrevistador: 'Carlos Rojas',
    },
    {
      id: 'ENT-005',
      idSolicitud: 'Req-025',
      candidato: 'Sebastian Araya',
      estado: 'Cerrada',
      tipo: 'Operacional',
      asunto: 'Entrevista 1',
      cargo: 'Backend',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '18:30',
      modalidad: 'Online',
      entrevistador: 'María Fernanda López',
    },
    {
      id: 'ENT-006',
      idSolicitud: 'Req-026',
      candidato: 'Juan Perez Gonzalez',
      estado: 'Cerrada',
      tipo: 'Técnica',
      asunto: 'Entrevista 1',
      cargo: 'Frontend',
      fecha: '2025-11-02',
      horaInicio: '18:00',
      horaFin: '19:00',
      modalidad: 'Online',
      entrevistador: 'Diego Salazar',
    },
  ]);

  listar() {
    return this.entrevistas.asObservable().pipe(delay(150));
  }

  crear(payload: EntrevistaPayload) {
    const nuevaEntrevista: EntrevistaResumen = {
      ...payload,
      id: `ENT-${String(this.entrevistas.value.length + 1).padStart(3, '0')}`,
      estado: 'Pendiente',
    };

    this.entrevistas.next([nuevaEntrevista, ...this.entrevistas.value]);
    return of(nuevaEntrevista).pipe(delay(150));
  }

  reprogramar(id: string, fecha: string, horaInicio: string, horaFin: string, observacion: string) {
    if (!this.entrevistas.value.some((entrevista) => entrevista.id === id)) {
      return throwError(() => ({ status: 404 }));
    }

    const actualizadas = this.entrevistas.value.map((entrevista) =>
      entrevista.id === id
        ? { ...entrevista, fecha, horaInicio, horaFin, observacion, estado: 'Pendiente' as EstadoEntrevista }
        : entrevista,
    );

    this.entrevistas.next(actualizadas);
    return of(actualizadas.find((entrevista) => entrevista.id === id)).pipe(delay(150));
  }

  cancelar(id: string, observacion: string) {
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
