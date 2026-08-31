import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-confirm-dialog',
  imports: [CommonModule, FormsModule],
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
  @Input() observacionLabel = '';
  @Input() observacionPlaceholder = '';
  @Input() observacionRequerida = false;

  @Output() cancelar = new EventEmitter<void>();
  @Output() confirmar = new EventEmitter<string>();

  readonly dialogId = `confirm-dialog-${Math.random().toString(36).slice(2)}`;
  observacion = '';

  get titleId() {
    return `${this.dialogId}-title`;
  }

  get messageId() {
    return `${this.dialogId}-message`;
  }

  get observacionInvalida() {
    return this.observacionRequerida && !this.observacion.trim();
  }

  confirmarAccion() {
    if (this.observacionInvalida) {
      return;
    }

    this.confirmar.emit(this.observacion.trim());
  }
}
