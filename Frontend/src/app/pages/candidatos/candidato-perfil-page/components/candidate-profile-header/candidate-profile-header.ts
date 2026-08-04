import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../../../../../shared/components/button/button';
import { CandidatoPerfil } from '../../candidato-perfil.models';
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

  @Output() back = new EventEmitter<void>();
  @Output() downloadCv = new EventEmitter<void>();
  @Output() addObservation = new EventEmitter<void>();
  @Output() scheduleInterview = new EventEmitter<void>();
  @Output() sendTest = new EventEmitter<void>();

  menuAccionesAbierto = false;

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

  selectAddObservation() {
    this.addObservation.emit();
    this.closeActions();
  }
}
