import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormsModule, ReactiveFormsModule, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { DatePicker } from '../../../shared/components/date-picker/date-picker';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { Modal } from '../../../shared/components/modal/modal';
import { AuthService } from '../../../services/auth.service';
import { NombreResultadoCatalogoApi } from '../../../services/catalogos.service';
import { EntrevistaApi, EntrevistaResumen } from '../../../services/entrevistas.service';

type ModoEstadoEntrevista = 'ver' | 'gestionar' | 'reprogramar' | 'cancelar' | 'confirmar' | 'realizar' | 'no-asistio';
type AccionGestionEntrevista = 'confirmar' | 'reprogramar' | 'realizar' | 'no-asistio' | 'cancelar';

export interface EvaluacionTipoPayload {
  tipoId: number;
  existe: boolean;
  nombreResultadoId: number;
  observacion: string | null;
}

interface EvaluacionTipoForm {
  resultadoId: number | null;
  observacion: string;
  existe: boolean;
}

interface AccionGestionOption {
  valor: AccionGestionEntrevista;
  etiqueta: string;
  estadoObjetivo: string;
}

@Component({
  selector: 'app-entrevista-estado-modal',
  imports: [CommonModule, FormsModule, ReactiveFormsModule, Button, DatePicker, FormActions, Modal],
  templateUrl: './entrevista-estado-modal.html',
  styleUrl: './entrevista-estado-modal.scss',
})
export class EntrevistaEstadoModal implements OnChanges {
  @Input() entrevista: EntrevistaResumen | null = null;
  @Input() detalle: EntrevistaApi | null = null;
  @Input() resultados: NombreResultadoCatalogoApi[] = [];
  @Input() modo: ModoEstadoEntrevista = 'gestionar';
  @Input() guardando = false;
  @Input() guardandoEvaluaciones = false;
  @Input() error = '';
  @Input() errorEvaluaciones = '';
  @Output() cerrar = new EventEmitter<void>();
  @Output() confirmar = new EventEmitter<{ estado?: string; fecha: string; horaInicio: string; horaFin: string; motivo: string }>();
  @Output() guardarEvaluaciones = new EventEmitter<EvaluacionTipoPayload[]>();

  evaluacionesPorTipo: Record<number, EvaluacionTipoForm> = {};
  intentoGuardarResultados = false;
  errorLocalEvaluaciones = '';

  formulario = new UntypedFormGroup({
    estado: new UntypedFormControl(''),
    fecha: new UntypedFormControl('', Validators.required),
    horaInicio: new UntypedFormControl('', Validators.required),
    horaFin: new UntypedFormControl('', Validators.required),
    motivo: new UntypedFormControl(''),
  });

  constructor(private authService: AuthService) {}

  ngOnChanges(changes: SimpleChanges) {
    if (!this.entrevista) {
      return;
    }

    if (changes['entrevista'] || changes['detalle'] || changes['modo']) {
      this.formulario.patchValue({
        estado: '',
        fecha: this.entrevista.fecha,
        horaInicio: this.entrevista.horaInicio,
        horaFin: this.entrevista.horaFin,
        motivo: '',
      }, { emitEvent: false });

      this.prepararEvaluacionesPorTipo();
      this.intentoGuardarResultados = false;
      this.errorLocalEvaluaciones = '';
      this.actualizarValidadores();
    }
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
    return this.modo === 'ver'
      ? 'Detalle de entrevista'
      : this.modo === 'reprogramar'
        ? 'Reprogramar entrevista'
        : this.estadoActualNormalizado === 'realizada'
          ? 'Registrar feedback'
          : 'Gestionar entrevista';
  }

  get accion() {
    if (this.modo === 'reprogramar') {
      return 'Guardar reprogramación';
    }

    if (this.mostrarResultadosPorArea && !this.mostrarSelectorEstado) {
      return 'Guardar resultados';
    }

    const seleccionada = this.accionSeleccionada;

    if (seleccionada === 'confirmar') {
      return 'Guardar confirmación';
    }

    if (seleccionada === 'reprogramar') {
      return 'Guardar reprogramación';
    }

    if (seleccionada === 'realizar') {
      return 'Guardar realizada';
    }

    if (seleccionada === 'no-asistio') {
      return 'Guardar no asistencia';
    }

    if (seleccionada === 'cancelar') {
      return 'Guardar cancelación';
    }

    return 'Continuar';
  }

  get estadoActual() {
    return this.detalle?.estado_nombre ||
      this.detalle?.estado ||
      this.entrevista?.estado ||
      'Sin estado';
  }

  get estadoActualNormalizado() {
    return this.normalizar(this.estadoActual);
  }

  get accionesDisponibles(): AccionGestionOption[] {
    // Decisión UX/UI M5: solo muestra transiciones que corresponden a endpoints reales ya integrados.
    if (['realizada', 'cancelada', 'no-asistio'].includes(this.estadoActualNormalizado)) {
      return [];
    }

    if (!['pendiente', 'confirmada', 'reprogramada'].includes(this.estadoActualNormalizado)) {
      return [];
    }

    const acciones: AccionGestionOption[] = [
      { valor: 'confirmar', etiqueta: 'Confirmar entrevista', estadoObjetivo: 'Confirmada' },
      { valor: 'reprogramar', etiqueta: 'Reprogramar', estadoObjetivo: 'Reprogramada' },
      { valor: 'realizar', etiqueta: 'Marcar como realizada', estadoObjetivo: 'Realizada' },
      { valor: 'no-asistio', etiqueta: 'Registrar no asistencia', estadoObjetivo: 'No Asistio' },
      { valor: 'cancelar', etiqueta: 'Cancelar entrevista', estadoObjetivo: 'Cancelada' },
    ];

    if (this.estadoActualNormalizado === 'confirmada') {
      return acciones.filter((accion) => accion.valor !== 'confirmar');
    }

    return acciones;
  }

  get accionSeleccionada() {
    return String(this.formulario.get('estado')?.value || '') as AccionGestionEntrevista | '';
  }

  get requiereMotivo() {
    return ['reprogramar', 'cancelar', 'no-asistio'].includes(this.accionSeleccionada) || this.modo === 'reprogramar';
  }

  get varianteAccion() {
    return this.accionSeleccionada === 'cancelar' || this.accionSeleccionada === 'no-asistio' ? 'danger' : 'primary';
  }

  get mostrarSelectorEstado() {
    return this.modo === 'gestionar' && this.accionesDisponibles.length > 0;
  }

  get esLectura() {
    return this.modo === 'ver';
  }

  get mostrarFecha() {
    return this.modo === 'reprogramar' || this.accionSeleccionada === 'reprogramar';
  }

  get mostrarResultadosPorArea() {
    return this.modo === 'gestionar' &&
      this.estadoActualNormalizado === 'realizada' &&
      this.tiposEvaluables.length > 0;
  }

  get entrevistaRealizadaSinEvaluacionDisponible() {
    return this.modo === 'gestionar' &&
      this.estadoActualNormalizado === 'realizada' &&
      this.tiposEvaluables.length === 0;
  }

  get tiposEvaluables() {
    const usuarioId = this.authService.obtenerUsuarioId();

    if (!usuarioId) {
      return [];
    }

    // Integración M5: la UI solo permite evaluar tipos donde el usuario actual está asignado.
    return (this.detalle?.tipos ?? []).filter((tipo) =>
      (tipo.entrevistadores ?? []).some((entrevistador) => entrevistador.usuario_id === usuarioId),
    );
  }

  get estadoObjetivo() {
    if (this.modo === 'gestionar') {
      return this.accionesDisponibles.find((accion) => accion.valor === this.accionSeleccionada)?.estadoObjetivo ?? '';
    }

    const objetivos = {
      ver: this.estadoActual,
      reprogramar: 'Reprogramada',
      cancelar: 'Cancelada',
      confirmar: 'Confirmada',
      realizar: 'Realizada',
      'no-asistio': 'No Asistio',
    };

    return objetivos[this.modo];
  }

  get estadoInicial() {
    return '';
  }

  get fechaHoyInput() {
    const ahora = new Date();
    const local = new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 10);
  }

  get mensajeConfirmacionSensible() {
    if (this.accionSeleccionada === 'reprogramar' || this.modo === 'reprogramar') {
      return 'La reprogramación conserva la misma entrevista y actualiza fecha, hora y motivo.';
    }

    if (this.accionSeleccionada === 'cancelar') {
      return 'Esta acción cancelará la entrevista. Indica el motivo para continuar.';
    }

    if (this.accionSeleccionada === 'no-asistio') {
      return 'Esta acción registrará la inasistencia. Indica el motivo para continuar.';
    }

    return '';
  }

  get tituloAccionSeleccionada() {
    return this.accionesDisponibles.find((accion) => accion.valor === this.accionSeleccionada)?.etiqueta ?? '';
  }

  seleccionarAccion(accion: string) {
    if (!accion) {
      this.formulario.patchValue({ estado: '', motivo: '' });
      this.actualizarValidadores();
      return;
    }

    if (!this.accionesDisponibles.some((item) => item.valor === accion)) {
      return;
    }

    // Integración M5: la acción seleccionada representa endpoint, no edición libre del estado.
    this.formulario.patchValue({ estado: accion, motivo: '' });
    this.actualizarValidadores();
  }

  enviar() {
    if (this.esLectura) {
      this.cerrar.emit();
      return;
    }

    if (this.mostrarResultadosPorArea && !this.mostrarSelectorEstado) {
      this.enviarEvaluaciones();
      return;
    }

    this.formulario.markAllAsTouched();

    if (
      this.formulario.invalid ||
      !this.horarioValido() ||
      !this.fechaValida()
    ) {
      return;
    }

    this.confirmar.emit(this.formulario.getRawValue());
  }

  enviarEvaluaciones() {
    this.intentoGuardarResultados = true;
    this.errorLocalEvaluaciones = '';

    const payload = this.payloadEvaluaciones();

    if (payload.length !== this.tiposEvaluables.length) {
      this.errorLocalEvaluaciones = 'Selecciona un resultado para cada área antes de guardar.';
      return;
    }

    this.guardarEvaluaciones.emit(payload);
  }

  horarioValido() {
    if (!this.mostrarFecha) {
      return true;
    }

    const inicio = String(this.formulario.get('horaInicio')?.value || '');
    const fin = String(this.formulario.get('horaFin')?.value || '');
    return !inicio || !fin || fin > inicio;
  }

  fechaValida() {
    if (!this.mostrarFecha) {
      return true;
    }

    const fecha = String(this.formulario.get('fecha')?.value || '');
    const horaInicio = String(this.formulario.get('horaInicio')?.value || '');

    if (!fecha) {
      return false;
    }

    if (!horaInicio) {
      return fecha >= this.fechaHoyInput;
    }

    const fechaHora = new Date(`${fecha}T${horaInicio}:00`);
    return !Number.isNaN(fechaHora.getTime()) && fechaHora > new Date();
  }

  evaluacionTipo(tipoId: number) {
    if (!this.evaluacionesPorTipo[tipoId]) {
      this.evaluacionesPorTipo[tipoId] = {
        resultadoId: null,
        observacion: '',
        existe: false,
      };
    }

    return this.evaluacionesPorTipo[tipoId];
  }

  resultadoTipoInvalido(tipoId: number) {
    return this.intentoGuardarResultados &&
      this.mostrarResultadosPorArea &&
      !this.evaluacionTipo(tipoId).resultadoId;
  }

  private prepararEvaluacionesPorTipo() {
    const evaluaciones = this.detalle?.evaluaciones ?? [];
    const valores: Record<number, EvaluacionTipoForm> = {};

    (this.detalle?.tipos ?? []).forEach((tipo) => {
      const evaluacion = evaluaciones.find((item) =>
        item.tipo_entrevista_id === tipo.tipo_entrevista_id,
      ) ?? null;

      valores[tipo.tipo_entrevista_id] = {
        resultadoId: evaluacion?.resultado_id ?? null,
        observacion: evaluacion?.observacion ?? '',
        existe: Boolean(evaluacion),
      };
    });

    this.evaluacionesPorTipo = valores;
  }

  private payloadEvaluaciones() {
    return this.tiposEvaluables
      .map((tipo) => {
        const evaluacion = this.evaluacionTipo(tipo.tipo_entrevista_id);

        return {
          tipoId: tipo.tipo_entrevista_id,
          existe: evaluacion.existe,
          nombreResultadoId: Number(evaluacion.resultadoId),
          observacion: evaluacion.observacion.trim() || null,
        };
      })
      .filter((item) =>
        Number.isFinite(item.nombreResultadoId) &&
        item.nombreResultadoId > 0,
      );
  }

  private normalizar(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-');
  }
}
