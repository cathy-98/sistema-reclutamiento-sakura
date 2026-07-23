import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { take, timeout } from 'rxjs';
import { AuthService } from '../../../services/auth.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { Alert } from '../../../shared/components/alert/alert';
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
    Alert,
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
  modoFormulario: 'crear' | 'ver' | 'editar' = 'crear';
  solicitudes: SolicitudResumen[] = [];
  seleccionados = new Set<string>();
  paginaActual = 1;
  registrosPorPagina = 5;
  filtros: FiltrosSolicitudes = this.filtrosIniciales();
  private cargaTimeoutId: ReturnType<typeof setTimeout> | null = null;

  readonly columnas: DataTableColumn<SolicitudResumen>[] = [
    {
      key: 'id',
      label: 'ID solicitud',
      width: 112,
      sticky: 'left',
    },
    {
      key: 'nombre',
      label: 'Nombre de solicitud',
      width: 260,
      type: 'stack',
      value: (solicitud) => solicitud.nombre,
      secondaryValue: (solicitud) => `${solicitud.vacantes} vacantes`,
    },
    {
      key: 'cliente',
      label: 'Cliente',
      width: 180,
    },
    {
      key: 'cargo',
      label: 'Cargo / vacantes',
      width: 155,
      value: (solicitud) => `${solicitud.cargo} / ${solicitud.vacantes}`,
    },
    {
      key: 'responsable',
      label: 'Responsable',
      width: 155,
    },
    {
      key: 'seleccion',
      label: 'Inicio y fin selección',
      width: 190,
    },
    {
      key: 'inicioEmpleo',
      label: 'Inicio empleo',
      width: 190,
    },
    {
      key: 'prioridad',
      label: 'Prioridad',
      width: 155,
      type: 'badge',
      className: (solicitud) => this.prioridadClase(solicitud.prioridad),
    },
    {
      key: 'estado',
      label: 'Estado',
      width: 155,
      type: 'badge',
      className: (solicitud) => this.estadoClase(solicitud.estado),
    },
    {
      key: 'observacion',
      label: 'Observación',
      width: 220,
      title: (solicitud) => solicitud.observacion,
    },
  ];

  constructor(
    private authService: AuthService,
    private solicitudesService: SolicitudesService,
  ) {}

  ngOnInit() {
    this.cargarSolicitudes();
  }

  get puedeCrearSolicitud() {
    return this.authService.tieneRol(['Administrador', 'Reclutador']);
  }

  get puedeEditarSolicitud() {
    return this.authService.tieneRol(['Administrador', 'Reclutador']);
  }

  get puedeCancelarSolicitud() {
    return this.authService.tieneRol(['Administrador']);
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
        `${solicitud.id} ${solicitud.nombre} ${solicitud.cliente} ${solicitud.cargo} ${solicitud.responsable}`,
      );

      return (
        textoSolicitud.includes(filtros.busquedaRapida) &&
        this.normalizar(solicitud.id).includes(filtros.id) &&
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
      },
    ];
  }

  estadoClase(estado: string) {
    return estado.toLowerCase().replace(/\s+/g, '-');
  }

  prioridadClase(prioridad: string) {
    return prioridad.toLowerCase();
  }

  cargarSolicitudes() {
    this.cargando = true;
    this.errorCarga = '';
    this.alerta = null;
    this.limpiarTimeoutCarga();
    this.cargaTimeoutId = setTimeout(() => {
      if (!this.cargando) {
        return;
      }

      this.cargando = false;
      this.solicitudes = [];
      this.errorCarga = 'El servidor tardó demasiado en responder. Intenta recargar el listado.';
    }, 10000);

    this.solicitudesService
      .listar()
      .pipe(
        timeout(10000),
        take(1),
      )
      .subscribe({
        next: (solicitudes) => {
          this.solicitudes = solicitudes;
          this.paginaActual = 1;
          this.cargando = false;
          this.errorCarga = '';
          this.limpiarTimeoutCarga();
        },
        error: (error) => {
          this.solicitudes = [];
          this.cargando = false;
          this.limpiarTimeoutCarga();
          this.errorCarga =
            error.name === 'TimeoutError'
              ? 'El servidor tardó demasiado en responder. Intenta recargar el listado.'
              : obtenerMensajeError(error, 'No se pudieron cargar las solicitudes.');
        },
      });
  }

  abrirFormulario() {
    if (!this.puedeCrearSolicitud) {
      this.mostrarAlertaPermisos();
      return;
    }

    this.solicitudSeleccionadaId = null;
    this.modoFormulario = 'crear';
    this.mostrarFormulario = true;
  }

  abrirDetalleSolicitud(id: string) {
    this.solicitudSeleccionadaId = id;
    this.modoFormulario = 'ver';
    this.mostrarFormulario = true;
  }

  abrirEdicionSolicitud(id: string) {
    if (!this.puedeEditarSolicitud) {
      this.mostrarAlertaPermisos();
      return;
    }

    this.solicitudSeleccionadaId = id;
    this.modoFormulario = 'editar';
    this.mostrarFormulario = true;
  }

  abrirConfirmacionCancelacion(id: string) {
    if (!this.puedeCancelarSolicitud) {
      this.mostrarAlertaPermisos();
      return;
    }

    this.solicitudSeleccionadaId = id;
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
      this.abrirDetalleSolicitud(evento.row.id);
      return;
    }

    if (evento.action === 'editar') {
      this.abrirEdicionSolicitud(evento.row.id);
      return;
    }

    if (evento.action === 'cancelar') {
      this.abrirConfirmacionCancelacion(evento.row.id);
    }
  }

  cerrarConfirmacionCancelacion() {
    this.mostrarConfirmacionCancelacion = false;
    this.solicitudSeleccionadaId = null;
  }

  confirmarCancelacionSolicitud() {
    if (!this.solicitudSeleccionadaId) {
      return;
    }

    this.solicitudesService
      .cambiarEstado(
        this.solicitudSeleccionadaId,
        'Cancelada',
        'Solicitud cancelada por confirmación del usuario.',
      )
      .subscribe({
        next: () => {
          this.alerta = {
            tipo: 'success',
            variante: 'soft',
            mensaje: 'Solicitud cancelada correctamente.',
          };
          this.cerrarConfirmacionCancelacion();
        },
        error: (error) => {
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo cancelar la solicitud.'),
          };
          this.cerrarConfirmacionCancelacion();
        },
      });
  }

  cerrarFormulario() {
    this.mostrarFormulario = false;
    this.solicitudSeleccionadaId = null;
    this.modoFormulario = 'crear';
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
    this.alerta = {
      tipo: 'warning',
      variante: 'soft',
      mensaje: 'No tienes permisos para realizar esta acción.',
    };
  }

  obtenerIdSolicitud(solicitud: SolicitudResumen) {
    return solicitud.id;
  }

  private limpiarTimeoutCarga() {
    if (!this.cargaTimeoutId) {
      return;
    }

    clearTimeout(this.cargaTimeoutId);
    this.cargaTimeoutId = null;
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
}

