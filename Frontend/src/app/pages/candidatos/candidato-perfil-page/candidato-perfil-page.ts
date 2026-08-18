import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { catchError, forkJoin, of, take, timeout } from 'rxjs';
import { CandidatoProfileTab, CandidatoProfileTabs } from '../candidato-profile-tabs/candidato-profile-tabs';
import { Button } from '../../../shared/components/button/button';
import { Modal } from '../../../shared/components/modal/modal';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { EntrevistaFormModal } from '../../entrevistas/entrevista-form-modal/entrevista-form-modal';
import { EntrevistaPayload, EntrevistasService } from '../../../services/entrevistas.service';
import {
  CandidatoPerfilCompletoApi,
  CandidatosService,
  EstudioCandidatoApi,
  ExperienciaCandidatoApi,
  HabilidadCandidatoApi,
  PostulacionCandidatoApi,
} from '../../../services/candidatos.service';
import { extraerLinkedinUrl } from '../../../shared/mappers/candidato.mapper';
import { CandidateApplicationsSection } from './components/candidate-applications-section/candidate-applications-section';
import { CandidateDocumentsSection } from './components/candidate-documents-section/candidate-documents-section';
import { CandidateEducationSection } from './components/candidate-education-section/candidate-education-section';
import { CandidateExperienceSection } from './components/candidate-experience-section/candidate-experience-section';
import { CandidateMatchSection } from './components/candidate-match-section/candidate-match-section';
import { CandidateObservationHistory } from './components/candidate-observation-history/candidate-observation-history';
import { CandidateProfileHeader } from './components/candidate-profile-header/candidate-profile-header';
import { CandidateQuickObservations } from './components/candidate-quick-observations/candidate-quick-observations';
import {
  CandidatoPerfil,
  DocumentoPerfil,
  EstudioPerfil,
  EtapaSeleccion,
  EvaluacionTecnicaPerfil,
  ExperienciaPerfil,
  HabilidadComparada,
  ObservacionPerfil,
  PerfilTab,
  PostulacionPerfil,
} from './candidato-perfil.models';

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
    CandidateObservationHistory,
    CandidateProfileHeader,
    CandidateQuickObservations,
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
  tabActiva: PerfilTab = 'postulaciones';
  postulacionSeleccionadaId = 'SOL-021';
  busquedaPostulacion = '';
  archivosDocumentos: File[] = [];
  mostrarModalObservacion = false;
  mostrarModalEntrevista = false;
  mostrarModalTest = false;
  nota = '';

  candidato: CandidatoPerfil;

  get tabs(): CandidatoProfileTab[] {
    const tabs: CandidatoProfileTab[] = [
      { id: 'experiencia', label: 'Experiencia', icon: 'briefcase' },
      { id: 'estudios', label: 'Estudios', icon: 'graduation' },
      { id: 'postulaciones', label: 'Postulaciones', icon: 'puzzle' },
      { id: 'match', label: 'Match', icon: 'users' },
      { id: 'evaluaciones', label: 'Evaluaciones técnicas', icon: 'file' },
      { id: 'observaciones', label: 'Observaciones', icon: 'list' },
    ];

    if (this.mostrarModuloDocumentos) {
      tabs.splice(5, 0, { id: 'documentos', label: 'Documentos', icon: 'file' });
    }

    return tabs;
  }

  experiencias: ExperienciaPerfil[] = [
    {
      empresa: 'TechSolutions S.A.',
      cargo: 'Desarrollador Full Stack Senior',
      fecha: 'Mar 2021 - Presente',
      descripcion:
        'Liderazgo técnico en el desarrollo de plataformas SaaS. Diseño de arquitectura en la nube usando AWS. Migración de monolito a microservicios.',
      tags: ['React', 'Node.js', 'AWS', 'PostgreSQL'],
    },
    {
      empresa: 'Cornershop',
      cargo: 'Desarrollador Full Stack',
      fecha: 'Jun 2020 - Dic 2021',
      descripcion: 'Desarrollo de APIs REST y funcionalidades frontend para aplicaciones internas.',
      tags: ['React', 'Node.js', 'Redux'],
    },
    {
      empresa: 'Bci',
      cargo: 'Desarrollador de Software',
      fecha: 'Ene 2019 - May 2020',
      descripcion: 'Construcción de módulos para banca digital e integraciones con servicios internos.',
      tags: ['JavaScript', 'Git', 'Jenkins'],
    },
  ];

  estudios: EstudioPerfil[] = [
    {
      titulo: 'Ingeniería Civil Informática',
      institucion: 'Universidad de Chile',
      fecha: '2016 - 2020',
    },
    {
      titulo: 'Técnico en Programación',
      institucion: 'Instituto Profesional AIEP',
      fecha: '2014 - 2016',
    },
  ];

  postulaciones: PostulacionPerfil[] = [
    ['SOL-021', 'Latam', 'Backend', '18/05/2025', 'En Curso'],
    ['SOL-026', 'Banco de Chile', 'Frontend', '18/05/2025', 'Cerrado'],
    ['SOL-028', 'SParta', 'QA', '18/05/2025', 'Cerrado'],
    ['SOL-029', 'Servicios Financieros', 'QA', '18/05/2025', 'En Curso'],
    ['SOL-030', 'Latam', 'Frontend', '18/05/2025', 'Cerrado'],
  ];

  readonly procesoBase: EtapaSeleccion[] = [
    {
      etapa: 'Entrevista RRHH',
      estado: 'Realizada',
      fecha: '10 Oct 2023',
      entrevistador: 'MACARENA LÓPEZ',
      resultado: 'Aprobado',
      observaciones: 'Buen perfil comunicacional, expectativas salariales alineadas.',
    },
    {
      etapa: 'Entrevista Cliente',
      estado: 'Realizada',
      fecha: '15 Oct 2023',
      entrevistador: 'Rodrigo Riquelme (PM)',
      resultado: 'Aprobado',
      observaciones: 'Preparado para avanzar.',
    },
    {
      etapa: 'Entrevista Tecnica',
      estado: 'Realizada',
      fecha: '15 Oct 2023',
      entrevistador: 'Carlos Ruiz (Líder)',
      resultado: 'Aprobado',
      observaciones: 'Sólidos conocimientos en React. Resolvió el caso práctico eficientemente.',
    },
    {
      etapa: 'Evaluaciones Técnicas',
      estado: 'Pendiente',
      fecha: 'Pendiente',
      entrevistador: 'Pendiente',
      resultado: 'Pendiente',
      observaciones: 'Code Challenge Backend pendiente de finalización.',
    },
  ];

  readonly procesosPorPostulacion: Record<string, EtapaSeleccion[]> = {
    'SOL-021': this.procesoBase,
    'SOL-026': [
      ...this.procesoBase.slice(0, 2),
      {
        etapa: 'Cierre de proceso',
        estado: 'Realizada',
        fecha: '22 Oct 2023',
        entrevistador: 'Equipo RRHH',
        resultado: 'No Aprobado',
        observaciones: 'Proceso cerrado por ajuste de presupuesto interno.',
      },
    ],
    'SOL-028': this.procesoBase.slice(0, 2),
    'SOL-029': this.procesoBase.slice(0, 3),
    'SOL-030': this.procesoBase.slice(0, 2),
  };

  habilidadesComparadas: HabilidadComparada[] = [
    ['Html', 'Junior', '4', 'Html', 'Junior', '4', '95%', 'success'],
    ['Python', 'Junior', '5', 'Python', 'Junior', '5', '95%', 'success'],
    ['Css', 'Junior', '8', 'Css', 'Junior', '8', '95%', 'success'],
    ['Java', 'Junior', '10', 'Java', 'Junior', '8', '66%', 'warning'],
    ['Angular', 'Junior', '4', 'Angular', 'Junior', '2', '20%', 'danger'],
  ];

  readonly fortalezasMatch = ['Excelente arquitectura en React y manejo de estados complejos.'];
  readonly areasMejoraMatch = ['Requiere nivelar conocimientos en el entorno backend con Node.js.'];

  readonly evaluacionesTecnicas: EvaluacionTecnicaPerfil[] = [
    ['Test Angular Junior', 'Enviado', 'SOL-021', '45 min', 'Pendiente'],
    ['Code Challenge Backend', 'Pendiente', 'SOL-021', '60 min', 'Sin enviar'],
  ];

  // Función futura oculta: lista de documentos visible solo si mostrarModuloDocumentos=true.
  readonly documentos: DocumentoPerfil[] = [
    ['CV_Juan_Perez_Gonzalez.pdf', 'Currículum', '24 oct 2024', '10:30'],
    ['Carta_de_presentacion.docx', 'Carta de presentación', '24 oct 2024', '10:36'],
    ['Certificado_Titulo_Ingenieria.pdf', 'Certificado', '24 oct 2024', '11:05'],
  ];

  readonly historialObservaciones: ObservacionPerfil[] = [
    ['18 may 2025', '10:42', 'María Fernanda López', 'Buen perfil comunicacional y expectativas alineadas con la vacante.'],
    ['16 may 2025', '16:15', 'Diego Salazar', 'Avanza con buen desempeño técnico; revisar profundidad en backend.'],
    ['24 oct 2024', '09:08', 'Sistema', 'Postulación recibida desde el portal de empleo.'],
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private entrevistasService: EntrevistasService,
    private candidatosService: CandidatosService,
  ) {
    const params = this.route.snapshot.queryParamMap;
    const tabInicial = params.get('tab') as PerfilTab | null;

    this.candidato = {
      idSolicitud: params.get('idSolicitud') || 'SOL-021',
      match: Number(params.get('match') || 78),
      nombre: params.get('nombre') || 'Juan Perez Gonzalez',
      correo: params.get('correo') || 'juan.perez@gmail.com',
      telefono: params.get('telefono') || '+56 9 1234 5678',
      cargo: params.get('cargo') || 'Senior React Developer',
      estado: params.get('estado') || 'En revision',
      disponibilidad: params.get('disponibilidad') || 'Inmediata',
      renta: Number(params.get('renta') || 2800000),
      rut: params.get('rut') || '18.123.456-7',
      fechaNacimiento: '12 may 1994',
      fechaRegistro: '24 oct 2024',
      tituloProfesional: 'Ingeniera Civil Informática',
      estadoUsuario: params.get('estadoUsuario') || 'Activo',
      resumenProfesional: 'Desarrolladora frontend con experiencia en React, TypeScript y plataformas SaaS.',
      urlPerfil: extraerLinkedinUrl(params.get('urlPerfil')) ?? '',
      comuna: 'Providencia',
      direccion: 'Av. Providencia 1234, Depto 502',
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
    return {
      idSolicitud: this.candidato.idSolicitud,
      candidato: this.candidato.nombre,
      cargo: this.candidato.cargo,
      tipo: 'RRHH',
      asunto: `Entrevista ${this.candidato.cargo}`,
    };
  }

  get matchClass() {
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

  get procesoSeleccionado() {
    return this.procesosPorPostulacion[this.postulacionSeleccionadaId] || this.procesoBase;
  }

  seleccionarPostulacion(id: string) {
    this.postulacionSeleccionadaId = id;
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

  abrirModalEntrevista() {
    this.mostrarModalEntrevista = true;
  }

  cerrarModalEntrevista() {
    this.mostrarModalEntrevista = false;
  }

  guardarEntrevista(payload: EntrevistaPayload) {
    this.entrevistasService.crear(payload).subscribe({
      next: () => {
        this.cerrarModalEntrevista();
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
    const candidatoId = this.route.snapshot.paramMap.get('id');
    const perfil$ = this.esAutoservicio
      ? this.candidatosService.obtenerMiPerfilCompleto()
      : this.candidatosService.obtenerPerfilCompleto(candidatoId ?? '');
    const solicitudes$ = this.esAutoservicio
      ? this.candidatosService.listarMisSolicitudes()
      : this.candidatosService.listarSolicitudes(candidatoId ?? '');

    if (!this.esAutoservicio && !candidatoId) {
      return;
    }

    // Integracion interna M3:
    // - Admin: GET /candidatos/{id}/perfil-completo + GET /candidatos/{id}/solicitudes.
    // - Portal: GET /candidatos/me/perfil-completo + GET /candidatos/me/solicitudes.
    // Si falla, se conservan datos de respaldo para evitar pantalla en blanco.
    forkJoin({
      perfil: perfil$.pipe(timeout(6000), catchError((error) => {
        console.warn('Perfil M3 no disponible; se conserva respaldo local.', error);
        return of(null);
      })),
      solicitudes: solicitudes$.pipe(timeout(6000), catchError((error) => {
        console.warn('Solicitudes del candidato no disponibles; se conserva respaldo local.', error);
        return of([] as PostulacionCandidatoApi[]);
      })),
    })
      .pipe(take(1))
      .subscribe(({ perfil, solicitudes }) => {
        if (perfil) {
          this.candidato = this.mapearPerfilM3(perfil, solicitudes);
          this.experiencias = this.mapearExperienciasM3(perfil.experiencias ?? []);
          this.estudios = this.mapearEstudiosM3(perfil.estudios ?? []);
          this.habilidadesComparadas = this.mapearHabilidadesM3(perfil.habilidades ?? []);
        }

        if (solicitudes.length > 0) {
          this.postulaciones = this.mapearPostulacionesM3(solicitudes);
          this.postulacionSeleccionadaId = this.postulaciones[0][0];
        }
      });
  }

  private get esAutoservicio() {
    return Boolean(this.route.snapshot.data['autoservicio']);
  }

  private mapearPerfilM3(
    perfil: CandidatoPerfilCompletoApi,
    solicitudes: PostulacionCandidatoApi[],
  ): CandidatoPerfil {
    // Integracion interna M3: transforma cand_* + bloques anidados al modelo visual del perfil.
    const nombre = [
      perfil.cand_nombres,
      perfil.cand_apellido_paterno,
      perfil.cand_apellido_materno,
    ]
      .filter(Boolean)
      .join(' ') || 'Candidato sin nombre';
    const primeraSolicitud = solicitudes[0];
    const direccion = perfil.direccion;

    return {
      ...this.candidato,
      idSolicitud: primeraSolicitud ? String(primeraSolicitud.slcd_solicitud_id) : String(perfil.cand_id),
      match: this.normalizarNumero(primeraSolicitud?.slcd_puntaje_compatibilidad) ?? this.candidato.match,
      nombre,
      correo: perfil.cand_email ?? 'Sin correo',
      telefono: perfil.cand_telefono ?? '',
      cargo: perfil.cand_titulo ?? this.candidato.cargo,
      estado: this.candidato.estado,
      disponibilidad: perfil.cand_disponibilidad_id ? `ID ${perfil.cand_disponibilidad_id}` : this.candidato.disponibilidad,
      renta: primeraSolicitud?.slcd_pretension_renta ?? this.candidato.renta,
      rut: this.formatearRut(perfil.cand_rut_sin_dv, perfil.cand_dv) ?? this.candidato.rut,
      fechaNacimiento: this.formatearFecha(perfil.cand_fecha_nacimiento) || this.candidato.fechaNacimiento,
      fechaRegistro: this.formatearFecha(perfil.cand_fecha_creacion) || this.candidato.fechaRegistro,
      tituloProfesional: perfil.cand_titulo ?? this.candidato.tituloProfesional,
      estadoUsuario: perfil.cand_estado_usuario_id === 1 ? 'Activo' : this.candidato.estadoUsuario,
      resumenProfesional: perfil.cand_resumen_profesional ?? this.candidato.resumenProfesional,
      urlPerfil: extraerLinkedinUrl(perfil.cand_url_1) ?? '',
      direccion: [direccion?.drcd_calle, direccion?.drcd_numero, direccion?.drcd_dpto_oficina]
        .filter(Boolean)
        .join(' ') || this.candidato.direccion,
    };
  }

  private mapearExperienciasM3(experiencias: ExperienciaCandidatoApi[]): ExperienciaPerfil[] {
    if (experiencias.length === 0) {
      return this.experiencias;
    }

    return experiencias.map((experiencia) => ({
      empresa: experiencia.empresa?.emp_nombre ?? experiencia.cdex_empresa ?? 'Empresa sin nombre',
      cargo: experiencia.cargo?.crgo_nombre ?? experiencia.cdex_cargo ?? 'Cargo sin nombre',
      fecha: this.rangoFechas(
        experiencia.expl_fecha_inicio ?? experiencia.cdex_fecha_inicio,
        experiencia.expl_fecha_fin ?? experiencia.cdex_fecha_fin,
      ),
      descripcion: experiencia.expl_descripcion_funciones ?? experiencia.cdex_descripcion ?? 'Sin descripción registrada.',
      tags: [],
    }));
  }

  private mapearEstudiosM3(estudios: EstudioCandidatoApi[]): EstudioPerfil[] {
    if (estudios.length === 0) {
      return this.estudios;
    }

    return estudios.map((estudio) => ({
      titulo: estudio.carrera?.crra_nombre ?? estudio.nivel_educacional?.nved_nombre ?? 'Estudio sin titulo',
      institucion: estudio.institucion?.inst_nombre ?? 'Institucion sin nombre',
      fecha: this.rangoFechas(
        estudio.etcd_fecha_inicio ?? estudio.cdet_fecha_inicio,
        estudio.etcd_fecha_fin ?? estudio.cdet_fecha_fin,
      ),
    }));
  }

  private mapearHabilidadesM3(habilidades: HabilidadCandidatoApi[]): HabilidadComparada[] {
    if (habilidades.length === 0) {
      return this.habilidadesComparadas;
    }

    return habilidades.map((habilidad) => {
      const nombre = habilidad.habilidad?.hab_nombre ?? `Habilidad ${habilidad.cdhb_habilidad_id ?? ''}`.trim();
      const nivel = habilidad.nivel_habilidad?.nvhb_nombre ?? 'Sin nivel';
      const anios = String(habilidad.cdhb_anios_experiencia ?? 0);
      return [nombre, nivel, anios, nombre, nivel, anios, '100%', 'success'];
    });
  }

  private mapearPostulacionesM3(solicitudes: PostulacionCandidatoApi[]): PostulacionPerfil[] {
    return solicitudes.map((solicitud) => [
      String(solicitud.slcd_solicitud_id),
      'Solicitud',
      `Solicitud ${solicitud.slcd_solicitud_id}`,
      this.formatearFecha(solicitud.slcd_fecha_postulacion),
      `Estado ${solicitud.slcd_estado_solicitud_candidato_id ?? '-'}`,
    ]);
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

  private normalizarNumero(valor?: number | string | null) {
    if (valor == null || valor === '') {
      return undefined;
    }

    const numero = Number(valor);
    return Number.isNaN(numero) ? undefined : numero;
  }
}
