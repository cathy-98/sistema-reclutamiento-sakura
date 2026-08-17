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
import { Observable, catchError, finalize, forkJoin, of, switchMap, take, timeout } from 'rxjs';
import {
  CargoCatalogoApi,
  CatalogosService,
  EstadoSolicitudCatalogoApi,
  HabilidadCatalogoApi,
  ModalidadCatalogoApi,
  NivelHabilidadCatalogoApi,
  PrioridadSolicitudCatalogoApi,
  TipoContratoCatalogoApi,
  UsuarioCatalogoApi,
} from '../../../services/catalogos.service';
import { ClienteApi, ClientesService, EmpresaApi } from '../../../services/clientes.service';
import { AuthService } from '../../../services/auth.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { AlertRegion } from '../../../shared/components/alert-region/alert-region';
import { Button } from '../../../shared/components/button/button';
import { CompactSelect } from '../../../shared/components/compact-select/compact-select';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { FormSection } from '../../../shared/components/form-section/form-section';
import { Modal } from '../../../shared/components/modal/modal';
import { Stepper } from '../../../shared/components/stepper/stepper';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import {
  SolicitudApi,
  SolicitudCreatePayload,
  SolicitudHabilidadPayload,
  SolicitudResumen,
  SolicitudUpdatePayload,
} from '../../../shared/models/solicitud.model';
import { obtenerMensajeError } from '../../../shared/utils/api-error';

interface HabilidadSolicitud {
  id_habilidad: number | null;
  id_nivel_habilidad: number | null;
  anios_experiencia: number;
  es_excluyente: boolean;
}

interface CatalogoOpcion {
  id: number;
  nombre: string;
}

interface CatalogosSolicitud {
  clientes: ClienteApi[];
  empresas: EmpresaApi[];
  cargos: CargoCatalogoApi[];
  usuarios: UsuarioCatalogoApi[];
  prioridades: PrioridadSolicitudCatalogoApi[];
  estados: EstadoSolicitudCatalogoApi[];
  modalidades: ModalidadCatalogoApi[];
  tiposContrato: TipoContratoCatalogoApi[];
  habilidades: HabilidadCatalogoApi[];
  nivelesHabilidad: NivelHabilidadCatalogoApi[];
}

const SOLICITUD_DETALLE_TIMEOUT_MS = 6000;
const CATALOGOS_DETALLE_TIMEOUT_MS = 3000;

@Component({
  selector: 'app-solicitud-form-modal',
  imports: [CommonModule, ReactiveFormsModule, AlertRegion, Button, CompactSelect, FormActions, FormSection, Modal, Stepper],
  templateUrl: './solicitud-form-modal.html',
  styleUrl: './solicitud-form-modal.scss',
})
export class SolicitudFormModal implements OnInit {
  @Input() idSolicitud: string | null = null;
  @Input() modo: 'crear' | 'ver' | 'editar' = 'crear';
  @Input() codigoSolicitudInicial = '';
  @Input() codigoSolicitudSugerido = '';
  @Input() solicitudResumenInicial: SolicitudResumen | null = null;
  @Output() cerrar = new EventEmitter<void>();
  @Output() guardado = new EventEmitter<void>();

  cargandoDetalle = false;
  guardando = false;
  tabFormulario = 'general';
  alerta: AlertaUi | null = null;
  codigoSolicitud: string | null = null;

  pasosFormulario = [
    { clave: 'general', numero: 1, titulo: 'Información general' },
    { clave: 'condiciones', numero: 2, titulo: 'Condiciones' },
    { clave: 'cronograma', numero: 3, titulo: 'Cronograma' },
    { clave: 'descripcion', numero: 4, titulo: 'Descripción' },
    { clave: 'habilidades', numero: 5, titulo: 'Habilidades' },
  ];

  camposPorPaso: Record<string, string[]> = {
    general: ['titulo', 'id_cargo', 'id_empresa_cliente', 'id_cliente'],
    condiciones: ['id_prioridad', 'cantidad_vacantes', 'id_modalidad'],
    cronograma: [],
    descripcion: [],
    habilidades: [],
  };

  cargosCatalogo: CatalogoOpcion[] = [];
  clientesCatalogo: CatalogoOpcion[] = [];
  empresasCatalogo: CatalogoOpcion[] = [];
  usuariosCatalogo: CatalogoOpcion[] = [];
  reclutadoresCatalogo: CatalogoOpcion[] = [];
  prioridadesCatalogo: CatalogoOpcion[] = [];
  estadosSolicitudCatalogo: CatalogoOpcion[] = [];
  modalidadesCatalogo: CatalogoOpcion[] = [];
  tiposContratoCatalogo: CatalogoOpcion[] = [];
  habilidadesCatalogo: CatalogoOpcion[] = [];
  nivelesHabilidadCatalogo: CatalogoOpcion[] = [];
  creandoEmpresa = false;
  creandoCliente = false;
  creandoCargo = false;
  mostrarCreacionCargo = false;
  mostrarCreacionEmpresa = false;
  mostrarCreacionCliente = false;
  private clientesBase: ClienteApi[] = [];

  formularioSolicitud = new UntypedFormGroup(
    {
      titulo: new UntypedFormControl('', Validators.required),
      descripcion: new UntypedFormControl(''),
      id_cargo: new UntypedFormControl(null, Validators.required),
      id_prioridad: new UntypedFormControl(null, Validators.required),
      cantidad_vacantes: new UntypedFormControl(1, [Validators.required, Validators.min(1)]),
      id_empresa_cliente: new UntypedFormControl(null, Validators.required),
      id_cliente: new UntypedFormControl(null, Validators.required),
      id_usuario_solicitante: new UntypedFormControl(null),
      id_usuario_responsable: new UntypedFormControl(null),
      id_modalidad: new UntypedFormControl(null, Validators.required),
      id_tipo_contrato: new UntypedFormControl(null),
      salario_minimo: new UntypedFormControl(null),
      salario_maximo: new UntypedFormControl(null),
      fecha_inicio_busqueda: new UntypedFormControl(''),
      fecha_cierre_busqueda: new UntypedFormControl(''),
      fecha_inicio_cliente: new UntypedFormControl(''),
      id_estado_solicitud: new UntypedFormControl(null),
      hora_inicio_jornada: new UntypedFormControl(''),
      hora_fin_jornada: new UntypedFormControl(''),
      nuevo_cargo_nombre: new UntypedFormControl(''),
      nueva_empresa_nombre: new UntypedFormControl(''),
      nuevo_cliente_nombre: new UntypedFormControl(''),
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
  private habilidadesOriginales: HabilidadSolicitud[] = [];

  constructor(
    private solicitudesService: SolicitudesService,
    private catalogosService: CatalogosService,
    private clientesService: ClientesService,
    private authService: AuthService,
  ) {}

  ngOnInit() {
    this.formularioSolicitud.get('id_empresa_cliente')?.valueChanges.subscribe(() => {
      this.actualizarClientesCatalogo();
    });

    if (this.idSolicitud) {
      this.cargarSolicitud(this.idSolicitud);
      return;
    }

    this.cargarCatalogosFormulario();
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

  get estadoSolicitudTexto() {
    const estadoId = this.numeroONull(this.formularioSolicitud.get('id_estado_solicitud')?.value);

    if (estadoId != null) {
      return this.estadosSolicitudCatalogo.find((estado) => estado.id === estadoId)?.nombre ?? this.solicitudResumenInicial?.estado ?? 'Pendiente';
    }

    return 'Pendiente';
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
    if (this.modo === 'ver') {
      return '';
    }

    if (this.codigoSolicitud) {
      return `Solicitud ${this.codigoSolicitud}`;
    }

    if (this.idSolicitud) {
      return `Solicitud ${this.idSolicitud}`;
    }

    return 'El código se asignará automáticamente al guardar.';
  }

  get codigoEncabezado() {
    if (this.modo !== 'crear') {
      return this.codigoSolicitud || this.codigoSolicitudInicial || 'Pendiente';
    }

    return this.codigoSolicitud || this.codigoSolicitudSugerido || 'Pendiente';
  }

  get etiquetaCodigoEncabezado() {
    return 'Código solicitud';
  }

  get detalleCliente() {
    return this.detalleCatalogo('id_cliente', this.clientesCatalogo, this.solicitudResumenInicial?.cliente ?? 'Sin cliente');
  }

  get detalleEmpresaCliente() {
    return this.detalleCatalogo('id_empresa_cliente', this.empresasCatalogo, 'Sin empresa cliente');
  }

  get detalleCargo() {
    return this.detalleCatalogo('id_cargo', this.cargosCatalogo, this.solicitudResumenInicial?.cargo ?? 'Sin cargo');
  }

  get detallePrioridad() {
    return this.detalleCatalogo('id_prioridad', this.prioridadesCatalogo, this.solicitudResumenInicial?.prioridad ?? 'Sin prioridad');
  }

  get detalleResponsable() {
    return this.detalleCatalogo(
      'id_usuario_responsable',
      this.usuariosCatalogo,
      this.solicitudResumenInicial?.responsable ?? 'Sin asignar',
    );
  }

  get solicitanteInternoActual() {
    return this.detalleUsuario('id_usuario_solicitante') || this.authService.obtenerNombreVisible();
  }

  get empresaClienteSeleccionada() {
    return this.numeroONull(this.formularioSolicitud.get('id_empresa_cliente')?.value) != null;
  }

  get detalleRangoSalario() {
    const minimo = this.numeroONull(this.formularioSolicitud.get('salario_minimo')?.value);
    const maximo = this.numeroONull(this.formularioSolicitud.get('salario_maximo')?.value);

    if (minimo == null && maximo == null) {
      return 'Sin rango informado';
    }

    if (minimo != null && maximo != null) {
      return `${this.formatearMonto(minimo)} - ${this.formatearMonto(maximo)}`;
    }

    return minimo != null ? `Desde ${this.formatearMonto(minimo)}` : `Hasta ${this.formatearMonto(maximo as number)}`;
  }

  get detalleJornada() {
    const inicio = this.detalleTexto('hora_inicio_jornada', 'Sin hora');
    const fin = this.detalleTexto('hora_fin_jornada', 'Sin hora');

    if (inicio === 'Sin hora' && fin === 'Sin hora') {
      return 'Sin jornada informada';
    }

    return `${inicio} - ${fin}`;
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
    const puedeMostrarResumen = this.modo === 'ver' && this.solicitudResumenInicial;
    this.cargandoDetalle = !puedeMostrarResumen;
    this.alerta = null;

    if (puedeMostrarResumen) {
      this.aplicarSolicitudResumenInicial();
      this.aplicarModoFormulario();
    }

    forkJoin({
      solicitud: this.solicitudesService.obtenerPorId(id).pipe(
        timeout(SOLICITUD_DETALLE_TIMEOUT_MS),
        catchError((error) => {
          console.warn('No se pudo cargar el detalle completo de la solicitud.', error);
          return of(null);
        }),
      ),
      catalogos: this.obtenerCatalogosDetalle(),
    })
      .pipe(take(1))
      .subscribe(({ solicitud, catalogos }) => {
        this.aplicarCatalogos(catalogos);

        if (solicitud) {
          this.aplicarSolicitudDetalle(solicitud);
        } else if (!puedeMostrarResumen) {
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: 'No se pudo cargar el detalle de la solicitud.',
          };
        }

        this.cargandoDetalle = false;
        this.aplicarModoFormulario();
      });
  }

  cargarCatalogosDetalle() {
    this.obtenerCatalogosDetalle()
      .pipe(take(1))
      .subscribe((catalogos) => {
        this.aplicarCatalogos(catalogos);
      });
  }

  private obtenerCatalogosDetalle(): Observable<CatalogosSolicitud> {
    return forkJoin({
      clientes: this.clientesService.listarClientes().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      empresas: this.clientesService.listarEmpresas().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      cargos: this.catalogosService.listarCargos().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      usuarios: this.catalogosService.listarUsuarios().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      prioridades: this.catalogosService.listarPrioridadesSolicitud().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      estados: this.catalogosService.listarEstadosSolicitud().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      modalidades: this.catalogosService.listarModalidades().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      tiposContrato: this.catalogosService.listarTiposContrato().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      habilidades: this.catalogosService.listarHabilidades().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
      nivelesHabilidad: this.catalogosService.listarNivelesHabilidad().pipe(timeout(CATALOGOS_DETALLE_TIMEOUT_MS), catchError(() => of([]))),
    });
  }

  cargarCatalogosFormulario() {
    forkJoin({
      clientes: this.clientesService.listarClientes().pipe(timeout(4000), catchError(() => of([]))),
      empresas: this.clientesService.listarEmpresas().pipe(timeout(4000), catchError(() => of([]))),
      cargos: this.catalogosService.listarCargos().pipe(timeout(4000), catchError(() => of([]))),
      usuarios: this.catalogosService.listarUsuarios().pipe(timeout(4000), catchError(() => of([]))),
      prioridades: this.catalogosService.listarPrioridadesSolicitud().pipe(timeout(4000), catchError(() => of([]))),
      estados: this.catalogosService.listarEstadosSolicitud().pipe(timeout(4000), catchError(() => of([]))),
      modalidades: this.catalogosService.listarModalidades().pipe(timeout(4000), catchError(() => of([]))),
      tiposContrato: this.catalogosService.listarTiposContrato().pipe(timeout(4000), catchError(() => of([]))),
      habilidades: this.catalogosService.listarHabilidades().pipe(timeout(4000), catchError(() => of([]))),
      nivelesHabilidad: this.catalogosService.listarNivelesHabilidad().pipe(timeout(4000), catchError(() => of([]))),
    })
      .pipe(take(1))
      .subscribe(({ clientes, empresas, cargos, usuarios, prioridades, estados, modalidades, tiposContrato, habilidades, nivelesHabilidad }) => {
        this.aplicarCatalogos({
          clientes,
          empresas,
          cargos,
          usuarios,
          prioridades,
          estados,
          modalidades,
          tiposContrato,
          habilidades,
          nivelesHabilidad,
        });
        this.aplicarModoFormulario();
      });
  }

  aplicarModoFormulario() {
    if (this.modo === 'ver') {
      this.formularioSolicitud.disable();
      this.nuevaHabilidad.disable();
      return;
    }

    this.formularioSolicitud.enable();
    this.nuevaHabilidad.enable();
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

    if (this.modo === 'ver' || this.guardando) {
      return;
    }

    if (this.modo === 'crear' && this.creacionBloqueadaPorDependencias()) {
      return;
    }

    if (this.formularioSolicitud.invalid || !this.validarHabilidadesSolicitud()) {
      this.formularioSolicitud.markAllAsTouched();
      return;
    }

    if (this.modo === 'crear') {
      this.crearSolicitud();
      return;
    }

    this.actualizarSolicitud();
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

  crearEmpresaCliente() {
    const nombre = String(this.formularioSolicitud.get('nueva_empresa_nombre')?.value ?? '').trim();

    if (!nombre || this.creandoEmpresa || this.modo === 'ver') {
      this.formularioSolicitud.get('nueva_empresa_nombre')?.markAsTouched();
      return;
    }

    const empresaExistente = this.empresasCatalogo.find((empresa) => this.normalizarTexto(empresa.nombre) === this.normalizarTexto(nombre));
    if (empresaExistente) {
      this.formularioSolicitud.patchValue({
        nueva_empresa_nombre: '',
        id_empresa_cliente: empresaExistente.id,
        id_cliente: null,
      });
      this.mostrarCreacionEmpresa = false;
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'La empresa ya existe. La dejamos seleccionada.',
      };
      return;
    }

    this.creandoEmpresa = true;
    this.clientesService
      .crearEmpresa({ emp_nombre: nombre })
      .pipe(
        timeout(6000),
        finalize(() => {
          this.creandoEmpresa = false;
        }),
        take(1),
      )
      .subscribe({
        next: (empresa) => {
          this.mostrarCreacionEmpresa = false;
          this.empresasCatalogo = [
            ...this.empresasCatalogo,
            { id: empresa.emp_id, nombre: empresa.emp_nombre ?? nombre },
          ].sort((a, b) => a.nombre.localeCompare(b.nombre));
          this.formularioSolicitud.patchValue({
            nueva_empresa_nombre: '',
            id_empresa_cliente: empresa.emp_id,
            id_cliente: null,
          });
          this.actualizarClientesCatalogo();
        },
        error: (error) => {
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo crear la empresa cliente.'),
          };
        },
      });
  }

  crearCargoSolicitado() {
    const nombre = String(this.formularioSolicitud.get('nuevo_cargo_nombre')?.value ?? '').trim();

    if (!nombre || this.creandoCargo || this.modo === 'ver') {
      this.formularioSolicitud.get('nuevo_cargo_nombre')?.markAsTouched();
      return;
    }

    const cargoExistente = this.cargosCatalogo.find((cargo) => this.normalizarTexto(cargo.nombre) === this.normalizarTexto(nombre));
    if (cargoExistente) {
      this.formularioSolicitud.patchValue({
        nuevo_cargo_nombre: '',
        id_cargo: cargoExistente.id,
      });
      this.mostrarCreacionCargo = false;
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'El cargo ya existe. Lo dejamos seleccionado.',
      };
      return;
    }

    this.creandoCargo = true;
    this.catalogosService
      .crearCargo({ crgo_nombre: nombre })
      .pipe(
        timeout(6000),
        finalize(() => {
          this.creandoCargo = false;
        }),
        take(1),
      )
      .subscribe({
        next: (cargo) => {
          this.mostrarCreacionCargo = false;
          this.cargosCatalogo = [
            ...this.cargosCatalogo,
            { id: cargo.crgo_id, nombre: cargo.crgo_nombre ?? nombre },
          ].sort((a, b) => a.nombre.localeCompare(b.nombre));
          this.formularioSolicitud.patchValue({
            nuevo_cargo_nombre: '',
            id_cargo: cargo.crgo_id,
          });
        },
        error: (error) => {
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo crear el cargo solicitado.'),
          };
        },
      });
  }

  crearClienteSolicitante() {
    const nombre = String(this.formularioSolicitud.get('nuevo_cliente_nombre')?.value ?? '').trim();
    const empresaId = this.numeroONull(this.formularioSolicitud.get('id_empresa_cliente')?.value);

    if (!nombre || empresaId == null || this.creandoCliente || this.modo === 'ver') {
      this.formularioSolicitud.get('nuevo_cliente_nombre')?.markAsTouched();
      this.formularioSolicitud.get('id_empresa_cliente')?.markAsTouched();
      return;
    }

    const clienteExistente = this.clientesBase.find(
      (cliente) => cliente.cli_empresa_id === empresaId && this.normalizarTexto(cliente.cli_nombre) === this.normalizarTexto(nombre),
    );
    if (clienteExistente) {
      this.actualizarClientesCatalogo();
      this.formularioSolicitud.patchValue({
        nuevo_cliente_nombre: '',
        id_cliente: clienteExistente.cli_id,
      });
      this.mostrarCreacionCliente = false;
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'El cliente solicitante ya existe para esa empresa. Lo dejamos seleccionado.',
      };
      return;
    }

    this.creandoCliente = true;
    this.clientesService
      .crearCliente({ cli_nombre: nombre, cli_empresa_id: empresaId })
      .pipe(
        timeout(6000),
        finalize(() => {
          this.creandoCliente = false;
        }),
        take(1),
      )
      .subscribe({
        next: (cliente) => {
          this.clientesBase = [...this.clientesBase, cliente];
          this.actualizarClientesCatalogo();
          this.formularioSolicitud.patchValue({
            nuevo_cliente_nombre: '',
            id_cliente: cliente.cli_id,
          });
          this.mostrarCreacionCliente = false;
        },
        error: (error) => {
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo crear el cliente solicitante.'),
          };
        },
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

  detalleTexto(control: string, fallback = 'Sin información') {
    const valor = String(this.formularioSolicitud.get(control)?.value ?? '').trim();
    return valor || fallback;
  }

  detalleNumero(control: string, fallback = 'Sin información') {
    const valor = this.numeroONull(this.formularioSolicitud.get(control)?.value);
    return valor == null ? fallback : String(valor);
  }

  detalleFecha(control: string) {
    const valor = this.detalleTexto(control, '');

    if (!valor) {
      return 'Sin fecha';
    }

    const [year, month, day] = valor.split('-');
    return year && month && day ? `${day}-${month}-${year}` : valor;
  }

  detalleCatalogo(control: string, catalogo: CatalogoOpcion[], fallback: string) {
    const id = this.numeroONull(this.formularioSolicitud.get(control)?.value);
    return id == null ? fallback : catalogo.find((item) => item.id === id)?.nombre ?? fallback;
  }

  detalleUsuario(control: string) {
    return this.detalleCatalogo(control, this.usuariosCatalogo, 'Sin asignar');
  }

  private aplicarSolicitudResumenInicial() {
    const resumen = this.solicitudResumenInicial;

    if (!resumen) {
      return;
    }

    this.codigoSolicitud = resumen.codigo;
    this.formularioSolicitud.patchValue({
      titulo: resumen.nombre ?? '',
      descripcion: resumen.observacion ?? '',
      cantidad_vacantes: resumen.vacantes ?? 1,
      fecha_inicio_busqueda: this.fechaResumenParaInput(resumen.seleccion),
      fecha_inicio_cliente: this.fechaResumenParaInput(resumen.inicioEmpleo),
    }, { emitEvent: false });
  }

  private aplicarSolicitudDetalle(solicitud: SolicitudApi) {
    this.codigoSolicitud = solicitud.sol_codigo ?? null;

    this.formularioSolicitud.patchValue({
      titulo: solicitud.sol_titulo ?? '',
      descripcion: solicitud.sol_descripcion ?? solicitud.sol_observacion ?? '',
      id_cargo: solicitud.sol_cargo_id ?? null,
      id_prioridad: solicitud.sol_prioridad_id ?? null,
      cantidad_vacantes: solicitud.sol_cantidad_vacantes ?? 1,
      id_cliente: solicitud.sol_cliente_id ?? null,
      id_usuario_solicitante: solicitud.sol_usuario_creador_id ?? null,
      id_usuario_responsable: solicitud.sol_usuario_asignado_id ?? null,
      id_modalidad: solicitud.sol_modalidad_id ?? null,
      id_tipo_contrato: solicitud.sol_tipo_contrato_id ?? null,
      salario_minimo: solicitud.sol_salario_min ?? null,
      salario_maximo: solicitud.sol_salario_max ?? null,
      fecha_inicio_busqueda: this.fechaParaInput(solicitud.sol_fecha_inicio_busqueda),
      fecha_cierre_busqueda: this.fechaParaInput(solicitud.sol_fecha_cierre_busqueda),
      fecha_inicio_cliente: this.fechaParaInput(solicitud.sol_fecha_inicio_cliente),
      id_estado_solicitud: solicitud.sol_estado_solicitud_id ?? null,
      hora_inicio_jornada: this.horaParaInput(solicitud.sol_hora_inicio_jornada),
      hora_fin_jornada: this.horaParaInput(solicitud.sol_hora_fin_jornada),
    });

    this.habilidadesFormArray.clear();
    this.habilidadesOriginales = [];
    (solicitud.habilidades ?? []).forEach((habilidad) => {
      const habilidadFormulario = {
        id_habilidad: habilidad.solhb_habilidad_id ?? null,
        id_nivel_habilidad: habilidad.solhb_nivel_habilidad_id ?? null,
        anios_experiencia: habilidad.solhb_anios_experiencia_req ?? 0,
        es_excluyente: habilidad.solhb_es_excluyente ?? false,
      };

      this.habilidadesOriginales.push(habilidadFormulario);
      this.habilidadesFormArray.push(this.crearHabilidadForm(habilidadFormulario));
    });

    this.actualizarEmpresaDesdeCliente();
    this.actualizarClientesCatalogo();
  }

  private aplicarCatalogos(catalogos: {
    clientes: ClienteApi[];
    empresas: EmpresaApi[];
    cargos: CargoCatalogoApi[];
    usuarios: UsuarioCatalogoApi[];
    prioridades: PrioridadSolicitudCatalogoApi[];
    estados: EstadoSolicitudCatalogoApi[];
    modalidades: ModalidadCatalogoApi[];
    tiposContrato: TipoContratoCatalogoApi[];
    habilidades: HabilidadCatalogoApi[];
    nivelesHabilidad: NivelHabilidadCatalogoApi[];
  }) {
    this.clientesBase = catalogos.clientes;
    this.empresasCatalogo = catalogos.empresas.map((empresa) => ({
      id: empresa.emp_id,
      nombre: empresa.emp_nombre ?? 'Empresa sin nombre',
    }));
    this.actualizarEmpresaDesdeCliente();
    this.actualizarClientesCatalogo();
    // Integración catálogo de cargos -> selector "Cargo solicitado" del formulario de solicitudes.
    this.cargosCatalogo = catalogos.cargos.map((cargo) => ({
      id: cargo.crgo_id,
      nombre: cargo.crgo_nombre ?? 'Cargo sin nombre',
    }));
    // Integración catálogo de usuarios -> solicitante interno y reclutador asignado.
    this.usuariosCatalogo = catalogos.usuarios.map((usuario) => ({
      id: usuario.usr_id,
      nombre: this.nombreUsuario(usuario),
    }));
    this.aplicarSolicitanteInternoPorDefecto();
    this.reclutadoresCatalogo = catalogos.usuarios
      .filter((usuario) => this.esReclutadorActivo(usuario))
      .map((usuario) => ({
        id: usuario.usr_id,
        nombre: this.nombreUsuario(usuario),
      }));
    // Integración catálogo de prioridades -> selector "Prioridad".
    this.prioridadesCatalogo = catalogos.prioridades.map((prioridad) => ({
      id: prioridad.prsol_id,
      nombre: prioridad.prsol_nombre ?? 'Sin prioridad',
    }));
    // Integración catálogo de estados de solicitud -> selector "Estado".
    this.estadosSolicitudCatalogo = catalogos.estados.map((estado) => ({
      id: estado.essl_id,
      nombre: estado.essl_nombre ?? 'Sin estado',
    }));
    // Integración catálogo de modalidades -> selector "Modalidad".
    this.modalidadesCatalogo = catalogos.modalidades.map((modalidad) => ({
      id: modalidad.mdld_id,
      nombre: modalidad.mdld_nombre ?? 'Sin modalidad',
    }));
    // Integración catálogo de tipos de contrato -> selector "Tipo de contrato".
    this.tiposContratoCatalogo = catalogos.tiposContrato.map((tipoContrato) => ({
      id: tipoContrato.tpct_id,
      nombre: tipoContrato.tpct_nombre ?? 'Sin tipo de contrato',
    }));
    // Integración catálogo de habilidades -> selector "Tecnología" en requisitos técnicos.
    this.habilidadesCatalogo = catalogos.habilidades.map((habilidad) => ({
      id: habilidad.hab_id,
      nombre: habilidad.hab_nombre ?? 'Habilidad sin nombre',
    }));
    // Integración catálogo de niveles de habilidad -> selector "Nivel técnico".
    this.nivelesHabilidadCatalogo = catalogos.nivelesHabilidad.map((nivel) => ({
      id: nivel.nvhb_id,
      nombre: nivel.nvhb_nombre ?? 'Nivel sin nombre',
    }));
  }

  private nombreUsuario(usuario: UsuarioCatalogoApi) {
    return [usuario.usr_nombres, usuario.usr_apellido_paterno, usuario.usr_apellido_materno]
      .filter(Boolean)
      .join(' ') || usuario.usr_email;
  }

  private nombreCliente(cliente: ClienteApi, empresasPorId: Map<number, string>) {
    const empresa = cliente.cli_empresa_id ? empresasPorId.get(cliente.cli_empresa_id) : null;
    return empresa ? `${cliente.cli_nombre} - ${empresa}` : cliente.cli_nombre;
  }

  private actualizarEmpresaDesdeCliente() {
    const clienteId = this.numeroONull(this.formularioSolicitud.get('id_cliente')?.value);
    const empresaActual = this.numeroONull(this.formularioSolicitud.get('id_empresa_cliente')?.value);
    const cliente = this.clientesBase.find((item) => item.cli_id === clienteId);

    if (cliente?.cli_empresa_id && empresaActual == null) {
      this.formularioSolicitud.patchValue({ id_empresa_cliente: cliente.cli_empresa_id }, { emitEvent: false });
    }
  }

  private actualizarClientesCatalogo() {
    const empresaId = this.numeroONull(this.formularioSolicitud.get('id_empresa_cliente')?.value);
    const empresasPorId = new Map(this.empresasCatalogo.map((empresa) => [empresa.id, empresa.nombre]));
    const clienteActual = this.numeroONull(this.formularioSolicitud.get('id_cliente')?.value);
    const clientesFiltrados = this.clientesBase.filter((cliente) => empresaId == null || cliente.cli_empresa_id === empresaId);

    this.clientesCatalogo = clientesFiltrados.map((cliente) => ({
      id: cliente.cli_id,
      nombre: empresaId == null ? this.nombreCliente(cliente, empresasPorId) : cliente.cli_nombre,
    }));

    if (clienteActual != null && !clientesFiltrados.some((cliente) => cliente.cli_id === clienteActual)) {
      this.formularioSolicitud.patchValue({ id_cliente: null }, { emitEvent: false });
    }
  }

  private aplicarSolicitanteInternoPorDefecto() {
    const usuarioActualId = this.authService.obtenerUsuarioId();

    if (usuarioActualId) {
      this.formularioSolicitud.patchValue({
        id_usuario_solicitante: this.formularioSolicitud.get('id_usuario_solicitante')?.value ?? usuarioActualId,
      }, { emitEvent: false });
    }
  }

  private esReclutadorActivo(usuario: UsuarioCatalogoApi) {
    const rol = usuario.rol?.rol_nombre ?? '';
    const estado = usuario.estado?.esusr_nombre ?? '';
    return rol.toLowerCase() === 'reclutador' && estado.toLowerCase() === 'activo';
  }

  private fechaParaInput(fecha?: string | null) {
    return fecha ? fecha.slice(0, 10) : '';
  }

  private fechaResumenParaInput(fecha?: string | null) {
    if (!fecha || fecha === 'Sin fecha') {
      return '';
    }

    const [day, month, year] = fecha.split('-');
    return year && month && day ? `${year}-${month}-${day}` : fecha;
  }

  private horaParaInput(hora?: string | null) {
    return hora ? hora.slice(0, 5) : '';
  }

  private formatearMonto(valor: number) {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: 'CLP',
      maximumFractionDigits: 0,
    }).format(valor);
  }

  private crearSolicitud() {
    const payload = this.crearPayloadCreacion();

    if (!payload) {
      return;
    }

    this.guardando = true;
    this.solicitudesService
      .crear(payload)
      .pipe(take(1))
      .subscribe({
        next: () => {
          this.guardando = false;
          this.guardado.emit();
        },
        error: (error) => {
          this.guardando = false;
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo crear la solicitud.'),
          };
        },
      });
  }

  private creacionBloqueadaPorDependencias() {
    if (this.empresasCatalogo.length === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona o crea una empresa cliente antes de guardar.',
      };
      this.tabFormulario = 'general';
      return true;
    }

    if (this.clientesCatalogo.length === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona o crea un cliente solicitante antes de guardar.',
      };
      this.tabFormulario = 'general';
      return true;
    }

    return false;
  }

  private actualizarSolicitud() {
    if (!this.idSolicitud) {
      return;
    }

    this.guardando = true;
    this.solicitudesService
      .actualizar(this.idSolicitud, this.crearPayloadActualizacion())
      .pipe(switchMap(() => this.sincronizarHabilidadesEditadas(this.idSolicitud as string)), take(1))
      .subscribe({
        next: () => {
          this.guardando = false;
          this.guardado.emit();
        },
        error: (error) => {
          this.guardando = false;
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo actualizar la solicitud.'),
          };
        },
      });
  }

  private crearPayloadCreacion(): SolicitudCreatePayload | null {
    const valor = this.formularioSolicitud.getRawValue();
    const clienteId = this.numeroONull(valor.id_cliente);
    const { sol_cantidad_vacantes: _vacantes, ...payloadBase } = this.crearPayloadBase();

    if (clienteId == null) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona o crea un cliente solicitante antes de guardar.',
      };
      this.tabFormulario = 'general';
      return null;
    }

    return {
      ...payloadBase,
      sol_cantidad_vacantes: this.numeroOValor(valor.cantidad_vacantes, 1),
      sol_cliente_id: clienteId,
      habilidades: this.crearPayloadHabilidades(),
    };
  }

  private crearPayloadActualizacion(): SolicitudUpdatePayload {
    const valor = this.formularioSolicitud.getRawValue();

    return {
      ...this.crearPayloadBase(),
      sol_cliente_id: this.numeroONull(valor.id_cliente),
    };
  }

  private crearPayloadBase() {
    const valor = this.formularioSolicitud.getRawValue();

    return {
      sol_titulo: String(valor.titulo ?? '').trim(),
      sol_descripcion: this.textoONull(valor.descripcion),
      sol_cantidad_vacantes: this.numeroONull(valor.cantidad_vacantes),
      sol_salario_min: this.numeroONull(valor.salario_minimo),
      sol_salario_max: this.numeroONull(valor.salario_maximo),
      sol_fecha_inicio_busqueda: this.fechaONull(valor.fecha_inicio_busqueda),
      sol_fecha_cierre_busqueda: this.fechaONull(valor.fecha_cierre_busqueda),
      sol_fecha_inicio_cliente: this.fechaONull(valor.fecha_inicio_cliente),
      sol_hora_inicio_jornada: this.textoONull(valor.hora_inicio_jornada),
      sol_hora_fin_jornada: this.textoONull(valor.hora_fin_jornada),
      sol_cargo_id: this.numeroONull(valor.id_cargo),
      sol_prioridad_id: this.numeroONull(valor.id_prioridad),
      sol_usuario_asignado_id: this.numeroONull(valor.id_usuario_responsable),
      sol_modalidad_id: this.numeroONull(valor.id_modalidad),
      sol_tipo_contrato_id: this.numeroONull(valor.id_tipo_contrato),
    };
  }

  private crearPayloadHabilidades(): SolicitudHabilidadPayload[] {
    return this.habilidadesSolicitud
      .filter((habilidad) => habilidad.id_habilidad != null)
      .map((habilidad) => ({
        solhb_habilidad_id: habilidad.id_habilidad as number,
        solhb_nivel_habilidad_id: habilidad.id_nivel_habilidad,
        solhb_anios_experiencia_req: habilidad.anios_experiencia,
        solhb_es_excluyente: habilidad.es_excluyente,
      }));
  }

  private sincronizarHabilidadesEditadas(idSolicitud: string): Observable<unknown> {
    const habilidadesActuales = this.habilidadesSolicitud;
    const eliminaciones = this.habilidadesOriginales
      .filter((original) => !habilidadesActuales.some((actual) => this.mismaHabilidad(original, actual)))
      .filter((habilidad) => habilidad.id_habilidad != null)
      .map((habilidad) => this.solicitudesService.eliminarHabilidad(idSolicitud, habilidad.id_habilidad as number));
    const nuevas = habilidadesActuales.filter(
      (actual) => !this.habilidadesOriginales.some((original) => this.mismaHabilidad(original, actual)),
    );
    const payloadNuevas = nuevas
      .filter((habilidad) => habilidad.id_habilidad != null)
      .map((habilidad) => ({
        solhb_habilidad_id: habilidad.id_habilidad as number,
        solhb_nivel_habilidad_id: habilidad.id_nivel_habilidad,
        solhb_anios_experiencia_req: habilidad.anios_experiencia,
        solhb_es_excluyente: habilidad.es_excluyente,
      }));
    const operaciones: Observable<unknown>[] = [...eliminaciones];

    if (payloadNuevas.length > 0) {
      operaciones.push(this.solicitudesService.agregarHabilidades(idSolicitud, payloadNuevas));
    }

    if (operaciones.length === 0) {
      return of(null);
    }

    return forkJoin(operaciones);
  }

  private mismaHabilidad(a: HabilidadSolicitud, b: HabilidadSolicitud) {
    return (
      a.id_habilidad === b.id_habilidad &&
      a.id_nivel_habilidad === b.id_nivel_habilidad &&
      a.anios_experiencia === b.anios_experiencia &&
      a.es_excluyente === b.es_excluyente
    );
  }

  private numeroONull(valor: unknown) {
    if (valor === null || valor === undefined || valor === '') {
      return null;
    }

    const numero = Number(valor);
    return Number.isNaN(numero) ? null : numero;
  }

  private numeroOValor(valor: unknown, fallback: number) {
    return this.numeroONull(valor) ?? fallback;
  }

  private normalizarTexto(valor: string) {
    return valor.trim().replace(/\s+/g, ' ').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  private textoONull(valor: unknown) {
    const texto = String(valor ?? '').trim();
    return texto || null;
  }

  private fechaONull(valor: unknown) {
    const texto = this.textoONull(valor);
    return texto ? `${texto}T00:00:00` : null;
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
