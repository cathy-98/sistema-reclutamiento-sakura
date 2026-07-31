import { Component, Input } from '@angular/core';
import { CandidatoPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-contact-line',
  templateUrl: './candidate-contact-line.html',
  styleUrl: './candidate-contact-line.scss',
})
export class CandidateContactLine {
  @Input({ required: true }) candidato!: CandidatoPerfil;
}
