import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormsModule, ReactiveFormsModule, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { Modal } from '../../../shared/components/modal/modal';
import { NombreResultadoCatalogoApi } from '../../../services/catalogos.service';
import { EntrevistaApi, EntrevistaResumen, EvaluacionEntrevistaApi } from '../../../services/entrevistas.service';

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
  imports: [CommonModule, FormsModule, ReactiveFormsModule, Button, FormActions, Modal],
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
  @Input() cargandoDetalle = false;
  @Input() error = '';
  @Input() errorEvaluaciones = '';
  @Input() mensajeEvaluaciones = '';
  @Input() usuarioActualId: number | null = null;
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

  constructor() {}

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
    return this.mostrarResultadosPorArea || this.feedbackSoloConsulta
      ? 'Feedback de entrevista'
      : this.modo === 'reprogramar'
        ? 'Reprogramar entrevista'
        : this.modo === 'cancelar'
          ? 'Cancelar entrevista'
          : this.modo === 'confirmar'
            ? 'Confirmar entrevista'
            : this.modo === 'realizar'
              ? 'Marcar entrevista realizada'
              : this.modo === 'no-asistio'
                ? 'Registrar no asistencia'
        : this.modo === 'ver'
          ? 'Detalle de entrevista'
          : 'Gestionar entrevista';
  }

  get subtituloModal() {
    if (this.mostrarResultadosPorArea) {
      return '';
    }

    if (this.esLectura) {
      return `${this.entrevista?.idSolicitud || 'Sin solicitud'} · ${this.entrevista?.cargo || 'Sin cargo'}`;
    }

    return this.entrevista?.idSolicitud || '';
  }

  get accion() {
    if (this.modo === 'reprogramar') {
      return 'Guardar reprogramación';
    }

    if (this.mostrarResultadosPorArea && !this.mostrarSelectorEstado) {
      return 'Guardar feedback';
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
    if (!this.solicitudPermiteAcciones) {
      return [];
    }

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
    return (
      ['reprogramar', 'cancelar', 'no-asistio'].includes(this.accionSeleccionada) ||
      ['reprogramar', 'cancelar', 'no-asistio'].includes(this.modo)
    );
  }

  get varianteAccion() {
    return (
      this.accionSeleccionada === 'cancelar' ||
      this.accionSeleccionada === 'no-asistio' ||
      this.modo === 'cancelar' ||
      this.modo === 'no-asistio'
    )
      ? 'danger'
      : 'primary';
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

  get mostrarGestionEstado() {
    return !this.esLectura && !this.mostrarResultadosPorArea && !this.feedbackSoloConsulta;
  }

  get mostrarBotonGestion() {
    if (!this.mostrarGestionEstado) {
      return false;
    }

    return this.modo !== 'gestionar' || Boolean(this.accionSeleccionada);
  }

  get mostrarResultadosPorArea() {
    return this.modo === 'gestionar' &&
      this.estadoActualNormalizado === 'realizada';
  }

  get feedbackSoloConsulta() {
    return false;
  }

  get mensajeFeedbackSoloConsulta() {
    return this.solicitudCancelada
      ? 'Esta solicitud está cancelada. No permite agendar nuevas entrevistas.'
      : 'No se pudo confirmar que la solicitud permita registrar feedback. Los feedbacks registrados quedan disponibles solo para consulta.';
  }

  get estadoPostulacionActual() {
    return this.entrevista?.estadoPostulacion || 'Sin estado';
  }

  get estadoSolicitudActual() {
    return this.entrevista?.estadoSolicitud || '';
  }

  get estadoSolicitudPresentado() {
    return this.solicitudCancelada
      ? 'Cancelada'
      : this.estadoSolicitudActual;
  }

  get solicitudDetalle() {
    const solicitud = this.entrevista?.idSolicitud || 'Sin solicitud';
    return this.estadoSolicitudPresentado
      ? `${solicitud} · ${this.estadoSolicitudPresentado}`
      : solicitud;
  }

  get solicitudCancelada() {
    return this.normalizar(this.estadoSolicitudActual) === 'cancelado';
  }

  get solicitudPermiteAcciones() {
    const estadoSolicitud = this.normalizar(this.estadoSolicitudActual);
    const estadoPostulacion = this.normalizar(this.estadoPostulacionActual);

    if (estadoSolicitud !== 'en entrevistas') {
      return false;
    }

    if (estadoPostulacion && estadoPostulacion !== 'en entrevista' && estadoPostulacion !== 'sin estado') {
      return false;
    }

    return true;
  }

  get entrevistaRealizadaSinEvaluacionDisponible() {
    return this.modo === 'gestionar' &&
      this.estadoActualNormalizado === 'realizada' &&
      this.opcionesFeedback.length < 2;
  }

  get tiposEvaluables() {
    return this.detalle?.tipos ?? [];
  }

  get feedbacksRegistrados() {
    return [...(this.detalle?.evaluaciones ?? [])].sort((a, b) =>
      this.fechaFeedbackValor(b) - this.fechaFeedbackValor(a),
    );
  }

  get totalFeedbacksRegistrados() {
    return this.feedbacksRegistrados.length;
  }

  get cantidadFeedbacksDetalle() {
    const total = this.totalFeedbacksRegistrados;
    return `${total} registrado${total === 1 ? '' : 's'}`;
  }

  get textoFeedbacksRegistrados() {
    const total = this.totalFeedbacksRegistrados;
    return `${total} feedback${total === 1 ? '' : 's'} registrado${total === 1 ? '' : 's'}`;
  }

  get tipoFeedbackActivo() {
    return this.tiposEvaluables[0] ?? null;
  }

  get tipoFeedbackActivoId() {
    return this.tipoFeedbackActivo?.tipo_entrevista_id ?? 0;
  }

  get tieneFeedbackHabilitado() {
    return Boolean(this.tipoFeedbackActivo && this.opcionesFeedback.length >= 2);
  }

  get resumenContextual() {
    return `${this.entrevista?.candidato || 'Sin candidato'} · ${this.estadoActual}`;
  }

  get lineaEntrevista() {
    return `Entrevista realizada · ${this.entrevista?.fecha || 'Sin fecha'} · ${this.entrevista?.horaInicio || '--:--'} - ${this.entrevista?.horaFin || '--:--'}`;
  }

  get lineaContextoFeedback() {
    return `${this.entrevista?.idSolicitud || 'Sin solicitud'} · ${this.entrevista?.cargo || 'Sin cargo'}`;
  }

  get lineaAgendaFeedback() {
    return `${this.entrevista?.tipo || 'Tipo no informado'} · ${this.fechaEntrevistaLegible} · ${this.entrevista?.horaInicio || '--:--'} - ${this.entrevista?.horaFin || '--:--'}`;
  }

  get fechaEntrevistaLegible() {
    return this.formatearFechaLegible(this.entrevista?.fecha, false) || this.entrevista?.fecha || 'Sin fecha';
  }

  get linkReunionDetalle() {
    return this.entrevista?.linkReunion || this.detalle?.enlace_reunion || '';
  }

  get opcionAprobado() {
    return this.opcionesFeedback.find((resultado) => this.esResultadoAprobado(resultado.nore_nombre)) ?? this.opcionesFeedback[0] ?? null;
  }

  get opcionNoAprobado() {
    return this.opcionesFeedback.find((resultado, index) =>
      this.esResultadoNoAprobado(resultado.nore_nombre) && resultado.nore_id !== this.opcionAprobado?.nore_id,
    ) ?? this.opcionesFeedback.find((resultado) => resultado.nore_id !== this.opcionAprobado?.nore_id) ?? null;
  }

  get opcionesFeedback() {
    const opciones = this.resultados.filter((resultado) => Boolean(resultado.nore_id));
    const prioridad = ['aprobado', 'aprobado-con-observaciones', 'no-aprobado'];

    return [...opciones].sort((a, b) => {
      const indiceA = prioridad.indexOf(this.normalizar(a.nore_nombre ?? ''));
      const indiceB = prioridad.indexOf(this.normalizar(b.nore_nombre ?? ''));

      return (indiceA === -1 ? 99 : indiceA) - (indiceB === -1 ? 99 : indiceB);
    });
  }

  etiquetaResultado(nombre?: string | null) {
    const normalizado = this.normalizar(nombre ?? '');

    if (normalizado === 'aprobado') {
      return 'Aprobado';
    }

    if (normalizado === 'aprobado-con-observaciones') {
      return 'Aprobado con observaciones';
    }

    if (normalizado === 'no-aprobado') {
      return 'No aprobado';
    }

    return nombre || 'Resultado';
  }

  autorFeedback(evaluacion: EvaluacionEntrevistaApi) {
    return evaluacion.usuario_nombre || 'Entrevistador no informado';
  }

  fechaFeedback(evaluacion: EvaluacionEntrevistaApi) {
    const fecha = evaluacion.fecha_actualizacion || evaluacion.fecha_creacion;

    if (!fecha) {
      return 'Fecha no informada';
    }

    const fechaParsed = new Date(fecha);
    return Number.isNaN(fechaParsed.getTime())
      ? fecha
      : this.formatearFechaLegible(fecha, true);
  }

  private esResultadoAprobado(nombre?: string | null) {
    return this.normalizar(nombre ?? '').includes('aprob');
  }

  private esResultadoNoAprobado(nombre?: string | null) {
    const normalizado = this.normalizar(nombre ?? '');
    return normalizado.includes('no-aprob') || normalizado.includes('rechaz') || normalizado.includes('desaprob');
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

    if (this.accionSeleccionada === 'cancelar' || this.modo === 'cancelar') {
      return 'Esta acción cancelará la entrevista. Indica el motivo para continuar.';
    }

    if (this.accionSeleccionada === 'no-asistio' || this.modo === 'no-asistio') {
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

    if (payload.length === 0) {
      this.errorLocalEvaluaciones = 'Selecciona un resultado e ingresa observaciones antes de guardar.';
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
      const evaluacion = this.usuarioActualId
        ? evaluaciones.find((item) =>
            item.tipo_entrevista_id === tipo.tipo_entrevista_id &&
            item.usuario_id === this.usuarioActualId,
          ) ?? null
        : null;

      valores[tipo.tipo_entrevista_id] = {
        resultadoId: evaluacion?.resultado_id ?? null,
        observacion: evaluacion?.observacion ?? '',
        existe: Boolean(evaluacion),
      };
    });

    this.evaluacionesPorTipo = valores;
  }

  private payloadEvaluaciones() {
    const tipo = this.tipoFeedbackActivo;
    const evaluacion = tipo ? this.evaluacionTipo(tipo.tipo_entrevista_id) : null;

    if (!tipo || !evaluacion) {
      return [];
    }

    return [{
      // Compatibilidad temporal: la UI sigue enviando el tipo requerido por backend,
      // pero el usuario solo ve un feedback breve a nivel de entrevista.
      tipoId: tipo.tipo_entrevista_id,
      existe: evaluacion.existe,
      nombreResultadoId: Number(evaluacion.resultadoId),
      observacion: evaluacion.observacion.trim() || null,
    }].filter((item) =>
      Number.isFinite(item.nombreResultadoId) &&
      item.nombreResultadoId > 0,
    );
  }

  private fechaFeedbackValor(evaluacion: EvaluacionEntrevistaApi) {
    const fecha = evaluacion.fecha_actualizacion || evaluacion.fecha_creacion || '';
    const fechaParsed = new Date(fecha);
    return Number.isNaN(fechaParsed.getTime()) ? 0 : fechaParsed.getTime();
  }

  private formatearFechaLegible(fecha?: string | null, incluirHora = false) {
    if (!fecha) {
      return '';
    }

    const fechaBase = /^\d{4}-\d{2}-\d{2}$/.test(fecha)
      ? new Date(`${fecha}T00:00:00`)
      : new Date(fecha);

    if (Number.isNaN(fechaBase.getTime())) {
      return '';
    }

    const fechaTexto = new Intl.DateTimeFormat('es-CL', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }).format(fechaBase).replace(/\./g, '');

    if (!incluirHora) {
      return fechaTexto;
    }

    const horaTexto = new Intl.DateTimeFormat('es-CL', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(fechaBase);

    return `${fechaTexto} · ${horaTexto}`;
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
