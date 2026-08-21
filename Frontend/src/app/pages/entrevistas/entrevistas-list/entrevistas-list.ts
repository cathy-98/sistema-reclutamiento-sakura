import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, finalize, forkJoin, of, take, timeout } from 'rxjs';
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

type ModoEstadoEntrevista = 'ver' | 'editar' | 'reprogramar' | 'cancelar' | 'confirmar' | 'realizar' | 'no-asistio';

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
  modoEstado: ModoEstadoEntrevista = 'editar';

  estados: EstadoEntrevista[] = ['Pendiente', 'Confirmada', 'Realizada', 'Reprogramada', 'Cancelada', 'No Asistio'];
  tipos: TipoEntrevista[] = [];

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
      id: 'confirmar',
      label: 'Confirmar entrevista',
      icon: 'edit',
      visible: (entrevista) => this.esEstadoEntrevista(entrevista, ['Pendiente', 'Reprogramada']),
    },
    {
      id: 'reprogramar',
      label: 'Reprogramar',
      icon: 'calendar',
      visible: (entrevista) => this.puedeCambiarEstado(entrevista),
    },
    {
      id: 'realizar',
      label: 'Marcar realizada',
      icon: 'edit',
      visible: (entrevista) => this.esEstadoEntrevista(entrevista, ['Pendiente', 'Confirmada', 'Reprogramada']),
    },
    {
      id: 'no-asistio',
      label: 'Marcar no asistio',
      icon: 'cancel',
      visible: (entrevista) => this.puedeCambiarEstado(entrevista),
    },
    {
      id: 'cancelar',
      label: 'Cancelar entrevista',
      icon: 'cancel',
      visible: (entrevista) => this.puedeCambiarEstado(entrevista),
    },
  ];

  constructor(
    private entrevistasService: EntrevistasService,
    private catalogosService: CatalogosService,
    private cdr: ChangeDetectorRef,
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

    this.entrevistasService.listar()
      .pipe(
        take(1),
        finalize(() => {
          this.cargando = false;
          this.cdr.detectChanges();
        }),
      )
      .subscribe({
      next: (entrevistas) => {
        this.entrevistas = entrevistas;
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
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudieron agendar las entrevistas.'),
          };
        },
      });
      return;
    }

    this.entrevistasService.crear(payload).subscribe({
      next: () => {
        this.mostrarFormulario = false;
        this.candidatosAgendaMasiva = [];
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

  abrirFormularioIndividual() {
    this.candidatosAgendaMasiva = [];
    this.mostrarFormulario = true;
  }

  abrirAgendaMasivaSeleccion() {
    const seleccionadas = this.entrevistasSeleccionadas;

    if (seleccionadas.length === 0) {
      return;
    }

    if (!this.seleccionMismaSolicitud) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona entrevistas de una misma solicitud para agendar masivamente.',
      };
      return;
    }

    if (seleccionadas.some((entrevista) => !entrevista.solicitudCandidatoId)) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'No se pudo identificar la postulación de todas las entrevistas seleccionadas.',
      };
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
    this.mostrarFormulario = true;
  }

  cerrarFormularioAgenda() {
    this.mostrarFormulario = false;
    this.candidatosAgendaMasiva = [];
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
    if (!this.entrevistaSeleccionada || this.modoEstado === 'ver') {
      return;
    }

    const solicitud = this.solicitudEstadoEntrevista(payload);

    solicitud.subscribe({
      next: () => {
        this.alerta = {
          tipo: 'success',
          variante: 'soft',
          mensaje:
            this.mensajeEstadoActualizado(),
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
    if (evento.action === 'ver') {
      this.abrirEstado(evento.row, 'ver');
      return;
    }

    if (evento.action === 'editar-estado') {
      this.abrirEstado(evento.row, 'editar');
      return;
    }

    if (evento.action === 'reprogramar') {
      this.abrirEstado(evento.row, 'reprogramar');
      return;
    }

    if (evento.action === 'cancelar') {
      this.abrirEstado(evento.row, 'cancelar');
      return;
    }

    if (evento.action === 'confirmar') {
      this.abrirEstado(evento.row, 'confirmar');
      return;
    }

    if (evento.action === 'realizar') {
      this.abrirEstado(evento.row, 'realizar');
      return;
    }

    if (evento.action === 'no-asistio') {
      this.abrirEstado(evento.row, 'no-asistio');
      return;
    }

    this.abrirEstado(evento.row, 'ver');
  }

  abrirEstado(entrevista: EntrevistaResumen, modo: ModoEstadoEntrevista) {
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

  private solicitudEstadoEntrevista(payload: { estado?: EstadoEntrevista; fecha: string; horaInicio: string; horaFin: string; motivo: string }) {
    const id = this.entrevistaSeleccionada?.id ?? '';
    const modo = this.modoEstado === 'editar'
      ? this.modoDesdeEstado(payload.estado)
      : this.modoEstado;

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

    return this.entrevistasService.reprogramar(
      id,
      payload.fecha,
      payload.horaInicio,
      payload.horaFin,
      payload.motivo,
    );
  }

  private mensajeEstadoActualizado() {
    const mensajes = {
      ver: 'Detalle de entrevista revisado.',
      editar: 'Estado de entrevista actualizado correctamente.',
      cancelar: 'Entrevista cancelada correctamente.',
      confirmar: 'Entrevista confirmada correctamente.',
      realizar: 'Entrevista marcada como realizada.',
      'no-asistio': 'Entrevista marcada como no asistio.',
      reprogramar: 'Entrevista reprogramada correctamente.',
    };

    return mensajes[this.modoEstado];
  }

  private modoDesdeEstado(estado?: EstadoEntrevista): Exclude<ModoEstadoEntrevista, 'ver' | 'editar'> {
    const estadoNormalizado = this.normalizar(estado ?? '');

    if (estadoNormalizado === 'confirmada') {
      return 'confirmar';
    }

    if (estadoNormalizado === 'realizada') {
      return 'realizar';
    }

    if (estadoNormalizado === 'no asistio') {
      return 'no-asistio';
    }

    if (estadoNormalizado === 'cancelada') {
      return 'cancelar';
    }

    return 'reprogramar';
  }

  private esEstadoEntrevista(entrevista: EntrevistaResumen, estados: string[]) {
    const actual = this.normalizar(entrevista.estado);
    return estados.some((estado) => this.normalizar(estado) === actual);
  }

  private puedeCambiarEstado(entrevista: EntrevistaResumen) {
    return !this.esEstadoEntrevista(entrevista, ['Cancelada', 'Realizada', 'No Asistio']);
  }

  private tipoEntrevistaValido(nombre?: string | null) {
    const normalizado = this.normalizar(nombre ?? '').replace(/\s+/g, '-');
    return Boolean(normalizado) && normalizado !== 'ingles';
  }
}
