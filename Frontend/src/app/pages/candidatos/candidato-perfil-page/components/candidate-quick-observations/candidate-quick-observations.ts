import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { ObservacionPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-quick-observations',
  imports: [CommonModule],
  templateUrl: './candidate-quick-observations.html',
  styleUrl: './candidate-quick-observations.scss',
})
export class CandidateQuickObservations {
  @Input() historial: ObservacionPerfil[] = [];

  get ultima() {
    return this.historial[0];
  }

}
