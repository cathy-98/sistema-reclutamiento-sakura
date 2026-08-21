import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../../../../../shared/components/button/button';
import { CandidatoPerfil, PostulacionPerfil } from '../../candidato-perfil.models';
import { CandidateContactLine } from '../candidate-contact-line/candidate-contact-line';
import { CandidateDetailsDisclosure } from '../candidate-details-disclosure/candidate-details-disclosure';
import { CandidateEditableMetrics } from '../candidate-editable-metrics/candidate-editable-metrics';

@Component({
  selector: 'app-candidate-profile-header',
  imports: [CommonModule, FormsModule, Button, CandidateContactLine, CandidateDetailsDisclosure, CandidateEditableMetrics],
  templateUrl: './candidate-profile-header.html',
  styleUrl: './candidate-profile-header.scss',
})
export class CandidateProfileHeader {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() matchClass = '';
  @Input() postulaciones: PostulacionPerfil[] = [];
  @Input() postulacionSeleccionadaId = '';
  @Input() estadosPostulacion: string[] = [];
  @Input() canSavePostulationState = true;

  @Output() back = new EventEmitter<void>();
  @Output() downloadCv = new EventEmitter<void>();
  @Output() scheduleInterview = new EventEmitter<void>();
  @Output() sendTest = new EventEmitter<void>();
  @Output() savePostulationState = new EventEmitter<void>();
  @Output() saveRent = new EventEmitter<number>();
  @Output() saveAvailability = new EventEmitter<string>();
  @Output() postulacionSeleccionadaIdChange = new EventEmitter<string>();

  menuAccionesAbierto = false;

  private readonly estadosPostulacionBase = [
    'En revision',
    'En entrevista',
    'Inhabilitado',
    'Seleccionado',
    'Descartado',
    'Contratado',
  ];

  get estadosPostulacionDisponibles() {
    const estados = this.estadosPostulacion.length
      ? this.estadosPostulacion
      : this.estadosPostulacionBase;

    return estados.includes(this.candidato.estado)
      ? estados
      : [this.candidato.estado, ...estados].filter(Boolean);
  }

  toggleActions() {
    this.menuAccionesAbierto = !this.menuAccionesAbierto;
  }

  closeActions() {
    this.menuAccionesAbierto = false;
  }

  selectDownloadCv() {
    this.downloadCv.emit();
    this.closeActions();
  }

  seleccionarPostulacion(id: string) {
    this.postulacionSeleccionadaIdChange.emit(id);
  }
}
