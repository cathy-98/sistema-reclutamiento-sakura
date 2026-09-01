import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { catchError, finalize, forkJoin, Observable, of, take, timeout } from 'rxjs';
import { CandidatoProfileTab, CandidatoProfileTabs } from '../candidato-profile-tabs/candidato-profile-tabs';
import { Button } from '../../../shared/components/button/button';
import { Modal } from '../../../shared/components/modal/modal';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { EntrevistaFormModal } from '../../entrevistas/entrevista-form-modal/entrevista-form-modal';
import {
  EntrevistaApi,
  EntrevistaPayload,
  EntrevistasService,
} from '../../../services/entrevistas.service';
import {
  AsignacionCuestionarioApi,
  AsignacionCuestionarioCandidatoApi,
  CuestionarioApi,
  CuestionariosService,
} from '../../../services/cuestionarios.service';
import {
  CargoCatalogoApi,
  CarreraCatalogoApi,
  CatalogosService,
  ComunaCatalogoApi,
  EstadoSolicitudCandidatoCatalogoApi,
  HabilidadCatalogoApi,
  InstitucionCatalogoApi,
  NivelEducacionalCatalogoApi,
  NivelHabilidadCatalogoApi,
  MotivoRechazoCatalogoApi,
  NombreResultadoCatalogoApi,
} from '../../../services/catalogos.service';
import {
  ClientesService,
  EmpresaApi,
} from '../../../services/clientes.service';
import {
  CandidatoPerfilCompletoApi,
  CandidatosService,
  EstudioCandidatoApi,
  ExperienciaCandidatoApi,
  HabilidadCandidatoApi,
  IdiomaCandidatoApi,
  PostulacionCandidatoApi,
} from '../../../services/candidatos.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { AuthService } from '../../../services/auth.service';
import { SolicitudResumen } from '../../../shared/models/solicitud.model';
import { extraerLinkedinUrl } from '../../../shared/mappers/candidato.mapper';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { CandidateApplicationsSection } from './components/candidate-applications-section/candidate-applications-section';
import { CandidateDocumentsSection } from './components/candidate-documents-section/candidate-documents-section';
import { CandidateEducationSection } from './components/candidate-education-section/candidate-education-section';
import { CandidateExperienceSection } from './components/candidate-experience-section/candidate-experience-section';
import { CandidateMatchSection } from './components/candidate-match-section/candidate-match-section';
import { CandidateProfileHeader } from './components/candidate-profile-header/candidate-profile-header';
import {
  CandidatoPerfil,
  DocumentoPerfil,
  EntrevistaPerfilResumen,
  EstudioPerfil,
  EtapaSeleccion,
  EvaluacionTecnicaPerfil,
  ExperienciaPerfil,
  HabilidadComparada,
  ObservacionPerfil,
  PerfilTab,
  PostulacionPerfil,
} from './candidato-perfil.models';

interface ContextoPostulacionPerfil {
  postulacionId?: number;
  solicitudId?: number;
  idSolicitud: string;
  cargo: string;
  estado: string;
  estadoId?: number | null;
  match: number | null;
  renta: number;
  fechaPostulacionTimestamp: number;
}

interface CatalogosPerfilM3 {
  cargos: Map<number, string>;
  empresas: Map<number, string>;
  habilidades: Map<number, string>;
  nivelesHabilidad: Map<number, string>;
  instituciones: Map<number, string>;
  carreras: Map<number, string>;
  nivelesEducacionales: Map<number, string>;
  comunas: Map<number, string>;
}

@Component({
  selector: 'app-candidato-perfil-page',
  imports: [
    CommonModule,
    FormsModule,
    Button,
    CandidatoProfileTabs,
    CandidateApplicationsSection,
    CandidateDocumentsSection,
    CandidateEducationSection,
    CandidateExperienceSection,
    CandidateMatchSection,
    CandidateProfileHeader,
    EntrevistaFormModal,
    Modal,
    PageLayout,
  ],
  templateUrl: './candidato-perfil-page.html',
  styleUrl: './candidato-perfil-page.scss',
})
export class CandidatoPerfilPage implements OnInit {
  // Función futura: documentos queda oculto porque la BD actual no tiene tbl_documento.
  // Para habilitarla cuando exista soporte backend/BD, cambiar a true.
  readonly mostrarModuloDocumentos = false;
  perfilCargado = false;
  tabActiva: PerfilTab = 'experiencia';
  postulacionSeleccionadaId = '';
  busquedaPostulacion = '';
  proximaEntrevista: EntrevistaPerfilResumen | null = null;
  entrevistasCandidato: EntrevistaApi[] = [];
  estadosPostulacionPerfil: string[] = [];
  private estadosPostulacionPorNombre = new Map<string, number>();
  private contextoPostulaciones = new Map<string, ContextoPostulacionPerfil>();
  private solicitudesCatalogoPerfil: SolicitudResumen[] = [];
  archivosDocumentos: File[] = [];
  mostrarModalObservacion = false;
  mostrarModalObservacionEntrevista = false;
  mostrarModalEstadoPostulacion = false;
  mostrarModalEntrevista = false;
  mostrarModalTest = false;
  nota = '';
  observacionEstadoPostulacion = '';
  estadoPostulacionPendienteId: number | null = null;
  estadoPostulacionPendienteNombre = '';
  estadoPostulacionOriginalNombre = '';
  estadoPostulacionError = '';
  guardandoEstadoPostulacion = false;
  motivoRechazoSeleccionadoId: number | null = null;
  motivosRechazo: MotivoRechazoCatalogoApi[] = [];
  private disponibilidadesPorNombre = new Map<string, number>();
  observacionEntrevistaTexto = '';
  observacionEntrevistaSeleccionada: EtapaSeleccion | null = null;
  agregandoObservacionEntrevista = false;
  tipoEvaluacionSeleccionadoId: number | null = null;
  resultadoEvaluacionSeleccionadoId: number | null = null;
  resultadosEvaluacion: NombreResultadoCatalogoApi[] = [];
  guardandoEvaluacionEntrevista = false;
  evaluacionEntrevistaError = '';
  guardandoContactoPerfil = false;
  contactoPerfilError = '';
  guardandoEntrevistaPerfil = false;
  entrevistaPerfilError = '';

  get puedeGuardarEstadoPostulacion() {
    const contexto =
      this.contextoPostulaciones.get(this.postulacionSeleccionadaId);

    return Boolean(contexto?.postulacionId);
  }

  get estadoPostulacionRequiereMotivo() {
    return [
      'descartado',
      'inhabilitado',
    ].includes(
      this.normalizarTexto(this.estadoPostulacionPendienteNombre),
    );
  }

  get puedeConfirmarEstadoPostulacion() {
    return !this.guardandoEstadoPostulacion &&
      (!this.estadoPostulacionRequiereMotivo ||
        Boolean(this.motivoRechazoSeleccionadoId));
  }

  get tituloModalObservacionEntrevista() {
    return this.agregandoObservacionEntrevista
      ? 'Agregar observación de entrevista'
      : 'Editar observación de entrevista';
  }

  get tiposEvaluacionDisponibles() {
    const usuarioId =
      this.authService.obtenerUsuarioId();
    const tipos =
      this.observacionEntrevistaSeleccionada?.tipos ?? [];

    if (!usuarioId) {
      return tipos;
    }

    const asignados = tipos.filter((tipo) =>
      tipo.entrevistadoresIds.includes(usuarioId),
    );

    return asignados.length ? asignados : tipos;
  }

  get puedeGuardarEvaluacionEntrevista() {
    return !this.guardandoEvaluacionEntrevista &&
      Boolean(this.observacionEntrevistaSeleccionada?.id) &&
      Boolean(this.tipoEvaluacionSeleccionadoId) &&
      Boolean(this.resultadoEvaluacionSeleccionadoId) &&
      this.nombreEstadoEntrevistaPerfil(
        this.observacionEntrevistaSeleccionada?.estado ?? '',
      ) === 'realizada';
  }

  candidato: CandidatoPerfil;

  get tabs(): CandidatoProfileTab[] {
    const tabs: CandidatoProfileTab[] = [
      { id: 'experiencia', label: 'Experiencia', icon: 'briefcase' },
      { id: 'estudios', label: 'Estudios', icon: 'graduation' },
      { id: 'postulaciones', label: 'Postulaciones', icon: 'puzzle' },
      { id: 'match', label: 'Match', icon: 'users' },
      { id: 'evaluaciones', label: 'Evaluaciones técnicas', icon: 'file' },
       // M3: Observaciones ocultas según definición funcional actual.
    // { id: 'observaciones', label: 'Observaciones', icon: 'list' },
    ];

    if (this.mostrarModuloDocumentos) {
      tabs.splice(5, 0, { id: 'documentos', label: 'Documentos', icon: 'file' });
    }

    return tabs;
  }

  experiencias: ExperienciaPerfil[] = [];

  estudios: EstudioPerfil[] = [];

  postulaciones: PostulacionPerfil[] = [];

  habilidadesComparadas: HabilidadComparada[] = [];

  readonly fortalezasMatch: string[] = [];
  readonly areasMejoraMatch: string[] = [];

  evaluacionesTecnicas: EvaluacionTecnicaPerfil[] = [];

  // Función futura oculta: lista de documentos visible solo si mostrarModuloDocumentos=true.
  readonly documentos: DocumentoPerfil[] = [];

  readonly historialObservaciones: ObservacionPerfil[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private entrevistasService: EntrevistasService,
    private cuestionariosService: CuestionariosService,
    private catalogosService: CatalogosService,
    private clientesService: ClientesService,
    private candidatosService: CandidatosService,
    private solicitudesService: SolicitudesService,
    private authService: AuthService,
  ) {
    const params = this.route.snapshot.queryParamMap;
    const tabInicial = params.get('tab') as PerfilTab | null;

    this.candidato = {
      idSolicitud: params.get('idSolicitud') || '',
      match: params.has('match')
        ? this.normalizarNumero(params.get('match')) ?? null
        : null,
      nombre: params.get('nombre') || 'Candidato sin nombre',
      correo: params.get('correo') || 'Sin correo',
      telefono: params.get('telefono') || 'Sin teléfono',
      cargo: params.get('cargo') || 'Sin cargo',
      estado: params.get('estado') || 'Sin estado',
      disponibilidad: params.get('disponibilidad') || 'Sin disponibilidad',
      renta: Number(params.get('renta') || 0),
      rut: params.get('rut') || 'Sin RUT',
      fechaNacimiento: 'Sin fecha',
      fechaRegistro: 'Sin fecha',
      tituloProfesional: 'Sin título registrado',
      estadoUsuario: params.get('estadoUsuario') || 'Sin estado',
      resumenProfesional: 'Sin resumen profesional registrado.',
      urlPerfil: extraerLinkedinUrl(params.get('urlPerfil')) ?? '',
      enlaces: this.extraerEnlacesPerfil(params.get('urlPerfil')),
      idiomas: [],
      comuna: 'Sin comuna',
      direccion: 'Sin dirección',
    };

    if (tabInicial && this.tabs.some((tab) => tab.id === tabInicial)) {
      this.tabActiva = tabInicial;
    }
  }

  ngOnInit() {
    this.cargarPerfilM3();
  }

  get iniciales() {
    return this.candidato.nombre
      .split(' ')
      .slice(0, 2)
      .map((parte) => parte[0])
      .join('')
      .toUpperCase();
  }

  get rentaFormateada() {
    return `$${this.candidato.renta.toLocaleString('es-CL')} CLP líquidos`;
  }

  get entrevistaInicial(): Partial<EntrevistaPayload> {
    const contexto =
      this.contextoPostulaciones.get(this.postulacionSeleccionadaId);

    return {
      idSolicitud: this.candidato.idSolicitud,
      solicitudCandidatoId: contexto?.postulacionId,
      candidato: this.candidato.nombre,
      cargo: this.candidato.cargo,
      tipo: 'RRHH',
      asunto: `Entrevista ${this.candidato.cargo}`,
    };
  }

  get matchClass() {
    if (this.candidato.match == null) {
      return 'is-empty';
    }

    if (this.candidato.match >= 75) {
      return 'is-high';
    }

    if (this.candidato.match >= 55) {
      return 'is-medium';
    }

    return 'is-low';
  }

  get postulacionesFiltradas() {
    const texto = this.busquedaPostulacion.trim().toLowerCase();
    return this.postulaciones.filter((postulacion) => postulacion.join(' ').toLowerCase().includes(texto));
  }

  get postulacionSeleccionada() {
    return this.postulaciones.find((postulacion) => postulacion[0] === this.postulacionSeleccionadaId) || this.postulaciones[0];
  }

  get matchTexto() {
    return this.candidato.match == null
      ? 'Sin match'
      : `${this.candidato.match}%`;
  }

  get procesoSeleccionado() {
    return this.mapearEntrevistasProcesoM5(
      this.entrevistasCandidato.filter(
        (entrevista) =>
          this.codigoEntrevista(
            entrevista,
          ) ===
          this.postulacionSeleccionadaId,
      ),
    );
  }

  get proximaEntrevistaSeleccionada() {
    return this.mapearProximaEntrevistaM5(
      this.entrevistasCandidato.filter(
        (entrevista) =>
          this.codigoEntrevista(entrevista) ===
          this.postulacionSeleccionadaId,
      ),
      this.solicitudesCatalogoPerfil,
    );
  }

  get evaluacionesTecnicasSeleccionadas() {
    if (!this.postulacionSeleccionadaId) {
      return this.evaluacionesTecnicas;
    }

    const seleccionada =
      this.normalizarCodigoSolicitud(this.postulacionSeleccionadaId);

    return this.evaluacionesTecnicas.filter(
      (evaluacion) =>
        this.normalizarCodigoSolicitud(evaluacion[2]) === seleccionada,
    );
  }

  get totalEvaluacionesTecnicas() {
    return this.evaluacionesTecnicasSeleccionadas.length;
  }

  get totalEvaluacionesPendientes() {
    return this.evaluacionesTecnicasSeleccionadas.filter((evaluacion) =>
      ['asignado', 'en-progreso', 'pendiente'].includes(
        this.normalizarTexto(evaluacion[1]),
      ),
    ).length;
  }

  get ultimoEstadoEvaluacionTecnica() {
    return this.evaluacionesTecnicasSeleccionadas[0]?.[1] ??
      'Sin evaluaciones';
  }

  get resultadosEntrevistasSeleccionadas() {
    return this.procesoSeleccionado.flatMap((etapa) =>
      etapa.evaluaciones.map((evaluacion) => ({
        entrevista: etapa.etapa,
        solicitud: etapa.solicitud || this.postulacionSeleccionadaId,
        fecha: etapa.fecha,
        tipo: evaluacion.tipoNombre || etapa.tipos.find((tipo) => tipo.id === evaluacion.tipoId)?.nombre || etapa.tipoEntrevista || 'Sin tipo',
        entrevistador: evaluacion.usuarioNombre || etapa.entrevistador || 'Sin entrevistador',
        resultado: evaluacion.resultado || 'Sin resultado',
        observacion: evaluacion.observacion?.trim() || 'Sin observación',
      })),
    );
  }

  seleccionarPostulacion(id: string) {
    this.postulacionSeleccionadaId = id;
    this.aplicarContextoPostulacion(id);
  }

  actualizarDocumentos(files: File[]) {
    this.archivosDocumentos = files;
  }

  abrirModalObservacion() {
    this.mostrarModalObservacion = true;
  }

  cerrarModalObservacion() {
    this.mostrarModalObservacion = false;
  }

  guardarObservacion() {
    this.nota = '';
    this.cerrarModalObservacion();
  }

  abrirModalObservacionEntrevista(etapa: EtapaSeleccion) {
    this.observacionEntrevistaSeleccionada = etapa;
    this.evaluacionEntrevistaError = '';
    this.tipoEvaluacionSeleccionadoId =
      this.tiposEvaluacionDisponibles[0]?.id ?? null;
    const evaluacionActual =
      this.evaluacionSeleccionadaActual();
    this.agregandoObservacionEntrevista =
      !evaluacionActual;
    this.resultadoEvaluacionSeleccionadoId =
      evaluacionActual?.resultadoId ??
      this.resultadosEvaluacion[0]?.nore_id ??
      null;
    this.observacionEntrevistaTexto =
      evaluacionActual?.observacion?.trim() ?? '';
    this.mostrarModalObservacionEntrevista = true;
  }

  cerrarModalObservacionEntrevista() {
    this.mostrarModalObservacionEntrevista = false;
    this.observacionEntrevistaSeleccionada = null;
    this.observacionEntrevistaTexto = '';
    this.agregandoObservacionEntrevista = false;
    this.tipoEvaluacionSeleccionadoId = null;
    this.resultadoEvaluacionSeleccionadoId = null;
    this.guardandoEvaluacionEntrevista = false;
    this.evaluacionEntrevistaError = '';
  }

  guardarObservacionEntrevista() {
    const etapa =
      this.observacionEntrevistaSeleccionada;

    if (
      !this.puedeGuardarEvaluacionEntrevista
    ) {
      this.evaluacionEntrevistaError =
        this.mensajeEvaluacionEntrevistaIncompleta();
      return;
    }

    const entrevistaId =
      etapa?.id as string;
    const tipoId =
      this.tipoEvaluacionSeleccionadoId as number;
    const resultadoId =
      this.resultadoEvaluacionSeleccionadoId as number;

    const payload = {
      nombre_resultado_id: resultadoId,
      observacion: this.observacionEntrevistaTexto.trim() || null,
    };
    const evaluacionActual =
      this.evaluacionSeleccionadaActual();
    const guardar$ = evaluacionActual
      ? this.entrevistasService.actualizarEvaluacion(
          entrevistaId,
          tipoId,
          payload,
        )
      : this.entrevistasService.crearEvaluacion(
          entrevistaId,
          tipoId,
          payload,
        );

    this.guardandoEvaluacionEntrevista = true;
    this.evaluacionEntrevistaError = '';

    guardar$
      .pipe(
        finalize(() => {
          this.guardandoEvaluacionEntrevista = false;
        }),
      )
      .subscribe({
        next: () => {
          this.cerrarModalObservacionEntrevista();
          this.recargarEntrevistasPerfil();
        },
        error: (error) => {
          this.evaluacionEntrevistaError =
            obtenerMensajeError(error, 'No fue posible guardar la evaluación de entrevista.');
        },
      });
  }

  private mensajeEvaluacionEntrevistaIncompleta() {
    if (
      this.nombreEstadoEntrevistaPerfil(
        this.observacionEntrevistaSeleccionada?.estado ?? '',
      ) !== 'realizada'
    ) {
      return 'Solo se puede evaluar una entrevista marcada como Realizada.';
    }

    if (this.tiposEvaluacionDisponibles.length === 0) {
      return 'Esta entrevista no tiene tipos asociados para evaluar.';
    }

    if (!this.tipoEvaluacionSeleccionadoId) {
      return 'Selecciona el tipo de entrevista a evaluar.';
    }

    if (!this.resultadoEvaluacionSeleccionadoId) {
      return 'Selecciona un resultado para guardar la evaluación.';
    }

    return 'Completa la evaluación antes de guardar.';
  }

  guardarEstadoPostulacion() {
    const contexto =
      this.contextoPostulaciones.get(this.postulacionSeleccionadaId);
    const estadoId =
      this.estadosPostulacionPorNombre.get(
        this.normalizarTexto(this.candidato.estado),
      );

    if (!contexto?.postulacionId) {
      this.candidato = {
        ...this.candidato,
        estado: contexto?.estado ?? this.candidato.estado,
      };
      return;
    }

    if (!estadoId) {
      this.candidato = {
        ...this.candidato,
        estado: contexto.estado,
      };
      return;
    }

    this.estadoPostulacionPendienteId = estadoId;
    this.estadoPostulacionPendienteNombre = this.candidato.estado;
    this.estadoPostulacionOriginalNombre = contexto.estado;
    this.observacionEstadoPostulacion = '';
    this.estadoPostulacionError = '';
    this.guardandoEstadoPostulacion = false;
    this.motivoRechazoSeleccionadoId =
      this.estadoPostulacionRequiereMotivo
        ? this.motivosRechazo[0]?.mtrc_id ?? null
        : null;
    this.mostrarModalEstadoPostulacion = true;
  }

  cerrarModalEstadoPostulacion(revertir = true) {
    if (revertir && this.estadoPostulacionOriginalNombre) {
      this.candidato = {
        ...this.candidato,
        estado: this.estadoPostulacionOriginalNombre,
      };
    }

    this.mostrarModalEstadoPostulacion = false;
    this.estadoPostulacionPendienteId = null;
    this.estadoPostulacionPendienteNombre = '';
    this.estadoPostulacionOriginalNombre = '';
    this.estadoPostulacionError = '';
    this.guardandoEstadoPostulacion = false;
    this.observacionEstadoPostulacion = '';
    this.motivoRechazoSeleccionadoId = null;
  }

  confirmarEstadoPostulacion() {
    const contexto =
      this.contextoPostulaciones.get(this.postulacionSeleccionadaId);

    if (!contexto?.postulacionId || !this.estadoPostulacionPendienteId) {
      this.estadoPostulacionError =
        'No se encontró la postulación o el estado para guardar.';
      return;
    }

    if (this.estadoPostulacionRequiereMotivo && !this.motivoRechazoSeleccionadoId) {
      this.estadoPostulacionError =
        'Selecciona un motivo para guardar este estado.';
      return;
    }

    this.guardandoEstadoPostulacion = true;
    this.estadoPostulacionError = '';

    this.candidatosService
      .cambiarEstadoPostulacion(contexto.postulacionId, {
        estado_id: this.estadoPostulacionPendienteId,
        motivo_rechazo_id: this.estadoPostulacionRequiereMotivo
          ? this.motivoRechazoSeleccionadoId
          : null,
        observaciones: this.observacionEstadoPostulacion.trim() || null,
      })
      .subscribe({
        next: (postulacion) => {
          const estado =
            this.estadoPostulacionNombre(postulacion) ??
            this.estadoPostulacionPendienteNombre;
          this.actualizarEstadoPostulacionSeleccionada(
            estado,
            this.estadoPostulacionPendienteId ?? 0,
          );
          this.cerrarModalEstadoPostulacion(false);
        },
        error: (error) => {
          console.warn('No fue posible guardar el estado de postulación.', error);
          this.guardandoEstadoPostulacion = false;
          this.estadoPostulacionError =
            this.mensajeErrorHttp(error) ||
            'No fue posible guardar el estado de postulación.';
        },
      });
  }

  guardarRentaPostulacion(renta: number) {
    const contexto =
      this.contextoPostulaciones.get(this.postulacionSeleccionadaId);

    if (!contexto?.postulacionId) {
      this.candidato = {
        ...this.candidato,
        renta,
      };
      return;
    }

    this.candidatosService
      .actualizarPostulacion(contexto.postulacionId, {
        slcd_pretension_renta: renta,
      })
      .pipe(take(1))
      .subscribe({
        next: (postulacion) => {
          const rentaActualizada =
            postulacion.slcd_pretension_renta ?? renta;
          this.candidato = {
            ...this.candidato,
            renta: rentaActualizada,
          };
          this.contextoPostulaciones.set(this.postulacionSeleccionadaId, {
            ...contexto,
            renta: rentaActualizada,
          });
        },
        error: (error) => {
          console.warn('No fue posible guardar la renta esperada.', error);
        },
      });
  }

  guardarDisponibilidadCandidato(disponibilidad: string) {
    const disponibilidadId =
      this.disponibilidadesPorNombre.get(
        this.normalizarTexto(disponibilidad),
      );

    const payload = disponibilidadId
      ? { cand_disponibilidad_id: disponibilidadId }
      : {};

    const guardar$ = this.esAutoservicio
      ? this.candidatosService.actualizarMiPerfil(payload)
      : this.candidatosService.actualizar(
          this.route.snapshot.paramMap.get('id') ?? '',
          payload,
        );

    guardar$
      .pipe(take(1))
      .subscribe({
        next: () => {
          this.candidato = {
            ...this.candidato,
            disponibilidad,
          };
        },
        error: (error) => {
          console.warn('No fue posible guardar la disponibilidad.', error);
        },
      });
  }

  guardarContactoCandidato(contacto: { correo: string; telefono: string }) {
    const candidatoId = this.route.snapshot.paramMap.get('id');
    const payload = {
      cand_email: contacto.correo.trim(),
      cand_telefono: contacto.telefono.trim() || null,
    };

    const guardar$ = this.esAutoservicio
      ? this.candidatosService.actualizarMiPerfil(payload)
      : this.candidatosService.actualizar(candidatoId ?? '', payload);

    if (!this.esAutoservicio && !candidatoId) {
      this.contactoPerfilError =
        'No se encontró el candidato para guardar la información de contacto.';
      return;
    }

    this.guardandoContactoPerfil = true;
    this.contactoPerfilError = '';

    guardar$
      .pipe(
        take(1),
        finalize(() => {
          this.guardandoContactoPerfil = false;
        }),
      )
      .subscribe({
        next: (perfil) => {
          this.candidato = {
            ...this.candidato,
            correo: perfil.cand_email ?? payload.cand_email,
            telefono: perfil.cand_telefono ?? payload.cand_telefono ?? '',
          };
        },
        error: (error) => {
          this.contactoPerfilError =
            obtenerMensajeError(error, 'No fue posible guardar correo y teléfono.');
        },
      });
  }

  actualizarFormularioEvaluacionEntrevista() {
    const evaluacionActual =
      this.evaluacionSeleccionadaActual();

    this.agregandoObservacionEntrevista =
      !evaluacionActual;
    this.resultadoEvaluacionSeleccionadoId =
      evaluacionActual?.resultadoId ??
      this.resultadoEvaluacionSeleccionadoId ??
      this.resultadosEvaluacion[0]?.nore_id ??
      null;
    this.observacionEntrevistaTexto =
      evaluacionActual?.observacion?.trim() ?? '';
  }

  private evaluacionSeleccionadaActual() {
    const etapa =
      this.observacionEntrevistaSeleccionada;

    if (!etapa || !this.tipoEvaluacionSeleccionadoId) {
      return null;
    }

    const usuarioId = this.authService.obtenerUsuarioId();
    const evaluacionesDelTipo = etapa.evaluaciones.filter(
      (evaluacion) =>
        evaluacion.tipoId === this.tipoEvaluacionSeleccionadoId,
    );

    return (
      (usuarioId
        ? evaluacionesDelTipo.find(
            (evaluacion) => evaluacion.usuarioId === usuarioId,
          )
        : null) ??
      evaluacionesDelTipo[0] ??
      null
    );
  }

  private recargarEntrevistasPerfil() {
    if (this.esAutoservicio) {
      this.entrevistasService
        .listarMisEntrevistas()
        .pipe(take(1))
        .subscribe({
          next: (entrevistas) => {
            this.entrevistasCandidato = entrevistas;
          },
        });
      return;
    }

    const candidatoId = this.route.snapshot.paramMap.get('id');

    if (!candidatoId) {
      return;
    }

    this.entrevistasService
      .listarPorCandidato(candidatoId)
      .pipe(take(1))
      .subscribe({
        next: (entrevistas) => {
          this.entrevistasCandidato = entrevistas;
        },
      });
  }

  private actualizarEstadoPostulacionSeleccionada(
    estado: string,
    estadoId: number,
  ) {
    const contexto =
      this.contextoPostulaciones.get(this.postulacionSeleccionadaId);

    if (contexto) {
      this.contextoPostulaciones.set(this.postulacionSeleccionadaId, {
        ...contexto,
        estado,
        estadoId,
      });
    }

    this.postulaciones = this.postulaciones.map((postulacion) =>
      postulacion[0] === this.postulacionSeleccionadaId
        ? [postulacion[0], postulacion[1], postulacion[2], postulacion[3], estado]
        : postulacion,
    );
    this.candidato = {
      ...this.candidato,
      estado,
    };
  }

  private estadoPostulacionNombre(
    postulacion: PostulacionCandidatoApi,
  ) {
    const estadoId =
      postulacion.slcd_estado_solicitud_candidato_id;

    if (estadoId == null) {
      return null;
    }

    return this.estadosPostulacionPerfil.find(
      (estado) =>
        this.estadosPostulacionPorNombre.get(
          this.normalizarTexto(estado),
        ) === estadoId,
    ) ?? null;
  }

  private mensajeErrorHttp(error: unknown) {
    const payload = error as {
      error?: {
        detail?: string | { message?: string } | Array<{ msg?: string }>;
        message?: string;
      };
      message?: string;
    };
    const detail = payload.error?.detail;

    if (typeof detail === 'string') {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => item.msg)
        .filter(Boolean)
        .join(' ');
    }

    return detail?.message ??
      payload.error?.message ??
      payload.message ??
      '';
  }

  abrirModalEntrevista() {
    this.entrevistaPerfilError = '';
    this.guardandoEntrevistaPerfil = false;
    this.mostrarModalEntrevista = true;
  }

  cerrarModalEntrevista() {
    this.entrevistaPerfilError = '';
    this.guardandoEntrevistaPerfil = false;
    this.mostrarModalEntrevista = false;
  }

  guardarEntrevista(payload: EntrevistaPayload) {
    this.guardandoEntrevistaPerfil = true;
    this.entrevistaPerfilError = '';
    this.entrevistasService
      .crear(payload)
      .pipe(
        take(1),
        finalize(() => {
          this.guardandoEntrevistaPerfil = false;
        }),
      )
      .subscribe({
        next: () => {
          this.cerrarModalEntrevista();
          this.recargarEntrevistasPerfil();
        },
        error: (error) => {
          this.entrevistaPerfilError =
            obtenerMensajeError(error, 'No fue posible agendar la entrevista.');
        },
      });
  }

  abrirModalTest() {
    this.mostrarModalTest = true;
  }

  cerrarModalTest() {
    this.mostrarModalTest = false;
  }

  cambiarTab(tab: string) {
    this.tabActiva = tab as PerfilTab;
  }

  volver() {
    this.router.navigate([this.esAutoservicio ? '/portal-candidato' : '/candidatos']);
  }

  private cargarPerfilM3() {
    this.perfilCargado = false;

    const candidatoId = this.route.snapshot.paramMap.get('id');
    const perfil$ = this.esAutoservicio
      ? this.candidatosService.obtenerMiPerfilCompleto()
      : this.candidatosService.obtenerPerfilCompleto(candidatoId ?? '');
    const solicitudes$ = this.esAutoservicio
      ? this.candidatosService.listarMisSolicitudes()
      : this.candidatosService.listarSolicitudes(candidatoId ?? '');
    const entrevistas$ = this.esAutoservicio
      ? this.entrevistasService.listarMisEntrevistas()
      : this.entrevistasService.listarPorCandidato(candidatoId ?? '');
    const idiomas$ = this.esAutoservicio
      ? this.candidatosService.listarMisIdiomas()
      : this.candidatosService.listarIdiomas(candidatoId ?? '');
    const evaluacionesTecnicas$: Observable<Array<AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi>> = this.esAutoservicio
      ? this.cuestionariosService.listarMisCuestionarios()
      : this.cuestionariosService.listarAsignacionesCandidato(candidatoId ?? '');

    if (!this.esAutoservicio && !candidatoId) {
      this.perfilCargado = true;
      return;
    }

    // Integracion interna M3:
    // - Admin: GET /candidatos/{id}/perfil-completo + GET /candidatos/{id}/solicitudes.
    // - Portal: GET /candidatos/me/perfil-completo + GET /candidatos/me/solicitudes.
    // Si una llamada falla, el bloque asociado se muestra vacío y el resto del perfil sigue disponible.
    forkJoin({
      perfil: perfil$.pipe(timeout(6000), catchError((error) => {
        console.info('Perfil M3 no disponible.', error);
        return of(null);
      })),
      solicitudes: solicitudes$.pipe(timeout(6000), catchError((error) => {
        console.info('Solicitudes del candidato no disponibles.', error);
        return of([] as PostulacionCandidatoApi[]);
      })),
      solicitudesCatalogo: this.solicitudesService.listar().pipe(timeout(8000), catchError((error) => {
        console.info('Catalogo de solicitudes no disponible para perfil candidato.', error);
        return of([] as SolicitudResumen[]);
      })),
      cuestionariosCatalogo: this.cuestionariosService.listarCuestionarios().pipe(timeout(8000), catchError((error) => {
        console.info('Cuestionarios no disponibles para evaluaciones tecnicas.', error);
        return of([] as CuestionarioApi[]);
      })),
      estadosSolicitudCandidato: this.catalogosService.listarEstadosSolicitudCandidatoSeguro(),
      motivosRechazo: this.catalogosService.listarMotivosRechazoSeguro(),
      resultadosEvaluacion: this.catalogosService.listarNombresResultado().pipe(timeout(4000), catchError((error) => {
        console.info('Resultados de entrevista no disponibles para evaluaciones.', error);
        return of([] as NombreResultadoCatalogoApi[]);
      })),
      disponibilidades: this.catalogosService.listarDisponibilidadesSeguro(),
      cargos: this.catalogosService.listarCatalogoSeguro<CargoCatalogoApi>('cargos'),
      empresas: this.clientesService.listarEmpresas().pipe(timeout(4000), catchError((error) => {
        console.info('Empresas no disponibles para experiencias del candidato.', error);
        return of([] as EmpresaApi[]);
      })),
      habilidadesCatalogo: this.catalogosService.listarHabilidadesSeguro(),
      nivelesHabilidad: this.catalogosService.listarNivelesHabilidadSeguro(),
      instituciones: this.catalogosService.listarCatalogoSeguro<InstitucionCatalogoApi>('instituciones'),
      carreras: this.catalogosService.listarCarrerasSeguro(),
      nivelesEducacionales: this.catalogosService.listarNivelesEducacionalesSeguro(),
      comunas: this.catalogosService.listarComunasSeguro(),
      entrevistas: entrevistas$.pipe(timeout(6000), catchError((error) => {
        console.info('Entrevistas del candidato no disponibles; se muestra resumen sin próxima entrevista.', error);
        return of([] as EntrevistaApi[]);
      })),
      evaluacionesTecnicas: evaluacionesTecnicas$.pipe(timeout(8000), catchError((error) => {
        console.info('Evaluaciones tecnicas del candidato no disponibles.', error);
        return of([] as Array<AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi>);
      })),
      idiomas: idiomas$.pipe(timeout(6000), catchError((error) => {
        console.info('Idiomas del candidato no disponibles; se muestra sin idiomas informados.', error);
        return of([] as IdiomaCandidatoApi[]);
      })),
    })
      .pipe(
        take(1),
        finalize(() => {
          this.perfilCargado = true;
        }),
      )
      .subscribe({
        next: ({ perfil, solicitudes, solicitudesCatalogo, cuestionariosCatalogo, estadosSolicitudCandidato, motivosRechazo, resultadosEvaluacion, disponibilidades, cargos, empresas, habilidadesCatalogo, nivelesHabilidad, instituciones, carreras, nivelesEducacionales, comunas, entrevistas, evaluacionesTecnicas, idiomas }) => {
        this.solicitudesCatalogoPerfil =
          solicitudesCatalogo;
        this.estadosPostulacionPerfil =
          estadosSolicitudCandidato
            .map((estado) => estado.essc_nombre?.trim() ?? '')
            .filter(Boolean);
        this.estadosPostulacionPorNombre = new Map(
          estadosSolicitudCandidato
            .filter((estado) => Boolean(estado.essc_nombre?.trim()))
            .map((estado) => [
              this.normalizarTexto(estado.essc_nombre ?? ''),
              estado.essc_id,
            ]),
        );
        this.resultadosEvaluacion = resultadosEvaluacion;
        this.motivosRechazo = motivosRechazo;
        this.disponibilidadesPorNombre = new Map(
          disponibilidades
            .filter((disponibilidad) => Boolean(disponibilidad.disp_nombre?.trim()))
            .map((disponibilidad) => [
              this.normalizarTexto(disponibilidad.disp_nombre ?? ''),
              disponibilidad.disp_id,
            ]),
        );
        const catalogosPerfil = this.mapearCatalogosPerfilM3({
          cargos,
          empresas,
          habilidades: habilidadesCatalogo,
          nivelesHabilidad,
          instituciones,
          carreras,
          nivelesEducacionales,
          comunas,
        });

        if (perfil) {
          this.candidato = this.mapearPerfilM3(perfil, solicitudes, solicitudesCatalogo, disponibilidades, idiomas, catalogosPerfil);
          this.experiencias = this.mapearExperienciasM3(perfil.experiencias ?? [], catalogosPerfil, perfil.habilidades ?? []);
          this.estudios = this.mapearEstudiosM3(perfil.estudios ?? [], catalogosPerfil);
          this.habilidadesComparadas = this.mapearHabilidadesM3(perfil.habilidades ?? [], catalogosPerfil);
        }

        this.postulaciones = this.mapearPostulacionesM3(
          solicitudes,
          solicitudesCatalogo,
          estadosSolicitudCandidato,
        );
        this.postulaciones = this.combinarPostulacionesPerfil(
          this.postulaciones,
          this.postulacionesDesdeQueryParams(),
        );
        this.postulacionSeleccionadaId =
          this.resolverPostulacionInicial() ??
          this.resolverPostulacionMasReciente() ??
          '';
        this.aplicarContextoPostulacion(this.postulacionSeleccionadaId);

        this.proximaEntrevista = this.mapearProximaEntrevistaM5(
          entrevistas,
          solicitudesCatalogo,
        );
        this.entrevistasCandidato = entrevistas;
        this.evaluacionesTecnicas = this.mapearEvaluacionesTecnicasM4(
          evaluacionesTecnicas,
          cuestionariosCatalogo,
          solicitudesCatalogo,
        );
        },
        error: (error) => {
          console.warn('No fue posible cargar el perfil completo.', error);
          this.perfilCargado = true;
        },
      });
  }

  private get esAutoservicio() {
    return Boolean(this.route.snapshot.data['autoservicio']);
  }

  private mapearCatalogosPerfilM3(catalogos: {
    cargos: CargoCatalogoApi[];
    empresas: EmpresaApi[];
    habilidades: HabilidadCatalogoApi[];
    nivelesHabilidad: NivelHabilidadCatalogoApi[];
    instituciones: InstitucionCatalogoApi[];
    carreras: CarreraCatalogoApi[];
    nivelesEducacionales: NivelEducacionalCatalogoApi[];
    comunas: ComunaCatalogoApi[];
  }): CatalogosPerfilM3 {
    return {
      cargos: new Map(catalogos.cargos.map((cargo) => [cargo.crgo_id, cargo.crgo_nombre ?? 'Cargo sin nombre'])),
      empresas: new Map(catalogos.empresas.map((empresa) => [empresa.emp_id, empresa.emp_nombre ?? 'Empresa sin nombre'])),
      habilidades: new Map(catalogos.habilidades.map((habilidad) => [habilidad.hab_id, habilidad.hab_nombre ?? 'Habilidad sin nombre'])),
      nivelesHabilidad: new Map(catalogos.nivelesHabilidad.map((nivel) => [nivel.nvhb_id, nivel.nvhb_nombre ?? 'Sin nivel'])),
      instituciones: new Map(catalogos.instituciones.map((institucion) => [institucion.inst_id, institucion.inst_nombre ?? 'Institucion sin nombre'])),
      carreras: new Map(catalogos.carreras.map((carrera) => [carrera.crra_id, carrera.crra_nombre ?? 'Estudio sin titulo'])),
      nivelesEducacionales: new Map(catalogos.nivelesEducacionales.map((nivel) => [nivel.nved_id, nivel.nved_nombre ?? 'Nivel sin nombre'])),
      comunas: new Map(catalogos.comunas.map((comuna) => [comuna.com_id, comuna.com_nombre ?? 'Sin comuna'])),
    };
  }

  private mapearPerfilM3(
    perfil: CandidatoPerfilCompletoApi,
    solicitudes: PostulacionCandidatoApi[],
    solicitudesCatalogo: SolicitudResumen[],
    disponibilidades: { disp_id: number; disp_nombre: string | null }[],
    idiomas: IdiomaCandidatoApi[],
    catalogos: CatalogosPerfilM3,
  ): CandidatoPerfil {
    // Integracion interna M3: transforma cand_* + bloques anidados al modelo visual del perfil.
    const nombre = [
      perfil.cand_nombres,
      perfil.cand_apellido_paterno,
      perfil.cand_apellido_materno,
    ]
      .filter(Boolean)
      .join(' ') || 'Candidato sin nombre';
    const primeraSolicitud = this.postulacionMasRecienteApi(solicitudes);
    const solicitudResumen = primeraSolicitud
      ? this.solicitudResumenPorId(solicitudesCatalogo, primeraSolicitud.slcd_solicitud_id)
      : null;
    const disponibilidadNombre =
      disponibilidades.find(
        (disponibilidad) =>
          disponibilidad.disp_id === perfil.cand_disponibilidad_id,
      )?.disp_nombre;
    const direccion = perfil.direccion;
    const comuna =
      direccion?.drcd_comuna_id
        ? catalogos.comunas.get(direccion.drcd_comuna_id)
        : null;

    return {
      ...this.candidato,
      idSolicitud: primeraSolicitud
        ? this.normalizarCodigoSolicitud(
            solicitudResumen?.codigo,
            primeraSolicitud.slcd_solicitud_id,
          )
        : '',
      match: this.normalizarNumero(primeraSolicitud?.slcd_puntaje_compatibilidad) ?? null,
      nombre,
      correo: perfil.cand_email ?? 'Sin correo',
      telefono: perfil.cand_telefono ?? '',
      cargo: solicitudResumen?.cargo ?? perfil.cand_titulo ?? this.candidato.cargo,
      estado: this.candidato.estado,
      disponibilidad: disponibilidadNombre ?? this.candidato.disponibilidad,
      renta: primeraSolicitud?.slcd_pretension_renta ?? this.candidato.renta,
      rut: this.formatearRut(perfil.cand_rut_sin_dv, perfil.cand_dv) ?? this.candidato.rut,
      fechaNacimiento: this.formatearFecha(perfil.cand_fecha_nacimiento) || this.candidato.fechaNacimiento,
      fechaRegistro: this.formatearFecha(perfil.cand_fecha_creacion) || this.candidato.fechaRegistro,
      tituloProfesional: perfil.cand_titulo ?? this.candidato.tituloProfesional,
      estadoUsuario: perfil.cand_estado_usuario_id === 1 ? 'Activo' : this.candidato.estadoUsuario,
      resumenProfesional: perfil.cand_resumen_profesional ?? this.candidato.resumenProfesional,
      urlPerfil: extraerLinkedinUrl(this.normalizarCampoUrls(perfil.cand_url_1)) ?? '',
      enlaces: this.extraerEnlacesPerfil(perfil.cand_url_1),
      idiomas: this.mapearIdiomasM3(idiomas),
      comuna: comuna ?? this.candidato.comuna,
      direccion: [direccion?.drcd_calle, direccion?.drcd_numero, direccion?.drcd_dpto_oficina]
        .filter(Boolean)
        .join(' ') || this.candidato.direccion,
    };
  }

  private mapearExperienciasM3(
    experiencias: ExperienciaCandidatoApi[],
    catalogos: CatalogosPerfilM3,
    habilidadesCandidato: HabilidadCandidatoApi[],
  ): ExperienciaPerfil[] {
    if (experiencias.length === 0) {
      return this.experiencias;
    }

    const nivelesPorHabilidad = this.mapearNivelesPorHabilidadM3(
      habilidadesCandidato,
      catalogos,
    );

    return experiencias.map((experiencia) => ({
      empresa:
        experiencia.empresa?.emp_nombre ??
        experiencia.cdex_empresa ??
        this.nombrePorId(catalogos.empresas, experiencia.expl_empresa_id) ??
        'Empresa sin nombre',
      cargo:
        experiencia.cargo?.crgo_nombre ??
        experiencia.cdex_cargo ??
        this.nombrePorId(catalogos.cargos, experiencia.expl_cargo_id) ??
        'Cargo sin nombre',
      fecha: this.rangoFechas(
        experiencia.expl_fecha_inicio ?? experiencia.cdex_fecha_inicio,
        experiencia.expl_fecha_fin ?? experiencia.cdex_fecha_fin,
      ),
      descripcion: experiencia.expl_descripcion_funciones ?? experiencia.cdex_descripcion ?? 'Sin descripción registrada.',
      tags: this.mapearTagsExperienciaM3(
        experiencia.habilidades_ids ?? [],
        catalogos,
        nivelesPorHabilidad,
      ),
    }));
  }

  private mapearNivelesPorHabilidadM3(
    habilidades: HabilidadCandidatoApi[],
    catalogos: CatalogosPerfilM3,
  ) {
    return new Map(
      habilidades
        .map((habilidad): [number, string] | null => {
          if (habilidad.cdhb_habilidad_id == null) {
            return null;
          }

          const nivel =
            habilidad.nivel_habilidad?.nvhb_nombre ??
            this.nombrePorId(catalogos.nivelesHabilidad, habilidad.cdhb_nivel_habilidad_id) ??
            '';

          return [habilidad.cdhb_habilidad_id, nivel];
        })
        .filter((item): item is [number, string] => Boolean(item)),
    );
  }

  private mapearTagsExperienciaM3(
    habilidadesIds: number[],
    catalogos: CatalogosPerfilM3,
    nivelesPorHabilidad: Map<number, string>,
  ) {
    return habilidadesIds
      .map((habilidadId) => {
        const habilidad =
          this.nombrePorId(catalogos.habilidades, habilidadId);
        const nivel =
          nivelesPorHabilidad.get(habilidadId);

        if (!habilidad) {
          return null;
        }

        return nivel
          ? `${habilidad} · ${nivel}`
          : habilidad;
      })
      .filter((tag): tag is string => Boolean(tag));
  }

  private mapearEstudiosM3(
    estudios: EstudioCandidatoApi[],
    catalogos: CatalogosPerfilM3,
  ): EstudioPerfil[] {
    if (estudios.length === 0) {
      return this.estudios;
    }

    return estudios.map((estudio) => ({
      titulo:
        estudio.carrera?.crra_nombre ??
        this.nombrePorId(catalogos.carreras, estudio.etcd_carrera_id ?? estudio.cdet_carrera_id) ??
        estudio.nivel_educacional?.nved_nombre ??
        this.nombrePorId(catalogos.nivelesEducacionales, estudio.etcd_nivel_educacional_id ?? estudio.cdet_nivel_educacional_id) ??
        'Estudio sin titulo',
      institucion:
        estudio.institucion?.inst_nombre ??
        this.nombrePorId(catalogos.instituciones, estudio.etcd_institucion_id ?? estudio.cdet_institucion_id) ??
        'Institucion sin nombre',
      fecha: this.rangoFechas(
        estudio.etcd_fecha_inicio ?? estudio.cdet_fecha_inicio,
        estudio.etcd_fecha_fin ?? estudio.cdet_fecha_fin,
      ),
    }));
  }

  private mapearHabilidadesM3(
    habilidades: HabilidadCandidatoApi[],
    catalogos: CatalogosPerfilM3,
  ): HabilidadComparada[] {
    if (habilidades.length === 0) {
      return this.habilidadesComparadas;
    }

    return habilidades.map((habilidad) => {
      const nombre =
        habilidad.habilidad?.hab_nombre ??
        this.nombrePorId(catalogos.habilidades, habilidad.cdhb_habilidad_id) ??
        `Habilidad ${habilidad.cdhb_habilidad_id ?? ''}`.trim();
      const nivel =
        habilidad.nivel_habilidad?.nvhb_nombre ??
        this.nombrePorId(catalogos.nivelesHabilidad, habilidad.cdhb_nivel_habilidad_id) ??
        'Sin nivel';
      const anios = String(habilidad.cdhb_anios_experiencia ?? 0);
      return [nombre, nivel, anios, nombre, nivel, anios, '100%', 'success'];
    });
  }

  private nombrePorId(
    nombres: Map<number, string>,
    id?: number | null,
  ) {
    return id == null
      ? undefined
      : nombres.get(id);
  }

  private mapearIdiomasM3(
    idiomas: IdiomaCandidatoApi[],
  ) {
    return idiomas
      .map((item) => {
        const idioma =
          item.idioma?.idio_nombre?.trim();
        const nivel =
          item.nivel_idioma?.nvid_nombre?.trim() ??
          item.nivel_idioma?.nvid_grupo?.trim();

        if (!idioma && !nivel) {
          return '';
        }

        if (!idioma) {
          return nivel ?? '';
        }

        return nivel
          ? `${idioma} (${nivel})`
          : idioma;
      })
      .filter(Boolean);
  }

  private mapearPostulacionesM3(
    solicitudes: PostulacionCandidatoApi[],
    solicitudesCatalogo: SolicitudResumen[],
    estadosSolicitudCandidato: { essc_id: number; essc_nombre: string | null }[],
  ): PostulacionPerfil[] {
    this.contextoPostulaciones = new Map();

    const estadosPorId = new Map(
      estadosSolicitudCandidato.map((estado) => [
        estado.essc_id,
        estado.essc_nombre ?? 'Sin estado',
      ]),
    );

    return [...solicitudes]
      .sort(
        (a, b) =>
          this.fechaTimestamp(b.slcd_fecha_postulacion) -
          this.fechaTimestamp(a.slcd_fecha_postulacion),
      )
      .map((postulacion) => {
        const solicitud =
          this.solicitudResumenPorId(
            solicitudesCatalogo,
            postulacion.slcd_solicitud_id,
          );

        const clienteEmpresa =
          solicitud
            ? this.formatearClienteEmpresa(solicitud)
            : 'Solicitud';

        const codigo = this.normalizarCodigoSolicitud(
            solicitud?.codigo,
            postulacion.slcd_solicitud_id,
          );
        const cargo = solicitud?.cargo ??
          `Solicitud ${postulacion.slcd_solicitud_id}`;
        const estado = estadosPorId.get(
          postulacion.slcd_estado_solicitud_candidato_id ?? 0,
        ) ?? 'Sin estado';
        const match = this.normalizarNumero(
          postulacion.slcd_puntaje_compatibilidad,
        ) ?? null;
        const renta = postulacion.slcd_pretension_renta ?? 0;

        this.contextoPostulaciones.set(codigo, {
          postulacionId: postulacion.slcd_id,
          solicitudId: postulacion.slcd_solicitud_id,
          idSolicitud: codigo,
          cargo,
          estado,
          estadoId: postulacion.slcd_estado_solicitud_candidato_id,
          match,
          renta,
          fechaPostulacionTimestamp: this.fechaTimestamp(
            postulacion.slcd_fecha_postulacion,
          ),
        });

        return [
          codigo,
          clienteEmpresa,
          cargo,
          this.formatearFecha(
            postulacion.slcd_fecha_postulacion,
          ) || 'Sin fecha',
          estado,
        ];
      });
  }

  private aplicarContextoPostulacion(id: string) {
    const contexto =
      this.contextoPostulaciones.get(id);

    if (!contexto) {
      return;
    }

    this.candidato = {
      ...this.candidato,
      idSolicitud: contexto.idSolicitud,
      cargo: contexto.cargo,
      estado: contexto.estado,
      match: contexto.match,
      renta: contexto.renta,
    };
  }

  private postulacionesDesdeQueryParams(): PostulacionPerfil[] {
    const valor =
      this.route.snapshot.queryParamMap.get('postulaciones');

    if (!valor) {
      return [];
    }

    try {
      const items = JSON.parse(valor) as Array<{
        idPostulacion?: number | string;
        idSolicitud?: number | string;
        codigo?: string;
        clienteEmpresa?: string;
        cargo?: string;
        fecha?: string;
        estado?: string;
        match?: number;
        renta?: number;
      }>;

      return items
        .map((item) => {
          if (!item.codigo?.trim() && !item.idSolicitud) {
            return null;
          }

          const codigo =
            this.normalizarCodigoSolicitud(
              item.codigo,
              Number(item.idSolicitud) || null,
            );
          const idPostulacion =
            Number(item.idPostulacion) ||
            (
              this.normalizarCodigoSolicitud(
                this.route.snapshot.queryParamMap.get('idSolicitud'),
              ) === codigo
                ? Number(this.route.snapshot.queryParamMap.get('idPostulacion'))
                : 0
            ) ||
            undefined;

          this.contextoPostulaciones.set(codigo, {
            postulacionId: idPostulacion,
            solicitudId: Number(item.idSolicitud) || undefined,
            idSolicitud: codigo,
            cargo: item.cargo || 'Sin cargo',
            estado: item.estado || 'Sin estado',
            match: item.match == null ? null : Number(item.match),
            renta: Number(item.renta ?? 0),
            fechaPostulacionTimestamp: this.fechaTimestamp(item.fecha),
          });

          return [
            codigo,
            item.clienteEmpresa || 'Solicitud',
            item.cargo || 'Sin cargo',
            item.fecha || 'Sin fecha',
            item.estado || 'Sin estado',
          ] as PostulacionPerfil;
        })
        .filter(
          (postulacion): postulacion is PostulacionPerfil =>
            Boolean(postulacion),
        );
    } catch {
      return [];
    }
  }

  private combinarPostulacionesPerfil(
    principales: PostulacionPerfil[],
    respaldo: PostulacionPerfil[],
  ) {
    const vistas = new Map<string, PostulacionPerfil>();

    respaldo.forEach((postulacion) => {
      vistas.set(postulacion[0], postulacion);
    });

    principales.forEach((postulacion) => {
      vistas.set(postulacion[0], postulacion);
    });

    return Array.from(vistas.values());
  }

  private resolverPostulacionMasReciente() {
    let seleccionada: string | null = null;
    let fechaMayor = Number.NEGATIVE_INFINITY;

    this.contextoPostulaciones.forEach((contexto, codigo) => {
      if (contexto.fechaPostulacionTimestamp > fechaMayor) {
        fechaMayor = contexto.fechaPostulacionTimestamp;
        seleccionada = codigo;
      }
    });

    return seleccionada;
  }

  private postulacionMasRecienteApi(
    solicitudes: PostulacionCandidatoApi[],
  ) {
    return [...solicitudes].sort(
      (a, b) =>
        this.fechaTimestamp(b.slcd_fecha_postulacion) -
        this.fechaTimestamp(a.slcd_fecha_postulacion),
    )[0];
  }

  private resolverPostulacionInicial() {
    const idSolicitudParam =
      this.route.snapshot.queryParamMap.get('idSolicitud');

    if (!idSolicitudParam) {
      return null;
    }

    const normalizado =
      this.normalizarCodigoSolicitud(idSolicitudParam);

    return this.contextoPostulaciones.has(normalizado)
      ? normalizado
      : null;
  }

  private mapearProximaEntrevistaM5(
    entrevistas: EntrevistaApi[],
    solicitudesCatalogo: SolicitudResumen[],
  ): EntrevistaPerfilResumen | null {
    const ahora = Date.now();

    const proxima = entrevistas
      .filter((entrevista) =>
        !this.esEstadoEntrevistaTerminal(
          this.nombreEstadoEntrevista(entrevista),
        ) &&
        this.fechaTimestamp(entrevista.fecha_hora_inicio) >= ahora,
      )
      .sort(
        (a, b) =>
          this.fechaTimestamp(a.fecha_hora_inicio) -
          this.fechaTimestamp(b.fecha_hora_inicio),
      )[0];

    if (!proxima) {
      return null;
    }

    const solicitud =
      this.solicitudResumenPorId(
        solicitudesCatalogo,
        proxima.solicitud_id,
      );

    return {
      titulo:
        proxima.titulo_evento ||
        solicitud?.cargo ||
        'Entrevista programada',
      solicitud:
        this.normalizarCodigoSolicitud(
          proxima.solicitud_codigo ??
            solicitud?.codigo,
          proxima.solicitud_id,
        ),
      clienteEmpresa:
        solicitud
          ? this.formatearClienteEmpresa(solicitud)
          : 'Sin cliente',
      fecha:
        this.formatearFecha(
          proxima.fecha_hora_inicio,
        ) || 'Sin fecha',
      hora:
        this.formatearHora(
          proxima.fecha_hora_inicio,
        ) || 'Sin hora',
      estado:
        this.nombreEstadoEntrevista(proxima),
    };
  }

  private mapearEntrevistasProcesoM5(
    entrevistas: EntrevistaApi[],
  ): EtapaSeleccion[] {
    return [...entrevistas]
      .sort(
        (a, b) =>
          this.fechaTimestamp(a.fecha_hora_inicio) -
          this.fechaTimestamp(b.fecha_hora_inicio),
      )
      .map((entrevista) => ({
        id: String(entrevista.entrevista_id),
        solicitud: this.codigoEntrevista(entrevista),
        etapa: this.tituloEntrevista(entrevista),
        estado: this.nombreEstadoEntrevista(entrevista),
        fecha:
          this.formatearFecha(entrevista.fecha_hora_inicio) ||
          'Sin fecha',
        entrevistador:
          this.formatearEntrevistadores(entrevista) ||
          'Sin entrevistador asignado',
        tipoEntrevista:
          this.formatearTipoEntrevista(entrevista),
        tipos:
          entrevista.tipos?.map((tipo) => ({
            id: tipo.tipo_entrevista_id,
            nombre: tipo.nombre,
            entrevistadoresIds:
              tipo.entrevistadores?.map(
                (entrevistador) => entrevistador.usuario_id,
              ) ?? [],
          })) ?? [],
        evaluaciones:
          entrevista.evaluaciones?.map((evaluacion) => ({
            id: evaluacion.evaluacion_id,
            tipoId: evaluacion.tipo_entrevista_id,
            tipoNombre: evaluacion.tipo_entrevista_nombre,
            usuarioId: evaluacion.usuario_id,
            usuarioNombre: evaluacion.usuario_nombre,
            resultadoId: evaluacion.resultado_id,
            resultado: evaluacion.resultado_nombre,
            observacion: evaluacion.observacion,
          })) ?? [],
        observacionEntrevista:
          this.observacionEvaluacionUsuarioActual(entrevista) ?? '',
        observaciones:
          this.formatearObservacionesEntrevista(entrevista),
        resultadoEntrevista:
          this.formatearResultadoEntrevista(entrevista),
      }));
  }

  private tituloEntrevista(
    entrevista: EntrevistaApi,
  ) {
    if (entrevista.titulo_evento?.trim()) {
      return entrevista.titulo_evento.trim();
    }

    const tipos = entrevista.tipos
      ?.map((tipo) => tipo.nombre)
      .filter(Boolean);

    return tipos?.join(' / ') ||
      'Entrevista agendada';
  }

  private formatearEntrevistadores(
    entrevista: EntrevistaApi,
  ) {
    const nombres = entrevista.tipos
      ?.flatMap((tipo) => tipo.entrevistadores ?? [])
      .map((entrevistador) =>
        [
          entrevistador.nombres,
          entrevistador.apellido_paterno,
        ]
          .filter(Boolean)
          .join(' '),
      )
      .filter(Boolean);

    return Array.from(new Set(nombres)).join(', ');
  }

  private formatearTipoEntrevista(
    entrevista: EntrevistaApi,
  ) {
    const tipos = [
      ...(entrevista.tipos
        ?.map((tipo) => tipo.nombre)
        .filter(Boolean) ?? []),
      ...(entrevista.evaluaciones
        ?.map((evaluacion) => evaluacion.tipo_entrevista_nombre)
        .filter(Boolean) ?? []),
    ];

    if (tipos.length) {
      return Array.from(new Set(tipos)).join(', ');
    }

    return 'Sin tipo registrado';
  }

  private mapearEvaluacionesTecnicasM4(
    asignaciones: Array<AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi>,
    cuestionarios: CuestionarioApi[],
    solicitudesCatalogo: SolicitudResumen[],
  ): EvaluacionTecnicaPerfil[] {
    const cuestionariosPorId = new Map(
      cuestionarios.map((cuestionario) => [
        cuestionario.cues_id,
        cuestionario,
      ]),
    );

    return [...asignaciones]
      .sort(
        (a, b) =>
          this.fechaTimestamp(this.fechaAsignacionTecnica(b)) -
          this.fechaTimestamp(this.fechaAsignacionTecnica(a)),
      )
      .map((asignacion) => {
        const cuestionarioId =
          this.idCuestionarioAsignacion(asignacion);
        const cuestionario =
          cuestionariosPorId.get(cuestionarioId);
        const solicitudId =
          this.idSolicitudAsignacion(asignacion) ??
          cuestionario?.cues_solicitud_id;
        const solicitud =
          this.solicitudResumenPorId(
            solicitudesCatalogo,
            solicitudId,
          );
        const codigoSolicitud =
          this.normalizarCodigoSolicitud(
            this.codigoSolicitudAsignacion(asignacion) ??
              cuestionario?.solicitud_codigo ??
              solicitud?.codigo,
            solicitudId,
          );

        return [
          this.nombreCuestionarioAsignacion(asignacion) ||
            cuestionario?.cues_nombre ||
            `Cuestionario ${cuestionarioId}`,
          this.estadoAsignacionTecnica(asignacion),
          codigoSolicitud,
          `${this.duracionAsignacionTecnica(asignacion) || cuestionario?.duracion_minutos || 0} min`,
          this.resultadoAsignacionTecnica(asignacion),
        ];
      });
  }

  private idCuestionarioAsignacion(
    asignacion: AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi,
  ) {
    return 'cdcu_cuestionario_id' in asignacion
      ? asignacion.cdcu_cuestionario_id
      : asignacion.cuestionario_id;
  }

  private idSolicitudAsignacion(
    asignacion: AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi,
  ) {
    return 'solicitud_id' in asignacion
      ? asignacion.solicitud_id
      : undefined;
  }

  private codigoSolicitudAsignacion(
    asignacion: AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi,
  ) {
    return 'solicitud_codigo' in asignacion
      ? asignacion.solicitud_codigo
      : undefined;
  }

  private nombreCuestionarioAsignacion(
    asignacion: AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi,
  ) {
    return asignacion.cuestionario_nombre?.trim() ?? '';
  }

  private estadoAsignacionTecnica(
    asignacion: AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi,
  ) {
    return 'estado_nombre' in asignacion
      ? asignacion.estado_nombre
      : asignacion.estado;
  }

  private fechaAsignacionTecnica(
    asignacion: AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi,
  ) {
    return 'cdcu_fecha_asignacion' in asignacion
      ? asignacion.cdcu_fecha_asignacion
      : asignacion.fecha_asignacion;
  }

  private duracionAsignacionTecnica(
    asignacion: AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi,
  ) {
    return asignacion.duracion_minutos;
  }

  private resultadoAsignacionTecnica(
    asignacion: AsignacionCuestionarioApi | AsignacionCuestionarioCandidatoApi,
  ) {
    const aprobado = 'cdcu_aprobado' in asignacion
      ? asignacion.cdcu_aprobado
      : 'aprobado' in asignacion
        ? asignacion.aprobado
        : null;
    const porcentaje = this.normalizarNumero(
      'cdcu_porcentaje_obtenido' in asignacion
        ? asignacion.cdcu_porcentaje_obtenido
        : 'porcentaje_obtenido' in asignacion
          ? asignacion.porcentaje_obtenido
          : null,
    );

    if (aprobado != null) {
      const resultado = aprobado ? 'Aprobado' : 'No aprobado';
      return porcentaje == null
        ? resultado
        : `${resultado} (${porcentaje}%)`;
    }

    return porcentaje == null
      ? 'Pendiente'
      : `${porcentaje}%`;
  }

  private formatearObservacionesEntrevista(
    entrevista: EntrevistaApi,
  ) {
    const observaciones = (entrevista.evaluaciones
      ?.map((evaluacion) => evaluacion.observacion)
      .filter(Boolean) ?? [])
      .filter((valor): valor is string =>
        Boolean(valor?.trim()),
      );

    return observaciones.length > 0
      ? observaciones.join(' ')
      : 'Sin observaciones de evaluación registradas.';
  }

  private formatearResultadoEntrevista(
    entrevista: EntrevistaApi,
  ) {
    const evaluaciones = entrevista.evaluaciones ?? [];
    const tipos = entrevista.tipos ?? [];

    if (
      evaluaciones.length === 0 &&
      tipos.length === 0
    ) {
      return 'Sin resultado registrado';
    }

    if (tipos.length === 0) {
      return evaluaciones
        .map((evaluacion) => {
          const tipo = evaluacion.tipo_entrevista_nombre?.trim() ||
            'Sin tipo';
          return `${tipo}: ${evaluacion.resultado_nombre}`;
        })
        .join(' | ');
    }

    return tipos
      .map((tipo) => {
        const evaluacionesTipo = evaluaciones.filter(
          (evaluacion) =>
            evaluacion.tipo_entrevista_id === tipo.tipo_entrevista_id,
        );

        // Integración M5: pendiente por área significa evaluación ausente para ese tipo.
        if (evaluacionesTipo.length === 0) {
          return `${tipo.nombre}: Pendiente`;
        }

        return `${tipo.nombre}: ${evaluacionesTipo
          .map((evaluacion) => evaluacion.resultado_nombre)
          .join(', ')}`;
      })
      .join(' | ');
  }

  private observacionEvaluacionUsuarioActual(
    entrevista: EntrevistaApi,
  ) {
    const usuarioId = this.authService.obtenerUsuarioId();
    const evaluaciones = entrevista.evaluaciones ?? [];
    const evaluacion = usuarioId
      ? evaluaciones.find((item) => item.usuario_id === usuarioId)
      : evaluaciones[0];

    return evaluacion?.observacion?.trim() ?? '';
  }

  private codigoEntrevista(
    entrevista: EntrevistaApi,
  ) {
    return this.normalizarCodigoSolicitud(
      entrevista.solicitud_codigo,
      entrevista.solicitud_id,
    );
  }

  private nombreEstadoEntrevista(
    entrevista: EntrevistaApi,
  ) {
    return entrevista.estado_nombre ??
      entrevista.estado ??
      'Sin estado';
  }

  private nombreEstadoEntrevistaPerfil(
    estado: string,
  ) {
    return this.normalizarTexto(estado);
  }

  private esEstadoEntrevistaTerminal(
    estado: string,
  ) {
    return [
      'cancelada',
      'cancelado',
      'realizada',
      'realizado',
      'no-asistio',
    ].includes(
      this.normalizarTexto(estado),
    );
  }

  private solicitudResumenPorId(
    solicitudes: SolicitudResumen[],
    solicitudId?: number | null,
  ) {
    return solicitudes.find(
      (solicitud) =>
        Number(solicitud.id) ===
        Number(solicitudId),
    ) ?? null;
  }

  private formatearClienteEmpresa(
    solicitud: SolicitudResumen,
  ) {
    const cliente =
      solicitud.cliente?.trim();

    const empresa =
      solicitud.empresaCliente?.trim();

    if (
      empresa &&
      cliente &&
      empresa !== cliente &&
      empresa !== 'Sin empresa cliente'
    ) {
      return `${cliente} / ${empresa}`;
    }

    return cliente || empresa || 'Sin cliente';
  }

  private extraerEnlacesPerfil(
    valor?: string | string[] | null,
  ) {
    const urls = this.normalizarCampoUrls(valor)
      .split(/[;\n,]+/)
      .map((url) => url.trim())
      .filter(Boolean);

    return Array.from(new Set(urls))
      .map((url) => {
        const href = /^https?:\/\//i.test(url)
          ? url
          : `https://${url}`;
        const tipo = this.tipoEnlacePerfil(href);

        return {
          tipo,
          url: href,
          texto: this.textoEnlacePerfil(href),
        };
      });
  }

  private normalizarCampoUrls(
    valor?: string | string[] | null,
  ) {
    if (Array.isArray(valor)) {
      return valor.join(';');
    }

    return valor ?? '';
  }

  private tipoEnlacePerfil(url: string) {
    const normalizada =
      url.toLowerCase();

    if (normalizada.includes('linkedin.com')) {
      return 'LinkedIn';
    }

    if (normalizada.includes('github.com')) {
      return 'GitHub';
    }

    if (normalizada.includes('gitlab.com')) {
      return 'GitLab';
    }

    if (
      normalizada.includes('behance.net') ||
      normalizada.includes('dribbble.com') ||
      normalizada.includes('portfolio')
    ) {
      return 'Portafolio';
    }

    return 'Web';
  }

  private textoEnlacePerfil(url: string) {
    try {
      const parsed = new URL(url);
      return parsed.hostname.replace(/^www\./, '') +
        parsed.pathname.replace(/\/$/, '');
    } catch {
      return url;
    }
  }

  private codigoSolicitudFallback(
    solicitudId?: number | null,
  ) {
    return solicitudId
      ? `SOL-${String(solicitudId).padStart(6, '0')}`
      : '';
  }

  private normalizarCodigoSolicitud(
    codigo?: string | null,
    solicitudId?: number | null,
  ) {
    const limpio = codigo?.trim();

    if (!limpio) {
      return this.codigoSolicitudFallback(solicitudId);
    }

    const coincidencia = limpio.match(/^SOL-(\d+)$/i);

    if (!coincidencia) {
      return limpio;
    }

    return `SOL-${coincidencia[1].padStart(6, '0')}`;
  }

  private rangoFechas(inicio?: string | null, fin?: string | null) {
    const desde = this.formatearFecha(inicio) || 'Sin fecha';
    const hasta = this.formatearFecha(fin) || 'Actual';
    return `${desde} - ${hasta}`;
  }

  private formatearRut(rut?: number | null, dv?: number | string | null) {
    return rut == null || dv == null ? undefined : `${rut}-${dv}`;
  }

  private formatearFecha(fecha?: string | null) {
    if (!fecha) {
      return '';
    }

    const fechaNormalizada = new Date(fecha);
    return Number.isNaN(fechaNormalizada.getTime())
      ? fecha
      : new Intl.DateTimeFormat('es-CL').format(fechaNormalizada);
  }

  private formatearHora(fecha?: string | null) {
    if (!fecha) {
      return '';
    }

    const fechaNormalizada = new Date(fecha);
    return Number.isNaN(fechaNormalizada.getTime())
      ? ''
      : new Intl.DateTimeFormat('es-CL', {
          hour: '2-digit',
          minute: '2-digit',
        }).format(fechaNormalizada);
  }

  private fechaTimestamp(fecha?: string | null) {
    if (!fecha) {
      return 0;
    }

    const timestamp = new Date(fecha).getTime();
    return Number.isNaN(timestamp) ? 0 : timestamp;
  }

  private normalizarTexto(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-');
  }

  private normalizarNumero(valor?: number | string | null) {
    if (valor == null || valor === '') {
      return undefined;
    }

    const numero = Number(valor);
    return Number.isNaN(numero) ? undefined : numero;
  }
}
