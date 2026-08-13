import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AlertRegion } from '../../shared/components/alert-region/alert-region';
import { ActionBar } from '../../shared/components/action-bar/action-bar';
import { Button } from '../../shared/components/button/button';
import {
  DataTable,
  DataTableAction,
  DataTableActionEvent,
  DataTableColumn,
} from '../../shared/components/data-table/data-table';
import { FilterPanel } from '../../shared/components/filter-panel/filter-panel';
import { PageLayout } from '../../shared/components/page-layout/page-layout';
import { PageHeader } from '../../shared/components/page-header/page-header';
import { TabItem, Tabs } from '../../shared/components/tabs/tabs';
import { AlertaUi } from '../../shared/models/alerta-ui.model';

type VistaInforme = 'aprobados' | 'no-aprobados';

interface InformeCandidato {
  id: string;
  idSolicitud: string;
  match: number;
  nombre: string;
  correo: string;
  telefono: string;
  cargo: string;
  estado: string;
  disponibilidad: string;
  aprobado: boolean;
}

interface FiltrosInformes {
  idSolicitud: string;
  nombre: string;
  estado: string;
  disponibilidad: string;
}

@Component({
  selector: 'app-informes-cliente',
  imports: [
    CommonModule,
    FormsModule,
    AlertRegion,
    ActionBar,
    Button,
    DataTable,
    FilterPanel,
    PageHeader,
    PageLayout,
    Tabs,
  ],
  templateUrl: './informes-cliente.html',
  styleUrl: './informes-cliente.scss',
})
export class InformesCliente {
  paginaActual = 1;
  registrosPorPagina = 5;
  seleccionados = new Set<string>();
  vistaActiva: VistaInforme = 'aprobados';
  alerta: AlertaUi | null = null;
  filtros: FiltrosInformes = this.filtrosIniciales();
  busquedaRapida = '';

  readonly tabsInformes: TabItem[] = [
    { id: 'aprobados', label: 'Aprobados' },
    { id: 'no-aprobados', label: 'No aprobados' },
  ];

  readonly columnas: DataTableColumn<InformeCandidato>[] = [
    {
      key: 'idSolicitud',
      label: 'ID solicitud',
      width: 138,
      sticky: 'left',
    },
    {
      key: 'match',
      label: 'Match',
      width: 88,
      type: 'match',
      value: (informe) => `${informe.match}%`,
      className: (informe) => this.matchClase(informe.match),
    },
    {
      key: 'nombre',
      label: 'Nombre completo',
      width: 210,
      type: 'person',
      wrap: true,
      value: (informe) => informe.nombre,
      secondaryValue: (informe) => this.iniciales(informe.nombre),
    },
    {
      key: 'correo',
      label: 'Correo electrónico',
      width: 220,
      wrap: true,
    },
    {
      key: 'telefono',
      label: 'Teléfono de contacto',
      width: 170,
    },
    {
      key: 'cargo',
      label: 'Cargo postulado',
      width: 160,
      wrap: true,
    },
    {
      key: 'estado',
      label: 'Estado',
      width: 150,
      type: 'badge',
      className: (informe) => this.estadoClase(informe.estado),
    },
    {
      key: 'disponibilidad',
      label: 'Disponibilidad',
      width: 150,
    },
  ];

  readonly acciones: DataTableAction<InformeCandidato>[] = [
    {
      id: 'descargar-cv',
      label: 'Descargar CV',
      icon: 'download',
    },
    {
      id: 'descargar-informe',
      label: 'Descargar informe',
      icon: 'edit',
    },
    {
      id: 'enviar-correo',
      label: 'Enviar correo',
      icon: 'mail',
    },
  ];

  readonly estados = ['Todos', 'En revision', 'En entrevista', 'Seleccionado', 'Descartado', 'Contratado'];
  readonly disponibilidades = ['Inmediata', '2 semanas', '1 mes'];

  readonly informes: InformeCandidato[] = [
    {
      id: 'inf-001',
      idSolicitud: 'SOL-021',
      match: 90,
      nombre: 'Macarena Lopez',
      correo: 'macarena.lopez@mail.com',
      telefono: '+56 9 5634 8547',
      cargo: 'Frontend',
      estado: 'Seleccionado',
      disponibilidad: 'Inmediata',
      aprobado: true,
    },
    {
      id: 'inf-002',
      idSolicitud: 'SOL-021',
      match: 80,
      nombre: 'Valentina Rojas',
      correo: 'valentina.rojas@mail.com',
      telefono: '+56 9 6721 1184',
      cargo: 'Frontend',
      estado: 'En entrevista',
      disponibilidad: '2 semanas',
      aprobado: true,
    },
    {
      id: 'inf-003',
      idSolicitud: 'SOL-019',
      match: 78,
      nombre: 'Diego Martinez',
      correo: 'diego.martinez@mail.com',
      telefono: '+56 9 7765 4402',
      cargo: 'Backend',
      estado: 'Seleccionado',
      disponibilidad: 'Inmediata',
      aprobado: true,
    },
    {
      id: 'inf-004',
      idSolicitud: 'SOL-018',
      match: 72,
      nombre: 'Camila Fuentes',
      correo: 'camila.fuentes@mail.com',
      telefono: '+56 9 3324 9811',
      cargo: 'UX Research',
      estado: 'Contratado',
      disponibilidad: '1 mes',
      aprobado: true,
    },
    {
      id: 'inf-005',
      idSolicitud: 'SOL-017',
      match: 76,
      nombre: 'Sebastian Araya',
      correo: 'sebastian.araya@mail.com',
      telefono: '+56 9 4218 7256',
      cargo: 'QA Automation',
      estado: 'En revision',
      disponibilidad: '2 semanas',
      aprobado: true,
    },
    {
      id: 'inf-006',
      idSolicitud: 'SOL-016',
      match: 82,
      nombre: 'Antonia Morales',
      correo: 'antonia.morales@mail.com',
      telefono: '+56 9 5874 1120',
      cargo: 'Frontend',
      estado: 'Seleccionado',
      disponibilidad: 'Inmediata',
      aprobado: true,
    },
    {
      id: 'inf-007',
      idSolicitud: 'SOL-019',
      match: 58,
      nombre: 'Tomas Herrera',
      correo: 'tomas.herrera@mail.com',
      telefono: '+56 9 4187 2201',
      cargo: 'Backend',
      estado: 'Descartado',
      disponibilidad: '1 mes',
      aprobado: false,
    },
    {
      id: 'inf-008',
      idSolicitud: 'SOL-018',
      match: 46,
      nombre: 'Camila Soto',
      correo: 'camila.soto@mail.com',
      telefono: '+56 9 3351 7820',
      cargo: 'UX Research',
      estado: 'Descartado',
      disponibilidad: '2 semanas',
      aprobado: false,
    },
  ];

  get informesFiltrados() {
    const filtrosNormalizados = {
      idSolicitud: this.normalizar(this.filtros.idSolicitud),
      nombre: this.normalizar(this.filtros.nombre),
      disponibilidad: this.normalizar(this.filtros.disponibilidad),
      busquedaRapida: this.normalizar(this.busquedaRapida),
    };

    return this.informes.filter((informe) => {
      const coincideVista = this.vistaActiva === 'aprobados' ? informe.aprobado : !informe.aprobado;
      const textoInforme = this.normalizar(
        `${informe.idSolicitud} ${informe.nombre} ${informe.correo} ${informe.cargo} ${informe.estado} ${informe.disponibilidad}`,
      );
      const coincideTexto =
        textoInforme.includes(filtrosNormalizados.busquedaRapida) &&
        this.normalizar(informe.idSolicitud).includes(filtrosNormalizados.idSolicitud) &&
        this.normalizar(informe.nombre).includes(filtrosNormalizados.nombre) &&
        this.normalizar(informe.disponibilidad).includes(filtrosNormalizados.disponibilidad);
      const coincideEstado = !this.filtros.estado || this.filtros.estado === 'Todos' || informe.estado === this.filtros.estado;

      return coincideVista && coincideTexto && coincideEstado;
    });
  }

  get informesPaginados() {
    const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
    return this.informesFiltrados.slice(inicio, inicio + this.registrosPorPagina);
  }

  get totalPaginas() {
    return Math.max(1, Math.ceil(this.informesFiltrados.length / this.registrosPorPagina));
  }

  get mensajeAccionesMasivas() {
    return this.seleccionados.size > 0
      ? `${this.seleccionados.size} informes seleccionados.`
      : 'Selecciona informes para habilitar acciones masivas.';
  }

  cambiarVista(vista: string) {
    this.vistaActiva = vista as VistaInforme;
    this.paginaActual = 1;
    this.seleccionados = new Set<string>();
  }

  buscar() {
    this.paginaActual = 1;
  }

  limpiarFiltros() {
    this.filtros = this.filtrosIniciales();
    this.busquedaRapida = '';
    this.paginaActual = 1;
  }

  cambiarPagina(pagina: number) {
    this.paginaActual = Math.min(Math.max(pagina, 1), this.totalPaginas);
  }

  cambiarRegistrosPorPagina(registros: number) {
    this.registrosPorPagina = registros;
    this.paginaActual = 1;
  }

  generarInforme() {
    this.mostrarConfirmacionAccion('Generación de informe preparada.');
  }

  descargarCvsMasivo() {
    this.mostrarConfirmacionAccion('Descarga masiva de CVs preparada.');
  }

  enviarCorreoMasivo() {
    this.mostrarConfirmacionAccion('Correo masivo preparado para los informes seleccionados.');
  }

  manejarAccionTabla(evento: DataTableActionEvent<InformeCandidato>) {
    const acciones: Record<string, string> = {
      'descargar-cv': `CV de ${evento.row.nombre} preparado para descarga.`,
      'descargar-informe': `Informe de ${evento.row.nombre} preparado para descarga.`,
      'enviar-correo': `Correo preparado para ${evento.row.correo}.`,
    };

    this.mostrarConfirmacionAccion(acciones[evento.action] || 'Acción preparada.');
  }

  cerrarAlerta() {
    this.alerta = null;
  }

  obtenerIdInforme(informe: InformeCandidato) {
    return informe.id;
  }

  estadoClase(estado: string) {
    return estado.toLowerCase().replace(/\s+/g, '-');
  }

  matchClase(match: number) {
    if (match >= 75) {
      return 'is-high';
    }

    if (match >= 55) {
      return 'is-medium';
    }

    return 'is-low';
  }

  iniciales(nombre: string) {
    return nombre
      .split(' ')
      .slice(0, 2)
      .map((parte) => parte[0])
      .join('')
      .toUpperCase();
  }

  private mostrarConfirmacionAccion(mensaje: string) {
    this.alerta = {
      tipo: 'success',
      variante: 'soft',
      mensaje,
    };
  }

  private filtrosIniciales(): FiltrosInformes {
    return {
      idSolicitud: '',
      nombre: '',
      estado: 'Todos',
      disponibilidad: '',
    };
  }

  private normalizar(valor: string) {
    return valor.trim().toLowerCase();
  }
}
