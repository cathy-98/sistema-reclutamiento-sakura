import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { CandidatoPerfilModal } from '../candidato-perfil-modal/candidato-perfil-modal';
import {
  DataTable,
  DataTableAction,
  DataTableActionEvent,
  DataTableColumn,
} from '../../../shared/components/data-table/data-table';
import { ActionBar } from '../../../shared/components/action-bar/action-bar';
import { FileDropzone } from '../../../shared/components/file-dropzone/file-dropzone';
import { FilterPanel } from '../../../shared/components/filter-panel/filter-panel';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { CurrencyClPipe } from '../../../shared/pipes/currency-cl.pipe';

type EstadoCandidato = 'Todos' | 'En revision' | 'Contactado' | 'Entrevista' | 'Descartado';
type NivelCandidato = 'Junior' | 'Semi senior' | 'Senior';

interface Candidato {
  idSolicitud: string;
  match: number;
  nombre: string;
  correo: string;
  telefono: string;
  cargo: string;
  estado: Exclude<EstadoCandidato, 'Todos'>;
  disponibilidad: string;
  renta: number;
  nivel: NivelCandidato;
  experiencia: number;
}

interface FiltrosCandidatos {
  idSolicitud: string;
  cargo: string;
  nombre: string;
  correo: string;
  telefono: string;
  estado: EstadoCandidato;
  disponibilidad: string;
  renta: string;
  match: string;
  nivel: '' | NivelCandidato;
  experiencia: string;
}

@Component({
  selector: 'app-candidatos-list',
  imports: [
    CommonModule,
    FormsModule,
    DataTable,
    FileDropzone,
    PageHeader,
    PageLayout,
    FilterPanel,
    ActionBar,
    CandidatoPerfilModal,
  ],
  templateUrl: './candidatos-list.html',
  styleUrl: './candidatos-list.scss',
})
export class CandidatosList {
  nombreUsuario = 'usuario';
  rolUsuario = '';
  cargando = false;
  errorCarga = '';
  paginaActual = 1;
  registrosPorPagina = 5;
  busquedaRapida = '';
  seleccionados = new Set<string>();
  archivosCv: File[] = [];
  candidatoSeleccionado: Candidato | null = null;

  filtros: FiltrosCandidatos = this.filtrosIniciales();

  readonly columnas: DataTableColumn<Candidato>[] = [
    {
      key: 'idSolicitud',
      label: 'ID solicitud',
      width: 112,
      sticky: 'left',
    },
    {
      key: 'match',
      label: 'Match',
      width: 90,
      type: 'match',
      value: (candidato) => `${candidato.match}%`,
      className: (candidato) => this.matchClase(candidato.match),
    },
    {
      key: 'nombre',
      label: 'Nombre completo',
      width: 220,
      type: 'person',
      value: (candidato) => candidato.nombre,
      secondaryValue: (candidato) => this.iniciales(candidato.nombre),
    },
    {
      key: 'correo',
      label: 'Correo electrónico',
      width: 230,
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
    },
    {
      key: 'estado',
      label: 'Estado del candidato',
      width: 170,
      type: 'badge',
      className: (candidato) => this.estadoClase(candidato.estado),
    },
    {
      key: 'disponibilidad',
      label: 'Disponibilidad',
      width: 160,
    },
    {
      key: 'renta',
      label: 'Pretensión de renta',
      width: 170,
      value: (candidato) => this.currencyCl.transform(candidato.renta),
    },
    {
      key: 'habilidades',
      label: 'Habilidades técnicas',
      width: 180,
      type: 'stack',
      value: (candidato) => candidato.nivel,
      secondaryValue: (candidato) => `${candidato.experiencia} años de experiencia`,
    },
  ];

  readonly acciones: DataTableAction<Candidato>[] = [
    {
      id: 'ver',
      label: 'Ver candidato',
      icon: 'eye',
    },
    {
      id: 'descargar-cv',
      label: 'Descargar CV',
      icon: 'download',
    },
    {
      id: 'agendar-entrevista',
      label: 'Agendar entrevista',
      icon: 'calendar',
    },
  ];

  readonly estados: EstadoCandidato[] = [
    'Todos',
    'En revision',
    'Contactado',
    'Entrevista',
    'Descartado',
  ];

  readonly niveles: NivelCandidato[] = ['Junior', 'Semi senior', 'Senior'];

  readonly candidatos: Candidato[] = [
    {
      idSolicitud: 'Req-021',
      match: 90,
      nombre: 'Macarena Lopez',
      correo: 'macarena.lopez@mail.com',
      telefono: '+56 9 5634 8547',
      cargo: 'Frontend',
      estado: 'En revision',
      disponibilidad: 'Inmediata',
      renta: 800000,
      nivel: 'Junior',
      experiencia: 4,
    },
    {
      idSolicitud: 'Req-021',
      match: 80,
      nombre: 'Valentina Rojas',
      correo: 'valentina.rojas@mail.com',
      telefono: '+56 9 6721 1184',
      cargo: 'Frontend',
      estado: 'Contactado',
      disponibilidad: '2 semanas',
      renta: 950000,
      nivel: 'Senior',
      experiencia: 5,
    },
    {
      idSolicitud: 'Req-019',
      match: 68,
      nombre: 'Diego Martinez',
      correo: 'diego.martinez@mail.com',
      telefono: '+56 9 7765 4402',
      cargo: 'Backend',
      estado: 'Entrevista',
      disponibilidad: 'Inmediata',
      renta: 1200000,
      nivel: 'Senior',
      experiencia: 6,
    },
    {
      idSolicitud: 'Req-018',
      match: 55,
      nombre: 'Camila Fuentes',
      correo: 'camila.fuentes@mail.com',
      telefono: '+56 9 3324 9811',
      cargo: 'UX Research',
      estado: 'En revision',
      disponibilidad: '1 mes',
      renta: 900000,
      nivel: 'Semi senior',
      experiencia: 3,
    },
    {
      idSolicitud: 'Req-017',
      match: 42,
      nombre: 'Sebastian Araya',
      correo: 'sebastian.araya@mail.com',
      telefono: '+56 9 4218 7256',
      cargo: 'QA Automation',
      estado: 'Descartado',
      disponibilidad: '2 semanas',
      renta: 1100000,
      nivel: 'Junior',
      experiencia: 2,
    },
  ];

  constructor(
    private authService: AuthService,
    private currencyCl: CurrencyClPipe,
  ) {
    this.actualizarDatosSesion();

    this.authService.cargarPerfilUsuario().subscribe(() => {
      this.actualizarDatosSesion();
    });
  }

  cargarCandidatos() {
    this.cargando = false;
    this.errorCarga = '';
    this.paginaActual = 1;
  }

  private actualizarDatosSesion() {
    this.nombreUsuario = this.authService.obtenerNombreVisible();
    this.rolUsuario = this.authService.obtenerRolVisible();
  }

  get candidatosFiltrados() {
    const filtrosNormalizados = {
      busquedaRapida: this.normalizar(this.busquedaRapida),
      idSolicitud: this.normalizar(this.filtros.idSolicitud),
      cargo: this.normalizar(this.filtros.cargo),
      nombre: this.normalizar(this.filtros.nombre),
      correo: this.normalizar(this.filtros.correo),
      telefono: this.normalizar(this.filtros.telefono),
      disponibilidad: this.normalizar(this.filtros.disponibilidad),
    };

    const renta = Number(this.filtros.renta);
    const match = Number(this.filtros.match);
    const experiencia = Number(this.filtros.experiencia);

    return this.candidatos.filter((candidato) => {
      const textoCandidato = this.normalizar(
        `${candidato.idSolicitud} ${candidato.nombre} ${candidato.correo} ${candidato.cargo}`,
      );
      const coincideTexto =
        textoCandidato.includes(filtrosNormalizados.busquedaRapida) &&
        this.normalizar(candidato.idSolicitud).includes(filtrosNormalizados.idSolicitud) &&
        this.normalizar(candidato.cargo).includes(filtrosNormalizados.cargo) &&
        this.normalizar(candidato.nombre).includes(filtrosNormalizados.nombre) &&
        this.normalizar(candidato.correo).includes(filtrosNormalizados.correo) &&
        this.normalizar(candidato.telefono).includes(filtrosNormalizados.telefono) &&
        this.normalizar(candidato.disponibilidad).includes(filtrosNormalizados.disponibilidad);

      const coincideEstado =
        this.filtros.estado === 'Todos' || candidato.estado === this.filtros.estado;
      const coincideNivel = !this.filtros.nivel || candidato.nivel === this.filtros.nivel;
      const coincideRenta = !renta || candidato.renta <= renta;
      const coincideMatch = !match || candidato.match >= match;
      const coincideExperiencia = !experiencia || candidato.experiencia >= experiencia;

      return (
        coincideTexto &&
        coincideEstado &&
        coincideNivel &&
        coincideRenta &&
        coincideMatch &&
        coincideExperiencia
      );
    });
  }

  get seleccionadosEnPagina() {
    return (
      this.candidatosPaginados.length > 0 &&
      this.candidatosPaginados.every((candidato) => this.estaSeleccionado(candidato))
    );
  }

  get totalPaginas() {
    return Math.max(1, Math.ceil(this.candidatosFiltrados.length / this.registrosPorPagina));
  }

  get mensajeAccionesMasivas() {
    return this.seleccionados.size > 0
      ? `${this.seleccionados.size} candidatos seleccionados.`
      : 'Selecciona candidatos para habilitar acciones masivas.';
  }

  get candidatosPaginados() {
    const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
    return this.candidatosFiltrados.slice(inicio, inicio + this.registrosPorPagina);
  }

  limpiarFiltros() {
    this.filtros = this.filtrosIniciales();
    this.busquedaRapida = '';
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

  trackCandidato(_index: number, candidato: Candidato) {
    return `${candidato.idSolicitud}-${candidato.correo}`;
  }

  estaSeleccionado(candidato: Candidato) {
    return this.seleccionados.has(this.obtenerIdCandidato(candidato));
  }

  alternarSeleccion(candidato: Candidato, seleccionado: boolean) {
    const id = this.obtenerIdCandidato(candidato);

    if (seleccionado) {
      this.seleccionados.add(id);
      return;
    }

    this.seleccionados.delete(id);
  }

  alternarSeleccionPagina(seleccionado: boolean) {
    this.candidatosPaginados.forEach((candidato) => {
      this.alternarSeleccion(candidato, seleccionado);
    });
  }

  manejarAccionTabla(evento: DataTableActionEvent<Candidato>) {
    if (evento.action === 'ver') {
      this.candidatoSeleccionado = evento.row;
      return;
    }

    console.log('Acción de candidato:', evento.action, evento.row);
  }

  cerrarPerfilCandidato() {
    this.candidatoSeleccionado = null;
  }

  actualizarArchivosCv(files: File[]) {
    this.archivosCv = files;
  }

  iniciales(nombre: string) {
    return nombre
      .split(' ')
      .slice(0, 2)
      .map((parte) => parte[0])
      .join('')
      .toUpperCase();
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

  estadoClase(estado: Candidato['estado']) {
    return estado.toLowerCase().replace(' ', '-');
  }

  private filtrosIniciales(): FiltrosCandidatos {
    return {
      idSolicitud: '',
      cargo: '',
      nombre: '',
      correo: '',
      telefono: '',
      estado: 'Todos',
      disponibilidad: '',
      renta: '',
      match: '',
      nivel: '',
      experiencia: '',
    };
  }

  private normalizar(valor: string) {
    return valor.trim().toLowerCase();
  }

  obtenerIdCandidato(candidato: Candidato) {
    return `${candidato.idSolicitud}-${candidato.correo}`;
  }
}
