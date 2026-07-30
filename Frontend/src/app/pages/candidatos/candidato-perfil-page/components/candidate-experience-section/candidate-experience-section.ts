import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { ExperienciaPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-experience-section',
  imports: [CommonModule],
  templateUrl: './candidate-experience-section.html',
  styleUrl: './candidate-experience-section.scss',
})
export class CandidateExperienceSection {
  @Input() experiencias: ExperienciaPerfil[] = [];
}
