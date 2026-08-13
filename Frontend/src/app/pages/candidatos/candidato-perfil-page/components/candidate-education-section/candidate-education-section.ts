import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { EstudioPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-education-section',
  imports: [CommonModule],
  templateUrl: './candidate-education-section.html',
  styleUrl: './candidate-education-section.scss',
})
export class CandidateEducationSection {
  @Input() estudios: EstudioPerfil[] = [];
}
