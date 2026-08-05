import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Alert } from '../alert/alert';
import { AlertaUi } from '../../models/alerta-ui.model';

@Component({
  selector: 'app-alert-region',
  imports: [CommonModule, Alert],
  templateUrl: './alert-region.html',
})
export class AlertRegion {
  @Input() alerta: AlertaUi | null = null;
  @Input() cerrable = true;
  @Output() cerrar = new EventEmitter<void>();
}
