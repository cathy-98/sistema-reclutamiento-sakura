import { Component, Input } from '@angular/core';
import { Avatar } from '../../../shared/components/avatar/avatar';

@Component({
  selector: 'app-candidato-summary-card',
  imports: [Avatar],
  templateUrl: './candidato-summary-card.html',
  styleUrl: './candidato-summary-card.scss',
})
export class CandidatoSummaryCard {
  @Input() initials = '';
  @Input() cargo = '';
  @Input() correo = '';
  @Input() telefono = '';
  @Input() disponibilidad = '';
  @Input() renta = '';
}
