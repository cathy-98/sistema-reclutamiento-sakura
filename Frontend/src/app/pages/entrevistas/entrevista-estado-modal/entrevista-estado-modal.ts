import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output } from '@angular/core';
import { ReactiveFormsModule, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { Modal } from '../../../shared/components/modal/modal';
import { EntrevistaResumen } from '../../../services/entrevistas.service';

@Component({
  selector: 'app-entrevista-estado-modal',
  imports: [CommonModule, ReactiveFormsModule, Button, FormActions, Modal],
  templateUrl: './entrevista-estado-modal.html',
  styleUrl: './entrevista-estado-modal.scss',
})
export class EntrevistaEstadoModal implements OnChanges {
  @Input() entrevista: EntrevistaResumen | null = null;
  @Input() modo: 'reprogramar' | 'cancelar' = 'reprogramar';
  @Output() cerrar = new EventEmitter<void>();
  @Output() confirmar = new EventEmitter<{ fecha: string; horaInicio: string; horaFin: string; motivo: string }>();

  formulario = new UntypedFormGroup({
    fecha: new UntypedFormControl('', Validators.required),
    horaInicio: new UntypedFormControl('', Validators.required),
    horaFin: new UntypedFormControl('', Validators.required),
    motivo: new UntypedFormControl('', Validators.required),
  });

  ngOnChanges() {
    if (!this.entrevista) {
      return;
    }

    this.formulario.patchValue({
      fecha: this.entrevista.fecha,
      horaInicio: this.entrevista.horaInicio,
      horaFin: this.entrevista.horaFin,
      motivo: '',
    });

    if (this.modo === 'cancelar') {
      this.formulario.get('fecha')?.clearValidators();
      this.formulario.get('horaInicio')?.clearValidators();
      this.formulario.get('horaFin')?.clearValidators();
    } else {
      this.formulario.get('fecha')?.setValidators(Validators.required);
      this.formulario.get('horaInicio')?.setValidators(Validators.required);
      this.formulario.get('horaFin')?.setValidators(Validators.required);
    }

    this.formulario.updateValueAndValidity();
  }

  get titulo() {
    return this.modo === 'cancelar' ? 'Cancelar entrevista' : 'Reprogramar entrevista';
  }

  get accion() {
    return this.modo === 'cancelar' ? 'Confirmar cancelación' : 'Guardar nueva fecha';
  }

  enviar() {
    this.formulario.markAllAsTouched();

    if (this.formulario.invalid || !this.horarioValido()) {
      return;
    }

    this.confirmar.emit(this.formulario.getRawValue());
  }

  horarioValido() {
    if (this.modo === 'cancelar') {
      return true;
    }

    const inicio = String(this.formulario.get('horaInicio')?.value || '');
    const fin = String(this.formulario.get('horaFin')?.value || '');
    return !inicio || !fin || fin > inicio;
  }
}
