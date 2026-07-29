import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { CandidatoPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-details-disclosure',
  imports: [CommonModule],
  templateUrl: './candidate-details-disclosure.html',
  styleUrl: './candidate-details-disclosure.scss',
})
export class CandidateDetailsDisclosure {
  @Input({ required: true }) candidato!: CandidatoPerfil;

  abierto = false;

  toggle() {
    this.abierto = !this.abierto;
  }
}
