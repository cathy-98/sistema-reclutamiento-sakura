import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnInit, QueryList, ViewChildren } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize, take } from 'rxjs';
import {
  CandidatosService,
  PostulacionCandidatoApi,
} from '../../services/candidatos.service';
import {
  CandidateEmailNotificationApi,
  CandidatoInformeApi,
  ClasificacionInforme,
  DocumentoInformeApi,
  EvaluacionEntrevistaResumenApi,
  InformeComparativoRequestApi,
  InformesService,
  PlantillaNotificacionApi,
  RechazoPreviewItemApi,
  TipoCorreoRechazoApi,
  TipoCorreoCandidatoApi,
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
import { SolicitudAutocomplete } from '../../shared/components/solicitud-autocomplete/solicitud-autocomplete';
import { AlertaUi } from '../../shared/models/alerta-ui.model';
import { obtenerMensajeError } from '../../shared/utils/api-error';
import {
  SolicitudAutocompleteOption,
  codigoSolicitudCoincide,
  resolverSolicitudReal,
} from '../../shared/utils/solicitud-autocomplete';

type VistaInforme = 'aprobados' | 'pendientes' | 'no-aprobados';
type ModoCorreoCandidatos = 'seleccion' | 'cierre';

interface AprobacionMatrizInforme {
  tipo: 'Aprobación técnica' | 'Aprobación operacional' | 'Otra aprobación' | 'Resultado final';
  resultado?: string;
  evaluador?: string;
  rolEvaluador?: string;
  observacion?: string;
}

interface InformeCandidato {
  id: string;
  solicitudCandidatoId: number;
  solicitudId: number;
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
  puedeEnviarRechazo: boolean;
  entrevistas: EvaluacionEntrevistaResumenApi[];
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
    SolicitudAutocomplete,
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
  adjuntosResumen: DocumentoInformeApi[] = [];
  preparandoDirectivos = false;
  enviandoDirectivos = false;
  errorResumenAdministrador = '';
  detallesResumenAbiertos = new Set<string>();
  cvsSeleccionadosResumen = new Set<number>();
  mostrarModalCorreoCandidatos = false;
  cargandoPlantillasCorreo = false;
  enviandoCorreoCandidatos = false;
  errorCorreoCandidatos = '';
  candidatosCorreoSeleccionados: InformeCandidato[] = [];
  plantillasCorreoCandidatos: PlantillaNotificacionApi[] = [];
  plantillasCorreoCierre: PlantillaNotificacionApi[] = [];
  modoCorreoCandidatos: ModoCorreoCandidatos = 'seleccion';
  plantillaCorreoCandidato: TipoCorreoCandidatoApi | 'manual' = 'manual';
  plantillaCorreoCandidatoId = 0;
  plantillaCorreoCierreId = 0;
  tipoCorreoCierre: TipoCorreoRechazoApi | '' = '';
  preparandoCorreoCierre = false;
  itemsCorreoCierre: RechazoPreviewItemApi[] = [];
  asuntoCorreoCandidatos = '';
  cuerpoCorreoCandidatos = '';
  resultadosCorreoCandidatos: CandidateEmailNotificationApi[] = [];
  descargandoInformeComparativo: 'pdf' | 'docx' | null = null;
  solicitudComparativoId: number | null = null;
  solicitudComparativoCodigo = '';
  candidatosComparativoSolicitud: InformeCandidato[] = [];
  cargandoCandidatosComparativo = false;
  errorCandidatosComparativo = '';
  private cargaCandidatosComparativoToken = 0;
  private preparacionCorreoCierreToken = 0;

  @ViewChildren('mensajeCorreoTextarea')
  private mensajeCorreoTextareas?: QueryList<ElementRef<HTMLTextAreaElement>>;

  readonly tabsInformes: TabItem[] = [
    { id: 'aprobados', label: 'Aprobados' },
    { id: 'no-aprobados', label: 'No aprobados' },
    { id: 'pendientes', label: 'Pendientes' },
  ];

  readonly columnas: DataTableColumn<InformeCandidato>[] = [
    {
      key: 'idSolicitud',
      label: 'Solicitud',
      width: 220,
      sticky: 'left',
      type: 'stack',
      value: (informe) => informe.idSolicitud,
      secondaryValue: (informe) => informe.cargo,
      title: (informe) => `${informe.idSolicitud} · ${informe.cargo}`,
    },
    {
      key: 'estado',
      label: 'Estado de postulación',
      width: 150,
      type: 'badge',
      className: (informe) => this.estadoClase(informe.estado),
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
      label: 'Resultado / motivo',
      width: 260,
      wrap: true,
    },
    {
      key: 'telefono',
      label: 'Teléfono de contacto',
      width: 170,
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
      id: 'descargar-informe-pdf',
      label: 'Informe PDF',
      icon: 'download',
    },
    {
      id: 'descargar-informe-docx',
      label: 'Informe Word',
      icon: 'download',
    },
    {
      id: 'enviar-correo',
      label: 'Enviar correo',
      icon: 'mail',
      visible: (informe) => this.vistaActiva === 'aprobados'
        ? informe.puedeEnviarDirectivos
        : this.vistaActiva === 'no-aprobados' && informe.puedeEnviarRechazo,
    },
  ];

  constructor(
    private informesService: InformesService,
    private candidatosService: CandidatosService,
  ) {}

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

  get solicitudesFiltro(): SolicitudAutocompleteOption[] {
    const solicitudes = new Map<number, SolicitudAutocompleteOption>();

    this.informes.forEach((informe) => {
      if (!informe.idSolicitud) {
        return;
      }

      if (!solicitudes.has(informe.solicitudId)) {
        solicitudes.set(informe.solicitudId, {
          id: informe.solicitudId,
          codigo: informe.idSolicitud,
          cargo: informe.cargo,
        });
      }
    });

    return Array.from(solicitudes.values());
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
        (
          textoInforme.includes(filtrosNormalizados.busquedaRapida) ||
          codigoSolicitudCoincide(informe.idSolicitud, this.busquedaRapida)
        ) &&
        (
          !filtrosNormalizados.idSolicitud ||
          codigoSolicitudCoincide(informe.idSolicitud, this.filtros.idSolicitud)
        ) &&
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
    const seleccion = this.seleccionados.size > 0
      ? `${this.seleccionados.size} informes seleccionados.`
      : 'Selecciona informes para habilitar acciones masivas.';
    return `${seleccion} ${this.mensajeInformeComparativo}`;
  }

  get informesSeleccionados() {
    return this.informes.filter((informe) => this.seleccionados.has(informe.id));
  }

  get puedeDescargarInformeComparativo() {
    return !!this.solicitudComparativoId
      && this.candidatosComparativoSolicitud.length > 0
      && !this.cargandoCandidatosComparativo
      && !this.errorCandidatosComparativo
      && this.descargandoInformeComparativo === null;
  }

  get solicitudesSeleccionadasComparativo() {
    return this.solicitudComparativoId ? [this.solicitudComparativoId] : [];
  }

  get mensajeInformeComparativo() {
    if (this.cargandoCandidatosComparativo) {
      return 'Preparando informe comparativo...';
    }

    if (this.errorCandidatosComparativo) {
      return this.errorCandidatosComparativo;
    }

    if (!this.solicitudComparativoId) {
      return 'Selecciona una solicitud para generar el informe comparativo.';
    }

    const total = this.candidatosComparativoSolicitud.length;
    const codigo = this.solicitudComparativoCodigo || `Solicitud ${this.solicitudComparativoId}`;
    if (total === 0) {
      return `La solicitud ${codigo} no tiene candidatos asociados.`;
    }

    return `El informe incluirá ${total} ${total === 1 ? 'candidato' : 'candidatos'} de ${codigo}.`;
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
    return this.candidatosConCvAdjunto.length;
  }

  get candidatosConCvAdjunto() {
    // TODO BACKEND M6:
    // El endpoint de envío debe recibir/respetar la selección de CV adjuntos
    // realizada por la reclutadora.
    return this.candidatosSeleccionadosResumen.filter((candidato) => this.candidatoTieneCvAdjunto(candidato));
  }

  get totalCvsDisponibles() {
    return this.candidatosSeleccionadosResumen.filter((candidato) => this.candidatoTieneCvDisponible(candidato)).length;
  }

  get todosCvsSeleccionados() {
    return this.totalCvsDisponibles > 0 && this.totalCvsAdjuntos === this.totalCvsDisponibles;
  }

  get algunosCvsSeleccionados() {
    return this.totalCvsAdjuntos > 0 && !this.todosCvsSeleccionados;
  }

  get resumenContenidoEnvio() {
    const solicitud = this.solicitudResumen;
    return [
      solicitud?.idSolicitud,
      solicitud?.cargo,
    ].filter(Boolean).join(' · ');
  }

  get puedeEnviarResumenAdministrador() {
    return !this.preparandoDirectivos
      && !this.enviandoDirectivos
      && this.destinatarioResumenValido;
  }

  get puedeAbrirCorreoAprobadosMasivo() {
    return this.vistaActiva === 'aprobados'
      && this.seleccionados.size > 0
      && this.informesSeleccionadosAprobados.length > 0;
  }

  get puedeAbrirCorreoNoAprobadosMasivo() {
    return this.vistaActiva === 'no-aprobados'
      && this.seleccionados.size > 0;
  }

  get puedeEnviarCorreoCandidatos() {
    if (this.modoCorreoCandidatos === 'cierre') {
      return !this.enviandoCorreoCandidatos
        && !this.preparandoCorreoCierre
        && this.tipoCorreoCierre !== ''
        && this.itemsCorreoCierre.length > 0
        && this.itemsCorreoCierre.every((item) => item.asunto.trim().length > 0 && item.cuerpo.trim().length > 0);
    }

    return !this.enviandoCorreoCandidatos
      && this.candidatosCorreoSeleccionados.length > 0
      && this.asuntoCorreoCandidatos.trim().length > 0
      && this.cuerpoCorreoCandidatos.trim().length > 0
      && this.plantillaCorreoCandidato === 'SELECCION';
  }

  get contextoCorreoCandidatos() {
    const total = this.candidatosCorreoSeleccionados.length;
    if (this.modoCorreoCandidatos === 'cierre') {
      return total === 1 ? '1 candidato no aprobado seleccionado' : `${total} candidatos no aprobados seleccionados`;
    }

    return total === 1 ? '1 candidato aprobado seleccionado' : `${total} candidatos aprobados seleccionados`;
  }

  get destinatariosCorreoCandidatos() {
    return this.candidatosCorreoSeleccionados.map((candidato) => ({
      nombre: candidato.nombre,
      correo: candidato.correo,
      solicitud: candidato.idSolicitud,
    }));
  }

  get resumenResultadosCorreoCandidatos() {
    const enviados = this.resultadosCorreoCandidatos.filter((resultado) => resultado.estado === 'ENVIADO').length;
    return `${enviados} de ${this.resultadosCorreoCandidatos.length} correos enviados.`;
  }

  get candidatosNoAprobadosSeleccionados() {
    return this.informes
      .filter((informe) => this.seleccionados.has(informe.id))
      .filter((informe) => informe.clasificacion === 'NO_APROBADO');
  }

  get destinatarioResumenValido() {
    return this.destinatariosValidos(this.destinatariosResumen).length > 0;
  }

  get aprobacionesMatriz(): AprobacionMatrizInforme[] {
    // TODO BACKEND:
    // Falta exponer el rol del evaluador junto al nombre
    // en aprobaciones/comentarios.
    //
    // TODO BACKEND M6:
    // Consumir aquí las aprobaciones Técnica, Operacional y Otra
    // cuando Backend exponga la matriz definitiva.
    //
    // IMPORTANTE:
    // El resultado final de la matriz debe venir calculado desde Backend.
    // Frontend solo lo presenta.
    return [];
  }

  get aprobacionesMatrizDisponibles() {
    return this.aprobacionesMatriz.length > 0;
  }

  cambiarVista(vista: string) {
    this.vistaActiva = vista as VistaInforme;
    this.paginaActual = 1;
    this.seleccionados = new Set<string>();
    if (this.filtros.idSolicitud.trim()) {
      this.actualizarContextoComparativoDesdeFiltros();
    } else {
      this.limpiarContextoComparativo();
    }
  }

  buscar() {
    this.paginaActual = 1;
  }

  seleccionarSolicitudBusquedaRapida(solicitud: SolicitudAutocompleteOption) {
    this.busquedaRapida = solicitud.codigo?.trim() ?? this.busquedaRapida;
    this.buscar();
  }

  actualizarFiltroSolicitud(valor: string) {
    this.filtros = {
      ...this.filtros,
      idSolicitud: valor,
    };
    this.buscar();
    this.actualizarContextoComparativoDesdeFiltros();
  }

  actualizarSeleccionInformes(seleccion: Set<string>) {
    this.seleccionados = new Set(seleccion);
    if (!this.filtros.idSolicitud.trim()) {
      this.actualizarContextoComparativoDesdeSeleccion();
    }
  }

  seleccionarFiltroSolicitud(solicitud: SolicitudAutocompleteOption | null) {
    this.filtros = {
      ...this.filtros,
      idSolicitud: solicitud?.codigo?.trim() ?? '',
    };
    this.buscar();
    this.actualizarContextoComparativoDesdeFiltros();
  }

  limpiarFiltros() {
    this.filtros = this.filtrosIniciales();
    this.busquedaRapida = '';
    this.paginaActual = 1;
    this.limpiarContextoComparativo();
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

  descargarInformeComparativoMasivo(formato: 'pdf' | 'docx') {
    this.generarInformeComparativoSolicitud(formato);
  }

  enviarCorreoMasivo() {
    if (this.vistaActiva === 'no-aprobados') {
      this.abrirCorreoCierre(this.candidatosNoAprobadosSeleccionados);
      return;
    }

    this.abrirCorreoAprobados(this.informesSeleccionadosAprobados);
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
    this.errorResumenAdministrador = '';
    this.adjuntosResumen = [];
    this.detallesResumenAbiertos = new Set<string>();
    this.inicializarSeleccionCvsResumen();
    this.mostrarResumenAdministrador = true;
    this.prepararResumenAdministrador();
  }

  cerrarResumenAdministrador() {
    if (this.enviandoDirectivos || this.preparandoDirectivos) {
      return;
    }

    this.mostrarResumenAdministrador = false;
    this.errorResumenAdministrador = '';
    this.detallesResumenAbiertos = new Set<string>();
    this.cvsSeleccionadosResumen = new Set<number>();
  }

  enviarResumenAdministrador() {
    if (this.preparandoDirectivos) {
      return;
    }

    const destinatarios = this.destinatariosValidos(this.destinatariosResumen);

    if (destinatarios.length === 0) {
      this.errorResumenAdministrador = 'Agrega al menos un destinatario para enviar el resumen.';
      return;
    }

    if (this.tieneCorreosInvalidos(this.destinatariosResumen) || this.tieneCorreosInvalidos(this.ccResumen)) {
      this.errorResumenAdministrador = 'Revisa el formato de los correos antes de enviar el resumen.';
      return;
    }

    this.enviandoDirectivos = true;
    this.errorResumenAdministrador = '';
    // TODO BACKEND CORREOS:
    // El proveedor de correo (Brevo) será gestionado desde Backend.
    // Frontend solo prepara y presenta destinatarios, asunto,
    // mensaje, candidatos y selección de adjuntos.
    this.informesService.enviarDirectivos({
      solicitudCandidatoIds: this.candidatosSeleccionadosResumen.map((informe) => informe.solicitudCandidatoId),
      destinatarios,
      cc: this.destinatariosValidos(this.ccResumen),
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
          this.errorResumenAdministrador = '';
          this.mostrarConfirmacionAccion(
            `Resumen enviado correctamente. ${this.candidatosSeleccionadosResumen.length} candidatos · ${this.totalCvsAdjuntos} CV adjuntos`,
          );
          this.adjuntosResumen = [];
        },
        error: (error) => {
          this.errorResumenAdministrador = this.mensajeErrorResumenAdministrador(
            error,
            'No pudimos enviar el resumen. Inténtalo nuevamente.',
          );
        },
      });
  }

  detalleCandidatoAbierto(candidato: InformeCandidato) {
    return this.detallesResumenAbiertos.has(candidato.id);
  }

  alternarDetalleCandidatoResumen(candidato: InformeCandidato) {
    const abiertos = new Set(this.detallesResumenAbiertos);

    if (abiertos.has(candidato.id)) {
      abiertos.delete(candidato.id);
    } else {
      abiertos.add(candidato.id);
    }

    this.detallesResumenAbiertos = abiertos;
  }

  candidatoTieneCvAdjunto(candidato: InformeCandidato) {
    return this.candidatoTieneCvDisponible(candidato)
      && this.cvsSeleccionadosResumen.has(candidato.solicitudCandidatoId);
  }

  candidatoTieneCvDisponible(candidato: InformeCandidato) {
    if (this.adjuntosResumen.length === 0) {
      return true;
    }

    return this.adjuntosResumen.some((adjunto) => adjunto.solicitud_candidato_id === candidato.solicitudCandidatoId);
  }

  alternarTodosCvs(evento: Event) {
    const seleccionar = (evento.target as HTMLInputElement).checked;
    const seleccion = new Set(this.cvsSeleccionadosResumen);

    this.candidatosSeleccionadosResumen.forEach((candidato) => {
      if (!this.candidatoTieneCvDisponible(candidato)) {
        return;
      }

      if (seleccionar) {
        seleccion.add(candidato.solicitudCandidatoId);
      } else {
        seleccion.delete(candidato.solicitudCandidatoId);
      }
    });

    this.cvsSeleccionadosResumen = seleccion;
  }

  alternarCvCandidato(candidato: InformeCandidato, evento: Event) {
    if (!this.candidatoTieneCvDisponible(candidato)) {
      return;
    }

    const seleccionar = (evento.target as HTMLInputElement).checked;
    const seleccion = new Set(this.cvsSeleccionadosResumen);

    // REGLA UX:
    // Incluir al candidato en el informe y adjuntar su CV son decisiones distintas.
    // Desmarcar el CV no elimina al candidato del resumen.
    if (seleccionar) {
      seleccion.add(candidato.solicitudCandidatoId);
    } else {
      seleccion.delete(candidato.solicitudCandidatoId);
    }

    this.cvsSeleccionadosResumen = seleccion;
  }

  textoClasificacion(clasificacion: ClasificacionInforme) {
    const etiquetas: Record<ClasificacionInforme, string> = {
      APROBADO: 'Aprobado',
      PENDIENTE: 'Pendiente',
      NO_APROBADO: 'No aprobado',
    };

    return etiquetas[clasificacion];
  }

  private prepararResumenAdministrador() {
    const solicitudCandidatoIds = this.candidatosSeleccionadosResumen.map((informe) => informe.solicitudCandidatoId);
    const destinatarios = this.destinatariosValidos(this.destinatariosResumen);

    if (destinatarios.length === 0 || this.tieneCorreosInvalidos(this.destinatariosResumen) || this.tieneCorreosInvalidos(this.ccResumen)) {
      return;
    }

    this.preparandoDirectivos = true;

    this.informesService.prepararDirectivos({
      solicitudCandidatoIds,
      destinatarios,
      cc: this.destinatariosValidos(this.ccResumen),
      asunto: this.asuntoResumen || null,
      cuerpo: this.cuerpoResumen || null,
    })
      .pipe(
        take(1),
        finalize(() => {
          this.preparandoDirectivos = false;
        }),
      )
      .subscribe({
        next: (preview) => {
          this.destinatariosResumen = preview.destinatarios.join(', ');
          this.ccResumen = preview.cc.join(', ');
          this.asuntoResumen = preview.asunto || this.asuntoResumen;
          this.cuerpoResumen = preview.cuerpo || this.cuerpoResumen;
          this.adjuntosResumen = preview.adjuntos ?? [];
          this.sincronizarSeleccionCvsConDisponibles();
        },
        error: (error) => {
          this.errorResumenAdministrador = this.mensajeErrorResumenAdministrador(
            error,
            'Ocurrió un problema al preparar el resumen. Inténtalo nuevamente.',
          );
        },
      });
  }

  descargarInformeResumen() {
    this.generarInformeComparativoSolicitud('pdf');
  }

  manejarAccionTabla(evento: DataTableActionEvent<InformeCandidato>) {
    if (evento.action === 'descargar-cv') {
      this.descargarDocumentoIndividual(evento.row, 'cv');
      return;
    }

    if (evento.action === 'descargar-informe-pdf') {
      this.generarInformeComparativoDesdeSolicitud(evento.row, 'pdf');
      return;
    }

    if (evento.action === 'descargar-informe-docx') {
      this.generarInformeComparativoDesdeSolicitud(evento.row, 'docx');
      return;
    }

    if (evento.action === 'enviar-correo') {
      if (this.vistaActiva === 'no-aprobados') {
        this.abrirCorreoCierre([evento.row]);
        return;
      }

      this.abrirCorreoAprobados([evento.row]);
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
          this.actualizarContextoComparativoDesdeFiltros();
        },
        error: (error) => {
          this.informes = [];
          this.errorCarga = obtenerMensajeError(error, 'No se pudieron cargar los informes desde M6.');
        },
      });
  }

  cargarCandidatosComparativo(solicitudId: number) {
    const token = ++this.cargaCandidatosComparativoToken;
    this.cargandoCandidatosComparativo = true;
    this.errorCandidatosComparativo = '';
    this.candidatosService.listarPorSolicitud(solicitudId)
      .pipe(
        take(1),
        finalize(() => {
          if (token === this.cargaCandidatosComparativoToken) {
            this.cargandoCandidatosComparativo = false;
          }
        }),
      )
      .subscribe({
        next: (postulaciones) => {
          if (token !== this.cargaCandidatosComparativoToken) {
            return;
          }

          this.candidatosComparativoSolicitud = postulaciones.map((postulacion) =>
            this.mapearPostulacionComparativo(postulacion),
          );
          if (this.candidatosComparativoSolicitud.length === 0) {
            this.errorCandidatosComparativo = 'La solicitud seleccionada no tiene candidatos asociados.';
          }
        },
        error: (error) => {
          if (token !== this.cargaCandidatosComparativoToken) {
            return;
          }

          this.candidatosComparativoSolicitud = [];
          this.errorCandidatosComparativo = obtenerMensajeError(error, 'No se pudieron cargar los candidatos asociados a la solicitud.');
        },
      });
  }

  abrirCorreoAprobados(candidatos: InformeCandidato[]) {
    const aprobados = candidatos.filter((candidato) => candidato.aprobado && candidato.puedeEnviarDirectivos);

    if (aprobados.length === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona candidatos aprobados para enviar correo.',
      };
      return;
    }

    this.modoCorreoCandidatos = 'seleccion';
    this.candidatosCorreoSeleccionados = aprobados;
    this.reiniciarEstadoCorreoCandidatos();
    this.plantillaCorreoCandidato = 'manual';
    this.plantillaCorreoCandidatoId = 0;
    this.mostrarModalCorreoCandidatos = true;
    this.cargarPlantillasCorreoCandidatos();
  }

  abrirCorreoCierre(candidatos: InformeCandidato[]) {
    const noAprobados = candidatos.filter((candidato) => candidato.clasificacion === 'NO_APROBADO');
    const noElegibles = noAprobados.filter((candidato) => !candidato.puedeEnviarRechazo);

    if (noAprobados.length === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona candidatos no aprobados para enviar una comunicación de cierre.',
      };
      return;
    }

    if (noElegibles.length > 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'La selección contiene candidatos que todavía no tienen habilitada una comunicación de cierre.',
      };
      return;
    }

    this.modoCorreoCandidatos = 'cierre';
    this.candidatosCorreoSeleccionados = noAprobados;
    this.reiniciarEstadoCorreoCandidatos();
    this.plantillaCorreoCierreId = 0;
    this.tipoCorreoCierre = '';
    this.mostrarModalCorreoCandidatos = true;
    this.cargarPlantillasCorreoCierre();
  }

  cerrarModalCorreoCandidatos() {
    if (this.enviandoCorreoCandidatos) {
      return;
    }

    this.mostrarModalCorreoCandidatos = false;
    this.errorCorreoCandidatos = '';
    this.candidatosCorreoSeleccionados = [];
    this.resultadosCorreoCandidatos = [];
    this.itemsCorreoCierre = [];
    this.plantillaCorreoCierreId = 0;
    this.tipoCorreoCierre = '';
  }

  seleccionarPlantillaCorreoCandidato(plantillaId: number | null) {
    const id = Number(plantillaId ?? 0);
    const plantilla = this.plantillasCorreoCandidatos.find((item) => item.plantilla_id === id);
    this.plantillaCorreoCandidatoId = plantilla?.plantilla_id ?? 0;
    this.plantillaCorreoCandidato = plantilla
      ? plantilla.tipo as TipoCorreoCandidatoApi
      : 'manual';
    this.aplicarPlantillaCorreoCandidato();
  }

  seleccionarPlantillaCorreoCierre(plantillaId: number | null) {
    const id = Number(plantillaId ?? 0);
    const plantilla = this.plantillasCorreoCierre.find((item) => item.plantilla_id === id);
    this.plantillaCorreoCierreId = plantilla?.plantilla_id ?? 0;
    this.tipoCorreoCierre = plantilla
      ? plantilla.tipo as TipoCorreoRechazoApi
      : '';
    this.itemsCorreoCierre = [];
    this.errorCorreoCandidatos = '';
    this.preparacionCorreoCierreToken++;
    this.resetearScrollMensajesCorreo();

    if (!this.tipoCorreoCierre) {
      return;
    }

    this.prepararCorreoCierre();
  }

  seleccionarTipoCorreoCierre(tipo: TipoCorreoRechazoApi | '') {
    this.tipoCorreoCierre = tipo;
    const plantilla = this.plantillasCorreoCierre.find((item) => item.tipo === tipo);
    this.plantillaCorreoCierreId = plantilla?.plantilla_id ?? 0;
    this.itemsCorreoCierre = [];
    this.errorCorreoCandidatos = '';
    this.preparacionCorreoCierreToken++;
    this.resetearScrollMensajesCorreo();

    if (!tipo) {
      return;
    }

    this.prepararCorreoCierre();
  }

  actualizarItemCorreoCierre(index: number, field: 'asunto' | 'cuerpo', value: string) {
    this.itemsCorreoCierre = this.itemsCorreoCierre.map((item, itemIndex) => (
      itemIndex === index ? { ...item, [field]: value } : item
    ));
  }

  enviarCorreoCandidatos() {
    this.errorCorreoCandidatos = '';
    this.resultadosCorreoCandidatos = [];

    if (!this.puedeEnviarCorreoCandidatos) {
      this.errorCorreoCandidatos = 'Revisa plantilla, asunto y mensaje antes de enviar.';
      return;
    }

    if (this.modoCorreoCandidatos === 'cierre') {
      this.enviarCorreoCierre();
      return;
    }

    this.enviandoCorreoCandidatos = true;
    this.informesService.enviarCorreosCandidatos({
      solicitudCandidatoIds: this.candidatosCorreoSeleccionados.map((candidato) => candidato.solicitudCandidatoId),
      tipo: 'SELECCION',
      asunto: this.asuntoCorreoCandidatos.trim(),
      cuerpo: this.cuerpoCorreoCandidatos.trim(),
    })
      .pipe(
        take(1),
        finalize(() => {
          this.enviandoCorreoCandidatos = false;
        }),
      )
      .subscribe({
        next: (resultados) => {
          this.resultadosCorreoCandidatos = resultados;
          const enviados = resultados.filter((resultado) => resultado.estado === 'ENVIADO').length;
          if (enviados === resultados.length) {
            this.errorCorreoCandidatos = '';
            return;
          }
          this.errorCorreoCandidatos = 'Algunos correos no se pudieron enviar. Revisa el detalle antes de cerrar.';
        },
        error: (error) => {
          this.errorCorreoCandidatos = obtenerMensajeError(error, 'No se pudo enviar el correo. Inténtalo nuevamente.');
        },
      });
  }

  enviarCorreoCandidatosAprobados() {
    this.enviarCorreoCandidatos();
  }

  private reiniciarEstadoCorreoCandidatos() {
    this.errorCorreoCandidatos = '';
    this.resultadosCorreoCandidatos = [];
    this.asuntoCorreoCandidatos = '';
    this.cuerpoCorreoCandidatos = '';
    this.itemsCorreoCierre = [];
    this.plantillaCorreoCierreId = 0;
    this.preparandoCorreoCierre = false;
  }

  private prepararCorreoCierre() {
    if (!this.tipoCorreoCierre) {
      return;
    }

    const token = ++this.preparacionCorreoCierreToken;
    this.preparandoCorreoCierre = true;
    this.errorCorreoCandidatos = '';
    this.informesService.prepararRechazos({
      solicitudCandidatoIds: this.candidatosCorreoSeleccionados.map((candidato) => candidato.solicitudCandidatoId),
      tipo: this.tipoCorreoCierre,
    })
      .pipe(
        take(1),
        finalize(() => {
          if (token === this.preparacionCorreoCierreToken) {
            this.preparandoCorreoCierre = false;
          }
        }),
      )
      .subscribe({
        next: (preview) => {
          if (token !== this.preparacionCorreoCierreToken) {
            return;
          }

          this.itemsCorreoCierre = preview.items;
          this.resetearScrollMensajesCorreo();
        },
        error: (error) => {
          if (token !== this.preparacionCorreoCierreToken) {
            return;
          }

          this.itemsCorreoCierre = [];
          this.errorCorreoCandidatos = obtenerMensajeError(error, 'No se pudo preparar el correo de cierre.');
        },
      });
  }

  private enviarCorreoCierre() {
    if (!this.tipoCorreoCierre) {
      return;
    }

    this.enviandoCorreoCandidatos = true;
    this.informesService.enviarRechazos(this.itemsCorreoCierre.map((item) => ({
      tipo: this.tipoCorreoCierre as TipoCorreoRechazoApi,
      solicitudCandidatoId: item.solicitud_candidato_id,
      asunto: item.asunto.trim(),
      cuerpo: item.cuerpo.trim(),
    })))
      .pipe(
        take(1),
        finalize(() => {
          this.enviandoCorreoCandidatos = false;
        }),
      )
      .subscribe({
        next: (resultados) => {
          this.resultadosCorreoCandidatos = resultados;
          const enviados = resultados.filter((resultado) => resultado.estado === 'ENVIADO').length;
          if (enviados === resultados.length) {
            this.errorCorreoCandidatos = '';
            return;
          }
          this.errorCorreoCandidatos = 'Algunos correos no se pudieron enviar. Revisa el detalle antes de cerrar.';
        },
        error: (error) => {
          this.errorCorreoCandidatos = obtenerMensajeError(error, 'No se pudo enviar el correo de cierre.');
        },
      });
  }

  private mapearInforme(item: CandidatoInformeApi): InformeCandidato {
    const resultadoEntrevista = this.resumenEntrevista(item);

    // TODO BACKEND M6:
    // La clasificación final deberá provenir de la nueva matriz
    // Técnica + Operacional + Otra.
    // No calcular este resultado en frontend.
    //
    // La clasificación M6 y el estado de postulación son conceptos distintos.
    // No cambiar automáticamente a "Seleccionado" desde frontend.
    // Esta transición depende de la regla de negocio/backend.
    return {
      id: String(item.solicitud_candidato_id),
      solicitudCandidatoId: item.solicitud_candidato_id,
      solicitudId: item.solicitud_id,
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
      // TODO BACKEND M6:
      // Reemplazar/ajustar esta información cuando Backend exponga
      // el resultado consolidado de la nueva matriz de aprobaciones.
      motivoM6: item.motivo_clasificacion.join(' ') || 'Sin motivo informado',
      estado: item.estado_postulacion || 'Sin estado',
      disponibilidad: item.disponibilidad || 'Sin disponibilidad',
      clasificacion: item.clasificacion,
      aprobado: item.clasificacion === 'APROBADO',
      puedeEnviarDirectivos: item.puede_enviar_directivos,
      puedeEnviarRechazo: item.puede_enviar_rechazo,
      entrevistas: item.entrevistas ?? [],
    };
  }

  private get informesSeleccionadosAprobados() {
    return this.informesSeleccionados
      .filter((informe) => informe.aprobado && informe.puedeEnviarDirectivos);
  }

  private actualizarContextoComparativoDesdeFiltros() {
    const solicitud = resolverSolicitudReal(this.solicitudesFiltro, this.filtros.idSolicitud);
    if (!solicitud) {
      this.limpiarContextoComparativo();
      return;
    }

    this.establecerSolicitudComparativo(Number(solicitud.id), solicitud.codigo ?? `Solicitud ${solicitud.id}`);
  }

  private actualizarContextoComparativoDesdeSeleccion() {
    if (this.seleccionados.size === 0) {
      this.limpiarContextoComparativo();
      return;
    }

    const seleccionados = this.informesSeleccionados;
    const solicitudes = Array.from(new Set(seleccionados.map((informe) => informe.solicitudId)));
    if (solicitudes.length !== 1) {
      this.limpiarContextoComparativo();
      this.errorCandidatosComparativo = 'Selecciona candidatos de una sola solicitud o usa el filtro de solicitud.';
      return;
    }

    const referencia = seleccionados[0];
    this.establecerSolicitudComparativo(referencia.solicitudId, referencia.idSolicitud);
  }

  private establecerSolicitudComparativo(solicitudId: number, codigo: string) {
    if (!Number.isFinite(solicitudId) || solicitudId <= 0) {
      this.limpiarContextoComparativo();
      return;
    }

    if (
      this.solicitudComparativoId === solicitudId
      && (this.cargandoCandidatosComparativo || this.candidatosComparativoSolicitud.length > 0)
    ) {
      return;
    }

    this.solicitudComparativoId = solicitudId;
    this.solicitudComparativoCodigo = codigo;
    this.candidatosComparativoSolicitud = [];
    this.errorCandidatosComparativo = '';
    this.cargarCandidatosComparativo(solicitudId);
  }

  private limpiarContextoComparativo() {
    this.cargaCandidatosComparativoToken++;
    this.solicitudComparativoId = null;
    this.solicitudComparativoCodigo = '';
    this.candidatosComparativoSolicitud = [];
    this.errorCandidatosComparativo = '';
  }

  private generarInformeComparativoDesdeSolicitud(candidato: InformeCandidato, formato: 'pdf' | 'docx') {
    this.cargarYDescargarInformeComparativo(candidato.solicitudId, candidato.idSolicitud, formato);
  }

  private generarInformeComparativoSolicitud(formato: 'pdf' | 'docx') {
    const solicitud = this.resolverSolicitudParaComparativo();
    if (!solicitud) {
      return;
    }

    this.cargarYDescargarInformeComparativo(solicitud.id, solicitud.codigo, formato);
  }

  private resolverSolicitudParaComparativo(): { id: number; codigo: string } | null {
    const solicitudFiltro = resolverSolicitudReal(this.solicitudesFiltro, this.filtros.idSolicitud);
    if (solicitudFiltro) {
      return {
        id: Number(solicitudFiltro.id),
        codigo: solicitudFiltro.codigo ?? `Solicitud ${solicitudFiltro.id}`,
      };
    }

    if (this.seleccionados.size === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona una solicitud en el filtro superior para generar el informe comparativo.',
      };
      return null;
    }

    const seleccionados = this.informesSeleccionados;
    const solicitudes = Array.from(new Set(seleccionados.map((informe) => informe.solicitudId)));
    if (solicitudes.length !== 1) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Elige una sola solicitud antes de generar el informe comparativo.',
      };
      return null;
    }

    return {
      id: seleccionados[0].solicitudId,
      codigo: seleccionados[0].idSolicitud,
    };
  }

  private cargarYDescargarInformeComparativo(solicitudId: number, codigo: string, formato: 'pdf' | 'docx') {
    const token = ++this.cargaCandidatosComparativoToken;
    this.solicitudComparativoId = solicitudId;
    this.solicitudComparativoCodigo = codigo;
    this.cargandoCandidatosComparativo = true;
    this.errorCandidatosComparativo = '';

    this.candidatosService.listarPorSolicitud(solicitudId)
      .pipe(
        take(1),
        finalize(() => {
          if (token === this.cargaCandidatosComparativoToken) {
            this.cargandoCandidatosComparativo = false;
          }
        }),
      )
      .subscribe({
        next: (postulaciones) => {
          if (token !== this.cargaCandidatosComparativoToken) {
            return;
          }

          const candidatos = postulaciones.map((postulacion) => this.mapearPostulacionComparativo(postulacion));
          this.candidatosComparativoSolicitud = candidatos;
          if (candidatos.length === 0) {
            this.errorCandidatosComparativo = `La solicitud ${codigo} no tiene candidatos asociados.`;
            this.alerta = {
              tipo: 'warning',
              variante: 'soft',
              mensaje: this.errorCandidatosComparativo,
            };
            return;
          }
          this.descargarInformeComparativo(candidatos, formato);
        },
        error: (error) => {
          if (token !== this.cargaCandidatosComparativoToken) {
            return;
          }

          this.candidatosComparativoSolicitud = [];
          this.errorCandidatosComparativo = obtenerMensajeError(error, 'No se pudieron cargar los candidatos asociados a la solicitud.');
          this.mostrarErrorAccion(error, 'No se pudieron cargar los candidatos asociados a la solicitud.');
        },
      });
  }

  private mapearPostulacionComparativo(postulacion: PostulacionCandidatoApi): InformeCandidato {
    const existente = this.informes.find((informe) => informe.solicitudCandidatoId === postulacion.slcd_id);
    if (existente) {
      return existente;
    }

    return {
      id: String(postulacion.slcd_id),
      solicitudCandidatoId: postulacion.slcd_id,
      solicitudId: postulacion.slcd_solicitud_id,
      idSolicitud: this.solicitudComparativoCodigo || `Solicitud ${postulacion.slcd_solicitud_id}`,
      match: Math.round(Number(postulacion.slcd_puntaje_compatibilidad ?? 0)),
      nombre: `Candidato ${postulacion.slcd_candidato_id ?? postulacion.slcd_id}`,
      correo: 'Correo no disponible',
      telefono: 'Sin telefono',
      cargo: 'Sin cargo',
      empresa: 'No informado',
      nivel: 'Sin tecnologias',
      experiencia: 'Sin informacion',
      resultadoEntrevista: 'Sin resultado',
      detalleResultado: 'Sin detalle',
      motivoM6: 'Sin motivo informado',
      estado: 'Sin estado',
      disponibilidad: 'Sin disponibilidad',
      clasificacion: 'PENDIENTE',
      aprobado: false,
      puedeEnviarDirectivos: false,
      puedeEnviarRechazo: false,
      entrevistas: [],
    };
  }

  private descargarInformeComparativo(candidatos: InformeCandidato[], formato: 'pdf' | 'docx') {
    const payload = this.payloadInformeComparativo(candidatos);
    if (!payload) {
      return;
    }

    const descarga$ = formato === 'pdf'
      ? this.informesService.descargarInformeComparativoPdf(payload)
      : this.informesService.descargarInformeComparativoDocx(payload);
    const nombre = formato === 'pdf' ? 'INFORME_COMPARATIVO.pdf' : 'INFORME_COMPARATIVO.docx';

    this.descargandoInformeComparativo = formato;
    descarga$
      .pipe(
        take(1),
        finalize(() => {
          this.descargandoInformeComparativo = null;
        }),
      )
      .subscribe({
        next: (respuesta) => {
          this.informesService.descargarBlob(respuesta, nombre);
          const solicitud = candidatos[0]?.idSolicitud ?? 'la solicitud';
          this.mostrarConfirmacionAccion(
            `Informe comparativo ${formato.toUpperCase()} descargado correctamente. Incluyó ${candidatos.length} ${candidatos.length === 1 ? 'candidato' : 'candidatos'} de ${solicitud}.`,
          );
        },
        error: (error) => {
          this.mostrarErrorAccion(error, `No se pudo descargar el informe comparativo ${formato.toUpperCase()}.`);
        },
      });
  }

  private payloadInformeComparativo(candidatos: InformeCandidato[]): InformeComparativoRequestApi | null {
    if (candidatos.length === 0) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'La solicitud seleccionada no tiene candidatos asociados para generar el informe comparativo.',
      };
      return null;
    }

    const solicitudes = Array.from(new Set(candidatos.map((candidato) => candidato.solicitudId)));
    if (solicitudes.length !== 1) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'El informe comparativo solo puede incluir candidatos de una misma solicitud.',
      };
      return null;
    }

    return {
      solicitud_id: solicitudes[0],
      solicitud_candidato_ids: candidatos.map((candidato) => candidato.solicitudCandidatoId),
    };
  }

  private cargarPlantillasCorreoCandidatos() {
    this.cargandoPlantillasCorreo = true;
    this.errorCorreoCandidatos = '';
    this.plantillasCorreoCandidatos = [];

    this.informesService.listarPlantillas()
      .pipe(
        take(1),
        finalize(() => {
          this.cargandoPlantillasCorreo = false;
        }),
      )
      .subscribe({
        next: (plantillas) => {
          this.plantillasCorreoCandidatos = this.filtrarPlantillasCorreoCandidatos(plantillas);
          const seleccion = this.plantillasCorreoCandidatos.find((plantilla) => plantilla.tipo === 'SELECCION');

          if (!seleccion) {
            this.errorCorreoCandidatos = 'No hay una plantilla activa de selección disponible.';
            return;
          }

          this.plantillaCorreoCandidato = 'SELECCION';
          this.plantillaCorreoCandidatoId = seleccion.plantilla_id;
          this.aplicarPlantillaCorreoCandidato();
        },
        error: () => {
          this.errorCorreoCandidatos = 'No se pudieron cargar las plantillas de correo.';
        },
      });
  }

  private cargarPlantillasCorreoCierre() {
    this.cargandoPlantillasCorreo = true;
    this.errorCorreoCandidatos = '';
    this.plantillasCorreoCierre = [];

    this.informesService.listarPlantillas()
      .pipe(
        take(1),
        finalize(() => {
          this.cargandoPlantillasCorreo = false;
        }),
      )
      .subscribe({
        next: (plantillas) => {
          this.plantillasCorreoCierre = plantillas
            .filter((plantilla) => plantilla.activa && ['RECHAZO', 'AGRADECIMIENTO'].includes(plantilla.tipo.toUpperCase()))
            .map((plantilla) => ({
              ...plantilla,
              tipo: plantilla.tipo.toUpperCase(),
            }));

          if (this.plantillasCorreoCierre.length === 0) {
            this.errorCorreoCandidatos = 'No hay plantillas activas de cierre disponibles.';
          }
        },
        error: () => {
          this.errorCorreoCandidatos = 'No se pudieron cargar las plantillas de correo.';
        },
      });
  }

  private aplicarPlantillaCorreoCandidato() {
    if (this.plantillaCorreoCandidato === 'manual') {
      this.asuntoCorreoCandidatos = '';
      this.cuerpoCorreoCandidatos = '';
      this.resetearScrollMensajesCorreo();
      return;
    }

    const plantilla = this.plantillasCorreoCandidatos.find((item) => item.plantilla_id === this.plantillaCorreoCandidatoId);
    if (!plantilla) {
      this.asuntoCorreoCandidatos = '';
      this.cuerpoCorreoCandidatos = '';
      this.resetearScrollMensajesCorreo();
      return;
    }

    this.asuntoCorreoCandidatos = plantilla.asunto;
    this.cuerpoCorreoCandidatos = plantilla.cuerpo;
    this.resetearScrollMensajesCorreo();
  }

  private resetearScrollMensajesCorreo() {
    queueMicrotask(() => {
      this.mensajeCorreoTextareas?.forEach((textarea) => {
        textarea.nativeElement.scrollTop = 0;
      });
    });
  }

  private filtrarPlantillasCorreoCandidatos(plantillas: PlantillaNotificacionApi[]) {
    return plantillas
      .filter((plantilla) => plantilla.activa && plantilla.tipo.toUpperCase() === 'SELECCION')
      .filter((plantilla) => this.variablesNoSoportadasPlantilla(plantilla).length === 0)
      .map((plantilla) => ({
        ...plantilla,
        tipo: plantilla.tipo.toUpperCase(),
      }));
  }

  private variablesNoSoportadasPlantilla(plantilla: PlantillaNotificacionApi) {
    const soportadas = new Set([
      '{nombre}',
      '{cargo}',
      '{codigo_solicitud}',
      '{solicitud}',
      '{{params.nombre}}',
      '{{params.cargo}}',
      '{{params.codigo_solicitud}}',
      '{{params.solicitud}}',
    ]);

    const texto = `${plantilla.asunto} ${plantilla.cuerpo}`;
    const variables = texto.match(/{{\s*params\.[^}]+\s*}}|{[^{}]+}/g) ?? [];

    return Array.from(new Set(
      variables
        .map((variable) => variable.replace(/\s+/g, ''))
        .filter((variable) => !soportadas.has(variable)),
    ));
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

  private inicializarSeleccionCvsResumen() {
    this.cvsSeleccionadosResumen = new Set(
      this.candidatosSeleccionadosResumen.map((candidato) => candidato.solicitudCandidatoId),
    );
  }

  private sincronizarSeleccionCvsConDisponibles() {
    if (this.adjuntosResumen.length === 0) {
      return;
    }

    const disponibles = new Set(this.adjuntosResumen.map((adjunto) => adjunto.solicitud_candidato_id));
    this.cvsSeleccionadosResumen = new Set(
      Array.from(this.cvsSeleccionadosResumen).filter((id) => disponibles.has(id)),
    );
  }

  private destinatariosValidos(valor: string) {
    return this.parsearCorreos(valor).filter((correo) => this.correoValido(correo));
  }

  private tieneCorreosInvalidos(valor: string) {
    return this.parsearCorreos(valor).some((correo) => !this.correoValido(correo));
  }

  private correoValido(correo: string) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo);
  }

  private mensajeErrorResumenAdministrador(error: unknown, fallback: string) {
    const mensaje = obtenerMensajeError(error, fallback);
    const normalizado = mensaje.toLowerCase();

    // REGLA UX:
    // Los errores técnicos provenientes de Backend no deben mostrarse
    // directamente al usuario. Se traducen a mensajes claros en español.
    if (
      normalizado.includes('destinatarios')
      || normalizado.includes('at least 1')
      || normalizado.includes('list should have at least')
    ) {
      return 'Agrega al menos un destinatario para enviar el resumen.';
    }

    if (normalizado.includes('adjunt') || normalizado.includes('documento')) {
      return 'No pudimos adjuntar uno o más CV. Revisa los documentos e inténtalo nuevamente.';
    }

    if (
      normalizado.includes('timeout')
      || normalizado.includes('connection')
      || normalizado.includes('conex')
      || normalizado.includes('servicio')
    ) {
      return 'No pudimos conectarnos con el servicio de envío. Inténtalo nuevamente.';
    }

    if (
      normalizado.includes('pydantic')
      || normalizado.includes('validation')
      || normalizado.includes('traceback')
      || normalizado.includes('solicitud_candidato_ids')
      || /[\{\}\[\]]/.test(mensaje)
    ) {
      return fallback;
    }

    return mensaje || 'Ocurrió un problema al enviar el resumen. Inténtalo nuevamente.';
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
