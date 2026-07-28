import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Button } from '../../../../../shared/components/button/button';
import { ObservacionPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-observation-history',
  imports: [CommonModule, Button],
  templateUrl: './candidate-observation-history.html',
  styleUrl: './candidate-observation-history.scss',
})
export class CandidateObservationHistory {
  @Input() historial: ObservacionPerfil[] = [];
  @Output() addObservation = new EventEmitter<void>();
}
