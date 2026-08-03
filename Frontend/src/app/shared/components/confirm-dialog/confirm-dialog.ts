import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-confirm-dialog',
  imports: [CommonModule],
  templateUrl: './confirm-dialog.html',
  styleUrl: './confirm-dialog.scss',
})
export class ConfirmDialog {
  @Input() titulo = 'Confirmar acción';
  @Input() mensaje = '¿Deseas continuar?';
  @Input() detalle = '';
  @Input() textoCancelar = 'Volver';
  @Input() textoConfirmar = 'Confirmar';
  @Input() variante: 'danger' | 'warning' | 'info' = 'danger';

  @Output() cancelar = new EventEmitter<void>();
  @Output() confirmar = new EventEmitter<void>();

  readonly dialogId = `confirm-dialog-${Math.random().toString(36).slice(2)}`;

  get titleId() {
    return `${this.dialogId}-title`;
  }

  get messageId() {
    return `${this.dialogId}-message`;
  }
}
