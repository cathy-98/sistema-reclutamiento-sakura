import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { FormField } from '../../../shared/components/form-field/form-field';
import { Modal } from '../../../shared/components/modal/modal';

export interface CuestionarioEnvioPayload {
  solicitudId: number;
  mensaje: string;
  candidatoIds: number[];
  fechaVencimiento: string;
}

@Component({
  selector: 'app-cuestionario-envio-modal',
  imports: [CommonModule, ReactiveFormsModule, Modal, FormField, Button],
  templateUrl: './cuestionario-envio-modal.html',
  styleUrl: './cuestionario-envio-modal.scss',
})
export class CuestionarioEnvioModal {
  private readonly fb = inject(FormBuilder);

  @Input() cantidadPreguntas = 0;
  @Input() duracion = '';
  @Input() resumen = '';
  @Input() enviando = false;

  @Output() cerrar = new EventEmitter<void>();
  @Output() enviar = new EventEmitter<CuestionarioEnvioPayload>();

  readonly formulario = this.fb.group({
    solicitudId: [null as number | null, [Validators.required, Validators.min(1)]],
    candidatoIds: ['', Validators.required],
    fechaVencimiento: ['', Validators.required],
    mensaje: [''],
  });

  confirmarEnvio() {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    const valor = this.formulario.getRawValue();
    const candidatoIds = this.obtenerIdsCandidatos(valor.candidatoIds ?? '');

    if (candidatoIds.length === 0) {
      this.formulario.get('candidatoIds')?.setErrors({ required: true });
      return;
    }

    this.enviar.emit({
      solicitudId: Number(valor.solicitudId),
      mensaje: valor.mensaje ?? '',
      candidatoIds,
      fechaVencimiento: this.normalizarFechaVencimiento(valor.fechaVencimiento ?? ''),
    });
  }

  private obtenerIdsCandidatos(valor: string) {
    return valor
      .split(/[\s,;]+/)
      .map((item) => Number(item.trim()))
      .filter((item, index, ids) => Number.isInteger(item) && item > 0 && ids.indexOf(item) === index);
  }

  private normalizarFechaVencimiento(valor: string) {
    const fecha = new Date(valor);
    return Number.isNaN(fecha.getTime()) ? valor : fecha.toISOString();
  }
}
