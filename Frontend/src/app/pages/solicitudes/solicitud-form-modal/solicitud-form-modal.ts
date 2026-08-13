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
import { Observable, catchError, forkJoin, of, switchMap, take, timeout } from 'rxjs';
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

@Component({
  selector: 'app-solicitud-form-modal',
  imports: [CommonModule, ReactiveFormsModule, AlertRegion, Button, CompactSelect, FormActions, FormSection, Modal, Stepper],
  templateUrl: './solicitud-form-modal.html',
  styleUrl: './solicitud-form-modal.scss',
})
export class SolicitudFormModal implements OnInit {
  @Input() idSolicitud: string | null = null;
  @Input() modo: 'crear' | 'ver' | 'editar' = 'crear';
  @Input() codigoSolicitudSugerido = '';
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
    general: ['titulo', 'id_cargo', 'id_cliente'],
    condiciones: ['id_prioridad', 'cantidad_vacantes', 'id_modalidad'],
    cronograma: [],
    descripcion: [],
    habilidades: [],
  };

  cargosCatalogo: CatalogoOpcion[] = [];
  clientesCatalogo: CatalogoOpcion[] = [];
  usuariosCatalogo: CatalogoOpcion[] = [];
  reclutadoresCatalogo: CatalogoOpcion[] = [];
  prioridadesCatalogo: CatalogoOpcion[] = [];
  estadosSolicitudCatalogo: CatalogoOpcion[] = [];
  modalidadesCatalogo: CatalogoOpcion[] = [];
  tiposContratoCatalogo: CatalogoOpcion[] = [];
  habilidadesCatalogo: CatalogoOpcion[] = [];
  nivelesHabilidadCatalogo: CatalogoOpcion[] = [];

  formularioSolicitud = new UntypedFormGroup(
    {
      titulo: new UntypedFormControl('', Validators.required),
      descripcion: new UntypedFormControl(''),
      id_cargo: new UntypedFormControl(null, Validators.required),
      id_prioridad: new UntypedFormControl(null, Validators.required),
      cantidad_vacantes: new UntypedFormControl(1, [Validators.required, Validators.min(1)]),
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
  ) {}

  ngOnInit() {
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
      return this.estadosSolicitudCatalogo.find((estado) => estado.id === estadoId)?.nombre ?? 'Estado registrado';
    }

    return 'Pendiente al guardar';
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
    if (this.codigoSolicitud) {
      return `Solicitud ${this.codigoSolicitud}`;
    }

    if (this.idSolicitud) {
      return `Solicitud ${this.idSolicitud}`;
    }

    return 'El código se asignará automáticamente al guardar.';
  }

  get codigoEncabezado() {
    return this.codigoSolicitud || this.codigoSolicitudSugerido || 'SOL-000001';
  }

  get etiquetaCodigoEncabezado() {
    return 'Código solicitud';
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
    this.alerta = null;

    forkJoin({
      solicitud: this.solicitudesService.obtenerPorId(id),
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
      .subscribe({
        next: ({
          solicitud,
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
        }) => {
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
          this.aplicarSolicitudDetalle(solicitud);
          this.cargandoDetalle = false;
          this.aplicarModoFormulario();
        },
        error: (error) => {
          this.cargandoDetalle = false;
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo cargar el detalle de la solicitud.'),
          };
          this.aplicarModoFormulario();
        },
      });
  }

  cargarCatalogosFormulario() {
    this.cargandoDetalle = true;

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
        this.cargandoDetalle = false;
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

  eliminarHabilidad(indice: number) {
    if (this.modo === 'ver') {
      return;
    }

    this.habilidadesFormArray.removeAt(indice);
  }

  cerrarAlerta() {
    this.alerta = null;
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
    const empresasPorId = new Map(
      catalogos.empresas.map((empresa) => [empresa.emp_id, empresa.emp_nombre ?? 'Empresa sin nombre']),
    );
    this.clientesCatalogo = catalogos.clientes.map((cliente) => ({
      id: cliente.cli_id,
      nombre: this.nombreCliente(cliente, empresasPorId),
    }));
    // Integración catálogo de cargos -> selector "Cargo solicitado" del formulario de solicitudes.
    this.cargosCatalogo = catalogos.cargos.map((cargo) => ({
      id: cargo.crgo_id,
      nombre: cargo.crgo_nombre ?? 'Cargo sin nombre',
    }));
    // Integración catálogo de usuarios -> selectores "Solicitante" y "Responsable".
    this.usuariosCatalogo = catalogos.usuarios.map((usuario) => ({
      id: usuario.usr_id,
      nombre: this.nombreUsuario(usuario),
    }));
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

  private esReclutadorActivo(usuario: UsuarioCatalogoApi) {
    const rol = usuario.rol?.rol_nombre ?? '';
    const estado = usuario.estado?.esusr_nombre ?? '';
    return rol.toLowerCase() === 'reclutador' && estado.toLowerCase() === 'activo';
  }

  private fechaParaInput(fecha?: string | null) {
    return fecha ? fecha.slice(0, 10) : '';
  }

  private horaParaInput(hora?: string | null) {
    return hora ? hora.slice(0, 5) : '';
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
    if (this.clientesCatalogo.length === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'No hay clientes disponibles para seleccionar.',
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
        mensaje: 'No hay clientes disponibles para seleccionar.',
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
