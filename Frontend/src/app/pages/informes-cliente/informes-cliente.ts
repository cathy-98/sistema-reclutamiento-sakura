import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize, take } from 'rxjs';
import {
  CandidatoInformeApi,
  ClasificacionInforme,
  InformesService,
} from '../../services/informes.service';
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
import { Modal } from '../../shared/components/modal/modal';
import { PageLayout } from '../../shared/components/page-layout/page-layout';
import { PageHeader } from '../../shared/components/page-header/page-header';
import { TabItem, Tabs } from '../../shared/components/tabs/tabs';
import { AlertaUi } from '../../shared/models/alerta-ui.model';
import { obtenerMensajeError } from '../../shared/utils/api-error';

type VistaInforme = 'aprobados' | 'pendientes' | 'no-aprobados';

interface InformeCandidato {
  id: string;
  solicitudCandidatoId: number;
  idSolicitud: string;
  match: number;
  nombre: string;
  correo: string;
  telefono: string;
  cargo: string;
  empresa: string;
  nivel: string;
  experiencia: string;
  resultadoEntrevista: string;
  detalleResultado: string;
  motivoM6: string;
  estado: string;
  disponibilidad: string;
  clasificacion: ClasificacionInforme;
  aprobado: boolean;
  puedeEnviarDirectivos: boolean;
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
    Modal,
    PageHeader,
    PageLayout,
    Tabs,
  ],
  templateUrl: './informes-cliente.html',
  styleUrl: './informes-cliente.scss',
})
export class InformesCliente implements OnInit {
  paginaActual = 1;
  registrosPorPagina = 5;
  seleccionados = new Set<string>();
  vistaActiva: VistaInforme = 'aprobados';
  alerta: AlertaUi | null = null;
  filtros: FiltrosInformes = this.filtrosIniciales();
  busquedaRapida = '';
  mostrarResumenAdministrador = false;
  cargando = false;
  errorCarga = '';
  informes: InformeCandidato[] = [];
  destinatariosResumen = '';
  ccResumen = '';
  asuntoResumen = '';
  cuerpoResumen = '';
  enviandoDirectivos = false;

  readonly tabsInformes: TabItem[] = [
    { id: 'aprobados', label: 'Aprobados' },
    { id: 'pendientes', label: 'Pendientes' },
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
      label: 'Match CV',
      width: 105,
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
      key: 'motivoM6',
      label: 'Motivo M6',
      width: 260,
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
      visible: (informe) => informe.puedeEnviarDirectivos,
    },
  ];

  constructor(private informesService: InformesService) {}

  ngOnInit() {
    this.cargarInformes();
  }

  get estados() {
    return [
      'Todos',
      ...Array.from(new Set(this.informes.map((informe) => informe.estado).filter(Boolean))).sort((a, b) =>
        a.localeCompare(b, 'es-CL', { sensitivity: 'base' }),
      ),
    ];
  }

  get disponibilidades() {
    return Array.from(new Set(this.informes.map((informe) => informe.disponibilidad).filter(Boolean))).sort((a, b) =>
      a.localeCompare(b, 'es-CL', { sensitivity: 'base' }),
    );
  }

  get tituloTablaInformes() {
    if (this.vistaActiva === 'aprobados') {
      return 'Informes aprobados';
    }

    if (this.vistaActiva === 'pendientes') {
      return 'Informes pendientes';
    }

    return 'Informes no aprobados';
  }

  get informesFiltrados() {
    const filtrosNormalizados = {
      idSolicitud: this.normalizar(this.filtros.idSolicitud),
      nombre: this.normalizar(this.filtros.nombre),
      disponibilidad: this.normalizar(this.filtros.disponibilidad),
      busquedaRapida: this.normalizar(this.busquedaRapida),
    };

    return this.informes.filter((informe) => {
      const coincideVista = this.coincideVistaActiva(informe);
      const textoInforme = this.normalizar(
        `${informe.idSolicitud} ${informe.nombre} ${informe.correo} ${informe.cargo} ${informe.estado} ${informe.disponibilidad} ${informe.motivoM6}`,
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

  get candidatosSeleccionadosResumen() {
    const base = this.seleccionados.size > 0
      ? this.informes.filter((informe) => this.seleccionados.has(informe.id))
      : this.informesFiltrados;

    return base.filter((informe) => informe.aprobado && informe.puedeEnviarDirectivos);
  }

  get solicitudResumen() {
    return this.candidatosSeleccionadosResumen[0] ?? this.informes.find((informe) => informe.aprobado);
  }

  get totalCvsAdjuntos() {
    return this.candidatosSeleccionadosResumen.length;
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
    this.abrirResumenAdministrador();
  }

  descargarCvsMasivo() {
    const ids = this.idsSeleccionados();

    if (ids.length === 0) {
      return;
    }

    this.informesService.descargarCvCorporativoMasivo(ids)
      .pipe(take(1))
      .subscribe({
        next: (respuesta) => {
          this.informesService.descargarBlob(respuesta, 'CV_CORPORATIVO_MASIVO.zip');
          this.mostrarConfirmacionAccion('CVs corporativos descargados correctamente.');
        },
        error: (error) => {
          this.mostrarErrorAccion(error, 'No se pudieron descargar los CVs corporativos.');
        },
      });
  }

  enviarCorreoMasivo() {
    this.abrirResumenAdministrador();
  }

  abrirResumenAdministrador() {
    if (this.candidatosSeleccionadosResumen.length === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona candidatos aprobados y habilitados para envío a directivos.',
      };
      return;
    }

    this.asuntoResumen = this.asuntoResumen || `Resumen candidatos ${this.solicitudResumen?.idSolicitud ?? ''}`.trim();
    this.mostrarResumenAdministrador = true;
  }

  cerrarResumenAdministrador() {
    this.mostrarResumenAdministrador = false;
  }

  enviarResumenAdministrador() {
    const destinatarios = this.parsearCorreos(this.destinatariosResumen);

    if (destinatarios.length === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Ingresa al menos un destinatario para enviar el resumen.',
      };
      return;
    }

    this.enviandoDirectivos = true;
    this.informesService.enviarDirectivos({
      solicitudCandidatoIds: this.candidatosSeleccionadosResumen.map((informe) => informe.solicitudCandidatoId),
      destinatarios,
      cc: this.parsearCorreos(this.ccResumen),
      asunto: this.asuntoResumen || null,
      cuerpo: this.cuerpoResumen || null,
    })
      .pipe(
        take(1),
        finalize(() => {
          this.enviandoDirectivos = false;
        }),
      )
      .subscribe({
        next: () => {
          this.mostrarResumenAdministrador = false;
          this.mostrarConfirmacionAccion(`Resumen ${this.solicitudResumen?.idSolicitud ?? ''} enviado a directivos.`.trim());
        },
        error: (error) => {
          this.mostrarErrorAccion(error, 'No se pudo enviar el resumen a directivos.');
        },
      });
  }

  descargarInformeResumen() {
    const ids = this.candidatosSeleccionadosResumen.map((informe) => informe.solicitudCandidatoId);

    if (ids.length === 0) {
      return;
    }

    this.informesService.descargarResumenMasivo(ids)
      .pipe(take(1))
      .subscribe({
        next: (respuesta) => {
          this.informesService.descargarBlob(respuesta, 'RESUMEN_MASIVO.zip');
          this.mostrarConfirmacionAccion('Informe resumen descargado correctamente.');
        },
        error: (error) => {
          this.mostrarErrorAccion(error, 'No se pudo descargar el informe resumen.');
        },
      });
  }

  manejarAccionTabla(evento: DataTableActionEvent<InformeCandidato>) {
    if (evento.action === 'descargar-cv') {
      this.descargarDocumentoIndividual(evento.row, 'cv');
      return;
    }

    if (evento.action === 'descargar-informe') {
      this.descargarDocumentoIndividual(evento.row, 'resumen');
      return;
    }

    if (evento.action === 'enviar-correo') {
      this.seleccionados = new Set([evento.row.id]);
      this.abrirResumenAdministrador();
      return;
    }
  }

  resultadoClase(informe: InformeCandidato) {
    return informe.resultadoEntrevista.toLowerCase().includes('observaciones') ? 'is-warning' : 'is-success';
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

  cargarInformes() {
    this.cargando = true;
    this.errorCarga = '';

    this.informesService.listarCandidatos({ limit: 200 })
      .pipe(
        take(1),
        finalize(() => {
          this.cargando = false;
        }),
      )
      .subscribe({
        next: (respuesta) => {
          this.informes = respuesta.items.map((item) => this.mapearInforme(item));
          this.seleccionados = new Set();
        },
        error: (error) => {
          this.informes = [];
          this.errorCarga = obtenerMensajeError(error, 'No se pudieron cargar los informes desde M6.');
        },
      });
  }

  private mapearInforme(item: CandidatoInformeApi): InformeCandidato {
    const resultadoEntrevista = this.resumenEntrevista(item);

    return {
      id: String(item.solicitud_candidato_id),
      solicitudCandidatoId: item.solicitud_candidato_id,
      idSolicitud: item.solicitud_codigo ?? `Solicitud ${item.solicitud_id}`,
      match: Math.round(Number(item.match ?? 0)),
      nombre: item.candidato_nombre || item.candidato_email,
      correo: item.candidato_email,
      telefono: item.candidato_telefono || 'Sin telefono',
      cargo: item.cargo || item.solicitud_titulo || 'Sin cargo',
      empresa: 'No informado',
      nivel: item.tecnologias.slice(0, 3).join(', ') || 'Sin tecnologias',
      experiencia: this.resumenTecnico(item),
      resultadoEntrevista,
      detalleResultado: item.motivo_clasificacion.join(' ') || this.resumenObservaciones(item),
      motivoM6: item.motivo_clasificacion.join(' ') || 'Sin motivo informado',
      estado: item.estado_postulacion || 'Sin estado',
      disponibilidad: item.disponibilidad || 'Sin disponibilidad',
      clasificacion: item.clasificacion,
      aprobado: item.clasificacion === 'APROBADO',
      puedeEnviarDirectivos: item.puede_enviar_directivos,
    };
  }

  private coincideVistaActiva(informe: InformeCandidato) {
    if (this.vistaActiva === 'aprobados') {
      return informe.clasificacion === 'APROBADO';
    }

    if (this.vistaActiva === 'pendientes') {
      return informe.clasificacion === 'PENDIENTE';
    }

    return informe.clasificacion === 'NO_APROBADO';
  }

  private resumenEntrevista(item: CandidatoInformeApi) {
    if (item.entrevistas.length === 0) {
      return item.clasificacion === 'APROBADO' ? 'Aprobado' : item.clasificacion === 'NO_APROBADO' ? 'No aprobado' : 'Pendiente';
    }

    return item.entrevistas
      .map((entrevista) => `${entrevista.tipo || 'Entrevista'}: ${entrevista.resultado}`)
      .join(' | ');
  }

  private resumenTecnico(item: CandidatoInformeApi) {
    if (item.tecnicas.length === 0) {
      return 'Sin evaluación técnica';
    }

    return item.tecnicas
      .map((tecnica) => `${tecnica.cuestionario}: ${tecnica.porcentaje ?? 0}%`)
      .join(' | ');
  }

  private resumenObservaciones(item: CandidatoInformeApi) {
    return item.entrevistas
      .map((entrevista) => entrevista.observacion)
      .filter(Boolean)
      .join(' ') || 'Sin observaciones registradas';
  }

  private descargarDocumentoIndividual(informe: InformeCandidato, tipo: 'cv' | 'resumen') {
    const generar$ = tipo === 'cv'
      ? this.informesService.generarCvCorporativo(informe.solicitudCandidatoId)
      : this.informesService.generarResumen(informe.solicitudCandidatoId);

    generar$
      .pipe(take(1))
      .subscribe({
        next: (documento) => {
          this.informesService.descargarDocumento(documento.documento_id)
            .pipe(take(1))
            .subscribe({
              next: (respuesta) => {
                this.informesService.descargarBlob(respuesta, documento.nombre_archivo);
              },
              error: (error) => {
                this.mostrarErrorAccion(error, 'El documento fue generado, pero no se pudo descargar.');
              },
            });
        },
        error: (error) => {
          this.mostrarErrorAccion(error, tipo === 'cv' ? 'No se pudo generar el CV corporativo.' : 'No se pudo generar el informe.');
        },
      });
  }

  private idsSeleccionados() {
    return this.informes
      .filter((informe) => this.seleccionados.has(informe.id))
      .map((informe) => informe.solicitudCandidatoId);
  }

  private parsearCorreos(valor: string) {
    return valor
      .split(/[,\n;]/)
      .map((correo) => correo.trim())
      .filter(Boolean);
  }

  private mostrarErrorAccion(error: unknown, fallback: string) {
    this.alerta = {
      tipo: 'danger',
      variante: 'soft',
      mensaje: obtenerMensajeError(error, fallback),
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
