import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize, take, timeout } from 'rxjs';
import { AuthService } from '../../../services/auth.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { AlertRegion } from '../../../shared/components/alert-region/alert-region';
import { Button } from '../../../shared/components/button/button';
import { ConfirmDialog } from '../../../shared/components/confirm-dialog/confirm-dialog';
import {
  DataTable,
  DataTableAction,
  DataTableActionEvent,
  DataTableColumn,
} from '../../../shared/components/data-table/data-table';
import { FilterPanel } from '../../../shared/components/filter-panel/filter-panel';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { SolicitudResumen } from '../../../shared/models/solicitud.model';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { SolicitudFormModal } from '../solicitud-form-modal/solicitud-form-modal';

const SOLICITUDES_LOAD_TIMEOUT_MS = 4000;

interface FiltrosSolicitudes {
  busquedaRapida: string;
  id: string;
  nombre: string;
  cliente: string;
  cargo: string;
  responsable: string;
  prioridad: string;
  estado: string;
}

@Component({
  selector: 'app-solicitudes-list',
  imports: [
    CommonModule,
    FormsModule,
    SolicitudFormModal,
    ConfirmDialog,
    AlertRegion,
    Button,
    DataTable,
    PageHeader,
    PageLayout,
    FilterPanel,
  ],
  templateUrl: './solicitudes-list.html',
  styleUrl: './solicitudes-list.scss',
})
export class SolicitudesList implements OnInit {
  cargando = false;
  errorCarga = '';
  alerta: AlertaUi | null = null;
  mostrarFormulario = false;
  mostrarConfirmacionCancelacion = false;
  solicitudSeleccionadaId: string | null = null;
  solicitudSeleccionadaCodigo: string | null = null;
  solicitudSeleccionadaResumen: SolicitudResumen | null = null;
  observacionCancelacion = '';
  modoFormulario: 'crear' | 'ver' | 'editar' = 'crear';
  solicitudes: SolicitudResumen[] = [];
  seleccionados = new Set<string>();
  paginaActual = 1;
  registrosPorPagina = 5;
  filtros: FiltrosSolicitudes = this.filtrosIniciales();

  readonly columnas: DataTableColumn<SolicitudResumen>[] = [
    {
      key: 'codigo',
      label: 'ID solicitud',
      width: 138,
      sticky: 'left',
      sortable: true,
    },
    {
      key: 'nombre',
      label: 'Nombre de solicitud',
      width: 300,
      type: 'stack',
      wrap: true,
      value: (solicitud) => solicitud.nombre,
      secondaryValue: (solicitud) => `${solicitud.vacantes} vacantes`,
      sortable: true,
    },
    {
      key: 'cliente',
      label: 'Cliente',
      width: 260,
      wrap: true,
      sortable: true,
    },
    {
      key: 'cargo',
      label: 'Cargo / vacantes',
      width: 250,
      wrap: true,
      value: (solicitud) => `${solicitud.cargo} / ${solicitud.vacantes}`,
      sortable: true,
    },
    {
      key: 'responsable',
      label: 'Reclutador asignado',
      width: 190,
      wrap: true,
      sortable: true,
    },
    {
      key: 'seleccion',
      label: 'Selección',
      width: 178,
      type: 'stack',
      value: (solicitud) => `Inicio: ${this.fechaInicioSeleccion(solicitud)}`,
      secondaryValue: (solicitud) => `Fin: ${this.fechaFinSeleccion(solicitud)}`,
      sortable: true,
    },
    {
      key: 'inicioEmpleo',
      label: 'Inicio empleo',
      width: 132,
      sortable: true,
    },
    {
      key: 'prioridad',
      label: 'Prioridad',
      width: 118,
      type: 'badge',
      className: (solicitud) => this.prioridadClase(solicitud.prioridad),
      sortable: true,
    },
    {
      key: 'estado',
      label: 'Estado',
      width: 132,
      type: 'badge',
      className: (solicitud) => this.estadoClase(solicitud.estado),
      sortable: true,
    },
    {
      key: 'descripcion',
      label: 'Descripción',
      width: 360,
      wrap: true,
      title: (solicitud) => solicitud.descripcion,
    },
  ];

  constructor(
    private authService: AuthService,
    private solicitudesService: SolicitudesService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.cargarSolicitudes();
  }

  get puedeCrearSolicitud() {
    return this.authService.puedeAcceder(['Administrador', 'Reclutador'], ['SOL_CREATE']);
  }

  get puedeEditarSolicitud() {
    return this.authService.puedeAcceder(['Administrador', 'Reclutador'], ['SOL_UPDATE']);
  }

  get puedeCancelarSolicitud() {
    return this.authService.puedeAcceder(['Administrador'], ['SOL_DELETE']);
  }

  puedeCancelarSolicitudFila(solicitud: SolicitudResumen) {
    return this.puedeCancelarSolicitud && this.estadoPermiteCancelacion(solicitud.estado);
  }

  get codigoSolicitudEstimado() {
    const correlativos = this.solicitudes
      .map((solicitud) => /^SOL-(\d{6})$/.exec(solicitud.codigo)?.[1])
      .filter((codigo): codigo is string => Boolean(codigo))
      .map((codigo) => Number(codigo));
    const siguiente = (correlativos.length > 0 ? Math.max(...correlativos) : 0) + 1;

    return `SOL-${String(siguiente).padStart(6, '0')}`;
  }

  get solicitudesPaginadas() {
    const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
    return this.solicitudesFiltradas.slice(inicio, inicio + this.registrosPorPagina);
  }

  get solicitudesFiltradas() {
    const filtros = {
      busquedaRapida: this.normalizar(this.filtros.busquedaRapida),
      id: this.normalizar(this.filtros.id),
      nombre: this.normalizar(this.filtros.nombre),
      cliente: this.normalizar(this.filtros.cliente),
      cargo: this.normalizar(this.filtros.cargo),
      responsable: this.normalizar(this.filtros.responsable),
      prioridad: this.normalizar(this.filtros.prioridad),
      estado: this.normalizar(this.filtros.estado),
    };

    return this.solicitudes.filter((solicitud) => {
      const textoSolicitud = this.normalizar(
        `${solicitud.codigo} ${solicitud.nombre} ${solicitud.cliente} ${solicitud.cargo} ${solicitud.responsable}`,
      );

      return (
        textoSolicitud.includes(filtros.busquedaRapida) &&
        this.normalizar(solicitud.codigo).includes(filtros.id) &&
        this.normalizar(solicitud.nombre).includes(filtros.nombre) &&
        this.normalizar(solicitud.cliente).includes(filtros.cliente) &&
        this.normalizar(solicitud.cargo).includes(filtros.cargo) &&
        this.normalizar(solicitud.responsable).includes(filtros.responsable) &&
        (!filtros.prioridad || this.normalizar(solicitud.prioridad) === filtros.prioridad) &&
        (!filtros.estado || this.normalizar(solicitud.estado) === filtros.estado)
      );
    });
  }

  get acciones(): DataTableAction<SolicitudResumen>[] {
    return [
      {
        id: 'ver',
        label: 'Ver solicitud',
        icon: 'eye',
      },
      {
        id: 'editar',
        label: 'Editar solicitud',
        icon: 'edit',
        visible: () => this.puedeEditarSolicitud,
      },
      {
        id: 'cancelar',
        label: 'Cancelar solicitud',
        icon: 'cancel',
        visible: () => this.puedeCancelarSolicitud,
        disabled: (solicitud) => !this.puedeCancelarSolicitudFila(solicitud),
      },
    ];
  }

  estadoClase(estado: string) {
    return estado.toLowerCase().replace(/\s+/g, '-');
  }

  prioridadClase(prioridad: string) {
    return prioridad.toLowerCase();
  }

  cargarSolicitudes(opciones: { conservarAlerta?: boolean } = {}) {
    this.cargando = true;
    this.errorCarga = '';
    if (!opciones.conservarAlerta) {
      this.alerta = null;
    }
    this.cdr.detectChanges();

    this.solicitudesService
      .listar()
      .pipe(
        timeout(SOLICITUDES_LOAD_TIMEOUT_MS),
        take(1),
        finalize(() => {
          this.cargando = false;
          this.cdr.detectChanges();
        }),
      )
      .subscribe({
        next: (solicitudes) => {
          this.solicitudes = solicitudes;
          this.paginaActual = 1;
          this.errorCarga = '';
        },
        error: (error) => {
          this.solicitudes = [];
          this.errorCarga = obtenerMensajeError(error, 'El listado superó 4 segundos de espera. Reintenta la carga.');
        },
      });
  }

  abrirFormulario() {
    if (!this.puedeCrearSolicitud) {
      this.mostrarAlertaPermisos();
      return;
    }

    this.solicitudSeleccionadaId = null;
    this.solicitudSeleccionadaCodigo = null;
    this.solicitudSeleccionadaResumen = null;
    this.modoFormulario = 'crear';
    this.mostrarFormulario = true;
  }

  abrirDetalleSolicitud(solicitud: SolicitudResumen) {
    this.solicitudSeleccionadaId = solicitud.id;
    this.solicitudSeleccionadaCodigo = solicitud.codigo;
    this.solicitudSeleccionadaResumen = solicitud;
    this.modoFormulario = 'ver';
    this.mostrarFormulario = true;
  }

  abrirEdicionSolicitud(solicitud: SolicitudResumen) {
    if (!this.puedeEditarSolicitud) {
      this.mostrarAlertaPermisos();
      return;
    }

    this.solicitudSeleccionadaId = solicitud.id;
    this.solicitudSeleccionadaCodigo = solicitud.codigo;
    this.solicitudSeleccionadaResumen = solicitud;
    this.modoFormulario = 'editar';
    this.mostrarFormulario = true;
  }

  abrirConfirmacionCancelacion(solicitud: SolicitudResumen) {
    if (!this.puedeCancelarSolicitud) {
      this.mostrarAlertaPermisos();
      return;
    }

    if (!this.estadoPermiteCancelacion(solicitud.estado)) {
      this.mostrarAlerta({
        tipo: 'warning',
        variante: 'soft',
        mensaje: `No puedes cancelar una solicitud en estado "${solicitud.estado}".`,
      });
      return;
    }

    this.solicitudSeleccionadaId = solicitud.id;
    this.solicitudSeleccionadaCodigo = solicitud.codigo;
    this.solicitudSeleccionadaResumen = solicitud;
    this.observacionCancelacion = '';
    this.mostrarConfirmacionCancelacion = true;
  }

  cambiarPagina(pagina: number) {
    const totalPaginas = Math.max(
      1,
      Math.ceil(this.solicitudesFiltradas.length / this.registrosPorPagina),
    );
    this.paginaActual = Math.min(Math.max(pagina, 1), totalPaginas);
  }

  cambiarRegistrosPorPagina(registros: number) {
    this.registrosPorPagina = registros;
    this.paginaActual = 1;
  }

  manejarAccionTabla(evento: DataTableActionEvent<SolicitudResumen>) {
    if (evento.action === 'ver') {
      this.abrirDetalleSolicitud(evento.row);
      return;
    }

    if (evento.action === 'editar') {
      this.abrirEdicionSolicitud(evento.row);
      return;
    }

    if (evento.action === 'cancelar') {
      this.abrirConfirmacionCancelacion(evento.row);
    }
  }

  cerrarConfirmacionCancelacion() {
    this.mostrarConfirmacionCancelacion = false;
    this.solicitudSeleccionadaId = null;
    this.solicitudSeleccionadaCodigo = null;
    this.solicitudSeleccionadaResumen = null;
    this.observacionCancelacion = '';
  }

  confirmarCancelacionSolicitud(observacion: string) {
    if (!this.solicitudSeleccionadaId) {
      return;
    }

    const observacionCancelacion = observacion.trim();

    if (!observacionCancelacion) {
      this.mostrarAlerta({
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Ingresa una observación para cancelar la solicitud.',
      });
      return;
    }

    this.solicitudesService
      .cambiarEstado(
        this.solicitudSeleccionadaId,
        'Cancelado',
        observacionCancelacion,
      )
      .subscribe({
        next: () => {
          this.aplicarCancelacionEnListado(this.solicitudSeleccionadaId as string, observacionCancelacion);
          this.mostrarAlerta({
            tipo: 'success',
            variante: 'soft',
            mensaje: 'Solicitud cancelada correctamente.',
          });
          this.cerrarConfirmacionCancelacion();
        },
        error: (error) => {
          this.mostrarAlerta({
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo cancelar la solicitud.'),
          });
          this.cerrarConfirmacionCancelacion();
        },
      });
  }

  cerrarFormulario() {
    this.mostrarFormulario = false;
    this.solicitudSeleccionadaId = null;
    this.solicitudSeleccionadaCodigo = null;
    this.solicitudSeleccionadaResumen = null;
    this.modoFormulario = 'crear';
  }

  manejarFormularioGuardado() {
    this.cerrarFormulario();
    this.mostrarAlerta({
      tipo: 'success',
      variante: 'soft',
      mensaje: 'Solicitud guardada correctamente.',
    });
    this.cargarSolicitudes({ conservarAlerta: true });
  }

  cerrarAlerta() {
    this.alerta = null;
  }

  buscar() {
    this.paginaActual = 1;
  }

  limpiarFiltros() {
    this.filtros = this.filtrosIniciales();
    this.paginaActual = 1;
  }

  private mostrarAlertaPermisos() {
    this.mostrarAlerta({
      tipo: 'warning',
      variante: 'soft',
      mensaje: 'No tienes permisos para realizar esta acción.',
    });
  }

  private mostrarAlerta(alerta: AlertaUi) {
    this.alerta = alerta;
    window.requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  private estadoPermiteCancelacion(estado: string) {
    return ['pendiente', 'en curso', 'en entrevistas', 'pausado'].includes(this.normalizar(estado));
  }

  private aplicarCancelacionEnListado(idSolicitud: string, observacion: string) {
    this.solicitudes = this.solicitudes.map((solicitud) =>
      solicitud.id === idSolicitud
        ? {
            ...solicitud,
            estado: 'Cancelado',
            descripcion: observacion,
          }
        : solicitud,
    );
  }

  obtenerIdSolicitud(solicitud: SolicitudResumen) {
    return solicitud.id;
  }

  fechaInicioSeleccion(solicitud: SolicitudResumen) {
    return this.partesSeleccion(solicitud)[0] ?? 'Sin fecha';
  }

  fechaFinSeleccion(solicitud: SolicitudResumen) {
    return this.partesSeleccion(solicitud)[1] ?? 'Sin fecha';
  }

  private filtrosIniciales(): FiltrosSolicitudes {
    return {
      busquedaRapida: '',
      id: '',
      nombre: '',
      cliente: '',
      cargo: '',
      responsable: '',
      prioridad: '',
      estado: '',
    };
  }

  private normalizar(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }

  private partesSeleccion(solicitud: SolicitudResumen) {
    if (solicitud.seleccion === 'Sin fechas') {
      return ['Sin fecha', 'Sin fecha'];
    }

    return solicitud.seleccion.split(' - ');
  }

}

