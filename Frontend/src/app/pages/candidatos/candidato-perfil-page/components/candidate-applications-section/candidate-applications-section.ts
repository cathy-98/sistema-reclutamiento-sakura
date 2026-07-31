import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../../../../../shared/components/button/button';
import { CandidatoPerfil, EtapaSeleccion, PostulacionPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-applications-section',
  imports: [CommonModule, FormsModule, Button],
  templateUrl: './candidate-applications-section.html',
  styleUrl: './candidate-applications-section.scss',
})
export class CandidateApplicationsSection {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() postulaciones: PostulacionPerfil[] = [];
  @Input() postulacionSeleccionadaId = '';
  @Input() busqueda = '';
  @Input() proceso: EtapaSeleccion[] = [];

  @Output() postulacionSeleccionadaIdChange = new EventEmitter<string>();
  @Output() busquedaChange = new EventEmitter<string>();

  get postulacionesFiltradas() {
    const texto = this.busqueda.trim().toLowerCase();
    return this.postulaciones.filter((postulacion) => postulacion.join(' ').toLowerCase().includes(texto));
  }

  get postulacionSeleccionada() {
    return this.postulaciones.find((postulacion) => postulacion[0] === this.postulacionSeleccionadaId) || this.postulaciones[0];
  }
}
