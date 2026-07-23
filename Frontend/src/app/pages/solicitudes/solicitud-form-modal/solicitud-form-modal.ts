import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import {
  AbstractControl,
  ReactiveFormsModule,
  UntypedFormArray,
  UntypedFormControl,
  UntypedFormGroup,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { Alert } from '../../../shared/components/alert/alert';
import { Button } from '../../../shared/components/button/button';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { FormSection } from '../../../shared/components/form-section/form-section';
import { Modal } from '../../../shared/components/modal/modal';
import { Stepper } from '../../../shared/components/stepper/stepper';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';

interface HabilidadSolicitud {
  id_habilidad: number | null;
  id_nivel_habilidad: number | null;
  anios_experiencia: number;
  es_excluyente: boolean;
}

type CatalogoActivo = '' | 'cargo' | 'area' | 'cliente' | 'habilidad';

@Component({
  selector: 'app-solicitud-form-modal',
  imports: [CommonModule, ReactiveFormsModule, Alert, Button, FormActions, FormSection, Modal, Stepper],
  templateUrl: './solicitud-form-modal.html',
  styleUrl: './solicitud-form-modal.scss',
})
export class SolicitudFormModal implements OnInit {
  @Input() idSolicitud: string | null = null;
  @Input() modo: 'crear' | 'ver' | 'editar' = 'crear';
  @Output() cerrar = new EventEmitter<void>();

  cargandoDetalle = false;
  tabFormulario = 'general';
  catalogoActivo: CatalogoActivo = '';
  alerta: AlertaUi | null = null;
  nuevoValorCatalogo = new UntypedFormControl('');

  pasosFormulario = [
    { clave: 'general', numero: 1, titulo: 'Información general' },
    { clave: 'condiciones', numero: 2, titulo: 'Condiciones' },
    { clave: 'cronograma', numero: 3, titulo: 'Cronograma' },
    { clave: 'descripcion', numero: 4, titulo: 'Descripción' },
    { clave: 'habilidades', numero: 5, titulo: 'Habilidades' },
  ];

  camposPorPaso: Record<string, string[]> = {
    general: ['titulo', 'id_cargo', 'id_area', 'id_cliente', 'id_usuario_solicitante'],
    condiciones: ['id_prioridad', 'cantidad_vacantes', 'id_modalidad', 'id_estado_solicitud'],
    cronograma: [],
    descripcion: [],
    habilidades: [],
  };

  cargosCatalogo = [
    { id: 1, nombre: 'Desarrollador Python' },
    { id: 2, nombre: 'Desarrollador Angular' },
    { id: 3, nombre: 'Analista QA' },
  ];

  areasCatalogo = [
    { id: 1, nombre: 'Tecnología' },
    { id: 2, nombre: 'Operaciones' },
    { id: 3, nombre: 'Recursos Humanos' },
  ];

  clientesCatalogo = [
    { id: 1, nombre: 'Banco Elitsoft' },
  ];

  habilidadesCatalogo = [
    { id: 1, nombre: 'Python' },
    { id: 2, nombre: 'SQL' },
    { id: 3, nombre: 'Angular' },
    { id: 4, nombre: 'Git' },
  ];

  nivelesHabilidadCatalogo = [
    { id: 1, nombre: 'Trainee' },
    { id: 2, nombre: 'Junior' },
    { id: 3, nombre: 'Semi Senior' },
    { id: 4, nombre: 'Senior' },
  ];

  formularioSolicitud = new UntypedFormGroup(
    {
      titulo: new UntypedFormControl('', Validators.required),
      descripcion: new UntypedFormControl(''),
      id_cargo: new UntypedFormControl(null, Validators.required),
      id_prioridad: new UntypedFormControl(null, Validators.required),
      cantidad_vacantes: new UntypedFormControl(1, [Validators.required, Validators.min(1)]),
      id_cliente: new UntypedFormControl(null, Validators.required),
      id_usuario_solicitante: new UntypedFormControl(null, Validators.required),
      id_usuario_responsable: new UntypedFormControl(null),
      id_modalidad: new UntypedFormControl(null, Validators.required),
      salario_minimo: new UntypedFormControl(null),
      salario_maximo: new UntypedFormControl(null),
      fecha_inicio_busqueda: new UntypedFormControl(''),
      fecha_cierre_busqueda: new UntypedFormControl(''),
      fecha_inicio_cliente: new UntypedFormControl(''),
      id_estado_solicitud: new UntypedFormControl(null, Validators.required),
      id_area: new UntypedFormControl(null, Validators.required),
      hora_inicio_jornada: new UntypedFormControl(''),
      hora_fin_jornada: new UntypedFormControl(''),
      habilidades: new UntypedFormArray([]),
    },
    { validators: this.validarRangoSalario },
  );

  nuevaHabilidad = new UntypedFormGroup({
    id_habilidad: new UntypedFormControl(null, Validators.required),
    id_nivel_habilidad: new UntypedFormControl(null, Validators.required),
    anios_experiencia: new UntypedFormControl(0, [Validators.required, Validators.min(0)]),
    es_excluyente: new UntypedFormControl(false),
  });

  solicitudesDemo = [
    {
      id: 'Req-001',
      titulo: 'Desarrollador Python Senior',
      descripcion: 'Perfil crítico para continuidad del equipo backend.',
      id_cargo: 1,
      id_prioridad: 1,
      cantidad_vacantes: 2,
      id_cliente: 1,
      id_usuario_solicitante: 3,
      id_usuario_responsable: 3,
      id_modalidad: 2,
      salario_minimo: 1800000,
      salario_maximo: 2400000,
      fecha_inicio_busqueda: '2026-06-01',
      fecha_cierre_busqueda: '2026-06-30',
      fecha_inicio_cliente: '2026-07-15',
      id_estado_solicitud: 1,
      id_area: 1,
      hora_inicio_jornada: '09:00',
      hora_fin_jornada: '18:00',
      habilidades: [
        { id_habilidad: 1, id_nivel_habilidad: 4, anios_experiencia: 4, es_excluyente: true },
      ] as HabilidadSolicitud[],
    },
    {
      id: 'Req-002',
      titulo: 'Desarrollador Python Junior',
      descripcion: 'Requiere disponibilidad para onboarding durante julio.',
      id_cargo: 1,
      id_prioridad: 2,
      cantidad_vacantes: 2,
      id_cliente: 1,
      id_usuario_solicitante: 3,
      id_usuario_responsable: 3,
      id_modalidad: 3,
      salario_minimo: 900000,
      salario_maximo: 1300000,
      fecha_inicio_busqueda: '2026-06-01',
      fecha_cierre_busqueda: '2026-06-30',
      fecha_inicio_cliente: '2026-07-15',
      id_estado_solicitud: 2,
      id_area: 1,
      hora_inicio_jornada: '09:00',
      hora_fin_jornada: '18:00',
      habilidades: [
        { id_habilidad: 1, id_nivel_habilidad: 2, anios_experiencia: 1, es_excluyente: true },
        { id_habilidad: 4, id_nivel_habilidad: 2, anios_experiencia: 1, es_excluyente: false },
      ] as HabilidadSolicitud[],
    },
    {
      id: 'Req-003',
      titulo: 'Analista QA',
      descripcion: 'Solicitud cubierta con candidato interno.',
      id_cargo: 3,
      id_prioridad: 3,
      cantidad_vacantes: 1,
      id_cliente: 1,
      id_usuario_solicitante: 1,
      id_usuario_responsable: 1,
      id_modalidad: 1,
      salario_minimo: 1000000,
      salario_maximo: 1500000,
      fecha_inicio_busqueda: '2026-07-10',
      fecha_cierre_busqueda: '2026-07-30',
      fecha_inicio_cliente: '2026-08-05',
      id_estado_solicitud: 3,
      id_area: 1,
      hora_inicio_jornada: '09:00',
      hora_fin_jornada: '18:00',
      habilidades: [
        { id_habilidad: 2, id_nivel_habilidad: 3, anios_experiencia: 2, es_excluyente: true },
      ] as HabilidadSolicitud[],
    },
  ];

  ngOnInit() {
    if (this.idSolicitud) {
      this.cargarSolicitud(this.idSolicitud);
      return;
    }

    this.aplicarModoFormulario();
  }

  get habilidadesFormArray() {
    return this.formularioSolicitud.get('habilidades') as UntypedFormArray;
  }

  get habilidadesSolicitud() {
    return this.habilidadesFormArray.getRawValue() as HabilidadSolicitud[];
  }

  get descripcionLength() {
    return String(this.formularioSolicitud.get('descripcion')?.value ?? '').length;
  }

  get pasosCompletados() {
    return this.pasosFormulario
      .filter((paso) => this.pasoCompletado(paso.clave))
      .map((paso) => paso.clave);
  }

  control(nombre: string) {
    return this.formularioSolicitud.get(nombre);
  }

  get tituloModal() {
    if (this.modo === 'ver') {
      return 'Detalle de la solicitud';
    }

    if (this.modo === 'editar') {
      return 'Editar solicitud de vacante';
    }

    return 'Nueva solicitud de vacante';
  }

  get subtituloModal() {
    if (this.idSolicitud) {
      return `Solicitud ${this.idSolicitud}`;
    }

    return 'Completa la información para crear una solicitud.';
  }

  validarRangoSalario(control: AbstractControl): ValidationErrors | null {
    const salarioMinimo = Number(control.get('salario_minimo')?.value);
    const salarioMaximo = Number(control.get('salario_maximo')?.value);

    if (!salarioMinimo || !salarioMaximo) {
      return null;
    }

    return salarioMinimo <= salarioMaximo ? null : { rangoSalarioInvalido: true };
  }

  cargarSolicitud(id: string) {
    this.cargandoDetalle = true;

    window.setTimeout(() => {
      const solicitud = this.solicitudesDemo.find((item) => item.id === id);

      if (solicitud) {
        const { id: _id, habilidades, ...datosFormulario } = solicitud;
        this.formularioSolicitud.patchValue(datosFormulario);
        this.habilidadesFormArray.clear();
        habilidades.forEach((habilidad) => this.habilidadesFormArray.push(this.crearHabilidadForm(habilidad)));
      }

      this.cargandoDetalle = false;
      this.aplicarModoFormulario();
    }, 300);
  }

  aplicarModoFormulario() {
    if (this.modo === 'ver') {
      this.formularioSolicitud.disable();
      this.nuevaHabilidad.disable();
      this.nuevoValorCatalogo.disable();
      return;
    }

    this.formularioSolicitud.enable();
    this.nuevaHabilidad.enable();
    this.nuevoValorCatalogo.enable();
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
    const indiceActual = this.pasoActualIndice();

    if (!this.validarPaso(this.tabFormulario)) {
      return;
    }

    if (indiceActual < this.pasosFormulario.length - 1) {
      this.tabFormulario = this.pasosFormulario[indiceActual + 1].clave;
    }
  }

  esUltimoPaso() {
    return this.pasoActualIndice() === this.pasosFormulario.length - 1;
  }

  guardarSolicitud() {
    this.alerta = null;

    if (this.formularioSolicitud.invalid || !this.validarHabilidadesSolicitud()) {
      this.formularioSolicitud.markAllAsTouched();
      return;
    }

    console.log('Guardar solicitud', this.formularioSolicitud.getRawValue());
  }

  validarPaso(clave: string) {
    const controles = this.camposPorPaso[clave] ?? [];
    this.alerta = null;

    controles.forEach((nombre) => this.control(nombre)?.markAsTouched());

    if (clave === 'condiciones') {
      this.formularioSolicitud.updateValueAndValidity();
    }

    const pasoValido =
      controles.every((nombre) => this.control(nombre)?.valid) &&
      !this.formularioSolicitud.hasError('rangoSalarioInvalido');

    if (clave === 'habilidades') {
      return pasoValido && this.validarHabilidadesSolicitud();
    }

    return pasoValido;
  }

  manejarSeleccionCatalogo(catalogo: CatalogoActivo, valor: string | number | null) {
    if (valor !== 'crear') {
      return;
    }

    this.catalogoActivo = catalogo;
    this.nuevoValorCatalogo.setValue('');

    if (catalogo === 'cargo') {
      this.formularioSolicitud.get('id_cargo')?.setValue(null);
    }

    if (catalogo === 'area') {
      this.formularioSolicitud.get('id_area')?.setValue(null);
    }

    if (catalogo === 'cliente') {
      this.formularioSolicitud.get('id_cliente')?.setValue(null);
    }

    if (catalogo === 'habilidad') {
      this.nuevaHabilidad.get('id_habilidad')?.setValue(null);
    }
  }

  guardarNuevoCatalogo() {
    const nombre = String(this.nuevoValorCatalogo.value ?? '').trim();

    if (!nombre) {
      return;
    }

    if (this.catalogoActivo === 'cargo') {
      const nuevoId = this.siguienteId(this.cargosCatalogo);
      this.cargosCatalogo.push({ id: nuevoId, nombre });
      this.formularioSolicitud.get('id_cargo')?.setValue(nuevoId);
    }

    if (this.catalogoActivo === 'area') {
      const nuevoId = this.siguienteId(this.areasCatalogo);
      this.areasCatalogo.push({ id: nuevoId, nombre });
      this.formularioSolicitud.get('id_area')?.setValue(nuevoId);
    }

    if (this.catalogoActivo === 'cliente') {
      const nuevoId = this.siguienteId(this.clientesCatalogo);
      this.clientesCatalogo.push({ id: nuevoId, nombre });
      this.formularioSolicitud.get('id_cliente')?.setValue(nuevoId);
    }

    if (this.catalogoActivo === 'habilidad') {
      const nuevoId = this.siguienteId(this.habilidadesCatalogo);
      this.habilidadesCatalogo.push({ id: nuevoId, nombre });
      this.nuevaHabilidad.get('id_habilidad')?.setValue(nuevoId);
    }

    this.cancelarNuevoCatalogo();
  }

  cancelarNuevoCatalogo() {
    this.catalogoActivo = '';
    this.nuevoValorCatalogo.setValue('');
  }

  siguienteId(catalogo: { id: number; nombre: string }[]) {
    return Math.max(...catalogo.map((item) => item.id), 0) + 1;
  }

  agregarHabilidad() {
    this.alerta = null;

    if (this.nuevaHabilidad.invalid || this.modo === 'ver') {
      this.nuevaHabilidad.markAllAsTouched();
      return;
    }

    this.habilidadesFormArray.push(this.crearHabilidadForm(this.nuevaHabilidad.getRawValue()));
    this.nuevaHabilidad.reset({
      id_habilidad: null,
      id_nivel_habilidad: null,
      anios_experiencia: 0,
      es_excluyente: false,
    });
  }

  eliminarHabilidad(indice: number) {
    if (this.modo === 'ver') {
      return;
    }

    this.habilidadesFormArray.removeAt(indice);
  }

  cerrarAlerta() {
    this.alerta = null;
  }

  crearHabilidadForm(habilidad: HabilidadSolicitud) {
    return new UntypedFormGroup({
      id_habilidad: new UntypedFormControl(habilidad.id_habilidad),
      id_nivel_habilidad: new UntypedFormControl(habilidad.id_nivel_habilidad),
      anios_experiencia: new UntypedFormControl(habilidad.anios_experiencia),
      es_excluyente: new UntypedFormControl(habilidad.es_excluyente),
    });
  }

  obtenerNombreHabilidad(id: number | null) {
    return this.habilidadesCatalogo.find((habilidad) => habilidad.id === id)?.nombre ?? 'Habilidad';
  }

  obtenerNombreNivel(id: number | null) {
    return this.nivelesHabilidadCatalogo.find((nivel) => nivel.id === id)?.nombre ?? 'Nivel';
  }

  habilidadExcluyenteClase(esExcluyente: boolean) {
    return esExcluyente ? 'excluyente' : 'no-excluyente';
  }

  private validarHabilidadesSolicitud() {
    if (this.habilidadesSolicitud.length === 0) {
      this.tabFormulario = 'habilidades';
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Agrega al menos una habilidad técnica para la solicitud.',
      };
      return false;
    }

    const tieneExcluyente = this.habilidadesSolicitud.some((habilidad) => habilidad.es_excluyente);

    if (!tieneExcluyente) {
      this.tabFormulario = 'habilidades';
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Marca al menos una habilidad como excluyente para evaluar candidatos.',
      };
      return false;
    }

    return true;
  }
}
