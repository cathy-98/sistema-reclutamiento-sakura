import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { FormArray, FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { FormField } from '../../../shared/components/form-field/form-field';
import { Modal } from '../../../shared/components/modal/modal';

export interface CuestionarioEnvioPayload {
  solicitudId: string;
  mensaje: string;
  destinatarios: Array<{
    nombre: string;
    correo: string;
  }>;
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

  @Output() cerrar = new EventEmitter<void>();
  @Output() enviar = new EventEmitter<CuestionarioEnvioPayload>();

  readonly formulario = this.fb.group({
    solicitudId: ['', Validators.required],
    mensaje: [''],
    destinatarios: this.fb.array([this.crearDestinatario()]),
  });

  get destinatarios() {
    return this.formulario.get('destinatarios') as FormArray;
  }

  agregarDestinatario() {
    this.destinatarios.push(this.crearDestinatario());
  }

  eliminarDestinatario(indice: number) {
    if (this.destinatarios.length === 1) {
      this.destinatarios.at(0).reset();
      return;
    }

    this.destinatarios.removeAt(indice);
  }

  confirmarEnvio() {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    const valor = this.formulario.getRawValue();
    this.enviar.emit({
      solicitudId: valor.solicitudId ?? '',
      mensaje: valor.mensaje ?? '',
      destinatarios: valor.destinatarios.map((destinatario) => ({
        nombre: destinatario.nombre ?? '',
        correo: destinatario.correo ?? '',
      })),
    });
  }

  private crearDestinatario() {
    return this.fb.group({
      nombre: ['', Validators.required],
      correo: ['', [Validators.required, Validators.email]],
    });
  }
}
