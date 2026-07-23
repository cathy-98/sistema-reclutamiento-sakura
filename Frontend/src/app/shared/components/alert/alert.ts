import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export type AlertTipo = 'success' | 'danger' | 'warning' | 'info' | 'neutral' | 'dark';
export type AlertVariante = 'solid' | 'soft';

@Component({
  selector: 'app-alert',
  imports: [CommonModule],
  templateUrl: './alert.html',
  styleUrl: './alert.scss',
})
export class Alert {
  @Input() tipo: AlertTipo = 'info';
  @Input() variante: AlertVariante = 'soft';
  @Input() titulo = '';
  @Input() mensaje = '';
  @Input() cerrable = false;
  @Input() mostrarIcono = true;
  @Output() cerrar = new EventEmitter<void>();

  visible = true;

  get clases() {
    return [`is-${this.tipo}`, `is-${this.variante}`];
  }

  get icono() {
    const iconos: Record<AlertTipo, string> = {
      success: '✓',
      danger: '!',
      warning: '!',
      info: 'i',
      neutral: 'i',
      dark: 'i',
    };

    return iconos[this.tipo];
  }

  cerrarAlerta() {
    this.visible = false;
    this.cerrar.emit();
  }
}
