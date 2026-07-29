import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { Button } from '../../../../../shared/components/button/button';
import { MatchScore } from '../../../../../shared/components/match-score/match-score';
import { CandidatoPerfil, HabilidadComparada } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-match-section',
  imports: [CommonModule, Button, MatchScore],
  templateUrl: './candidate-match-section.html',
  styleUrl: './candidate-match-section.scss',
})
export class CandidateMatchSection {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() matchClass = '';
  @Input() habilidades: HabilidadComparada[] = [];
  @Input() fortalezas: string[] = [];
  @Input() areasMejora: string[] = [];
}
