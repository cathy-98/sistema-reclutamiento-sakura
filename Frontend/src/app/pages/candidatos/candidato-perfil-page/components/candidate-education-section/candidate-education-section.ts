import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { CursoPerfil, EstudioPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-education-section',
  imports: [CommonModule],
  templateUrl: './candidate-education-section.html',
  styleUrl: './candidate-education-section.scss',
})
export class CandidateEducationSection {
  @Input() estudios: EstudioPerfil[] = [];
  @Input() cursos: CursoPerfil[] = [];

  get tieneEstudios() {
    return this.estudios.length > 0;
  }

  get tieneCursos() {
    return this.cursos.length > 0;
  }

  get tieneContenido() {
    return this.tieneEstudios || this.tieneCursos;
  }
}
