import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  EntrevistaResumen,
  EntrevistasService,
  EstadoEntrevista,
} from '../../../services/entrevistas.service';
import { AlertRegion } from '../../../shared/components/alert-region/alert-region';
import { Button } from '../../../shared/components/button/button';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { TabItem, Tabs } from '../../../shared/components/tabs/tabs';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { EntrevistaEstadoModal } from '../entrevista-estado-modal/entrevista-estado-modal';

type AgendaTab = 'hoy' | 'proximas' | 'pendientes' | 'realizadas' | 'canceladas';

interface DiaAgenda {
  fecha: Date;
  fechaIso: string;
  esMesActual: boolean;
  cantidad: number;
}

@Component({
  selector: 'app-entrevistas-agenda',
  imports: [CommonModule, FormsModule, AlertRegion, Button, EntrevistaEstadoModal, PageHeader, PageLayout, Tabs],
  templateUrl: './entrevistas-agenda.html',
  styleUrl: './entrevistas-agenda.scss',
})
export class EntrevistasAgenda implements OnInit {
  cargando = false;
  errorCarga = '';
  alerta: AlertaUi | null = null;
  entrevistas: EntrevistaResumen[] = [];
  entrevistaSeleccionada: EntrevistaResumen | null = null;
  modoEstado: 'reprogramar' | 'cancelar' = 'reprogramar';
  tabActiva: AgendaTab = 'hoy';
  fechaSeleccionada = this.fechaHoy();
  mesSeleccionado = this.fechaHoy().slice(0, 7);
  busqueda = '';
  diasCalendario: DiaAgenda[] = [];

  readonly diasSemana = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];
  readonly tabs: TabItem[] = [
    { id: 'hoy', label: 'Hoy' },
    { id: 'proximas', label: 'Próximas' },
    { id: 'pendientes', label: 'Pendientes' },
    { id: 'realizadas', label: 'Realizadas' },
    { id: 'canceladas', label: 'Canceladas' },
  ];

  constructor(private entrevistasService: EntrevistasService) {}

  ngOnInit() {
    this.actualizarCalendario();
    this.cargarEntrevistas();
  }

  get tituloMes() {
    const [anio, mes] = this.mesSeleccionado.split('-').map(Number);
    return new Intl.DateTimeFormat('es-CL', { month: 'long', year: 'numeric' }).format(new Date(anio, mes - 1, 1));
  }

  get entrevistasDia() {
    const busquedaNormalizada = this.normalizar(this.busqueda);

    return this.entrevistasFiltradasPorTab
      .filter((entrevista) => entrevista.fecha === this.fechaSeleccionada)
      .filter((entrevista) => {
        const texto = this.normalizar(
          `${entrevista.candidato} ${entrevista.idSolicitud} ${entrevista.cargo} ${entrevista.tipo} ${entrevista.entrevistador}`,
        );
        return !busquedaNormalizada || texto.includes(busquedaNormalizada);
      })
      .sort((a, b) => a.horaInicio.localeCompare(b.horaInicio));
  }

  get entrevistasFiltradasPorTab() {
    const hoy = this.fechaHoy();
    const limiteProximas = this.sumarDias(hoy, 14);
    const limitePendientes = this.sumarDias(hoy, 30);
    const limiteHistorico = this.sumarDias(hoy, -30);

    return this.entrevistas.filter((entrevista) => {
      if (this.tabActiva === 'hoy') {
        return entrevista.fecha === hoy;
      }
      if (this.tabActiva === 'proximas') {
        return entrevista.fecha >= hoy && entrevista.fecha <= limiteProximas && entrevista.estado !== 'Cancelada' && entrevista.estado !== 'Realizada';
      }
      if (this.tabActiva === 'pendientes') {
        return (
          (entrevista.estado === 'Pendiente' || entrevista.estado === 'Confirmada' || entrevista.estado === 'Reprogramada') &&
          entrevista.fecha >= hoy &&
          entrevista.fecha <= limitePendientes
        );
      }
      if (this.tabActiva === 'realizadas') {
        return entrevista.estado === 'Realizada' && entrevista.fecha >= limiteHistorico && entrevista.fecha <= hoy;
      }
      if (this.tabActiva === 'canceladas') {
        return entrevista.estado === 'Cancelada' && entrevista.fecha >= limiteHistorico && entrevista.fecha <= hoy;
      }
      return false;
    });
  }

  cargarEntrevistas() {
    this.cargando = true;
    this.errorCarga = '';

    this.entrevistasService.listar().subscribe({
      next: (entrevistas) => {
        this.entrevistas = entrevistas;
        this.seleccionarFechaInicial();
        this.actualizarCalendario();
        this.cargando = false;
      },
      error: (error) => {
        this.entrevistas = [];
        this.errorCarga = obtenerMensajeError(error, 'No se pudieron cargar las entrevistas.');
        this.cargando = false;
      },
    });
  }

  cambiarTab(tab: string) {
    this.tabActiva = tab as AgendaTab;
    if (this.tabActiva === 'hoy') {
      this.fechaSeleccionada = this.fechaHoy();
      this.mesSeleccionado = this.fechaSeleccionada.slice(0, 7);
    } else {
      this.seleccionarFechaInicial();
    }
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

  abrirEstado(entrevista: EntrevistaResumen, modo: 'reprogramar' | 'cancelar') {
    this.entrevistaSeleccionada = entrevista;
    this.modoEstado = modo;
  }

  cerrarModalEstado() {
    this.entrevistaSeleccionada = null;
  }

  confirmarEstado(payload: { fecha: string; horaInicio: string; horaFin: string; motivo: string }) {
    if (!this.entrevistaSeleccionada) {
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

    solicitud.subscribe({
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
        this.alerta = {
          tipo: 'danger',
          variante: 'soft',
          mensaje: obtenerMensajeError(error, 'No se pudo actualizar la entrevista.'),
        };
      },
    });
  }

  verDetalle(entrevista: EntrevistaResumen) {
    this.alerta = {
      tipo: 'info',
      variante: 'soft',
      mensaje: `${entrevista.candidato} - ${entrevista.tipo} ${entrevista.horaInicio} a ${entrevista.horaFin}.`,
    };
  }

  abrirFeedback(entrevista: EntrevistaResumen) {
    this.alerta = {
      tipo: 'warning',
      variante: 'soft',
      mensaje: `El formulario de feedback para ${entrevista.candidato} queda como siguiente paso del módulo entrevistas.`,
    };
  }

  cerrarAlerta() {
    this.alerta = null;
  }

  estadoClase(estado: EstadoEntrevista) {
    return estado.toLowerCase().replace(/\s+/g, '-');
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
        cantidad: this.entrevistasFiltradasPorTab.filter((entrevista) => entrevista.fecha === fechaIso).length,
      };
    });
  }

  private seleccionarFechaInicial() {
    const entrevistasOrdenadas = [...this.entrevistasFiltradasPorTab].sort((a, b) => {
      const ordenFecha = a.fecha.localeCompare(b.fecha);
      return ordenFecha !== 0 ? ordenFecha : a.horaInicio.localeCompare(b.horaInicio);
    });
    const fechaDisponible = entrevistasOrdenadas[0]?.fecha;

    if (fechaDisponible) {
      this.fechaSeleccionada = fechaDisponible;
      this.mesSeleccionado = fechaDisponible.slice(0, 7);
      return;
    }

    this.fechaSeleccionada = this.fechaHoy();
    this.mesSeleccionado = this.fechaSeleccionada.slice(0, 7);
  }

  private fechaHoy() {
    return this.formatearIso(new Date());
  }

  private formatearMes(fecha: Date) {
    return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
  }

  private formatearIso(fecha: Date) {
    return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`;
  }

  private sumarDias(fechaIso: string, dias: number) {
    const fecha = new Date(`${fechaIso}T00:00:00`);
    fecha.setDate(fecha.getDate() + dias);
    return this.formatearIso(fecha);
  }

  private normalizar(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }
}
