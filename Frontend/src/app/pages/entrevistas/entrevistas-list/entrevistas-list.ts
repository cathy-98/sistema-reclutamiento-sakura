import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, forkJoin, of, take, timeout } from 'rxjs';
import {
  EntrevistaPayload,
  EntrevistaResumen,
  EntrevistasService,
  EstadoEntrevista,
  TipoEntrevista,
} from '../../../services/entrevistas.service';
import { ActionBar } from '../../../shared/components/action-bar/action-bar';
import { AlertRegion } from '../../../shared/components/alert-region/alert-region';
import { Button } from '../../../shared/components/button/button';
import {
  DataTable,
  DataTableAction,
  DataTableActionEvent,
  DataTableColumn,
} from '../../../shared/components/data-table/data-table';
import { FilterPanel } from '../../../shared/components/filter-panel/filter-panel';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { CatalogosService } from '../../../services/catalogos.service';
import { EntrevistaEstadoModal } from '../entrevista-estado-modal/entrevista-estado-modal';
import { EntrevistaFormModal } from '../entrevista-form-modal/entrevista-form-modal';

interface FiltrosEntrevistas {
  busquedaRapida: string;
  cargo: string;
  fecha: string;
  estado: '' | EstadoEntrevista;
  tipo: '' | TipoEntrevista;
}

@Component({
  selector: 'app-entrevistas-list',
  imports: [
    CommonModule,
    FormsModule,
    ActionBar,
    AlertRegion,
    Button,
    DataTable,
    EntrevistaEstadoModal,
    EntrevistaFormModal,
    FilterPanel,
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
  entrevistaSeleccionada: EntrevistaResumen | null = null;
  modoEstado: 'reprogramar' | 'cancelar' = 'reprogramar';

  estados: EstadoEntrevista[] = ['Pendiente', 'Confirmada', 'Realizada', 'Reprogramada', 'Cancelada', 'No Asistio'];
  tipos: TipoEntrevista[] = ['RRHH', 'Tecnica', 'Cliente', 'Psicolaboral', 'Gerencial', 'Ingles'];

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
    { key: 'asunto', label: 'Asunto del evento', width: 220, wrap: true },
    { key: 'cargo', label: 'Cargo vacante', width: 190, wrap: true },
    { key: 'fecha', label: 'Fecha', width: 135, value: (entrevista) => this.formatearFecha(entrevista.fecha) },
    { key: 'horaInicio', label: 'Hora', width: 110, value: (entrevista) => entrevista.horaInicio },
    { key: 'entrevistador', label: 'Entrevistador', width: 210, wrap: true },
  ];

  readonly acciones: DataTableAction<EntrevistaResumen>[] = [
    { id: 'ver', label: 'Ver detalle', icon: 'eye' },
    { id: 'reprogramar', label: 'Reprogramar entrevista', icon: 'calendar' },
    {
      id: 'cancelar',
      label: 'Cancelar entrevista',
      icon: 'cancel',
      disabled: (entrevista) => entrevista.estado === 'Cancelada' || entrevista.estado === 'Realizada',
    },
  ];

  constructor(
    private entrevistasService: EntrevistasService,
    private catalogosService: CatalogosService,
  ) {}

  ngOnInit() {
    this.cargarCatalogosFiltros();
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
        `${entrevista.idSolicitud} ${entrevista.candidato} ${entrevista.cargo} ${entrevista.asunto} ${entrevista.entrevistador}`,
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

  cargarEntrevistas() {
    this.cargando = true;
    this.errorCarga = '';

    this.entrevistasService.listar().subscribe({
      next: (entrevistas) => {
        this.entrevistas = entrevistas;
        this.cargando = false;
      },
      error: (error) => {
        this.entrevistas = [];
        this.cargando = false;
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
        const tiposCatalogo = tipos.map((tipo) => tipo.tpet_nombre).filter((nombre): nombre is string => Boolean(nombre));

        if (estadosCatalogo.length > 0) {
          this.estados = estadosCatalogo;
        }

        if (tiposCatalogo.length > 0) {
          this.tipos = tiposCatalogo;
        }
      });
  }

  guardarEntrevista(payload: EntrevistaPayload) {
    this.entrevistasService.crear(payload).subscribe({
      next: () => {
        this.mostrarFormulario = false;
        this.alerta = {
          tipo: 'success',
          variante: 'soft',
          mensaje: 'Entrevista creada correctamente.',
        };
        this.cargarEntrevistas();
      },
      error: (error) => {
        this.alerta = {
          tipo: 'danger',
          variante: 'soft',
          mensaje: obtenerMensajeError(error, 'No se pudo crear la entrevista.'),
        };
      },
    });
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
          mensaje:
            this.modoEstado === 'cancelar'
              ? 'Entrevista cancelada correctamente.'
              : 'Entrevista reprogramada correctamente.',
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

  manejarAccionTabla(evento: DataTableActionEvent<EntrevistaResumen>) {
    if (evento.action === 'reprogramar') {
      this.abrirEstado(evento.row, 'reprogramar');
      return;
    }

    if (evento.action === 'cancelar') {
      this.abrirEstado(evento.row, 'cancelar');
      return;
    }

    console.log('Detalle entrevista:', evento.row);
  }

  abrirEstado(entrevista: EntrevistaResumen, modo: 'reprogramar' | 'cancelar') {
    this.entrevistaSeleccionada = entrevista;
    this.modoEstado = modo;
  }

  cerrarModalEstado() {
    this.entrevistaSeleccionada = null;
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
}
