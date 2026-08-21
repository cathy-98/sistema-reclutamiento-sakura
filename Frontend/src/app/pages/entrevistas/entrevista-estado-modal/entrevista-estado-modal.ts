import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output } from '@angular/core';
import { ReactiveFormsModule, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { DatePicker } from '../../../shared/components/date-picker/date-picker';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { Modal } from '../../../shared/components/modal/modal';
import { EntrevistaResumen } from '../../../services/entrevistas.service';

type ModoEstadoEntrevista = 'ver' | 'editar' | 'reprogramar' | 'cancelar' | 'confirmar' | 'realizar' | 'no-asistio';

@Component({
  selector: 'app-entrevista-estado-modal',
  imports: [CommonModule, ReactiveFormsModule, Button, DatePicker, FormActions, Modal],
  templateUrl: './entrevista-estado-modal.html',
  styleUrl: './entrevista-estado-modal.scss',
})
export class EntrevistaEstadoModal implements OnChanges {
  @Input() entrevista: EntrevistaResumen | null = null;
  @Input() modo: ModoEstadoEntrevista = 'editar';
  @Output() cerrar = new EventEmitter<void>();
  @Output() confirmar = new EventEmitter<{ estado?: string; fecha: string; horaInicio: string; horaFin: string; motivo: string }>();

  readonly estadosEditables = ['Confirmada', 'Reprogramada', 'Realizada', 'No Asistio', 'Cancelada'];

  formulario = new UntypedFormGroup({
    estado: new UntypedFormControl('', Validators.required),
    fecha: new UntypedFormControl('', Validators.required),
    horaInicio: new UntypedFormControl('', Validators.required),
    horaFin: new UntypedFormControl('', Validators.required),
    motivo: new UntypedFormControl(''),
  });

  ngOnChanges() {
    if (!this.entrevista) {
      return;
    }

    this.formulario.patchValue({
      estado: this.estadoInicial,
      fecha: this.entrevista.fecha,
      horaInicio: this.entrevista.horaInicio,
      horaFin: this.entrevista.horaFin,
      motivo: '',
    });

    this.actualizarValidadores();
  }

  actualizarValidadores() {
    if (!this.mostrarFecha) {
      this.formulario.get('fecha')?.clearValidators();
      this.formulario.get('horaInicio')?.clearValidators();
      this.formulario.get('horaFin')?.clearValidators();
    } else {
      this.formulario.get('fecha')?.setValidators(Validators.required);
      this.formulario.get('horaInicio')?.setValidators(Validators.required);
      this.formulario.get('horaFin')?.setValidators(Validators.required);
    }

    if (this.requiereMotivo) {
      this.formulario.get('motivo')?.setValidators(Validators.required);
    } else {
      this.formulario.get('motivo')?.clearValidators();
    }

    if (this.mostrarSelectorEstado) {
      this.formulario.get('estado')?.setValidators(Validators.required);
    } else {
      this.formulario.get('estado')?.clearValidators();
    }

    this.formulario.updateValueAndValidity();
  }

  get titulo() {
    const titulos = {
      ver: 'Detalle de entrevista',
      editar: 'Editar estado de entrevista',
      reprogramar: 'Reprogramar entrevista',
      cancelar: 'Cancelar entrevista',
      confirmar: 'Confirmar entrevista',
      realizar: 'Marcar entrevista realizada',
      'no-asistio': 'Marcar no asistio',
    };

    return titulos[this.modo];
  }

  get accion() {
    const acciones = {
      ver: 'Cerrar',
      editar: 'Guardar estado',
      reprogramar: 'Guardar nueva fecha',
      cancelar: 'Confirmar cancelación',
      confirmar: 'Confirmar entrevista',
      realizar: 'Marcar realizada',
      'no-asistio': 'Confirmar no asistio',
    };

    return acciones[this.modo];
  }

  get requiereMotivo() {
    return ['Reprogramada', 'Cancelada', 'No Asistio'].includes(this.estadoObjetivo);
  }

  get varianteAccion() {
    return this.estadoObjetivo === 'Cancelada' || this.estadoObjetivo === 'No Asistio' ? 'danger' : 'primary';
  }

  get mostrarSelectorEstado() {
    return this.modo === 'editar';
  }

  get esLectura() {
    return this.modo === 'ver';
  }

  get mostrarFecha() {
    return this.estadoObjetivo === 'Reprogramada';
  }

  get estadoObjetivo() {
    if (this.modo === 'editar') {
      return String(this.formulario.get('estado')?.value || '');
    }

    const estados = {
      ver: this.entrevista?.estado ?? '',
      reprogramar: 'Reprogramada',
      cancelar: 'Cancelada',
      confirmar: 'Confirmada',
      realizar: 'Realizada',
      'no-asistio': 'No Asistio',
    };

    return estados[this.modo];
  }

  get estadoInicial() {
    if (!this.entrevista) {
      return '';
    }

    if (this.estadosEditables.includes(this.entrevista.estado)) {
      return this.entrevista.estado;
    }

    return this.estadosEditables[0];
  }

  get fechaHoyInput() {
    return new Date().toISOString().slice(0, 10);
  }

  enviar() {
    if (this.esLectura) {
      this.cerrar.emit();
      return;
    }

    this.formulario.markAllAsTouched();

    if (this.formulario.invalid || !this.horarioValido()) {
      return;
    }

    this.confirmar.emit(this.formulario.getRawValue());
  }

  horarioValido() {
    if (!this.mostrarFecha) {
      return true;
    }

    const inicio = String(this.formulario.get('horaInicio')?.value || '');
    const fin = String(this.formulario.get('horaFin')?.value || '');
    return !inicio || !fin || fin > inicio;
  }
}
