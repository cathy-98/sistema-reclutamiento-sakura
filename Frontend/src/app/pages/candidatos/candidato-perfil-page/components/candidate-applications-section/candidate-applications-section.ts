import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../../../../../shared/components/button/button';
import {
  CandidatoPerfil,
  EntrevistaPerfilResumen,
  EtapaSeleccion,
  PostulacionPerfil,
} from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-applications-section',
  imports: [CommonModule, FormsModule, Button],
  templateUrl: './candidate-applications-section.html',
  styleUrl: './candidate-applications-section.scss',
})
export class CandidateApplicationsSection {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() postulaciones: PostulacionPerfil[] = [];
  @Input() proximaEntrevista: EntrevistaPerfilResumen | null = null;
  @Input() postulacionSeleccionadaId = '';
  @Input() busqueda = '';
  @Input() proceso: EtapaSeleccion[] = [];

  @Output() postulacionSeleccionadaIdChange = new EventEmitter<string>();
  @Output() busquedaChange = new EventEmitter<string>();
  @Output() editInterviewObservation = new EventEmitter<EtapaSeleccion>();

  get postulacionesFiltradas() {
    const texto = this.busqueda.trim().toLowerCase();
    return this.postulaciones.filter((postulacion) => postulacion.join(' ').toLowerCase().includes(texto));
  }

  get postulacionSeleccionada() {
    return this.postulaciones.find((postulacion) => postulacion[0] === this.postulacionSeleccionadaId) ||
      this.postulaciones[0] ||
      (['Sin solicitud', 'Sin cliente', 'Sin puesto', 'Sin fecha', 'Sin estado'] as PostulacionPerfil);
  }

  get totalPostulaciones() {
    return this.postulaciones.length;
  }

  get totalPostulacionesActivas() {
    return this.postulaciones.filter(
      (postulacion) =>
        !this.esEstadoPostulacionTerminal(
          postulacion[4],
        ),
    ).length;
  }

  formatoContador(valor: number) {
    return String(valor).padStart(2, '0');
  }

  estadoPostulacionClase(estado: string) {
    const normalizado = estado
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-');

    if (['descartado', 'inhabilitado'].includes(normalizado)) {
      return 'is-danger';
    }

    if (normalizado === 'contratado' || normalizado === 'seleccionado') {
      return 'is-success';
    }

    if (normalizado === 'en-entrevista') {
      return 'is-info';
    }

    return 'is-warning';
  }

  estadoEntrevistaClase(estado: string) {
    const normalizado =
      this.normalizarEstado(estado);

    if (['realizada', 'confirmada'].includes(normalizado)) {
      return 'is-success';
    }

    if (['cancelada', 'cancelado', 'no-asistio'].includes(normalizado)) {
      return 'is-danger';
    }

    if (normalizado === 'reprogramada') {
      return 'is-info';
    }

    return 'is-warning';
  }

  agregarObservacionEntrevista() {
    const etapa =
      this.proceso.find(
        (item) => !item.observacionEntrevista?.trim(),
      ) ??
      this.proceso[0];

    if (etapa) {
      this.editInterviewObservation.emit({
        ...etapa,
        observacionEntrevista: '',
        observaciones: '',
      });
    }
  }

  private esEstadoPostulacionTerminal(estado: string) {
    const normalizado = this.normalizarEstado(estado);

    return [
      'descartado',
      'inhabilitado',
      'contratado',
      'cerrado',
    ].includes(normalizado);
  }

  private normalizarEstado(estado: string) {
    return estado
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-');
  }
}
