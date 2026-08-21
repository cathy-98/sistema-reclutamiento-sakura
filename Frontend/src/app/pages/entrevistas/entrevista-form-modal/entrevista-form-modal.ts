import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { ReactiveFormsModule, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { DataTable, DataTableColumn } from '../../../shared/components/data-table/data-table';
import { DatePicker } from '../../../shared/components/date-picker/date-picker';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { FormField } from '../../../shared/components/form-field/form-field';
import { FormSection } from '../../../shared/components/form-section/form-section';
import { IconButton } from '../../../shared/components/icon-button/icon-button';
import { Modal } from '../../../shared/components/modal/modal';
import { Stepper } from '../../../shared/components/stepper/stepper';
import { EntrevistaPayload, TipoEntrevista } from '../../../services/entrevistas.service';
import {
  CatalogosService,
  TipoEntrevistaCatalogoApi,
  UsuarioCatalogoApi,
} from '../../../services/catalogos.service';
import {
  CandidatoApi,
  CandidatosService,
  PostulacionCandidatoApi,
} from '../../../services/candidatos.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { SolicitudResumen } from '../../../shared/models/solicitud.model';
import { catchError, finalize, forkJoin, of, take, timeout } from 'rxjs';

interface IntegranteEntrevista {
  id: string;
  nombre: string;
  rol: string;
  fechaAgendamiento: string;
}

export interface EntrevistaCandidatoSeleccionado {
  id?: string;
  solicitudCandidatoId?: number;
  idSolicitud: string;
  nombre: string;
  cargo: string;
}

@Component({
  selector: 'app-entrevista-form-modal',
  imports: [CommonModule, ReactiveFormsModule, Button, DataTable, DatePicker, FormActions, FormField, FormSection, IconButton, Modal, Stepper],
  templateUrl: './entrevista-form-modal.html',
  styleUrl: './entrevista-form-modal.scss',
})
export class EntrevistaFormModal implements OnChanges, OnInit {
  @Input() initialData: Partial<EntrevistaPayload> | null = null;
  @Input() candidatos: EntrevistaCandidatoSeleccionado[] = [];

  @Output() cerrar = new EventEmitter<void>();
  @Output() candidatosChange = new EventEmitter<EntrevistaCandidatoSeleccionado[]>();
  @Output() guardar = new EventEmitter<EntrevistaPayload>();

  tipos: TipoEntrevista[] = [];
  tiposCatalogo: TipoEntrevistaCatalogoApi[] = [];
  solicitudes: SolicitudResumen[] = [];
  candidatosDisponibles: CandidatoApi[] = [];
  postulacionesSolicitud: PostulacionCandidatoApi[] = [];
  postulacionesPorCandidato = new Map<number, PostulacionCandidatoApi[]>();
  cargandoDatos = false;
  cargandoCandidatosSolicitud = false;
  errorEnvio = '';
  readonly duraciones = ['30 min', '45 min', '60 min', '90 min'];
  integrantesSeleccionados = new Set<string>();
  postulacionesSeleccionadas = new Set<number>();
  tabFormulario = 'datos';

  pasosFormulario = [
    { clave: 'datos', numero: 1, titulo: 'Datos' },
    { clave: 'agenda', numero: 2, titulo: 'Agenda' },
    { clave: 'integrantes', numero: 3, titulo: 'Responsables' },
    { clave: 'detalle', numero: 4, titulo: 'Detalle' },
  ];

  camposPorPaso: Record<string, string[]> = {
    datos: ['idSolicitud', 'candidato', 'cargo'],
    agenda: ['tipo', 'fecha', 'horaInicio', 'horaFin'],
    integrantes: [],
    detalle: ['asunto'],
  };

  columnasIntegrantes: DataTableColumn<IntegranteEntrevista>[] = [
    { key: 'nombre', label: 'Nombre', width: 190, wrap: true },
    { key: 'rol', label: 'Rol', width: 160, wrap: true },
    {
      key: 'fechaAgendamiento',
      label: 'Fecha agendamiento',
      width: 170,
      value: () => String(this.formulario.get('fecha')?.value || 'Sin fecha'),
    },
  ];

  integrantes: IntegranteEntrevista[] = [];

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
    entrevistador: new UntypedFormControl(''),
    linkReunion: new UntypedFormControl(''),
    observacion: new UntypedFormControl(''),
  });

  constructor(
    private catalogosService: CatalogosService,
    private candidatosService: CandidatosService,
    private solicitudesService: SolicitudesService,
  ) {}

  ngOnInit() {
    this.cargarCatalogosEntrevista();
    this.cargarDatosSeleccion();
    this.formulario.get('idSolicitud')?.valueChanges.subscribe(() => this.alCambiarSolicitud());
    this.formulario.get('candidato')?.valueChanges.subscribe((candidatoId) => {
      const id = Number(candidatoId);
      if (Number.isFinite(id) && id > 0) {
        this.cargarPostulacionesCandidato(id);
      }
    });
    this.aplicarDatosIniciales();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['initialData'] || changes['candidatos']) {
      this.aplicarDatosIniciales();
    }
  }

  get tituloModal() {
    return this.esAgendaMasiva ? 'Agendar entrevistas masivas' : 'Agendar nueva entrevista';
  }

  get subtituloModal() {
    return this.esAgendaMasiva
      ? 'Define una misma fecha y hora para los candidatos seleccionados.'
      : 'Completa los datos para crear la cita.';
  }

  get esAgendaMasiva() {
    return this.candidatos.length > 1;
  }

  get tieneCandidatosPreseleccionados() {
    return this.candidatos.length > 0;
  }

  get resumenCandidatos() {
    return this.esAgendaMasiva
      ? `${this.candidatos.length} candidatos seleccionados`
      : this.candidatos[0]?.nombre || String(this.control('candidato')?.value || 'Sin candidato');
  }

  get pasosCompletados() {
    return this.pasosFormulario
      .filter((paso) => this.pasoCompletado(paso.clave))
      .map((paso) => paso.clave);
  }

  enviar() {
    this.formulario.markAllAsTouched();
    this.errorEnvio = '';

    const payload = this.crearPayload();

    if (this.formulario.invalid || !this.horarioValido() || !payload) {
      this.errorEnvio = this.mensajePayloadIncompleto();
      return;
    }

    this.guardar.emit(payload);
  }

  get fechaHoyInput() {
    return new Date().toISOString().slice(0, 10);
  }

  get solicitudSeleccionadaCodigo() {
    const valor = this.control('idSolicitud')?.value;
    const solicitudId = this.resolverSolicitudId(valor);

    if (solicitudId) {
      return this.solicitudes.find((solicitud) => Number(solicitud.id) === solicitudId)?.codigo ?? String(valor);
    }

    return typeof valor === 'string' && valor.trim()
      ? valor
      : 'Sin solicitud seleccionada';
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

    if (clave === 'integrantes') {
      return this.integrantesSeleccionadosInternos().length > 0;
    }

    return controlesValidos;
  }

  seleccionarTipo(tipo: TipoEntrevista) {
    this.formulario.get('tipo')?.setValue(tipo);
    this.formulario.get('tipo')?.markAsTouched();
  }

  cargarCatalogosEntrevista() {
    // Integración de catálogos para agenda de entrevistas:
    // - tipos-entrevista alimenta las opciones "Tipo de entrevista".
    // - usuarios alimenta la tabla de integrantes/entrevistadores.
    // Nota BD: tbl_cita_entrevista no tiene columna de modalidad; por eso no se carga aquí.
    forkJoin({
      tipos: this.catalogosService.listarTiposEntrevista().pipe(timeout(4000), catchError(() => of([]))),
      usuarios: this.catalogosService.listarUsuarios().pipe(timeout(4000), catchError(() => of([]))),
    })
      .pipe(take(1))
      .subscribe(({ tipos, usuarios }) => {
        const tiposValidos = tipos.filter((tipo) => this.tipoEntrevistaValido(tipo.tpet_nombre));
        const tiposCatalogo = tiposValidos.map((tipo) => tipo.tpet_nombre).filter((nombre): nombre is string => Boolean(nombre));

        this.tipos = tiposCatalogo;
        this.tiposCatalogo = tiposValidos;

        if (usuarios.length > 0) {
          this.integrantes = usuarios.map((usuario) => this.mapearUsuarioAIntegrante(usuario));
          this.integrantesSeleccionados = new Set();
        }
      });
  }

  cargarDatosSeleccion() {
    this.cargandoDatos = true;

    forkJoin({
      solicitudes: this.solicitudesService.listar().pipe(timeout(5000), catchError(() => of([]))),
      candidatos: this.candidatosService.listar().pipe(timeout(5000), catchError(() => of([]))),
    })
      .pipe(take(1))
      .subscribe(({ solicitudes, candidatos }) => {
        this.solicitudes = solicitudes;
        this.candidatosDisponibles = candidatos;
        this.cargandoDatos = false;
        this.aplicarDatosIniciales();
        this.cargarPostulacionesPreseleccionadas();
      });
  }

  obtenerIdIntegrante(integrante: IntegranteEntrevista) {
    return integrante.id;
  }

  private mapearUsuarioAIntegrante(usuario: UsuarioCatalogoApi): IntegranteEntrevista {
    // Mapeo catálogo usuarios -> tabla "Integrantes": muestra nombre completo y rol del usuario.
    const nombre = [usuario.usr_nombres, usuario.usr_apellido_paterno, usuario.usr_apellido_materno]
      .filter(Boolean)
      .join(' ') || usuario.usr_email;

    return {
      id: String(usuario.usr_id),
      nombre,
      rol: usuario.rol?.rol_nombre ?? 'Usuario',
      fechaAgendamiento: 'Sin fecha',
    };
  }

  actualizarSeleccionIntegrantes(ids: Set<string>) {
    this.integrantesSeleccionados = ids;
  }

  private tipoEntrevistaValido(nombre?: string | null) {
    const normalizado = this.crearId(nombre ?? '');
    return Boolean(normalizado) && normalizado !== 'ingles';
  }

  nombreCandidato(candidato: CandidatoApi) {
    return [candidato.cand_nombres, candidato.cand_apellido_paterno, candidato.cand_apellido_materno]
      .filter(Boolean)
      .join(' ') || candidato.cand_email || `Candidato ${candidato.cand_id}`;
  }

  candidatosSolicitudDisponibles() {
    const solicitudId = this.resolverSolicitudId(this.formulario.get('idSolicitud')?.value);

    if (!solicitudId) {
      return [];
    }

    return this.postulacionesSolicitud
      .map((postulacion) => this.candidatoDesdePostulacion(postulacion))
      .filter((candidato): candidato is CandidatoApi => Boolean(candidato));
  }

  postulacionMarcada(postulacionId: number) {
    return this.postulacionesSeleccionadas.has(postulacionId);
  }

  alternarPostulacion(postulacion: PostulacionCandidatoApi, seleccionado: boolean) {
    const postulaciones = new Set(this.postulacionesSeleccionadas);

    if (seleccionado) {
      postulaciones.add(postulacion.slcd_id);
    } else {
      postulaciones.delete(postulacion.slcd_id);
    }

    this.postulacionesSeleccionadas = postulaciones;
    this.sincronizarControlCandidato();
  }

  seleccionarTodasPostulaciones() {
    this.postulacionesSeleccionadas = new Set(this.postulacionesSolicitud.map((postulacion) => postulacion.slcd_id));
    this.sincronizarControlCandidato();
  }

  limpiarPostulaciones() {
    this.postulacionesSeleccionadas = new Set();
    this.sincronizarControlCandidato();
  }

  nombrePostulacion(postulacion: PostulacionCandidatoApi) {
    const candidato = this.candidatoDesdePostulacion(postulacion);
    return candidato ? this.nombreCandidato(candidato) : `Candidato ${postulacion.slcd_candidato_id ?? ''}`.trim();
  }

  detallePostulacion(postulacion: PostulacionCandidatoApi) {
    const candidato = this.candidatoDesdePostulacion(postulacion);
    return [
      candidato?.cand_email,
      `Postulación ${postulacion.slcd_id}`,
    ].filter(Boolean).join(' - ');
  }

  alCambiarSolicitud() {
    if (this.tieneCandidatosPreseleccionados) {
      return;
    }

    const solicitudId = this.resolverSolicitudId(this.formulario.get('idSolicitud')?.value);

    this.formulario.patchValue({ candidato: null, cargo: '' }, { emitEvent: false });
    this.postulacionesSolicitud = [];
    this.postulacionesSeleccionadas = new Set();
    this.actualizarCargoDesdeSolicitud();

    if (!solicitudId || this.tieneCandidatosPreseleccionados) {
      return;
    }

    this.cargarCandidatosSolicitud(solicitudId);
  }

  eliminarCandidatoAgenda(candidato: EntrevistaCandidatoSeleccionado) {
    const candidatosActualizados = this.candidatos.filter(
      (item) => this.obtenerIdCandidatoAgenda(item) !== this.obtenerIdCandidatoAgenda(candidato),
    );

    if (candidatosActualizados.length === 0) {
      this.cerrar.emit();
      return;
    }

    this.candidatos = candidatosActualizados;
    this.candidatosChange.emit(candidatosActualizados);
    this.aplicarDatosIniciales();
  }

  private aplicarDatosIniciales() {
    if (this.initialData) {
      this.formulario.patchValue(this.initialData);
    }

    if (!this.tieneCandidatosPreseleccionados) {
      return;
    }

    const primerCandidato = this.candidatos[0];

    this.formulario.patchValue({
      idSolicitud: this.esAgendaMasiva ? 'Múltiples solicitudes' : primerCandidato.idSolicitud,
      candidato: this.esAgendaMasiva ? `${this.candidatos.length} candidatos seleccionados` : primerCandidato.nombre,
      cargo: this.esAgendaMasiva ? 'Múltiples cargos' : primerCandidato.cargo,
      asunto:
        this.formulario.get('asunto')?.value ||
        (this.esAgendaMasiva ? 'Agendamiento de entrevistas' : `Entrevista ${primerCandidato.idSolicitud}`),
    });

    this.sincronizarIntegrantesPreseleccionados();
    this.cargarPostulacionesPreseleccionadas();
  }

  private sincronizarIntegrantesPreseleccionados() {
    this.integrantesSeleccionados = new Set(Array.from(this.integrantesSeleccionados));
  }

  private crearId(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-');
  }

  private obtenerIdCandidatoAgenda(candidato: EntrevistaCandidatoSeleccionado) {
    return candidato.id || this.crearId(`${candidato.idSolicitud}-${candidato.nombre}`);
  }

  private crearPayload(): EntrevistaPayload | null {
    const raw = this.formulario.getRawValue() as EntrevistaPayload;
    const tipoEntrevistaId = this.resolverTipoEntrevistaId(raw.tipo);
    const entrevistadorIds = this.integrantesSeleccionadosInternos();
    const postulacionesSeleccionadas = this.postulacionesSeleccionadasIds();

    const solicitudesCandidatosIds = this.esAgendaMasiva
      ? this.candidatos.map((candidato) => this.resolverSolicitudCandidatoId(candidato)).filter((id): id is number => Boolean(id))
      : postulacionesSeleccionadas.length > 1
        ? postulacionesSeleccionadas
        : [];

    const solicitudCandidatoId = this.esAgendaMasiva
      ? solicitudesCandidatosIds[0]
      : postulacionesSeleccionadas[0] ?? this.resolverSolicitudCandidatoId(this.candidatos[0]);

    if (!tipoEntrevistaId || entrevistadorIds.length === 0 || !solicitudCandidatoId) {
      return null;
    }

    if (this.esAgendaMasiva && solicitudesCandidatosIds.length !== this.candidatos.length) {
      return null;
    }

    return {
      ...raw,
      solicitudCandidatoId,
      solicitudesCandidatosIds,
      tipoEntrevistaId,
      entrevistadorIds,
    };
  }

  private resolverTipoEntrevistaId(nombre: string) {
    return this.tiposCatalogo.find((tipo) => tipo.tpet_nombre === nombre)?.tpet_id ?? null;
  }

  integrantesSeleccionadosInternos() {
    return Array.from(this.integrantesSeleccionados)
      .map((id) => Number(id))
      .filter((id) => Number.isFinite(id) && id > 0);
  }

  private resolverSolicitudCandidatoId(candidatoAgenda?: EntrevistaCandidatoSeleccionado) {
    if (candidatoAgenda?.solicitudCandidatoId) {
      return candidatoAgenda.solicitudCandidatoId;
    }

    const candidatoId = Number(candidatoAgenda?.id ?? this.formulario.get('candidato')?.value);
    const solicitudId = this.resolverSolicitudId(candidatoAgenda?.idSolicitud ?? this.formulario.get('idSolicitud')?.value);

    if (!candidatoId || !solicitudId) {
      return null;
    }

    return this.postulacionesPorCandidato
      .get(candidatoId)
      ?.find((postulacion) => postulacion.slcd_solicitud_id === solicitudId)
      ?.slcd_id ?? null;
  }

  private resolverSolicitudId(valor: unknown) {
    const numero = Number(valor);
    if (Number.isFinite(numero) && numero > 0) {
      return numero;
    }

    return Number(this.solicitudes.find((solicitud) => solicitud.codigo === valor)?.id) || null;
  }

  private cargarPostulacionesPreseleccionadas() {
    const ids = this.candidatos
      .map((candidato) => Number(candidato.id))
      .filter((id) => Number.isFinite(id) && id > 0 && !this.postulacionesPorCandidato.has(id));

    ids.forEach((id) => this.cargarPostulacionesCandidato(id));
  }

  private cargarPostulacionesCandidato(candidatoId: number) {
    if (this.postulacionesPorCandidato.has(candidatoId)) {
      this.actualizarCargoDesdeSolicitud();
      return;
    }

    this.candidatosService.listarSolicitudes(String(candidatoId))
      .pipe(take(1), catchError(() => of([])))
      .subscribe((postulaciones) => {
        this.postulacionesPorCandidato.set(candidatoId, postulaciones);
        this.actualizarCargoDesdeSolicitud();
      });
  }

  private cargarCandidatosSolicitud(solicitudId: number) {
    this.cargandoCandidatosSolicitud = true;

    this.candidatosService.listarPorSolicitud(solicitudId)
      .pipe(take(1), catchError(() => of([])))
      .subscribe((postulaciones) => {
        this.postulacionesSolicitud = postulaciones;
        this.postulacionesSeleccionadas = new Set();
        this.sincronizarControlCandidato();
        postulaciones.forEach((postulacion) => {
          if (!postulacion.slcd_candidato_id) {
            return;
          }

          const actuales = this.postulacionesPorCandidato.get(postulacion.slcd_candidato_id) ?? [];
          this.postulacionesPorCandidato.set(
            postulacion.slcd_candidato_id,
            [...actuales.filter((item) => item.slcd_id !== postulacion.slcd_id), postulacion],
          );
        });
        this.cargarCandidatosFaltantes(postulaciones);
      });
  }

  private cargarCandidatosFaltantes(postulaciones: PostulacionCandidatoApi[]) {
    const idsActuales = new Set(this.candidatosDisponibles.map((candidato) => candidato.cand_id));
    const idsFaltantes = Array.from(
      new Set(
        postulaciones
          .map((postulacion) => postulacion.slcd_candidato_id)
          .filter((id): id is number => Boolean(id) && !idsActuales.has(id)),
      ),
    );

    if (idsFaltantes.length === 0) {
      this.cargandoCandidatosSolicitud = false;
      return;
    }

    forkJoin(
      idsFaltantes.map((id) =>
        this.candidatosService.obtenerPorId(String(id)).pipe(
          take(1),
          catchError(() => of(null)),
        ),
      ),
    )
      .pipe(
        finalize(() => {
          this.cargandoCandidatosSolicitud = false;
        }),
      )
      .subscribe((candidatos) => {
        const nuevos = candidatos.filter((candidato): candidato is CandidatoApi => Boolean(candidato));
        const porId = new Map(this.candidatosDisponibles.map((candidato) => [candidato.cand_id, candidato]));

        nuevos.forEach((candidato) => porId.set(candidato.cand_id, candidato));
        this.candidatosDisponibles = Array.from(porId.values());
      });
  }

  private candidatoDesdePostulacion(postulacion: PostulacionCandidatoApi) {
    const candidato = this.candidatosDisponibles.find((item) => item.cand_id === postulacion.slcd_candidato_id);

    if (candidato) {
      return candidato;
    }

    const anidado = (postulacion as PostulacionCandidatoApi & { candidato?: CandidatoApi | null }).candidato;
    if (anidado?.cand_id) {
      return anidado;
    }

    return postulacion.slcd_candidato_id
      ? {
          cand_id: postulacion.slcd_candidato_id,
          cand_email: null,
          cand_nombres: `Candidato ${postulacion.slcd_candidato_id}`,
          cand_apellido_paterno: null,
        }
      : null;
  }

  private postulacionesSeleccionadasIds() {
    return Array.from(this.postulacionesSeleccionadas)
      .filter((id) => Number.isFinite(id) && id > 0);
  }

  private sincronizarControlCandidato() {
    const primeraPostulacionId = this.postulacionesSeleccionadasIds()[0];
    const primeraPostulacion = this.postulacionesSolicitud.find((postulacion) => postulacion.slcd_id === primeraPostulacionId);

    this.formulario.patchValue(
      { candidato: primeraPostulacion?.slcd_candidato_id ?? null },
      { emitEvent: false },
    );

    if (primeraPostulacion?.slcd_candidato_id) {
      this.cargarPostulacionesCandidato(primeraPostulacion.slcd_candidato_id);
    }
  }

  private actualizarCargoDesdeSolicitud() {
    if (this.tieneCandidatosPreseleccionados) {
      return;
    }

    const solicitudId = this.resolverSolicitudId(this.formulario.get('idSolicitud')?.value);
    const solicitud = this.solicitudes.find((item) => Number(item.id) === solicitudId);

    if (solicitud) {
      this.formulario.patchValue(
        {
          cargo: solicitud.cargo,
          asunto: this.formulario.get('asunto')?.value || `Entrevista ${solicitud.codigo}`,
        },
        { emitEvent: false },
      );
    }
  }

  private mensajePayloadIncompleto() {
    if (!this.resolverTipoEntrevistaId(String(this.formulario.get('tipo')?.value || ''))) {
      return 'Selecciona un tipo de entrevista válido.';
    }

    if (this.integrantesSeleccionadosInternos().length === 0) {
      return 'Selecciona al menos un responsable interno para la entrevista.';
    }

    if (!this.postulacionesSeleccionadasIds()[0] && !this.resolverSolicitudCandidatoId(this.candidatos[0])) {
      return 'Selecciona una solicitud y un candidato asociado a esa solicitud.';
    }

    return 'Completa los campos obligatorios antes de enviar.';
  }
}
