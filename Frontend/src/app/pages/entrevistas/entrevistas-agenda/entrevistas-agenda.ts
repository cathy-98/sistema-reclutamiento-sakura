import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, HostListener, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, take, throwError, timeout } from 'rxjs';
import {
  EntrevistaApi,
  EntrevistaPayload,
  EntrevistaResumen,
  EntrevistasService,
  EstadoEntrevista,
} from '../../../services/entrevistas.service';
import { CatalogosService, NombreResultadoCatalogoApi } from '../../../services/catalogos.service';
import { AlertRegion } from '../../../shared/components/alert-region/alert-region';
import { Button } from '../../../shared/components/button/button';
import { IconButton } from '../../../shared/components/icon-button/icon-button';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { EntrevistaEstadoModal, EvaluacionTipoPayload } from '../entrevista-estado-modal/entrevista-estado-modal';
import { AuthService } from '../../../services/auth.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { InformesService } from '../../../services/informes.service';
import { EntrevistaFormModal } from '../entrevista-form-modal/entrevista-form-modal';

interface DiaAgenda {
  fecha: Date;
  fechaIso: string;
  esMesActual: boolean;
  cantidad: number;
}

@Component({
  selector: 'app-entrevistas-agenda',
  imports: [CommonModule, FormsModule, AlertRegion, Button, IconButton, EntrevistaEstadoModal, EntrevistaFormModal, PageHeader, PageLayout],
  templateUrl: './entrevistas-agenda.html',
  styleUrl: './entrevistas-agenda.scss',
})
export class EntrevistasAgenda implements OnInit {
  cargando = false;
  errorCarga = '';
  alerta: AlertaUi | null = null;
  entrevistas: EntrevistaResumen[] = [];
  entrevistaSeleccionada: EntrevistaResumen | null = null;
  entrevistaDetalle: EntrevistaApi | null = null;
  modoEstado: 'ver' | 'gestionar' | 'reprogramar' | 'cancelar' = 'reprogramar';
  guardandoEstado = false;
  guardandoEvaluaciones = false;
  cargandoDetalle = false;
  errorEstado = '';
  errorEvaluaciones = '';
  mensajeEvaluaciones = '';
  usuarioActualId: number | null = null;
  mostrarFormulario = false;
  guardandoFormularioAgenda = false;
  errorFormularioAgenda = '';
  estadoFiltro: '' | EstadoEntrevista = '';
  fechaSeleccionada = this.fechaHoy();
  mesSeleccionado = this.fechaHoy().slice(0, 7);
  busqueda = '';
  diasCalendario: DiaAgenda[] = [];
  resultadosEvaluacion: NombreResultadoCatalogoApi[] = [];
  estadosEntrevista: EstadoEntrevista[] = ['Pendiente', 'Confirmada', 'Realizada', 'Reprogramada', 'Cancelada', 'No Asistio'];
  menuAbiertoId = '';

  readonly diasSemana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];
  constructor(
    private entrevistasService: EntrevistasService,
    private catalogosService: CatalogosService,
    private authService: AuthService,
    private solicitudesService: SolicitudesService,
    private informesService: InformesService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.usuarioActualId = this.authService.obtenerUsuarioId();
    this.actualizarCalendario();
    this.cargarCatalogosGestion();
    this.cargarEntrevistas();
  }

  get tituloMes() {
    const [anio, mes] = this.mesSeleccionado.split('-').map(Number);
    return new Intl.DateTimeFormat('es-CL', { month: 'long', year: 'numeric' }).format(new Date(anio, mes - 1, 1));
  }

  get entrevistasDia() {
    const busquedaNormalizada = this.normalizar(this.busqueda);

    return this.entrevistasFiltradasPorEstado
      .filter((entrevista) => entrevista.fecha === this.fechaSeleccionada)
      .filter((entrevista) => {
        const texto = this.normalizar(
          `${entrevista.candidato} ${entrevista.idSolicitud} ${entrevista.cargo} ${entrevista.tipo} ${entrevista.entrevistador}`,
        );
        return !busquedaNormalizada || texto.includes(busquedaNormalizada);
      })
      .sort((a, b) => a.horaInicio.localeCompare(b.horaInicio));
  }

  get entrevistasFiltradasPorEstado() {
    return this.entrevistas.filter((entrevista) => {
      return !this.estadoFiltro || this.normalizar(entrevista.estado) === this.normalizar(this.estadoFiltro);
    });
  }

  get tituloPanelDia() {
    return this.fechaSeleccionada === this.fechaHoy()
      ? 'Entrevistas de hoy'
      : `Entrevistas · ${this.formatearFechaCorta(this.fechaSeleccionada)}`;
  }

  get resumenEntrevistasDia() {
    const total = this.entrevistasDia.length;
    return `${total} entrevista${total === 1 ? '' : 's'}`;
  }

  get fechaSeleccionadaLegible() {
    return this.formatearFechaCorta(this.fechaSeleccionada);
  }

  get initialDataAgenda(): Partial<EntrevistaPayload> {
    return {
      fecha: this.fechaSeleccionada,
    };
  }

  cargarEntrevistas() {
    this.cargando = true;
    this.errorCarga = '';
    this.cdr.detectChanges();

    forkJoin({
      entrevistas: this.entrevistasService.listar(),
      solicitudes: this.solicitudesService.listar().pipe(timeout(5000), catchError(() => of([]))),
      informes: this.informesService.listarCandidatos({ limit: 200 }).pipe(timeout(5000), catchError(() => of({ total: 0, items: [] }))),
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
        const estadosSolicitudPorCodigo = new Map(
          solicitudes.map((solicitud) => [solicitud.codigo, solicitud.estado]),
        );
        const estadosPostulacionPorId = new Map(
          informes.items.map((informe) => [informe.solicitud_candidato_id, informe.estado_postulacion ?? 'Sin estado']),
        );

        this.entrevistas = entrevistas.map((entrevista) => ({
          ...entrevista,
          estadoSolicitud: estadosSolicitudPorCodigo.get(entrevista.idSolicitud) ?? entrevista.estadoSolicitud,
          estadoPostulacion: entrevista.solicitudCandidatoId
            ? estadosPostulacionPorId.get(entrevista.solicitudCandidatoId) ?? entrevista.estadoPostulacion
            : entrevista.estadoPostulacion,
        }));
        this.actualizarCalendario();
      },
      error: (error) => {
        this.entrevistas = [];
        this.errorCarga = obtenerMensajeError(error, 'No se pudieron cargar las entrevistas.');
      },
    });
  }

  seleccionarHoy() {
    this.fechaSeleccionada = this.fechaHoy();
    this.mesSeleccionado = this.fechaSeleccionada.slice(0, 7);
    this.actualizarCalendario();
  }

  cambiarEstadoFiltro(estado: '' | EstadoEntrevista) {
    this.estadoFiltro = estado;
    this.actualizarCalendario();
  }

  seleccionarFecha(fechaIso: string) {
    this.fechaSeleccionada = fechaIso;
    this.mesSeleccionado = fechaIso.slice(0, 7);
    this.actualizarCalendario();
  }

  cambiarMes(delta: number) {
    const [anio, mes] = this.mesSeleccionado.split('-').map(Number);
    const fecha = new Date(anio, mes - 1 + delta, 1);
    this.mesSeleccionado = this.formatearMes(fecha);
    this.actualizarCalendario();
  }

  abrirEstado(entrevista: EntrevistaResumen, modo: 'ver' | 'gestionar' | 'reprogramar' | 'cancelar') {
    this.entrevistaSeleccionada = entrevista;
    this.entrevistaDetalle = null;
    this.modoEstado = modo;
    this.errorEstado = '';
    this.errorEvaluaciones = '';
    this.mensajeEvaluaciones = '';
    this.guardandoEstado = false;
    this.guardandoEvaluaciones = false;
    this.cargarDetalleEntrevista(entrevista.id);
  }

  cerrarModalEstado() {
    this.entrevistaSeleccionada = null;
    this.entrevistaDetalle = null;
    this.errorEstado = '';
    this.errorEvaluaciones = '';
    this.mensajeEvaluaciones = '';
    this.guardandoEstado = false;
    this.guardandoEvaluaciones = false;
  }

  confirmarEstado(payload: { fecha: string; horaInicio: string; horaFin: string; motivo: string }) {
    if (!this.entrevistaSeleccionada || this.guardandoEstado || !this.puedeCambiarEstado(this.entrevistaSeleccionada)) {
      return;
    }

    const solicitud =
      this.modoEstado === 'cancelar'
        ? this.entrevistasService.cancelar(this.entrevistaSeleccionada.id, payload.motivo)
        : this.entrevistasService.reprogramar(
            this.entrevistaSeleccionada.id,
            payload.fecha,
            payload.horaInicio,
            payload.horaFin,
            payload.motivo,
          );

    this.guardandoEstado = true;
    this.errorEstado = '';

    solicitud
      .pipe(
        finalize(() => {
          this.guardandoEstado = false;
        }),
      )
      .subscribe({
      next: () => {
        this.alerta = {
          tipo: 'success',
          variante: 'soft',
          mensaje: this.modoEstado === 'cancelar' ? 'Entrevista cancelada correctamente.' : 'Entrevista reprogramada correctamente.',
        };
        this.cerrarModalEstado();
        this.cargarEntrevistas();
      },
      error: (error) => {
        this.errorEstado = obtenerMensajeError(error, 'No se pudo actualizar la entrevista.');
      },
    });
  }

  verDetalle(entrevista: EntrevistaResumen) {
    this.abrirEstado(entrevista, 'ver');
  }

  abrirFeedback(entrevista: EntrevistaResumen) {
    if (!this.esEstadoEntrevista(entrevista, ['Realizada'])) {
      return;
    }

    if (!this.puedeRegistrarFeedback(entrevista)) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: this.mensajeSolicitudBloqueada(entrevista),
      };
      return;
    }

    // El feedback reutiliza la modal de gestión para mantener la trazabilidad
    // por entrevista y no inventar una pantalla paralela.
    this.abrirEstado(entrevista, 'gestionar');
  }

  cerrarAlerta() {
    this.alerta = null;
  }

  abrirFormularioIndividual() {
    this.errorFormularioAgenda = '';
    this.guardandoFormularioAgenda = false;
    this.mostrarFormulario = true;
  }

  cerrarFormularioAgenda() {
    this.mostrarFormulario = false;
    this.errorFormularioAgenda = '';
    this.guardandoFormularioAgenda = false;
  }

  guardarEntrevista(payload: EntrevistaPayload) {
    this.errorFormularioAgenda = '';
    this.guardandoFormularioAgenda = true;

    this.entrevistasService.crear(payload).pipe(
      finalize(() => {
        this.guardandoFormularioAgenda = false;
      }),
    ).subscribe({
      next: () => {
        const totalProgramaciones = payload.programacionesPorTipo?.length ?? 0;
        this.mostrarFormulario = false;
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

  abrirMenuAcciones(entrevista: EntrevistaResumen, event: MouseEvent) {
    event.stopPropagation();
    this.menuAbiertoId = this.menuAbiertoId === entrevista.id ? '' : entrevista.id;
  }

  cerrarMenuAcciones() {
    this.menuAbiertoId = '';
  }

  menuAccionesAbierto(entrevista: EntrevistaResumen) {
    return this.menuAbiertoId === entrevista.id;
  }

  accionGestionar(entrevista: EntrevistaResumen) {
    if (!this.puedeCambiarEstado(entrevista)) {
      return;
    }

    this.cerrarMenuAcciones();
    this.abrirEstado(entrevista, 'gestionar');
  }

  accionReprogramar(entrevista: EntrevistaResumen) {
    if (!this.puedeCambiarEstado(entrevista)) {
      return;
    }

    this.cerrarMenuAcciones();
    this.abrirEstado(entrevista, 'reprogramar');
  }

  accionCancelar(entrevista: EntrevistaResumen) {
    if (!this.puedeCambiarEstado(entrevista)) {
      return;
    }

    this.cerrarMenuAcciones();
    this.abrirEstado(entrevista, 'cancelar');
  }

  accionFeedback(entrevista: EntrevistaResumen) {
    this.cerrarMenuAcciones();
    this.abrirFeedback(entrevista);
  }

  guardarEvaluaciones(payloads: EvaluacionTipoPayload[]) {
    if (!this.entrevistaSeleccionada || payloads.length === 0 || this.guardandoEvaluaciones) {
      return;
    }

    if (!this.esEstadoEntrevista(this.entrevistaSeleccionada, ['Realizada'])) {
      this.errorEvaluaciones = 'Solo puedes registrar feedback cuando la entrevista está realizada.';
      this.cdr.markForCheck();
      return;
    }

    this.guardandoEvaluaciones = true;
    this.errorEvaluaciones = '';
    this.mensajeEvaluaciones = '';

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
          catchError((error) => {
            this.registrarDiagnosticoFeedback(payload, body, error);
            const mensaje = this.mensajeErrorEvaluacion(error, 'no se pudo guardar el resultado.');
            return throwError(() => new Error(this.esErrorEstadoSolicitudFeedback(mensaje) ? mensaje : `${area}: ${mensaje}`));
          }),
        );
      }),
    )
      .pipe(
        finalize(() => {
          this.guardandoEvaluaciones = false;
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: () => {
          this.mensajeEvaluaciones = 'Feedback guardado correctamente.';
          this.cargarDetalleEntrevista(this.entrevistaSeleccionada!.id);
          this.cargarEntrevistas();
          this.cdr.markForCheck();
        },
        error: (error) => {
          this.errorEvaluaciones = this.mensajeErrorEvaluacion(error, 'No se pudo guardar el feedback.');
          this.cdr.markForCheck();
        },
      });
  }

  estadoClase(estado: string) {
    return this.normalizar(estado).replace(/\s+/g, '-');
  }

  puedeCambiarEstado(entrevista: EntrevistaResumen) {
    return this.cumplePrecondicionEntrevista(entrevista) &&
      !this.esEstadoEntrevista(entrevista, ['Cancelada', 'Realizada', 'No Asistio']);
  }

  puedeRegistrarFeedback(entrevista: EntrevistaResumen) {
    return this.esEstadoEntrevista(entrevista, ['Realizada']);
  }

  private esEstadoEntrevista(entrevista: EntrevistaResumen, estados: string[]) {
    const actual = this.normalizar(entrevista.estado);
    return estados.some((estado) => this.normalizar(estado) === actual);
  }

  private cumplePrecondicionEntrevista(entrevista: EntrevistaResumen) {
    const estadoPostulacion = this.normalizar(entrevista.estadoPostulacion ?? '');
    const estadoSolicitud = this.normalizar(entrevista.estadoSolicitud ?? '');

    return estadoPostulacion === 'en entrevista' && estadoSolicitud === 'en entrevistas';
  }

  private mensajeSolicitudBloqueada(entrevista: EntrevistaResumen) {
    return this.solicitudCancelada(entrevista)
      ? 'Esta solicitud está cancelada. Puedes revisar la entrevista como historial, pero no realizar nuevas acciones.'
      : 'La entrevista no cumple las condiciones actuales para realizar esta acción.';
  }

  private solicitudCancelada(entrevista: EntrevistaResumen) {
    return this.normalizar(entrevista.estadoSolicitud ?? '') === 'cancelado';
  }

  actualizarCalendario() {
    const [anio, mes] = this.mesSeleccionado.split('-').map(Number);
    const inicioMes = new Date(anio, mes - 1, 1);
    const finMes = new Date(anio, mes, 0);
    const offsetInicio = (inicioMes.getDay() + 6) % 7;
    const totalDias = offsetInicio + finMes.getDate();
    const totalCeldas = Math.ceil(totalDias / 7) * 7;
    const primerDia = new Date(inicioMes);
    primerDia.setDate(inicioMes.getDate() - offsetInicio);

    this.diasCalendario = Array.from({ length: totalCeldas }, (_, indice) => {
      const fecha = new Date(primerDia);
      fecha.setDate(primerDia.getDate() + indice);
      const fechaIso = this.formatearIso(fecha);

      return {
        fecha,
        fechaIso,
        esMesActual: fecha.getMonth() === mes - 1,
        cantidad: this.entrevistasFiltradasPorEstado.filter((entrevista) => entrevista.fecha === fechaIso).length,
      };
    });
  }

  private cargarCatalogosGestion() {
    forkJoin({
      resultados: this.catalogosService.listarNombresResultado().pipe(catchError(() => of([]))),
      estados: this.catalogosService.listarEstadosEntrevista().pipe(catchError(() => of([]))),
    })
      .pipe(take(1))
      .subscribe(({ resultados, estados }) => {
        this.resultadosEvaluacion = resultados;
        const estadosCatalogo = estados.map((estado) => estado.esev_nombre).filter((nombre): nombre is string => Boolean(nombre));
        if (estadosCatalogo.length > 0) {
          this.estadosEntrevista = estadosCatalogo;
        }
        this.cdr.markForCheck();
      });
  }

  motivoAccionNoDisponible(entrevista: EntrevistaResumen, accion: 'feedback' | 'gestion' = 'gestion') {
    if (accion === 'feedback') {
      return 'No disponible: la entrevista aún no está realizada.';
    }

    if (this.solicitudCancelada(entrevista)) {
      return 'No disponible: la solicitud está cancelada.';
    }

    if (this.normalizar(entrevista.estadoSolicitud ?? '') !== 'en entrevistas') {
      return 'No disponible: la solicitud no está en etapa de entrevistas.';
    }

    if (this.normalizar(entrevista.estadoPostulacion ?? '') !== 'en entrevista') {
      return 'No disponible: la postulación no está en entrevista.';
    }

    return 'No disponible para el estado actual de la entrevista.';
  }

  @HostListener('document:click')
  cerrarMenuAlHacerClickFuera() {
    this.cerrarMenuAcciones();
  }

  private cargarDetalleEntrevista(id: string) {
    this.cargandoDetalle = true;
    this.cdr.markForCheck();

    forkJoin({
      detalle: this.entrevistasService.obtener(id),
      evaluaciones: this.entrevistasService.listarEvaluaciones(id).pipe(catchError(() => of([]))),
    })
      .pipe(
        take(1),
        finalize(() => {
          this.cargandoDetalle = false;
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: ({ detalle, evaluaciones }) => {
          this.entrevistaDetalle = {
            ...detalle,
            evaluaciones,
          };
          this.registrarDiagnosticoAperturaFeedback();
          this.cdr.markForCheck();
        },
        error: (error) => {
          this.errorEstado = obtenerMensajeError(error, 'No se pudo cargar el detalle de la entrevista.');
          this.cdr.markForCheck();
        },
      });
  }

  fechaHoy() {
    return this.formatearIso(new Date());
  }

  private formatearMes(fecha: Date) {
    return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
  }

  private formatearIso(fecha: Date) {
    return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`;
  }

  private formatearFechaCorta(fechaIso: string) {
    return new Date(`${fechaIso}T00:00:00`).toLocaleDateString('es-CL', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  }

  private normalizar(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  private mensajeErrorEvaluacion(error: unknown, mensajePorDefecto: string) {
    if (error instanceof Error && error.message.trim()) {
      return this.mensajeEstadoSolicitudFeedback(error.message);
    }

    return this.mensajeEstadoSolicitudFeedback(obtenerMensajeError(error, mensajePorDefecto));
  }

  private mensajeEstadoSolicitudFeedback(mensaje: string) {
    return this.esErrorEstadoSolicitudFeedback(mensaje)
      ? 'No se pudo guardar el feedback. La solicitud asociada a esta entrevista no permite registrar evaluaciones en su estado actual.'
      : mensaje;
  }

  private esErrorEstadoSolicitudFeedback(mensaje: string) {
    return /Solo se permiten entrevistas y evaluaciones cuando la solicitud está en estado 'En Entrevistas'/i.test(mensaje);
  }

  private registrarDiagnosticoFeedback(
    payload: EvaluacionTipoPayload,
    body: { nombre_resultado_id: number; observacion: string | null },
    error: unknown,
  ) {
    console.warn('Diagnóstico feedback entrevista', {
      entrevista_id: this.entrevistaSeleccionada?.id,
      solicitud_id: this.entrevistaDetalle?.solicitud_id,
      solicitud_candidato_id: this.entrevistaDetalle?.solicitud_candidato_id,
      candidato_id: this.entrevistaDetalle?.candidato_id,
      tipo_entrevista_id: payload.tipoId,
      usuario_id: this.usuarioActualId,
      payload: body,
      error,
    });
  }

  private registrarDiagnosticoAperturaFeedback() {
    if (this.modoEstado !== 'gestionar' || !this.entrevistaDetalle) {
      return;
    }

    console.debug('Diagnóstico apertura feedback entrevista', {
      entrevista_id: this.entrevistaDetalle.entrevista_id,
      solicitud_id: this.entrevistaDetalle.solicitud_id,
      solicitud_candidato_id: this.entrevistaDetalle.solicitud_candidato_id,
      candidato_id: this.entrevistaDetalle.candidato_id,
      tipo_entrevista_id: this.entrevistaDetalle.tipos?.map((tipo) => tipo.tipo_entrevista_id) ?? [],
      usuario_id: this.usuarioActualId,
    });
  }
}
