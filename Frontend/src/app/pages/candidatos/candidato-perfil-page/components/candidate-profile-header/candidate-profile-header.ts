import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../../../../../shared/components/button/button';
import { MatchScore } from '../../../../../shared/components/match-score/match-score';
import { CandidatoPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-profile-header',
  imports: [CommonModule, FormsModule, Button, MatchScore],
  templateUrl: './candidate-profile-header.html',
  styleUrl: './candidate-profile-header.scss',
})
export class CandidateProfileHeader {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() rentaFormateada = '';
  @Input() matchClass = '';

  @Output() back = new EventEmitter<void>();
  @Output() downloadCv = new EventEmitter<void>();
  @Output() addObservation = new EventEmitter<void>();

  menuAccionesAbierto = false;
  datosCompletosAbiertos = false;

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

  toggleDatosCompletos() {
    this.datosCompletosAbiertos = !this.datosCompletosAbiertos;
  }
}
