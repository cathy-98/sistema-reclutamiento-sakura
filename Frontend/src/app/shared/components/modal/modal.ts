import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-modal',
  imports: [CommonModule],
  templateUrl: './modal.html',
  styleUrl: './modal.scss',
})
export class Modal {
  @Input() titulo = '';
  @Input() subtitulo = '';
  @Input() ancho: 'sm' | 'md' | 'lg' = 'lg';
  @Output() cerrar = new EventEmitter<void>();
}
