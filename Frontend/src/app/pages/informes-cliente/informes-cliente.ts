import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize, take } from 'rxjs';
import {
  CandidatoInformeApi,
  ClasificacionInforme,
  DocumentoInformeApi,
  EvaluacionEntrevistaResumenApi,
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
      entrevistas: item.entrevistas ?? [],
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
