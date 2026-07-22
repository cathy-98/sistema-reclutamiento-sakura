import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
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
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { SolicitudResumen } from '../../../shared/models/solicitud.model';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { SolicitudFormModal } from '../solicitud-form-modal/solicitud-form-modal';

@Component({
  selector: 'app-solicitudes-list',
  imports: [CommonModule, SolicitudFormModal, ConfirmDialog, Alert, DataTable, PageHeader],
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
    return this.solicitudes.slice(inicio, inicio + this.registrosPorPagina);
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
    const totalPaginas = Math.max(1, Math.ceil(this.solicitudes.length / this.registrosPorPagina));
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
}

