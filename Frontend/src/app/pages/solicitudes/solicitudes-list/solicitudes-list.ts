import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { SolicitudFormModal } from '../solicitud-form-modal/solicitud-form-modal';

@Component({
  selector: 'app-solicitudes-list',
  imports: [CommonModule, SolicitudFormModal],
  templateUrl: './solicitudes-list.html',
  styleUrl: './solicitudes-list.scss',
})
export class SolicitudesList {
  cargando = false;
  error = '';
  mostrarFormulario = false;
  solicitudSeleccionadaId: string | null = null;
  modoFormulario: 'crear' | 'ver' | 'editar' = 'crear';

  estadoClase(estado: string) {
    return estado.toLowerCase().replace(/\s+/g, '-');
  }

  prioridadClase(prioridad: string) {
    return prioridad.toLowerCase();
  }

  solicitudes = [
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
  ];

  abrirFormulario() {
    this.solicitudSeleccionadaId = null;
    this.modoFormulario = 'crear';
    this.mostrarFormulario = true;
  }

  abrirDetalleSolicitud(id: string) {
    this.solicitudSeleccionadaId = id;
    this.modoFormulario = 'ver';
    this.mostrarFormulario = true;
  }

  abrirEdicionSolicitud(id: string) {
    this.solicitudSeleccionadaId = id;
    this.modoFormulario = 'editar';
    this.mostrarFormulario = true;
  }

  cerrarFormulario() {
    this.mostrarFormulario = false;
    this.solicitudSeleccionadaId = null;
    this.modoFormulario = 'crear';
  }
}

