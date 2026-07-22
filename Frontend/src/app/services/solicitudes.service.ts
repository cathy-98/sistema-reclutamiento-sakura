import { Injectable } from '@angular/core';
import { BehaviorSubject, delay, map, of, throwError } from 'rxjs';
import { EstadoSolicitud, SolicitudResumen } from '../shared/models/solicitud.model';

@Injectable({
  providedIn: 'root',
})
export class SolicitudesService {
  private readonly solicitudes = new BehaviorSubject<SolicitudResumen[]>([
    {
      id: 'Req-001',
      nombre: 'Desarrollador Python Senior',
      cliente: 'Banco Elitsoft',
      cargo: 'Desarrollador Python',
      vacantes: 2,
      responsable: 'Cathy',
      seleccion: '01/06/2026 - 30/06/2026',
      inicioEmpleo: '15/07/2026',
      prioridad: 'Alta',
      estado: 'Pendiente',
      observacion: 'Perfil crítico para continuidad del equipo backend.',
    },
    {
      id: 'Req-002',
      nombre: 'Desarrollador Python Junior',
      cliente: 'Banco Elitsoft',
      cargo: 'Desarrollador Python',
      vacantes: 2,
      responsable: 'Cathy',
      seleccion: '01/06/2026 - 30/06/2026',
      inicioEmpleo: '15/07/2026',
      prioridad: 'Media',
      estado: 'En curso',
      observacion: 'Requiere disponibilidad para onboarding durante julio.',
    },
    {
      id: 'Req-003',
      nombre: 'Analista QA',
      cliente: 'Cliente interno',
      cargo: 'Analista QA',
      vacantes: 1,
      responsable: 'Felipe',
      seleccion: '10/07/2026 - 30/07/2026',
      inicioEmpleo: '05/08/2026',
      prioridad: 'Baja',
      estado: 'Cerrada',
      observacion: 'Solicitud cubierta con candidato interno.',
    },
  ]);

  listar() {
    return this.solicitudes.asObservable().pipe(delay(150));
  }

  cambiarEstado(id: string, estado: EstadoSolicitud, observacion: string) {
    const existeSolicitud = this.solicitudes.value.some((solicitud) => solicitud.id === id);

    if (!existeSolicitud) {
      return throwError(() => ({ status: 404 }));
    }

    const solicitudesActualizadas = this.solicitudes.value.map((solicitud) =>
      solicitud.id === id ? { ...solicitud, estado, observacion } : solicitud,
    );

    this.solicitudes.next(solicitudesActualizadas);
    return of(solicitudesActualizadas.find((solicitud) => solicitud.id === id)).pipe(
      delay(150),
      map((solicitud) => solicitud as SolicitudResumen),
    );
  }
}
