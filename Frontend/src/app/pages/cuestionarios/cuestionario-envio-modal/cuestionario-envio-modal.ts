import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { DatePicker } from '../../../shared/components/date-picker/date-picker';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { FormField } from '../../../shared/components/form-field/form-field';
import { Modal } from '../../../shared/components/modal/modal';

export interface CuestionarioEnvioPayload {
  solicitudId: number;
  mensaje: string;
  candidatoIds: number[];
  fechaVencimiento: string;
}

export interface SolicitudCuestionarioOption {
  id: number;
  codigo: string;
  cargo: string;
  cliente: string;
  estado: string;
}

export interface CandidatoCuestionarioOption {
  id: number;
  nombre: string;
  correo: string;
  solicitudId: number;
  estado: string;
}

@Component({
  selector: 'app-cuestionario-envio-modal',
  imports: [CommonModule, ReactiveFormsModule, Modal, FormField, DatePicker, FormActions, Button],
  templateUrl: './cuestionario-envio-modal.html',
  styleUrl: './cuestionario-envio-modal.scss',
})
export class CuestionarioEnvioModal {
  private readonly fb = inject(FormBuilder);

  @Input() cantidadPreguntas = 0;
  @Input() duracion = '';
  @Input() resumen = '';
  @Input() enviando = false;
  @Input() cargandoOpciones = false;
  @Input() solicitudes: SolicitudCuestionarioOption[] = [];
  @Input() candidatos: CandidatoCuestionarioOption[] = [];

  @Output() cerrar = new EventEmitter<void>();
  @Output() enviar = new EventEmitter<CuestionarioEnvioPayload>();

  readonly formulario = this.fb.group({
    solicitudId: [null as number | null, [Validators.required, Validators.min(1)]],
    fechaVencimiento: ['', Validators.required],
    horaVencimiento: ['', Validators.required],
    mensaje: [''],
  });

  candidatosSeleccionados = new Set<number>();
  errorCandidatos = '';

  get fechaHoyInput() {
    const fecha = new Date();
    return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`;
  }

  get candidatosSolicitud() {
    const solicitudId = Number(this.formulario.value.solicitudId);

    if (!solicitudId) {
      return [];
    }

    return this.candidatos.filter((candidato) => candidato.solicitudId === solicitudId);
  }

  get solicitudSeleccionada() {
    const solicitudId = Number(this.formulario.value.solicitudId);
    return this.solicitudes.find((solicitud) => solicitud.id === solicitudId) ?? null;
  }

  get solicitudPermiteAsignacion() {
    const estado = this.normalizar(this.solicitudSeleccionada?.estado ?? '');
    return !estado || (!estado.includes('cancelado') && !estado.includes('cerrado'));
  }

  get motivoBloqueoSolicitud() {
    if (!this.solicitudSeleccionada || this.solicitudPermiteAsignacion) {
      return '';
    }

    return `No se puede asignar un cuestionario a una solicitud en estado ${this.solicitudSeleccionada.estado}.`;
  }

  cambiarSolicitud() {
    this.candidatosSeleccionados = new Set();
    this.errorCandidatos = '';
  }

  alternarCandidato(candidatoId: number, seleccionado: boolean) {
    const candidatos = new Set(this.candidatosSeleccionados);

    if (seleccionado) {
      candidatos.add(candidatoId);
    } else {
      candidatos.delete(candidatoId);
    }

    this.candidatosSeleccionados = candidatos;
    this.errorCandidatos = '';
  }

  seleccionarTodosCandidatos() {
    this.candidatosSeleccionados = new Set(this.candidatosSolicitud.map((candidato) => candidato.id));
    this.errorCandidatos = '';
  }

  limpiarCandidatos() {
    this.candidatosSeleccionados = new Set();
  }

  candidatoMarcado(candidatoId: number) {
    return this.candidatosSeleccionados.has(candidatoId);
  }

  confirmarEnvio() {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    const valor = this.formulario.getRawValue();
    const candidatoIds = Array.from(this.candidatosSeleccionados);

    if (!this.solicitudPermiteAsignacion) {
      return;
    }

    if (candidatoIds.length === 0) {
      this.errorCandidatos = 'Selecciona al menos un candidato asociado a la solicitud.';
      return;
    }

    this.enviar.emit({
      solicitudId: Number(valor.solicitudId),
      mensaje: valor.mensaje ?? '',
      candidatoIds,
      fechaVencimiento: this.normalizarFechaVencimiento(
        valor.fechaVencimiento ?? '',
        valor.horaVencimiento ?? '',
      ),
    });
  }

  private normalizarFechaVencimiento(fechaValor: string, horaValor: string) {
    const valor = `${fechaValor}T${horaValor}:00`;
    const fecha = new Date(valor);
    return Number.isNaN(fecha.getTime()) ? valor : fecha.toISOString();
  }

  private normalizar(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }
}
