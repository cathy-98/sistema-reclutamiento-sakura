import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Stepper, StepperPaso } from '../stepper/stepper';

@Component({
  selector: 'app-wizard-layout',
  imports: [CommonModule, Stepper],
  templateUrl: './wizard-layout.html',
  styleUrl: './wizard-layout.scss',
})
export class WizardLayout {
  @Input() pasos: StepperPaso[] = [];
  @Input() pasoActivo = '';
  @Input() pasosCompletados: string[] = [];

  @Output() cambiarPaso = new EventEmitter<string>();
}
