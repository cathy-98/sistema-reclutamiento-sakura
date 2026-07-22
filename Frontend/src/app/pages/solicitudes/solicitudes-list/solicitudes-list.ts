import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../../services/auth.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { Alert } from '../../../shared/components/alert/alert';
import { ConfirmDialog } from '../../../shared/components/confirm-dialog/confirm-dialog';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { SolicitudResumen } from '../../../shared/models/solicitud.model';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { SolicitudFormModal } from '../solicitud-form-modal/solicitud-form-modal';

@Component({
  selector: 'app-solicitudes-list',
  imports: [CommonModule, SolicitudFormModal, ConfirmDialog, Alert],
  templateUrl: './solicitudes-list.html',
  styleUrl: './solicitudes-list.scss',
})
export class SolicitudesList implements OnInit {
  cargando = false;
  alerta: AlertaUi | null = null;
  mostrarFormulario = false;
  mostrarConfirmacionCancelacion = false;
  solicitudSeleccionadaId: string | null = null;
  modoFormulario: 'crear' | 'ver' | 'editar' = 'crear';
  solicitudes: SolicitudResumen[] = [];

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

  estadoClase(estado: string) {
    return estado.toLowerCase().replace(/\s+/g, '-');
  }

  prioridadClase(prioridad: string) {
    return prioridad.toLowerCase();
  }

  cargarSolicitudes() {
    this.cargando = true;
    this.alerta = null;

    this.solicitudesService.listar().subscribe({
      next: (solicitudes) => {
        this.solicitudes = solicitudes;
        this.cargando = false;
      },
      error: (error) => {
        this.cargando = false;
        this.alerta = {
          tipo: 'danger',
          variante: 'soft',
          mensaje: obtenerMensajeError(error, 'No se pudieron cargar las solicitudes.'),
        };
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
}

