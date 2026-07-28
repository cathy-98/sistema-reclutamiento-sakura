import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { ReactiveFormsModule, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { DataTable, DataTableColumn } from '../../../shared/components/data-table/data-table';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { FormField } from '../../../shared/components/form-field/form-field';
import { FormSection } from '../../../shared/components/form-section/form-section';
import { Modal } from '../../../shared/components/modal/modal';
import { Stepper } from '../../../shared/components/stepper/stepper';
import { EntrevistaPayload, TipoEntrevista } from '../../../services/entrevistas.service';

interface IntegranteEntrevista {
  id: string;
  nombre: string;
  rol: string;
  fechaAgendamiento: string;
}

@Component({
  selector: 'app-entrevista-form-modal',
  imports: [CommonModule, ReactiveFormsModule, Button, DataTable, FormActions, FormField, FormSection, Modal, Stepper],
  templateUrl: './entrevista-form-modal.html',
  styleUrl: './entrevista-form-modal.scss',
})
export class EntrevistaFormModal {
  @Output() cerrar = new EventEmitter<void>();
  @Output() guardar = new EventEmitter<EntrevistaPayload>();

  readonly tipos: TipoEntrevista[] = ['Reclutamiento', 'Técnica', 'Operacional'];
  readonly modalidades: EntrevistaPayload['modalidad'][] = ['Online', 'Presencial', 'Híbrida'];
  readonly duraciones = ['30 min', '45 min', '60 min', '90 min'];
  integrantesSeleccionados = new Set(['macarena-lopez', 'felipe-valdes']);
  tabFormulario = 'datos';

  pasosFormulario = [
    { clave: 'datos', numero: 1, titulo: 'Datos' },
    { clave: 'agenda', numero: 2, titulo: 'Agenda' },
    { clave: 'integrantes', numero: 3, titulo: 'Integrantes' },
    { clave: 'detalle', numero: 4, titulo: 'Detalle' },
  ];

  camposPorPaso: Record<string, string[]> = {
    datos: ['idSolicitud', 'candidato', 'cargo'],
    agenda: ['tipo', 'fecha', 'horaInicio', 'horaFin', 'modalidad'],
    integrantes: ['entrevistador'],
    detalle: ['asunto'],
  };

  columnasIntegrantes: DataTableColumn<IntegranteEntrevista>[] = [
    { key: 'nombre', label: 'Nombre', width: 180 },
    { key: 'rol', label: 'Rol', width: 150 },
    {
      key: 'fechaAgendamiento',
      label: 'Fecha agendamiento',
      width: 170,
      value: () => String(this.formulario.get('fecha')?.value || 'Sin fecha'),
    },
  ];

  integrantes: IntegranteEntrevista[] = [
    { id: 'macarena-lopez', nombre: 'Macarena Lopez', rol: 'Candidata', fechaAgendamiento: 'Sin fecha' },
    { id: 'valentina-rojas', nombre: 'Valentina Rojas', rol: 'Candidata', fechaAgendamiento: 'Sin fecha' },
    { id: 'felipe-valdes', nombre: 'Felipe Valdes', rol: 'Reclutador', fechaAgendamiento: 'Sin fecha' },
    { id: 'cathy', nombre: 'Cathy', rol: 'Area tecnica', fechaAgendamiento: 'Sin fecha' },
  ];

  formulario = new UntypedFormGroup({
    idSolicitud: new UntypedFormControl(null, Validators.required),
    candidato: new UntypedFormControl(null, Validators.required),
    tipo: new UntypedFormControl(null, Validators.required),
    asunto: new UntypedFormControl('', Validators.required),
    cargo: new UntypedFormControl('', Validators.required),
    fecha: new UntypedFormControl('', Validators.required),
    horaInicio: new UntypedFormControl('', Validators.required),
    horaFin: new UntypedFormControl('', Validators.required),
    duracion: new UntypedFormControl('45 min', Validators.required),
    modalidad: new UntypedFormControl('Online', Validators.required),
    entrevistador: new UntypedFormControl('', Validators.required),
    linkReunion: new UntypedFormControl(''),
    observacion: new UntypedFormControl(''),
  });

  get pasosCompletados() {
    return this.pasosFormulario
      .filter((paso) => this.pasoCompletado(paso.clave))
      .map((paso) => paso.clave);
  }

  enviar() {
    this.formulario.markAllAsTouched();

    if (this.formulario.invalid || !this.horarioValido()) {
      return;
    }

    this.guardar.emit(this.formulario.getRawValue() as EntrevistaPayload);
  }

  control(nombre: string) {
    return this.formulario.get(nombre);
  }

  horarioValido() {
    const inicio = String(this.formulario.get('horaInicio')?.value || '');
    const fin = String(this.formulario.get('horaFin')?.value || '');
    return !inicio || !fin || fin > inicio;
  }

  cambiarTabFormulario(tab: string) {
    const indiceDestino = this.pasosFormulario.findIndex((paso) => paso.clave === tab);

    if (indiceDestino > this.pasoActualIndice() && !this.validarPaso(this.tabFormulario)) {
      return;
    }

    this.tabFormulario = tab;
  }

  pasoActualIndice() {
    return this.pasosFormulario.findIndex((paso) => paso.clave === this.tabFormulario);
  }

  pasoCompletado(clave: string) {
    const indicePaso = this.pasosFormulario.findIndex((paso) => paso.clave === clave);
    return indicePaso < this.pasoActualIndice();
  }

  volverPaso() {
    const indiceActual = this.pasoActualIndice();

    if (indiceActual > 0) {
      this.tabFormulario = this.pasosFormulario[indiceActual - 1].clave;
    }
  }

  siguientePaso() {
    if (!this.validarPaso(this.tabFormulario)) {
      return;
    }

    const indiceActual = this.pasoActualIndice();

    if (indiceActual < this.pasosFormulario.length - 1) {
      this.tabFormulario = this.pasosFormulario[indiceActual + 1].clave;
    }
  }

  esUltimoPaso() {
    return this.pasoActualIndice() === this.pasosFormulario.length - 1;
  }

  validarPaso(clave: string) {
    const controles = this.camposPorPaso[clave] ?? [];
    controles.forEach((nombre) => this.control(nombre)?.markAsTouched());

    const controlesValidos = controles.every((nombre) => this.control(nombre)?.valid);

    if (clave === 'agenda') {
      return controlesValidos && this.horarioValido();
    }

    return controlesValidos;
  }

  seleccionarTipo(tipo: TipoEntrevista) {
    this.formulario.get('tipo')?.setValue(tipo);
    this.formulario.get('tipo')?.markAsTouched();
  }

  agregarIntegrante() {
    const entrevistador = String(this.formulario.get('entrevistador')?.value ?? '').trim();

    if (!entrevistador || this.integrantes.some((integrante) => integrante.nombre === entrevistador)) {
      return;
    }

    const id = entrevistador.toLowerCase().replace(/\s+/g, '-');

    this.integrantes = [
      ...this.integrantes,
      {
        id,
        nombre: entrevistador,
        rol: 'Entrevistador',
        fechaAgendamiento: String(this.formulario.get('fecha')?.value || 'Sin fecha'),
      },
    ];
    this.integrantesSeleccionados = new Set([...this.integrantesSeleccionados, id]);
  }

  obtenerIdIntegrante(integrante: IntegranteEntrevista) {
    return integrante.id;
  }

  actualizarSeleccionIntegrantes(ids: Set<string>) {
    this.integrantesSeleccionados = ids;
  }
}
