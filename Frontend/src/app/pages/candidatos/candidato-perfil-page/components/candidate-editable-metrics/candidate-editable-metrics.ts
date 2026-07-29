import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatchScore } from '../../../../../shared/components/match-score/match-score';
import { CandidatoPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-editable-metrics',
  imports: [CommonModule, FormsModule, MatchScore],
  templateUrl: './candidate-editable-metrics.html',
  styleUrl: './candidate-editable-metrics.scss',
})
export class CandidateEditableMetrics {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() matchClass = '';

  get rentaFormateada() {
    return `$${this.candidato.renta.toLocaleString('es-CL')} CLP líquidos`;
  }

  get rentaInput() {
    return this.candidato.renta;
  }

  set rentaInput(value: number) {
    this.candidato.renta = Number(value) || 0;
  }
}
