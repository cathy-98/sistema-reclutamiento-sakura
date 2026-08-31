import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin, of, take, timeout, catchError, finalize } from 'rxjs';
import { Button } from '../../../shared/components/button/button';
import { DatePicker } from '../../../shared/components/date-picker/date-picker';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { FormField } from '../../../shared/components/form-field/form-field';
import { IconButton } from '../../../shared/components/icon-button/icon-button';
import { Modal } from '../../../shared/components/modal/modal';
import { Stepper } from '../../../shared/components/stepper/stepper';
import { EntrevistaPayload, ProgramacionTipoEntrevistaPayload } from '../../../services/entrevistas.service';
import { CatalogosService, TipoEntrevistaCatalogoApi, UsuarioCatalogoApi } from '../../../services/catalogos.service';
import { CandidatoApi, CandidatosService, PostulacionCandidatoApi } from '../../../services/candidatos.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { SolicitudResumen } from '../../../shared/models/solicitud.model';

interface IntegranteEntrevista {
  id: string;
  nombre: string;
  rol: string;
}

export interface EntrevistaCandidatoSeleccionado {
  id?: string;
  solicitudCandidatoId?: number;
  idSolicitud: string;
  nombre: string;
  cargo: string;
}

interface ProgramacionTipoForm {
  tipoId: number;
  tipoNombre: string;
  asunto: string;
  fecha: string;
  horaInicio: string;
  horaFin: string;
  duracion: string;
  linkReunion: string;
  observacion: string;
  responsablesIds: Set<string>;
  busquedaResponsable: string;
}

@Component({
  selector: 'app-entrevista-form-modal',
  imports: [
    CommonModule,
    FormsModule,
    Button,
    DatePicker,
    FormActions,
    FormField,
    IconButton,
    Modal,
    Stepper,
  ],
  templateUrl: './entrevista-form-modal.html',
  styleUrl: './entrevista-form-modal.scss',
})
export class EntrevistaFormModal implements OnInit {
  @Input() initialData: Partial<EntrevistaPayload> | null = null;
  @Input() candidatos: EntrevistaCandidatoSeleccionado[] = [];
  @Input() errorApi = '';
  @Output() cerrar = new EventEmitter<void>();
  @Output() candidatosChange = new EventEmitter<EntrevistaCandidatoSeleccionado[]>();
  @Output() guardar = new EventEmitter<EntrevistaPayload>();

  solicitudes: SolicitudResumen[] = [];
  candidatosDisponibles: CandidatoApi[] = [];
  postulacionesSolicitud: PostulacionCandidatoApi[] = [];
  tiposCatalogo: TipoEntrevistaCatalogoApi[] = [];
  integrantes: IntegranteEntrevista[] = [];

  solicitudSeleccionadaId: number | null = null;
  postulacionesSeleccionadas = new Set<number>();
  cargo = '';
  errorEnvio = '';
  cargandoDatos = false;
  cargandoCandidatosSolicitud = false;
  tabFormulario: 'datos' | 'programacion' | 'participantes' | 'revision' = 'datos';
  tipoActivoId: number | null = null;

  programaciones = new Map<number, ProgramacionTipoForm>();

  readonly duracionesBase = ['30 min', '45 min', '60 min', '90 min'];
  readonly pasosFormulario = [
    { clave: 'datos', numero: 1, titulo: 'Datos' },
    { clave: 'programacion', numero: 2, titulo: 'Reunión' },
    { clave: 'participantes', numero: 3, titulo: 'Participantes' },
    { clave: 'revision', numero: 4, titulo: 'Revisión' },
  ];

  constructor(
    private catalogosService: CatalogosService,
    private candidatosService: CandidatosService,
    private solicitudesService: SolicitudesService,
  ) {}

  ngOnInit() {
    this.cargarCatalogos();
    this.cargarDatosSeleccion();
    this.aplicarPreseleccion();
  }

  get tituloModal() {
    return this.esAgendaMasiva ? 'Agendar entrevistas masivas' : 'Agendar entrevistas';
  }

  get subtituloModal() {
    return 'Selecciona una solicitud y los candidatos que deseas agendar.';
  }

  get esAgendaMasiva() {
    return this.candidatos.length > 1 || this.postulacionesSeleccionadas.size > 1;
  }

  get tieneCandidatosPreseleccionados() {
    return this.candidatos.length > 0;
  }

  get fechaHoyInput() {
    const ahora = new Date();
    const local = new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 10);
  }

  get programacionesLista() {
    return Array.from(this.programaciones.values());
  }

  get programacionActiva() {
    if (!this.tipoActivoId) {
      return this.programacionesLista[0] ?? null;
    }

    return this.programaciones.get(this.tipoActivoId) ?? this.programacionesLista[0] ?? null;
  }

  get programacionesCompletas() {
    return this.programacionesLista.filter((programacion) => this.programacionCompleta(programacion)).length;
  }

  get postulacionesSeleccionadasCantidad() {
    return this.postulacionesSeleccionadasIds.length;
  }

  get todasPostulacionesSeleccionadas() {
    return (
      this.postulacionesSolicitud.length > 0 &&
      this.postulacionesSolicitud.every((postulacion) => this.postulacionesSeleccionadas.has(postulacion.slcd_id))
    );
  }

  get solicitudSeleccionada() {
    return this.solicitudes.find((item) => Number(item.id) === Number(this.solicitudSeleccionadaId)) ?? null;
  }

  get candidatosRevision() {
    if (this.tieneCandidatosPreseleccionados) {
      return this.candidatos.map((candidato) => candidato.nombre);
    }

    return this.postulacionesSolicitud
      .filter((postulacion) => this.postulacionesSeleccionadas.has(postulacion.slcd_id))
      .map((postulacion) => this.nombrePostulacion(postulacion));
  }

  get participantesProgramacion() {
    return this.programacionActiva ? this.responsablesSeleccionados(this.programacionActiva) : [];
  }

  get pasosCompletados() {
    const actual = this.pasosFormulario.findIndex((paso) => paso.clave === this.tabFormulario);
    return this.pasosFormulario.slice(0, actual).map((paso) => paso.clave);
  }

  get postulacionesSeleccionadasIds() {
    if (this.tieneCandidatosPreseleccionados) {
      return this.candidatos
        .map((candidato) => candidato.solicitudCandidatoId)
        .filter((id): id is number => Boolean(id));
    }

    return Array.from(this.postulacionesSeleccionadas);
  }

  cambiarTabFormulario(tab: string) {
    const destino = this.pasosFormulario.findIndex((paso) => paso.clave === tab);
    const actual = this.pasosFormulario.findIndex((paso) => paso.clave === this.tabFormulario);

    if (destino > actual) {
      const pasosPrevios = this.pasosFormulario.slice(0, destino);
      const invalido = pasosPrevios.some((paso) => !this.validarPaso(paso.clave));
      if (invalido) {
        return;
      }
    }

    this.tabFormulario = tab as typeof this.tabFormulario;
  }

  volverPaso() {
    const actual = this.pasosFormulario.findIndex((paso) => paso.clave === this.tabFormulario);
    if (actual > 0) {
      this.tabFormulario = this.pasosFormulario[actual - 1].clave as typeof this.tabFormulario;
    }
  }

  siguientePaso() {
    if (!this.validarPaso(this.tabFormulario)) {
      return;
    }

    const actual = this.pasosFormulario.findIndex((paso) => paso.clave === this.tabFormulario);
    if (actual < this.pasosFormulario.length - 1) {
      this.tabFormulario = this.pasosFormulario[actual + 1].clave as typeof this.tabFormulario;
    }
  }

  esUltimoPaso() {
    return this.tabFormulario === 'revision';
  }

  alternarPostulacion(postulacion: PostulacionCandidatoApi, seleccionado: boolean) {
    // Selección múltiple de candidatos asociados a la solicitud actual.
    const ids = new Set(this.postulacionesSeleccionadas);
    if (seleccionado) {
      ids.add(postulacion.slcd_id);
    } else {
      ids.delete(postulacion.slcd_id);
    }
    this.postulacionesSeleccionadas = ids;
  }

  postulacionMarcada(postulacionId: number) {
    return this.postulacionesSeleccionadas.has(postulacionId);
  }

  alternarTodasPostulaciones(seleccionado: boolean) {
    // Seleccionar todos solo actúa sobre candidatos de la solicitud cargada.
    this.postulacionesSeleccionadas = seleccionado
      ? new Set(this.postulacionesSolicitud.map((postulacion) => postulacion.slcd_id))
      : new Set();
  }

  limpiarPostulaciones() {
    this.postulacionesSeleccionadas = new Set();
  }

  alCambiarSolicitud(solicitudId?: string | number | null) {
    if (solicitudId !== undefined) {
      this.solicitudSeleccionadaId = solicitudId ? Number(solicitudId) : null;
    }

    // Al cambiar de solicitud se descartan candidatos de la selección anterior.
    this.postulacionesSolicitud = [];
    this.postulacionesSeleccionadas = new Set();
    this.actualizarCargoDesdeSolicitud();
    if (this.solicitudSeleccionadaId) {
      this.cargarCandidatosSolicitud(this.solicitudSeleccionadaId);
    }
    this.actualizarTitulosSugeridos();
  }

  eliminarCandidatoAgenda(candidato: EntrevistaCandidatoSeleccionado) {
    const actualizados = this.candidatos.filter((item) => item !== candidato);
    if (actualizados.length === 0) {
      this.cerrar.emit();
      return;
    }
    this.candidatos = actualizados;
    this.candidatosChange.emit(actualizados);
  }

  responsablesFiltrados(programacion: ProgramacionTipoForm) {
    const busqueda = this.normalizar(programacion.busquedaResponsable);
    if (!busqueda) {
      return this.integrantes;
    }
    return this.integrantes.filter((integrante) =>
      this.normalizar(`${integrante.nombre} ${integrante.rol}`).includes(busqueda),
    );
  }

  seleccionarResponsablesFiltrados(programacion: ProgramacionTipoForm) {
    const ids = new Set(programacion.responsablesIds);
    this.responsablesFiltrados(programacion).forEach((integrante) => ids.add(integrante.id));
    programacion.responsablesIds = ids;
    this.programaciones = new Map(this.programaciones);
  }

  limpiarResponsables(programacion: ProgramacionTipoForm) {
    programacion.responsablesIds = new Set<string>();
    this.programaciones = new Map(this.programaciones);
  }

  responsableSeleccionado(programacion: ProgramacionTipoForm, integranteId: string) {
    return programacion.responsablesIds.has(integranteId);
  }

  alternarResponsable(programacion: ProgramacionTipoForm, integranteId: string, seleccionado: boolean) {
    const ids = new Set(programacion.responsablesIds);
    if (seleccionado) {
      ids.add(integranteId);
    } else {
      ids.delete(integranteId);
    }
    programacion.responsablesIds = ids;
    this.programaciones = new Map(this.programaciones);
  }

  responsablesSeleccionados(programacion: ProgramacionTipoForm) {
    return this.integrantes.filter((integrante) => programacion.responsablesIds.has(integrante.id));
  }

  nombresResponsables(programacion: ProgramacionTipoForm) {
    return this.responsablesSeleccionados(programacion).map((responsable) => responsable.nombre).join(', ');
  }

  programacionCompleta(programacion: ProgramacionTipoForm) {
    return Boolean(
      this.datosReunionCompletos(programacion) &&
      programacion.responsablesIds.size > 0,
    );
  }

  private datosReunionCompletos(programacion: ProgramacionTipoForm) {
    return Boolean(
      programacion.asunto.trim() &&
      this.fechaValida(programacion) &&
      programacion.horaInicio &&
      programacion.horaFin &&
      this.horarioValido(programacion),
    );
  }

  horaFin(programacion: ProgramacionTipoForm) {
    return programacion.horaFin;
  }

  sincronizarHoraFin(programacion: ProgramacionTipoForm) {
    const minutos = this.minutosDesdeDuracion(programacion.duracion);
    if (!programacion.horaInicio) {
      programacion.horaFin = '';
      this.programaciones = new Map(this.programaciones);
      return;
    }

    if (minutos) {
      programacion.horaFin = this.sumarMinutosHora(programacion.horaInicio, minutos);
    }
    this.programaciones = new Map(this.programaciones);
  }

  sincronizarDuracionDesdeHoraFin(programacion: ProgramacionTipoForm) {
    const minutos = this.minutosEntreHoras(programacion.horaInicio, programacion.horaFin);
    if (minutos) {
      programacion.duracion = this.duracionDesdeMinutos(minutos);
    }
    this.programaciones = new Map(this.programaciones);
  }

  duracionesDisponibles(programacion: ProgramacionTipoForm) {
    if (this.duracionesBase.includes(programacion.duracion)) {
      return this.duracionesBase;
    }

    return [...this.duracionesBase, programacion.duracion];
  }

  horarioValido(programacion: ProgramacionTipoForm) {
    if (!programacion.horaInicio || !programacion.horaFin) {
      return true;
    }

    return programacion.horaFin > programacion.horaInicio;
  }

  fechaValida(programacion: ProgramacionTipoForm) {
    return Boolean(programacion.fecha) && programacion.fecha >= this.fechaHoyInput;
  }

  validarPaso(paso: string) {
    this.errorEnvio = '';

    if (paso === 'datos') {
      if (!this.solicitudSeleccionadaId && !this.tieneCandidatosPreseleccionados) {
        this.errorEnvio = 'Selecciona una solicitud para continuar.';
        return false;
      }
      if (this.postulacionesSeleccionadasIds.length === 0) {
        this.errorEnvio = 'Selecciona al menos un candidato asociado a una solicitud.';
        return false;
      }
      if (this.programaciones.size === 0) {
        this.errorEnvio = 'No se pudo preparar la reunión por una dependencia técnica del contrato actual.';
        return false;
      }
      return true;
    }

    if (paso === 'programacion') {
      const incompleta = this.programacionesLista.find((programacion) =>
        !this.datosReunionCompletos(programacion),
      );
      if (incompleta) {
        this.tipoActivoId = incompleta.tipoId;
        this.errorEnvio = 'Completa fecha, horario válido y nombre de reunión.';
        return false;
      }
      return true;
    }

    if (paso === 'participantes') {
      const incompleta = this.programacionesLista.find((programacion) =>
        programacion.responsablesIds.size === 0,
      );
      if (incompleta) {
        this.tipoActivoId = incompleta.tipoId;
        this.errorEnvio = 'Agrega al menos un participante.';
        return false;
      }
      return true;
    }

    return true;
  }

  enviar() {
    if (!this.validarPaso('datos') || !this.validarPaso('programacion') || !this.validarPaso('participantes')) {
      return;
    }

    const payload = this.crearPayload();
    if (!payload) {
      this.errorEnvio = 'No se pudo construir el agendamiento con IDs reales.';
      return;
    }

    this.guardar.emit(payload);
  }

  nombrePostulacion(postulacion: PostulacionCandidatoApi) {
    const candidato = this.candidatoDesdePostulacion(postulacion);
    return candidato ? this.nombreCandidato(candidato) : `Candidato ${postulacion.slcd_candidato_id ?? ''}`.trim();
  }

  detallePostulacion(postulacion: PostulacionCandidatoApi) {
    return [
      this.matchPostulacion(postulacion),
    ].filter(Boolean).join(' · ');
  }

  contextoHeader() {
    const total = this.postulacionesSeleccionadasIds.length;
    const cantidad = total === 1 ? '1 candidato' : `${total || 0} candidatos`;

    if (!this.tieneCandidatosPreseleccionados && !this.solicitudSeleccionadaId) {
      return 'Selecciona una solicitud';
    }

    return `${this.codigoSolicitudResumen()} · ${cantidad}`;
  }

  private cargarCatalogos() {
    forkJoin({
      tipos: this.catalogosService.listarTiposEntrevista().pipe(timeout(4000), catchError(() => of([]))),
      usuarios: this.catalogosService.listarUsuarios().pipe(timeout(4000), catchError(() => of([]))),
    })
      .pipe(take(1))
      .subscribe(({ tipos, usuarios }) => {
        this.tiposCatalogo = tipos.filter((tipo) => this.tipoEntrevistaValido(tipo.tpet_nombre));
        this.integrantes = usuarios.map((usuario) => this.mapearUsuarioAIntegrante(usuario));
        this.prepararProgramacionReunion();
      });
  }

  private cargarDatosSeleccion() {
    this.cargandoDatos = true;
    forkJoin({
      solicitudes: this.solicitudesService.listar().pipe(timeout(5000), catchError(() => of([]))),
      candidatos: this.candidatosService.listar().pipe(timeout(5000), catchError(() => of([]))),
    })
      .pipe(
        take(1),
        finalize(() => {
          this.cargandoDatos = false;
        }),
      )
      .subscribe(({ solicitudes, candidatos }) => {
        this.solicitudes = solicitudes;
        this.candidatosDisponibles = candidatos;
        this.aplicarPreseleccion();
      });
  }

  private cargarCandidatosSolicitud(solicitudId: number) {
    this.cargandoCandidatosSolicitud = true;
    this.candidatosService
      .listarPorSolicitud(solicitudId)
      .pipe(
        timeout(5000),
        take(1),
        catchError(() => of([])),
        finalize(() => {
          this.cargandoCandidatosSolicitud = false;
        }),
      )
      .subscribe((postulaciones) => {
        // Carga únicamente candidatos asociados a la solicitud seleccionada.
        this.postulacionesSolicitud = postulaciones;
        this.cargarCandidatosFaltantes(postulaciones);
      });
  }

  private cargarCandidatosFaltantes(postulaciones: PostulacionCandidatoApi[]) {
    const actuales = new Set(this.candidatosDisponibles.map((candidato) => candidato.cand_id));
    const faltantes = Array.from(new Set(
      postulaciones
        .map((postulacion) => postulacion.slcd_candidato_id)
        .filter((id): id is number => Boolean(id) && !actuales.has(id)),
    ));

    if (faltantes.length === 0) {
      return;
    }

    forkJoin(faltantes.map((id) => this.candidatosService.obtenerPorId(String(id)).pipe(take(1), catchError(() => of(null)))))
      .subscribe((candidatos) => {
        this.candidatosDisponibles = [
          ...this.candidatosDisponibles,
          ...candidatos.filter((candidato): candidato is CandidatoApi => Boolean(candidato)),
        ];
      });
  }

  private aplicarPreseleccion() {
    if (!this.tieneCandidatosPreseleccionados) {
      return;
    }
    this.cargo = this.candidatos.length === 1 ? this.candidatos[0].cargo : 'Múltiples cargos';
    this.actualizarTitulosSugeridos();
  }

  private crearPayload(): EntrevistaPayload | null {
    const solicitudesCandidatosIds = this.postulacionesSeleccionadasIds;
    const solicitudCandidatoId = solicitudesCandidatosIds[0];

    if (!solicitudCandidatoId) {
      return null;
    }

    // Workaround frontend: backend aún exige tipo_entrevista_id aunque la UI no lo expone.
    const programacionesPorTipo: ProgramacionTipoEntrevistaPayload[] = this.programacionesLista.map((programacion) => ({
      tipoEntrevistaId: programacion.tipoId,
      nombreTipo: programacion.tipoNombre,
      entrevistadorIds: Array.from(programacion.responsablesIds).map(Number),
      asunto: programacion.asunto,
      fecha: programacion.fecha,
      horaInicio: programacion.horaInicio,
      horaFin: programacion.horaFin,
      duracion: programacion.duracion,
      linkReunion: programacion.linkReunion,
      observacion: programacion.observacion,
    }));

    return {
      solicitudCandidatoId,
      solicitudesCandidatosIds,
      programacionesPorTipo,
      tiposEntrevista: programacionesPorTipo,
      tipoEntrevistaId: programacionesPorTipo[0]?.tipoEntrevistaId,
      entrevistadorIds: programacionesPorTipo[0]?.entrevistadorIds ?? [],
      idSolicitud: this.codigoSolicitudResumen(),
      candidato: this.resumenCandidatos(),
      tipo: 'Entrevista',
      asunto: programacionesPorTipo[0]?.asunto ?? 'Entrevista',
      cargo: this.cargo,
      fecha: programacionesPorTipo[0]?.fecha ?? '',
      horaInicio: programacionesPorTipo[0]?.horaInicio ?? '',
      horaFin: programacionesPorTipo[0]?.horaFin ?? '',
      entrevistador: '',
      linkReunion: programacionesPorTipo[0]?.linkReunion,
      observacion: programacionesPorTipo[0]?.observacion,
    };
  }

  private tituloSugerido(_tipoNombre: string) {
    return `Entrevista ${this.cargo || this.resumenCandidatos()}`;
  }

  private actualizarTitulosSugeridos() {
    this.programaciones.forEach((programacion) => {
      if (!programacion.asunto.trim() || programacion.asunto.includes('·')) {
        programacion.asunto = this.tituloSugerido(programacion.tipoNombre);
      }
    });
  }

  private actualizarTipoActivo() {
    if (this.tipoActivoId && this.programaciones.has(this.tipoActivoId)) {
      return;
    }

    this.tipoActivoId = this.programacionesLista[0]?.tipoId ?? null;
  }

  private prepararProgramacionReunion() {
    if (this.programaciones.size > 0) {
      return;
    }

    const tipoCompatibilidad = this.tiposCatalogo[0];

    if (!tipoCompatibilidad?.tpet_id) {
      return;
    }

    // Se usa solo para cumplir el contrato actual; no se muestra como selector.
    this.programaciones.set(tipoCompatibilidad.tpet_id, {
      tipoId: tipoCompatibilidad.tpet_id,
      tipoNombre: tipoCompatibilidad.tpet_nombre ?? 'Entrevista',
      asunto: this.tituloSugerido(tipoCompatibilidad.tpet_nombre ?? 'Entrevista'),
      fecha: '',
      horaInicio: '',
      horaFin: '',
      duracion: '60 min',
      linkReunion: '',
      observacion: '',
      responsablesIds: new Set<string>(),
      busquedaResponsable: '',
    });
    this.tipoActivoId = tipoCompatibilidad.tpet_id;
    this.programaciones = new Map(this.programaciones);
  }

  resumenCandidatos() {
    if (this.candidatos.length > 1 || this.postulacionesSeleccionadas.size > 1) {
      return `${this.postulacionesSeleccionadasIds.length || this.candidatos.length} candidatos`;
    }
    if (this.candidatos[0]?.nombre) {
      return this.candidatos[0].nombre;
    }
    const postulacion = this.postulacionesSolicitud.find((item) => this.postulacionesSeleccionadas.has(item.slcd_id));
    return postulacion ? this.nombrePostulacion(postulacion) : 'Candidato';
  }

  codigoSolicitudResumen() {
    if (this.candidatos.length === 1) {
      return this.candidatos[0].idSolicitud;
    }
    const solicitud = this.solicitudes.find((item) => Number(item.id) === Number(this.solicitudSeleccionadaId));
    if (solicitud?.codigo) {
      return solicitud.codigo;
    }

    return this.esAgendaMasiva ? 'Agenda masiva' : 'Sin solicitud';
  }

  private actualizarCargoDesdeSolicitud() {
    const solicitud = this.solicitudes.find((item) => Number(item.id) === Number(this.solicitudSeleccionadaId));
    this.cargo = solicitud?.cargo ?? this.candidatos[0]?.cargo ?? '';
  }

  private mapearUsuarioAIntegrante(usuario: UsuarioCatalogoApi): IntegranteEntrevista {
    return {
      id: String(usuario.usr_id),
      nombre: [usuario.usr_nombres, usuario.usr_apellido_paterno, usuario.usr_apellido_materno].filter(Boolean).join(' ') || usuario.usr_email,
      rol: usuario.rol?.rol_nombre ?? 'Usuario',
    };
  }

  private candidatoDesdePostulacion(postulacion: PostulacionCandidatoApi) {
    return this.candidatosDisponibles.find((candidato) => candidato.cand_id === postulacion.slcd_candidato_id) ?? null;
  }

  private matchPostulacion(postulacion: PostulacionCandidatoApi) {
    const match = postulacion.slcd_puntaje_compatibilidad;
    const numero = Number(match);
    return match !== null && match !== undefined && match !== '' && Number.isFinite(numero)
      ? `${numero}% match`
      : 'Sin match';
  }

  private nombreCandidato(candidato: CandidatoApi) {
    return [candidato.cand_nombres, candidato.cand_apellido_paterno, candidato.cand_apellido_materno].filter(Boolean).join(' ') ||
      candidato.cand_email ||
      `Candidato ${candidato.cand_id}`;
  }

  private tipoEntrevistaValido(nombre?: string | null) {
    const normalizado = this.normalizar(nombre ?? '');
    return Boolean(normalizado) && normalizado !== 'ingles';
  }

  private normalizar(valor: string) {
    return valor.trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-');
  }

  private minutosDesdeDuracion(duracion: string) {
    const match = duracion.match(/(\d+)\s*min/i);
    return match ? Number(match[1]) : null;
  }

  private duracionDesdeMinutos(minutos: number) {
    const etiqueta = `${minutos} min`;
    return this.duracionesBase.includes(etiqueta) ? etiqueta : `Personalizada (${etiqueta})`;
  }

  private sumarMinutosHora(hora: string, minutos: number) {
    const [horas, mins] = hora.split(':').map(Number);
    if (!Number.isFinite(horas) || !Number.isFinite(mins)) {
      return '';
    }
    const total = horas * 60 + mins + minutos;
    return `${String(Math.floor(total / 60) % 24).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
  }

  private minutosEntreHoras(inicio: string, fin: string) {
    const [inicioHoras, inicioMinutos] = inicio.split(':').map(Number);
    const [finHoras, finMinutos] = fin.split(':').map(Number);

    if (
      !Number.isFinite(inicioHoras) ||
      !Number.isFinite(inicioMinutos) ||
      !Number.isFinite(finHoras) ||
      !Number.isFinite(finMinutos)
    ) {
      return null;
    }

    const minutos = finHoras * 60 + finMinutos - (inicioHoras * 60 + inicioMinutos);
    return minutos > 0 ? minutos : null;
  }
}
