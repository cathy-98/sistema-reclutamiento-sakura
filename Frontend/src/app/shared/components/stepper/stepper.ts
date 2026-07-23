import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export interface StepperPaso {
  clave: string;
  numero: number;
  titulo: string;
}

@Component({
  selector: 'app-stepper',
  imports: [CommonModule],
  templateUrl: './stepper.html',
  styleUrl: './stepper.scss',
})
export class Stepper {
  @Input() pasos: StepperPaso[] = [];
  @Input() pasoActivo = '';
  @Input() pasosCompletados: string[] = [];
  @Output() cambiarPaso = new EventEmitter<string>();

  estaCompleto(clave: string) {
    return this.pasosCompletados.includes(clave);
  }
}
