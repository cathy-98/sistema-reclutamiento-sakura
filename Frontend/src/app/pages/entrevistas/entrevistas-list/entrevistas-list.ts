import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, take, throwError, timeout } from 'rxjs';
import {
  EntrevistaApi,
  EntrevistaPayload,
  EntrevistaResumen,
  EntrevistasService,
  EstadoEntrevista,
  TipoEntrevista,
} from '../../../services/entrevistas.service';
import { ActionBar } from '../../../shared/components/action-bar/action-bar';
import { AlertRegion } from '../../../shared/components/alert-region/alert-region';
import { Button } from '../../../shared/components/button/button';
import { DatePicker } from '../../../shared/components/date-picker/date-picker';
import {
  DataTable,
  DataTableAction,
  DataTableActionEvent,
  DataTableColumn,
} from '../../../shared/components/data-table/data-table';
import { FilterPanel } from '../../../shared/components/filter-panel/filter-panel';
import { Modal } from '../../../shared/components/modal/modal';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { CatalogosService, NombreResultadoCatalogoApi } from '../../../services/catalogos.service';
import { EntrevistaEstadoModal, EvaluacionTipoPayload } from '../entrevista-estado-modal/entrevista-estado-modal';
import { EntrevistaFormModal } from '../entrevista-form-modal/entrevista-form-modal';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { InformesService } from '../../../services/informes.service';

interface FiltrosEntrevistas {
  busquedaRapida: string;
  cargo: string;
  fecha: string;
  estado: '' | EstadoEntrevista;
  tipo: '' | TipoEntrevista;
}

type ModoEstadoEntrevista = 'ver' | 'gestionar' | 'reprogramar' | 'confirmar' | 'realizar' | 'no-asistio' | 'cancelar';

@Component({
  selector: 'app-entrevistas-list',
  imports: [
    CommonModule,
    FormsModule,
    ActionBar,
    AlertRegion,
    Button,
    DataTable,
    DatePicker,
    EntrevistaEstadoModal,
    EntrevistaFormModal,
    FilterPanel,
    Modal,
    PageHeader,
    PageLayout,
  ],
  templateUrl: './entrevistas-list.html',
  styleUrl: './entrevistas-list.scss',
})
export class EntrevistasList implements OnInit {
  cargando = false;
  errorCarga = '';
  alerta: AlertaUi | null = null;
  paginaActual = 1;
  registrosPorPagina = 5;
  seleccionados = new Set<string>();
  entrevistas: EntrevistaResumen[] = [];
  filtros: FiltrosEntrevistas = this.filtrosIniciales();
  mostrarFormulario = false;
  errorFormularioAgenda = '';
  candidatosAgendaMasiva: {
    id?: string;
    solicitudCandidatoId?: number;
    idSolicitud: string;
    nombre: string;
    cargo: string;
  }[] = [];
  mostrarModalCorreo = false;
  plantillaCorreo: 'recordatorio' | 'reagendar' | 'personalizada' = 'recordatorio';
  asuntoCorreo = '';
  cuerpoCorreo = '';
  entrevistaSeleccionada: EntrevistaResumen | null = null;
  entrevistaDetalle: EntrevistaApi | null = null;
  modoEstado: ModoEstadoEntrevista = 'gestionar';
  guardandoEstado = false;
  guardandoEvaluaciones = false;
  errorEstado = '';
  errorEvaluaciones = '';

  estados: EstadoEntrevista[] = ['Pendiente', 'Confirmada', 'Realizada', 'Reprogramada', 'Cancelada', 'No Asistio'];
  tipos: TipoEntrevista[] = [];
  resultadosEvaluacion: NombreResultadoCatalogoApi[] = [];

  readonly columnas: DataTableColumn<EntrevistaResumen>[] = [
    { key: 'idSolicitud', label: 'ID solicitud', width: 138, sticky: 'left' },
    {
      key: 'estado',
      label: 'Estado entrevista',
      width: 160,
      type: 'badge',
      className: (entrevista) => this.estadoClase(entrevista.estado),
    },
    { key: 'tipo', label: 'Tipo de entrevista', width: 170 },
    { key: 'resultadoEntrevista', label: 'Resultado por área', width: 260, wrap: true },
    { key: 'asunto', label: 'Asunto del evento', width: 220, wrap: true },
    { key: 'cargo', label: 'Cargo vacante', width: 190, wrap: true },
    { key: 'fecha', label: 'Fecha', width: 135, value: (entrevista) => this.formatearFecha(entrevista.fecha) },
    { key: 'horaInicio', label: 'Hora', width: 110, value: (entrevista) => entrevista.horaInicio },
    { key: 'entrevistador', label: 'Entrevistador', width: 210, wrap: true },
  ];

  readonly acciones: DataTableAction<EntrevistaResumen>[] = [
    { id: 'ver', label: 'Ver detalle', icon: 'eye' },
    {
      id: 'gestionar',
      label: 'Gestionar entrevista',
      icon: 'edit',
      visible: (entrevista) => this.puedeCambiarEstado(entrevista),
    },
    {
      id: 'reprogramar',
      label: 'Reprogramar',
      icon: 'calendar',
      visible: (entrevista) => this.puedeCambiarEstado(entrevista),
    },
    {
      id: 'feedback',
      label: 'Registrar feedback',
      icon: 'edit',
      visible: (entrevista) => this.esEstadoEntrevista(entrevista, ['Realizada']) && this.cumplePrecondicionM5(entrevista),
    },
  ];

  constructor(
    private entrevistasService: EntrevistasService,
    private catalogosService: CatalogosService,
    private informesService: InformesService,
    private solicitudesService: SolicitudesService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.cargarCatalogosFiltros();
    this.cargarCatalogosGestion();
    this.cargarEntrevistas();
  }

  get entrevistasFiltradas() {
    const filtros = {
      busquedaRapida: this.normalizar(this.filtros.busquedaRapida),
      cargo: this.normalizar(this.filtros.cargo),
      fecha: this.filtros.fecha,
      estado: this.filtros.estado,
      tipo: this.filtros.tipo,
    };

    return this.entrevistas.filter((entrevista) => {
      const texto = this.normalizar(
        `${entrevista.idSolicitud} ${entrevista.candidato} ${entrevista.cargo} ${entrevista.asunto} ${entrevista.entrevistador} ${entrevista.tipo} ${entrevista.resultadoEntrevista}`,
      );

      return (
        texto.includes(filtros.busquedaRapida) &&
        this.normalizar(entrevista.cargo).includes(filtros.cargo) &&
        (!filtros.fecha || entrevista.fecha === filtros.fecha) &&
        (!filtros.estado || entrevista.estado === filtros.estado) &&
        (!filtros.tipo || entrevista.tipo === filtros.tipo)
      );
    });
  }

  get entrevistasPaginadas() {
    const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
    return this.entrevistasFiltradas.slice(inicio, inicio + this.registrosPorPagina);
  }

  get totalPaginas() {
    return Math.max(1, Math.ceil(this.entrevistasFiltradas.length / this.registrosPorPagina));
  }

  get mensajeAccionesMasivas() {
    return this.seleccionados.size > 0
      ? `${this.seleccionados.size} entrevistas seleccionadas.`
      : 'Selecciona entrevistas para habilitar acciones masivas.';
  }

  get entrevistasSeleccionadas() {
    return this.entrevistas.filter((entrevista) => this.seleccionados.has(entrevista.id));
  }

  get seleccionMismaSolicitud() {
    const solicitudes = new Set(this.entrevistasSeleccionadas.map((entrevista) => entrevista.idSolicitud));
    return this.entrevistasSeleccionadas.length > 0 && solicitudes.size === 1;
  }

  get correosPreview() {
    return this.entrevistasSeleccionadas
      .map((entrevista) => entrevista.candidatoCorreo || entrevista.candidato)
      .filter(Boolean)
      .join(', ');
  }

  cargarEntrevistas() {
    this.cargando = true;
    this.errorCarga = '';
    this.cdr.detectChanges();

    forkJoin({
      entrevistas: this.entrevistasService.listar(),
      solicitudes: this.solicitudesService.listar().pipe(timeout(5000), catchError(() => of([]))),
      informes: this.informesService.listarCandidatos({ limit: 500 }).pipe(timeout(5000), catchError(() => of({ total: 0, items: [] }))),
    })
      .pipe(
        take(1),
        finalize(() => {
          this.cargando = false;
          this.cdr.detectChanges();
        }),
      )
      .subscribe({
      next: ({ entrevistas, solicitudes, informes }) => {
        const cargosPorSolicitud = new Map(
          solicitudes.map((solicitud) => [solicitud.codigo, solicitud.cargo]),
        );
        const estadosSolicitudPorCodigo = new Map(
          solicitudes.map((solicitud) => [solicitud.codigo, solicitud.estado]),
        );
        const estadosPostulacionPorId = new Map(
          informes.items.map((informe) => [informe.solicitud_candidato_id, informe.estado_postulacion ?? 'Sin estado']),
        );

        // Integración M5: se cruza estado de solicitud/postulación para no ofrecer acciones que backend rechazará.
        this.entrevistas = entrevistas.map((entrevista) => ({
          ...entrevista,
          cargo: entrevista.cargo && entrevista.cargo !== 'Sin cargo'
            ? entrevista.cargo
            : cargosPorSolicitud.get(entrevista.idSolicitud) ?? entrevista.cargo,
          estadoSolicitud: estadosSolicitudPorCodigo.get(entrevista.idSolicitud) ?? entrevista.estadoSolicitud,
          estadoPostulacion: entrevista.solicitudCandidatoId
            ? estadosPostulacionPorId.get(entrevista.solicitudCandidatoId) ?? entrevista.estadoPostulacion
            : entrevista.estadoPostulacion,
        }));
      },
      error: (error) => {
        this.entrevistas = [];
        this.errorCarga = obtenerMensajeError(error, 'No se pudieron cargar las entrevistas.');
      },
    });
  }

  cargarCatalogosFiltros() {
    // Integración catálogos entrevistas -> filtros del listado:
    // - estados-entrevista llena "Estado entrevista".
    // - tipos-entrevista llena "Tipo de entrevista".
    forkJoin({
      estados: this.catalogosService.listarEstadosEntrevista().pipe(timeout(4000), catchError(() => of([]))),
      tipos: this.catalogosService.listarTiposEntrevista().pipe(timeout(4000), catchError(() => of([]))),
    })
      .pipe(take(1))
      .subscribe(({ estados, tipos }) => {
        const estadosCatalogo = estados.map((estado) => estado.esev_nombre).filter((nombre): nombre is string => Boolean(nombre));
        const tiposCatalogo = tipos
          .map((tipo) => tipo.tpet_nombre)
          .filter((nombre): nombre is string => Boolean(nombre) && this.tipoEntrevistaValido(nombre));

        if (estadosCatalogo.length > 0) {
          this.estados = estadosCatalogo;
        }

        if (tiposCatalogo.length > 0) {
          this.tipos = tiposCatalogo;
        }
      });
  }

  guardarEntrevista(payload: EntrevistaPayload) {
    const solicitudesCandidatosIds = payload.solicitudesCandidatosIds ?? [];
    this.errorFormularioAgenda = '';

    if (solicitudesCandidatosIds.length > 1) {
      this.entrevistasService.crearMasiva(
        solicitudesCandidatosIds.map((solicitudCandidatoId) => ({
          ...payload,
          solicitudCandidatoId,
        })),
      ).subscribe({
        next: () => {
          this.mostrarFormulario = false;
          this.candidatosAgendaMasiva = [];
          this.alerta = {
            tipo: 'success',
            variante: 'soft',
            mensaje: `${solicitudesCandidatosIds.length} entrevistas agendadas correctamente.`,
          };
          this.cargarEntrevistas();
        },
        error: (error) => {
          this.errorFormularioAgenda = obtenerMensajeError(error, 'No se pudieron agendar las entrevistas.');
        },
      });
      return;
    }

    this.entrevistasService.crear(payload).subscribe({
      next: () => {
        const totalProgramaciones = payload.programacionesPorTipo?.length ?? 0;
        this.mostrarFormulario = false;
        this.candidatosAgendaMasiva = [];
        this.alerta = {
          tipo: 'success',
          variante: 'soft',
          mensaje: totalProgramaciones > 1 ? 'Entrevistas agendadas correctamente.' : 'Entrevista creada correctamente.',
        };
        this.cargarEntrevistas();
      },
      error: (error) => {
        this.errorFormularioAgenda = obtenerMensajeError(error, 'No se pudo crear la entrevista.');
      },
    });
  }

  cargarCatalogosGestion() {
    this.catalogosService
      .listarNombresResultado()
      .pipe(
        take(1),
        catchError(() => of([])),
      )
      .subscribe((resultados) => {
        this.resultadosEvaluacion = resultados;
      });
  }

  abrirFormularioIndividual() {
    this.candidatosAgendaMasiva = [];
    this.errorFormularioAgenda = '';
    this.mostrarFormulario = true;
  }

  abrirAgendaMasivaSeleccion() {
    const seleccionadas = this.entrevistasSeleccionadas;

    if (seleccionadas.length === 0) {
      return;
    }

    if (!this.seleccionMismaSolicitud) {
      this.candidatosAgendaMasiva = [];
      this.errorFormularioAgenda = 'Selecciona entrevistas de una misma solicitud para agendar masivamente.';
      this.mostrarFormulario = true;
      return;
    }

    if (seleccionadas.some((entrevista) => !entrevista.solicitudCandidatoId)) {
      this.candidatosAgendaMasiva = [];
      this.errorFormularioAgenda = 'No se pudo identificar la postulación de todas las entrevistas seleccionadas.';
      this.mostrarFormulario = true;
      return;
    }

    const porPostulacion = new Map<number, (typeof this.candidatosAgendaMasiva)[number]>();
    seleccionadas.forEach((entrevista) => {
      if (!entrevista.solicitudCandidatoId) {
        return;
      }

      porPostulacion.set(entrevista.solicitudCandidatoId, {
        id: entrevista.candidatoId ? String(entrevista.candidatoId) : undefined,
        solicitudCandidatoId: entrevista.solicitudCandidatoId,
        idSolicitud: entrevista.idSolicitud,
        nombre: entrevista.candidato,
        cargo: entrevista.cargo,
      });
    });

    this.candidatosAgendaMasiva = Array.from(porPostulacion.values());
    this.errorFormularioAgenda = '';
    this.mostrarFormulario = true;
  }

  cerrarFormularioAgenda() {
    this.mostrarFormulario = false;
    this.candidatosAgendaMasiva = [];
    this.errorFormularioAgenda = '';
  }

  abrirModalCorreo() {
    if (this.seleccionados.size === 0) {
      return;
    }

    this.plantillaCorreo = 'recordatorio';
    this.aplicarPlantillaCorreo();
    this.mostrarModalCorreo = true;
  }

  cerrarModalCorreo() {
    this.mostrarModalCorreo = false;
  }

  aplicarPlantillaCorreo() {
    const solicitud = this.entrevistasSeleccionadas[0]?.idSolicitud ?? '{{Solicitud}}';

    if (this.plantillaCorreo === 'recordatorio') {
      this.asuntoCorreo = `Recordatorio entrevista - ${solicitud}`;
      this.cuerpoCorreo = 'Hola {{Nombre}}, te recordamos tu entrevista para el proceso {{Solicitud}}. Revisa fecha, hora y enlace de reunión antes de asistir.';
      return;
    }

    if (this.plantillaCorreo === 'reagendar') {
      this.asuntoCorreo = `Reagendamiento entrevista - ${solicitud}`;
      this.cuerpoCorreo = 'Hola {{Nombre}}, necesitamos reagendar tu entrevista del proceso {{Solicitud}}. Te contactaremos con una nueva fecha y horario.';
      return;
    }

    this.asuntoCorreo = '';
    this.cuerpoCorreo = '';
  }

  confirmarEstado(payload: { estado?: EstadoEntrevista; fecha: string; horaInicio: string; horaFin: string; motivo: string }) {
    if (!this.entrevistaSeleccionada || this.modoEstado === 'ver' || this.guardandoEstado) {
      return;
    }

    const solicitud = this.solicitudEstadoEntrevista(payload);

    this.guardandoEstado = true;
    this.errorEstado = '';

    solicitud
      .pipe(
        finalize(() => {
          this.guardandoEstado = false;
        }),
      )
      .subscribe({
        next: (entrevistaActualizada) => {
          const estadoDevuelto =
            entrevistaActualizada.estado ||
            payload.estado ||
            '';

          this.alerta = {
            tipo: 'success',
            variante: 'soft',
            mensaje:
              this.mensajeEstadoActualizado(estadoDevuelto),
          };
          this.cargarEntrevistas();

          if (this.modoEstado === 'gestionar' && this.entrevistaSeleccionada && this.normalizar(estadoDevuelto).replace(/\s+/g, '-') === 'realizada') {
            this.cargarDetalleEntrevista(this.entrevistaSeleccionada.id);
            return;
          }

          this.cerrarModalEstado();
        },
        error: (error) => {
          this.errorEstado = obtenerMensajeError(error, 'No se pudo actualizar la entrevista.');
          if (this.errorEstado.includes('no se puede gestionar porque la postulación')) {
            this.modoEstado = 'ver';
          }
        },
      });
  }

  manejarAccionTabla(evento: DataTableActionEvent<EntrevistaResumen>) {
    if (evento.action === 'ver') {
      this.abrirEstado(evento.row, 'ver');
      return;
    }

    if (evento.action === 'gestionar') {
      this.abrirEstado(evento.row, 'gestionar');
      return;
    }

    if (evento.action === 'feedback') {
      this.abrirEstado(evento.row, 'gestionar');
      return;
    }

    if (evento.action === 'reprogramar') {
      this.abrirEstado(evento.row, 'reprogramar');
      return;
    }

    this.abrirEstado(evento.row, 'ver');
  }

  abrirEstado(entrevista: EntrevistaResumen, modo: ModoEstadoEntrevista) {
    this.entrevistaSeleccionada = entrevista;
    this.entrevistaDetalle = null;
    this.modoEstado = modo;
    this.errorEstado = '';
    this.errorEvaluaciones = '';
    this.guardandoEstado = false;
    this.guardandoEvaluaciones = false;
    this.cargarDetalleEntrevista(entrevista.id);
  }

  cerrarModalEstado() {
    this.entrevistaSeleccionada = null;
    this.entrevistaDetalle = null;
    this.errorEstado = '';
    this.errorEvaluaciones = '';
    this.guardandoEstado = false;
    this.guardandoEvaluaciones = false;
  }

  guardarEvaluaciones(payloads: EvaluacionTipoPayload[]) {
    if (!this.entrevistaSeleccionada || payloads.length === 0 || this.guardandoEvaluaciones) {
      return;
    }

    this.guardandoEvaluaciones = true;
    this.errorEvaluaciones = '';

    forkJoin(
      payloads.map((payload) => {
        const body = {
          nombre_resultado_id: payload.nombreResultadoId,
          observacion: payload.observacion,
        };

        const area = this.entrevistaDetalle?.tipos?.find((tipo) => tipo.tipo_entrevista_id === payload.tipoId)?.nombre ?? `Área ${payload.tipoId}`;
        const solicitud = payload.existe
          ? this.entrevistasService.actualizarEvaluacion(this.entrevistaSeleccionada!.id, payload.tipoId, body)
          : this.entrevistasService.crearEvaluacion(this.entrevistaSeleccionada!.id, payload.tipoId, body);

        return solicitud.pipe(
          catchError((error) =>
            throwError(() => new Error(`${area}: ${obtenerMensajeError(error, 'no se pudo guardar el resultado.')}`)),
          ),
        );
      }),
    )
      .pipe(
        finalize(() => {
          this.guardandoEvaluaciones = false;
        }),
      )
      .subscribe({
        next: () => {
          this.alerta = {
            tipo: 'success',
            variante: 'soft',
            mensaje: 'Resultados por área guardados correctamente.',
          };
          this.cargarDetalleEntrevista(this.entrevistaSeleccionada!.id);
          this.cargarEntrevistas();
        },
        error: (error) => {
          this.errorEvaluaciones = obtenerMensajeError(error, 'No se pudieron guardar los resultados por área.');
        },
      });
  }

  cerrarAlerta() {
    this.alerta = null;
  }

  limpiarFiltros() {
    this.filtros = this.filtrosIniciales();
    this.paginaActual = 1;
  }

  buscar() {
    this.paginaActual = 1;
  }

  cambiarPagina(pagina: number) {
    this.paginaActual = Math.min(Math.max(pagina, 1), this.totalPaginas);
  }

  cambiarRegistrosPorPagina(registros: number) {
    this.registrosPorPagina = registros;
    this.paginaActual = 1;
  }

  obtenerIdEntrevista(entrevista: EntrevistaResumen) {
    return entrevista.id;
  }

  estadoClase(estado: EstadoEntrevista) {
    return estado.toLowerCase().replace(/\s+/g, '-');
  }

  private filtrosIniciales(): FiltrosEntrevistas {
    return {
      busquedaRapida: '',
      cargo: '',
      fecha: '',
      estado: '',
      tipo: '',
    };
  }

  private normalizar(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  private formatearFecha(fecha: string) {
    return new Date(`${fecha}T00:00:00`).toLocaleDateString('es-CL');
  }

  private solicitudEstadoEntrevista(payload: { estado?: EstadoEntrevista; fecha: string; horaInicio: string; horaFin: string; motivo: string }) {
    const id = this.entrevistaSeleccionada?.id ?? '';
    const modo = this.modoEstado === 'gestionar'
      ? this.modoDesdeEstado(payload.estado)
      : this.modoEstado;

    if (!modo) {
      return throwError(() => new Error('La acción seleccionada no está disponible para esta entrevista.'));
    }

    if (modo === 'cancelar') {
      return this.entrevistasService.cancelar(id, payload.motivo);
    }

    if (modo === 'confirmar') {
      return this.entrevistasService.confirmar(id);
    }

    if (modo === 'realizar') {
      return this.entrevistasService.realizar(id);
    }

    if (modo === 'no-asistio') {
      return this.entrevistasService.noAsistio(id, payload.motivo);
    }

    if (modo === 'reprogramar') {
      return this.entrevistasService.reprogramar(
        id,
        payload.fecha,
        payload.horaInicio,
        payload.horaFin,
        payload.motivo,
      );
    }

    return throwError(() => new Error('La acción seleccionada no está disponible para esta entrevista.'));
  }

  private mensajeEstadoActualizado(estadoDevuelto = '') {
    if (this.modoEstado === 'reprogramar') {
      return `Entrevista reprogramada correctamente${estadoDevuelto ? `: ${estadoDevuelto}` : ''}.`;
    }

    return `Entrevista actualizada correctamente${estadoDevuelto ? `: ${estadoDevuelto}` : ''}.`;
  }

  private modoDesdeEstado(estado?: EstadoEntrevista): ModoEstadoEntrevista | '' {
    const estadoNormalizado = this.normalizar(estado ?? '');

    if (estadoNormalizado === 'confirmar' || estadoNormalizado === 'confirmada') {
      return 'confirmar' as ModoEstadoEntrevista;
    }

    if (estadoNormalizado === 'reprogramar' || estadoNormalizado === 'reprogramada') {
      return 'reprogramar';
    }

    if (estadoNormalizado === 'realizar' || estadoNormalizado === 'realizada') {
      return 'realizar' as ModoEstadoEntrevista;
    }

    if (estadoNormalizado === 'no-asistio' || estadoNormalizado === 'no asistio') {
      return 'no-asistio' as ModoEstadoEntrevista;
    }

    if (estadoNormalizado === 'cancelar' || estadoNormalizado === 'cancelada') {
      return 'cancelar' as ModoEstadoEntrevista;
    }

    return '';
  }

  private cargarDetalleEntrevista(id: string) {
    forkJoin({
      detalle: this.entrevistasService.obtener(id),
      evaluaciones: this.entrevistasService.listarEvaluaciones(id).pipe(catchError(() => of([]))),
    })
      .pipe(take(1))
      .subscribe({
        next: ({ detalle, evaluaciones }) => {
          // Integración M5: GET evaluaciones completa el detalle para decidir POST vs PATCH por tipo.
          this.entrevistaDetalle = {
            ...detalle,
            evaluaciones,
          };
        },
        error: (error) => {
          this.errorEstado = obtenerMensajeError(error, 'No se pudo cargar el detalle de la entrevista.');
        },
      });
  }

  private esEstadoEntrevista(entrevista: EntrevistaResumen, estados: string[]) {
    const actual = this.normalizar(entrevista.estado);
    return estados.some((estado) => this.normalizar(estado) === actual);
  }

  private puedeCambiarEstado(entrevista: EntrevistaResumen) {
    return this.cumplePrecondicionM5(entrevista) &&
      !this.esEstadoEntrevista(entrevista, ['Cancelada', 'Realizada', 'No Asistio']);
  }

  private cumplePrecondicionM5(entrevista: EntrevistaResumen) {
    const estadoPostulacion = this.normalizar(entrevista.estadoPostulacion ?? 'En entrevista');
    const estadoSolicitud = this.normalizar(entrevista.estadoSolicitud ?? 'En Entrevistas');

    return estadoPostulacion === 'en entrevista' && estadoSolicitud === 'en entrevistas';
  }

  private tipoEntrevistaValido(nombre?: string | null) {
    const normalizado = this.normalizar(nombre ?? '').replace(/\s+/g, '-');
    return Boolean(normalizado) && normalizado !== 'ingles';
  }
}
