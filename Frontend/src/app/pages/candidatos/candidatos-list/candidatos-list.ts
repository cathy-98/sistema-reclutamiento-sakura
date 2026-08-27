import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';
import {
  catchError,
  finalize,
  forkJoin,
  map,
  of,
  Subscription,
  switchMap,
  take,
  timeout,
} from 'rxjs';

import {
  EntrevistaPayload,
  EntrevistasService,
} from '../../../services/entrevistas.service';

import {
  CatalogosService,
  HabilidadCatalogoApi,
  NivelHabilidadCatalogoApi,
} from '../../../services/catalogos.service';

import {
  CandidatoApi,
  CandidatosService,
  HabilidadCandidatoApi,
  PostulacionCandidatoApi,
} from '../../../services/candidatos.service';

import { SolicitudesService } from '../../../services/solicitudes.service';

import { AlertRegion } from '../../../shared/components/alert-region/alert-region';

import {
  DataTable,
  DataTableAction,
  DataTableActionEvent,
  DataTableColumn,
} from '../../../shared/components/data-table/data-table';

import { ActionBar } from '../../../shared/components/action-bar/action-bar';
import { Button } from '../../../shared/components/button/button';
import { ConfirmDialog } from '../../../shared/components/confirm-dialog/confirm-dialog';
import { FileDropzone } from '../../../shared/components/file-dropzone/file-dropzone';
import { FilterPanel } from '../../../shared/components/filter-panel/filter-panel';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';

import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { SolicitudHabilidadApi, SolicitudResumen } from '../../../shared/models/solicitud.model';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import { CurrencyClPipe } from '../../../shared/pipes/currency-cl.pipe';

import {
  EntrevistaCandidatoSeleccionado,
  EntrevistaFormModal,
} from '../../entrevistas/entrevista-form-modal/entrevista-form-modal';

type EstadoCandidato = 'Todos' | string;
type NivelCandidato = string;

/**
 * Integración M3 - Candidatos y Postulaciones
 *
 * Modelo visual resumido de una postulación.
 *
 * Los datos relacionados con el proceso de selección pertenecen
 * a la postulación y no directamente al candidato:
 * - solicitud
 * - estado
 * - match
 * - pretensión de renta
 * - fecha de postulación
 *
 * Se construye principalmente desde:
 * GET /candidatos/{candidate_id}/solicitudes
 */
interface PostulacionTabla {
  idPostulacion: number;
  idSolicitud: number;
  codigoSolicitud: string;
  cargo: string;
  match: number;
  matchDisponible: boolean;
  renta: number;
  fechaPostulacion: string;
  fechaPostulacionRaw: string | null;
  estado: string;
}

/**
 * Integración M3 - Candidatos y Postulaciones
 *
 * El candidato representa la identidad/persona mediante cand_id.
 *
 * Un mismo candidato puede estar asociado a múltiples solicitudes,
 * por lo que no se debe utilizar una única idSolicitud como
 * identificador del candidato.
 *
 * Las postulaciones se conservan como colección para representar
 * correctamente todos los procesos en los que participa.
 */
interface Candidato {
  idCandidato: string;
  postulaciones: PostulacionTabla[];

  match: number;
  matchDisponible: boolean;
  nombre: string;
  correo: string;
  telefono: string;
  cargo: string;
  fechaPostulacion: string;
  estado: Exclude<EstadoCandidato, 'Todos'>;
  estadoUsuario: string;
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

interface SolicitudContextoCandidatos {
  id: string;
  codigo: string;
  cargo: string;
  estado: string;
  prioridad?: string;
  vacantes?: number;
}

interface HabilidadSolicitudContexto {
  id: number;
  nombre: string;
}

@Component({
  selector: 'app-candidatos-list',
  imports: [
    CommonModule,
    FormsModule,
    AlertRegion,
    DataTable,
    Button,
    ConfirmDialog,
    FileDropzone,
    PageHeader,
    PageLayout,
    FilterPanel,
    ActionBar,
    EntrevistaFormModal,
  ],
  templateUrl: './candidatos-list.html',
  styleUrl: './candidatos-list.scss',
})
export class CandidatosList implements OnInit, OnDestroy {
  cargando = false;
  importandoCvs = false;
  errorCarga = '';
  alerta: AlertaUi | null = null;
  vistaGeneral: 'listado' | 'carga' = 'listado';

  paginaActual = 1;
  registrosPorPagina = 5;

  busquedaRapida = '';

  /**
   * Integración M3
   *
   * La selección de filas utiliza cand_id.
   * No utiliza solicitud ni postulación porque un candidato
   * puede participar en múltiples procesos.
   */
  seleccionados = new Set<string>();

  archivosCv: File[] = [];

  candidatosAgenda: EntrevistaCandidatoSeleccionado[] = [];
  mostrarModalAgenda = false;

  mostrarConfirmacionDesactivacion = false;
  candidatoSeleccionadoDesactivacion: Candidato | null = null;

  filtros: FiltrosCandidatos = this.filtrosIniciales();

  estados: EstadoCandidato[] = [
    'Todos',
    'En revision',
    'En entrevista',
    'Inhabilitado',
    'Seleccionado',
    'Descartado',
    'Contratado',
  ];

  niveles: NivelCandidato[] = [
    'Junior',
    'Semi senior',
    'Senior',
  ];

  disponibilidades: string[] = [];

  candidatos: Candidato[] = [];
  solicitudContexto: SolicitudContextoCandidatos | null = null;
  habilidadesSolicitudContexto: HabilidadSolicitudContexto[] = [];
  solicitudesCargaDisponibles: SolicitudResumen[] = [];
  codigoSolicitudCarga = '';
  solicitudCargaSeleccionada: SolicitudResumen | null = null;
  solicitudCargaFueBuscada = false;
  private queryParamsSubscription?: Subscription;

  /**
   * Decisión UX/UI M3
   *
   * El listado mantiene Match, Estado, Cargo, Renta y Fecha
   * porque son datos relevantes para el recruiter.
   *
   * Cuando un candidato tiene varias postulaciones, la tabla usa
   * la postulación más reciente como resumen visual de esos campos.
   *
   * Todas las postulaciones permanecen disponibles internamente
   * y posteriormente se mostrarán individualmente en el perfil.
   */
  readonly columnas: DataTableColumn<Candidato>[] = [
    {
      key: 'postulaciones',
      label: 'Solicitudes',
      width: 190,
      sticky: 'left',
      wrap: true,

      value: (candidato) =>
        this.formatearSolicitudes(candidato.postulaciones),

      className: (candidato) =>
        candidato.postulaciones.length === 0
          ? 'is-empty-request'
          : '',
    },

    {
      key: 'match',
      label: 'Match',
      width: 112,
      type: 'match',
      value: (candidato) => {
        if (!candidato.matchDisponible) {
          return 'Sin match';
        }

        return this.enContextoSolicitud
          ? `${candidato.match}% match`
          : `${candidato.match}%`;
      },
      className: (candidato) =>
        this.matchClase(candidato),
    },

    {
      key: 'nombre',
      label: 'Nombre completo',
      width: 220,
      type: 'person',
      wrap: true,

      value: (candidato) =>
        candidato.nombre,

      secondaryValue: (candidato) =>
        this.iniciales(candidato.nombre),
    },

    {
      key: 'correo',
      label: 'Correo electrónico',
      width: 230,
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
      width: 260,
      wrap: true,
    },

    {
      key: 'fechaPostulacion',
      label: 'Fecha postulación',
      width: 150,
    },

    {
      key: 'estado',
      label: 'Estado postulación',
      width: 170,
      type: 'badge',

      className: (candidato) =>
        this.estadoClase(candidato.estado),
    },

    {
      key: 'estadoUsuario',
      label: 'Estado cuenta',
      width: 140,
      type: 'badge',

      className: (candidato) =>
        this.estadoClase(candidato.estadoUsuario),
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

      value: (candidato) =>
        candidato.renta > 0
          ? this.currencyCl.transform(candidato.renta)
          : 'Sin información',
    },

  ];

  get columnasTabla(): DataTableColumn<Candidato>[] {
    if (!this.enContextoSolicitud) {
      return this.columnas;
    }

    // En contexto de solicitud se omiten columnas redundantes y se prioriza el match.
    const ordenContexto = new Map([
      ['nombre', 1],
      ['match', 2],
      ['estado', 3],
      ['fechaPostulacion', 4],
      ['disponibilidad', 5],
      ['nivel', 6],
      ['estadoUsuario', 7],
      ['correo', 8],
      ['telefono', 9],
      ['renta', 10],
    ]);

    return this.columnas
      .filter((columna) => !['postulaciones', 'cargo'].includes(columna.key))
      .sort((a, b) => (ordenContexto.get(a.key) ?? 99) - (ordenContexto.get(b.key) ?? 99))
      .map((columna) =>
        columna.key === 'match'
          ? {
              ...columna,
              label: 'Ranking match',
              width: 142,
            }
          : columna.key === 'nombre'
          ? {
              ...columna,
              sticky: 'left',
            }
          : columna,
      );
  }

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

    {
      id: 'enviar-test',
      label: 'Enviar test',
      icon: 'edit',
    },

    {
      id: 'desactivar',
      label: 'Desactivar cuenta',
      icon: 'trash',

      visible: (candidato) =>
        !this.enContextoSolicitud &&
        candidato.estadoUsuario !== 'Inactivo',
    },
  ];

  constructor(
    private currencyCl: CurrencyClPipe,
    private router: Router,
    private route: ActivatedRoute,
    private entrevistasService: EntrevistasService,
    private catalogosService: CatalogosService,
    private candidatosService: CandidatosService,
    private solicitudesService: SolicitudesService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.queryParamsSubscription = this.route.queryParamMap.subscribe((params) => {
      const contextoAnterior = this.enContextoSolicitud;

      this.aplicarVistaDesdeRuta(params);
      this.aplicarContextoSolicitudDesdeRuta(params);

      if (contextoAnterior !== this.enContextoSolicitud) {
        this.limpiarFiltros();
      }
    });

    this.cargarCandidatos();
  }

  ngOnDestroy() {
    this.queryParamsSubscription?.unsubscribe();
  }

  get enContextoSolicitud() {
    return Boolean(this.solicitudContexto);
  }

  get mostrarListadoCandidatos() {
    // El contexto de solicitud siempre usa el listado, aunque no venga vista=listado.
    return this.enContextoSolicitud || this.vistaGeneral === 'listado';
  }

  get mostrarCargaCandidatos() {
    // La carga queda disponible solo desde el submenú general, no desde una solicitud.
    return !this.enContextoSolicitud && this.vistaGeneral === 'carga';
  }

  get tituloPagina() {
    return this.solicitudContexto
      ? `Candidatos para ${this.solicitudContexto.codigo || this.solicitudContexto.id}`
      : this.mostrarCargaCandidatos
      ? 'Carga de candidatos'
      : 'Listado de candidatos';
  }

  get subtituloPagina() {
    return this.solicitudContexto
      ? this.solicitudContexto.cargo || 'Gestión contextual de candidatos'
      : this.mostrarCargaCandidatos
      ? 'Carga y procesamiento de CVs'
      : 'Gestión de candidatos y postulaciones';
  }

  get metadataSolicitudContexto() {
    if (!this.solicitudContexto) {
      return [];
    }

    return [
      this.solicitudContexto.estado,
      this.solicitudContexto.prioridad ? `Prioridad ${this.solicitudContexto.prioridad}` : '',
      this.solicitudContexto.vacantes != null ? `${this.solicitudContexto.vacantes} vacante${this.solicitudContexto.vacantes === 1 ? '' : 's'}` : '',
    ].filter(Boolean);
  }

  get mostrarFiltroMatch() {
    // Evita filtrar por match cuando backend aún no entregó puntajes calculados.
    return !this.enContextoSolicitud || this.tieneMatchCalculadoContexto;
  }

  get tieneCandidatosAsociadosContexto() {
    return !this.enContextoSolicitud || this.candidatosSolicitudContexto.length > 0;
  }

  get tieneMatchCalculadoContexto() {
    return this.candidatosSolicitudContexto.some((candidato) => candidato.matchDisponible);
  }

  get mostrarMensajeSinMatchContexto() {
    return (
      this.enContextoSolicitud &&
      this.tieneCandidatosAsociadosContexto &&
      !this.tieneMatchCalculadoContexto
    );
  }

  get tituloTabla() {
    return this.solicitudContexto
      ? `Candidatos para ${this.solicitudContexto.codigo || this.solicitudContexto.id}`
      : 'Listado de candidatos';
  }

  get descripcionFiltros() {
    return this.enContextoSolicitud
      ? 'Refina los candidatos asociados a esta solicitud.'
      : 'Busca rápidamente o combina filtros para encontrar candidatos dentro de sus procesos de selección.';
  }

  get placeholderBusquedaRapida() {
    return this.enContextoSolicitud
      ? 'Buscar por nombre, correo o teléfono'
      : 'Buscar por nombre, correo, solicitud o cargo';
  }

  get tituloVacio() {
    if (this.enContextoSolicitud && !this.tieneCandidatosAsociadosContexto) {
      return 'No hay candidatos asociados a esta solicitud.';
    }

    return this.enContextoSolicitud
      ? 'No se encontraron candidatos compatibles para esta solicitud.'
      : 'No hay candidatos para mostrar';
  }

  get mensajeVacio() {
    if (this.enContextoSolicitud && !this.tieneCandidatosAsociadosContexto) {
      return 'Cuando existan candidatos asociados, podrás revisarlos y gestionarlos desde aquí.';
    }

    return this.enContextoSolicitud
      ? 'Puedes ajustar los filtros o continuar con la búsqueda por otros medios.'
      : 'Ajusta los filtros o limpia la búsqueda para volver al listado completo.';
  }

  get mostrarSolicitudCargaNoEncontrada() {
    // El campo es opcional: solo muestra error cuando la reclutadora ingresó un código.
    return (
      this.mostrarCargaCandidatos &&
      this.solicitudCargaFueBuscada &&
      this.codigoSolicitudCarga.trim().length > 0 &&
      !this.solicitudCargaSeleccionada
    );
  }

  volverASolicitud() {
    if (!this.solicitudContexto?.id) {
      this.router.navigate(['/solicitudes']);
      return;
    }

    this.router.navigate(['/solicitudes'], {
      queryParams: {
        detalleSolicitud: this.solicitudContexto.id,
        codigoSolicitud: this.solicitudContexto.codigo,
      },
      state: {
        solicitudContexto: this.solicitudContexto,
      },
    });
  }

  /**
   * Integración M3
   *
   * Carga inicial:
   * - GET /candidatos entrega los datos base de la persona.
   * - GET /candidatos/{candidate_id}/solicitudes entrega sus postulaciones.
   * - GET /solicitudes permite resolver slcd_solicitud_id a código SOL-XXX
   *   y cargo visible.
   * - Los catálogos resuelven estado, disponibilidad y nivel sin hardcodear IDs.
   *
   * El frontend únicamente orquesta y presenta estos datos.
   * La fuente de verdad permanece en Backend.
   */
  cargarCandidatos() {
    this.cargando = true;
    this.errorCarga = '';
    this.paginaActual = 1;

    forkJoin({
      candidatos: this.candidatosService.listar().pipe(
        timeout(6000),

        catchError((error) => {
          console.warn(
            'GET /candidatos no disponible.',
            error,
          );

          return of([] as CandidatoApi[]);
        }),
      ),

      estados:
        this.catalogosService.listarEstadosSolicitudCandidatoSeguro(),

      disponibilidades:
        this.catalogosService.listarDisponibilidadesSeguro(),

      niveles:
        this.catalogosService.listarNivelesHabilidadSeguro(),

      solicitudes: this.solicitudesService.listar().pipe(
        timeout(8000),

        catchError((error) => {
          console.warn(
            'No se pudo cargar el catálogo de solicitudes.',
            error,
          );

          return of([]);
        }),
      ),

      habilidadesSolicitud: this.obtenerHabilidadesSolicitudContexto(),

      habilidadesCatalogo: this.obtenerHabilidadesCatalogoContexto(),

      nivelesHabilidadSolicitud: this.obtenerNivelesHabilidadContexto(),
    })
      .pipe(
        /**
         * Integración M3
         *
         * GET /candidatos no incluye todas las postulaciones.
         * Por eso, una vez obtenidos los candidatos, consultamos
         * /candidatos/{candidate_id}/solicitudes para cada uno.
         *
         * Esto mantiene correctamente separadas las entidades:
         *
         * Candidato -> cand_id
         * Postulación -> slcd_id
         * Solicitud -> slcd_solicitud_id
         */
        switchMap(
          ({
            candidatos,
            estados,
            disponibilidades,
            niveles,
            solicitudes,
            habilidadesSolicitud,
            habilidadesCatalogo,
            nivelesHabilidadSolicitud,
          }) => {
            if (candidatos.length === 0) {
              return of({
                candidatos,
                estados,
                disponibilidades,
                niveles,
                solicitudes,
                habilidadesSolicitud,
                habilidadesCatalogo,
                nivelesHabilidadSolicitud,

                postulacionesPorCandidato:
                  new Map<number, PostulacionCandidatoApi[]>(),
                habilidadesPorCandidato:
                  new Map<number, HabilidadCandidatoApi[]>(),
              });
            }

            const datosCandidato$ = candidatos.map(
              (candidato) =>
                forkJoin({
                  postulaciones: this.candidatosService
                    .listarSolicitudes(String(candidato.cand_id))
                    .pipe(
                      timeout(5000),

                      catchError((error) => {
                        console.warn(
                          `No se pudieron cargar postulaciones del candidato ${candidato.cand_id}.`,
                          error,
                        );

                        return of(
                          [] as PostulacionCandidatoApi[],
                        );
                      }),
                    ),
                  habilidades: this.candidatosService
                    .listarHabilidades(candidato.cand_id)
                    .pipe(
                      timeout(5000),

                      catchError((error) => {
                        console.warn(
                          `No se pudieron cargar habilidades del candidato ${candidato.cand_id}.`,
                          error,
                        );

                        return of(
                          [] as HabilidadCandidatoApi[],
                        );
                      }),
                    ),
                }).pipe(
                  map(({ postulaciones, habilidades }) => ({
                    candidatoId: candidato.cand_id,
                    postulaciones,
                    habilidades,
                  })),
                ),
            );

            return forkJoin(datosCandidato$).pipe(
              map((resultados) => {
                const postulacionesPorCandidato =
                  new Map<number, PostulacionCandidatoApi[]>();
                const habilidadesPorCandidato =
                  new Map<number, HabilidadCandidatoApi[]>();

                resultados.forEach((resultado) => {
                  postulacionesPorCandidato.set(
                    resultado.candidatoId,
                    resultado.postulaciones,
                  );
                  habilidadesPorCandidato.set(
                    resultado.candidatoId,
                    resultado.habilidades,
                  );
                });

                return {
                  candidatos,
                  estados,
                  disponibilidades,
                  niveles,
                  solicitudes,
                  habilidadesSolicitud,
                  habilidadesCatalogo,
                  nivelesHabilidadSolicitud,
                  postulacionesPorCandidato,
                  habilidadesPorCandidato,
                };
              }),
            );
          },
        ),

        take(1),

        finalize(() => {
          this.cargando = false;
          this.cdr.detectChanges();
        }),
      )
      .subscribe({
        next: ({
          candidatos,
          estados,
          disponibilidades,
          niveles,
          solicitudes,
          habilidadesSolicitud,
          habilidadesCatalogo,
          nivelesHabilidadSolicitud,
          postulacionesPorCandidato,
          habilidadesPorCandidato,
        }) => {
          const estadosCatalogo = estados
            .map((estado) => estado.essc_nombre)
            .filter(
              (nombre): nombre is string =>
                Boolean(nombre),
            );

          const disponibilidadesCatalogo = disponibilidades
            .map(
              (disponibilidad) =>
                disponibilidad.disp_nombre,
            )
            .filter(
              (nombre): nombre is string =>
                Boolean(nombre),
            );

          const nivelesCatalogo = niveles
            .map((nivel) => nivel.nvhb_nombre)
            .filter(
              (nombre): nombre is string =>
                Boolean(nombre),
            );

          const disponibilidadesPorId = new Map(
            disponibilidades.map((disponibilidad) => [
              disponibilidad.disp_id,
              disponibilidad.disp_nombre ??
                'Sin disponibilidad',
            ]),
          );

          const estadosPorId = new Map(
            estados.map((estado) => [
              estado.essc_id,
              estado.essc_nombre ?? 'Sin estado',
            ]),
          );

          /**
           * Integración M3
           *
           * PostulacionCandidatoApi entrega slcd_solicitud_id.
           *
           * Para presentar un identificador útil al recruiter,
           * cruzamos ese ID con SolicitudesService.listar()
           * y recuperamos:
           *
           * - código funcional SOL-XXX
           * - cargo asociado a esa solicitud
           *
           * No se utiliza cand_id como código de solicitud.
           */
          const solicitudesPorId = new Map(
            solicitudes.map((solicitud) => [
              Number(solicitud.id),

              {
                codigo: solicitud.codigo,
                cargo: solicitud.cargo,
                estado: solicitud.estado,
                prioridad: solicitud.prioridad,
                vacantes: solicitud.vacantes,
              },
            ]),
          );

          this.solicitudesCargaDisponibles = solicitudes;
          this.completarContextoSolicitud(solicitudesPorId);
          this.aplicarHabilidadesSolicitudContexto(
            habilidadesSolicitud,
            habilidadesCatalogo,
            nivelesHabilidadSolicitud,
          );

          if (estadosCatalogo.length > 0) {
            this.estados = [
              'Todos',
              ...estadosCatalogo,
            ];
          }

          if (disponibilidadesCatalogo.length > 0) {
            this.disponibilidades =
              disponibilidadesCatalogo;
          }

          if (nivelesCatalogo.length > 0) {
            this.niveles =
              nivelesCatalogo;
          }

          if (candidatos.length === 0) {
            this.errorCarga = this.enContextoSolicitud
              ? ''
              : 'No se encontraron candidatos registrados en el backend.';

            this.candidatos =
              [];

            this.cdr.detectChanges();

            return;
          }

          this.candidatos = candidatos.map(
            (candidato) =>
              this.aplicarPostulacionContexto(
                this.mapearCandidatoTabla(
                  candidato,

                  disponibilidadesPorId,

                  postulacionesPorCandidato.get(
                    candidato.cand_id,
                  ) ?? [],

                  solicitudesPorId,

                  estadosPorId,
                  habilidadesPorCandidato.get(
                    candidato.cand_id,
                  ) ?? [],
                ),
              ),
          );

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'Error inesperado cargando candidatos:',
            error,
          );

          this.errorCarga =
            'No se pudieron cargar candidatos desde el backend.';

          this.candidatos =
            [];

          this.cdr.detectChanges();
        },
      });
  }

  /**
   * Integración M3
   *
   * El filtro por ID de solicitud considera TODAS las postulaciones
   * asociadas al candidato y no únicamente la postulación utilizada
   * como resumen visual en la tabla.
   *
   * La búsqueda rápida también considera códigos SOL-XXX,
   * cargos, nombre, correo y teléfono.
   */
  get candidatosFiltrados() {
    const filtrosNormalizados = {
      busquedaRapida:
        this.normalizar(this.busquedaRapida),

      idSolicitud:
        this.normalizar(this.filtros.idSolicitud),

      cargo:
        this.normalizar(this.filtros.cargo),

      nombre:
        this.normalizar(this.filtros.nombre),

      correo:
        this.normalizar(this.filtros.correo),

      telefono:
        this.normalizar(this.filtros.telefono),

      disponibilidad:
        this.normalizar(this.filtros.disponibilidad),
    };

    const renta = Number(
      this.filtros.renta,
    );

    const match = this.mostrarFiltroMatch
      ? Number(this.filtros.match)
      : 0;

    const experiencia = Number(
      this.filtros.experiencia,
    );

    const candidatosFiltrados = this.candidatos.filter((candidato) => {
      const codigosSolicitudes = candidato.postulaciones
        .map(
          (postulacion) =>
            postulacion.codigoSolicitud,
        )
        .join(' ');

      const cargosPostulaciones = candidato.postulaciones
        .map(
          (postulacion) =>
            postulacion.cargo,
        )
        .join(' ');

      const textoCandidato =
        this.normalizar(
          `
            ${codigosSolicitudes}
            ${cargosPostulaciones}
            ${candidato.nombre}
            ${candidato.correo}
            ${candidato.telefono}
          `,
        );

      const coincideTexto =
        textoCandidato.includes(
          filtrosNormalizados.busquedaRapida,
        );

      const coincideSolicitud =
        this.normalizar(codigosSolicitudes).includes(
          filtrosNormalizados.idSolicitud,
        );

      const coincideCargo =
        this.normalizar(
          `${candidato.cargo} ${cargosPostulaciones}`,
        ).includes(
          filtrosNormalizados.cargo,
        );

      const coincideNombre =
        this.normalizar(candidato.nombre).includes(
          filtrosNormalizados.nombre,
        );

      const coincideCorreo =
        this.normalizar(candidato.correo).includes(
          filtrosNormalizados.correo,
        );

      const coincideTelefono =
        this.normalizar(candidato.telefono).includes(
          filtrosNormalizados.telefono,
        );

      const coincideDisponibilidad =
        this.normalizar(
          candidato.disponibilidad,
        ).includes(
          filtrosNormalizados.disponibilidad,
        );

      /**
       * Integración M3
       *
       * Estado es propiedad de la postulación.
       * Por eso comprobamos cualquiera de las postulaciones
       * asociadas al candidato.
       */
      const coincideEstado =
        this.filtros.estado === 'Todos' ||
        candidato.postulaciones.some((postulacion) => {
          const postulacionContexto = this.obtenerPostulacionContexto(candidato);

          return (
            (!this.enContextoSolicitud || postulacion === postulacionContexto) &&
            postulacion.estado === this.filtros.estado
          );
        });

      const coincideNivel =
        !this.filtros.nivel ||
        candidato.nivel ===
          this.filtros.nivel;

      /**
       * Decisión UX/UI M3
       *
       * Match y renta del listado representan la postulación
       * actualmente utilizada como resumen de la fila.
       *
       * Cuando gestionemos una postulación específica en el perfil,
       * estos datos se mostrarán por proceso.
       */
      const coincideRenta =
        !renta ||
        candidato.renta <= renta;

      const coincideMatch =
        !match ||
        candidato.match >= match;

      const coincideExperiencia =
        !experiencia ||
        candidato.experiencia >= experiencia;

      return (
        coincideTexto &&
        coincideSolicitud &&
        coincideCargo &&
        coincideNombre &&
        coincideCorreo &&
        coincideTelefono &&
        coincideDisponibilidad &&
        coincideEstado &&
        coincideNivel &&
        coincideRenta &&
        coincideMatch &&
        coincideExperiencia
      );
    });

    return this.enContextoSolicitud
      ? this.ordenarPorMatch(candidatosFiltrados)
      : candidatosFiltrados;
  }

  get seleccionadosEnPagina() {
    return (
      this.candidatosPaginados.length > 0 &&
      this.candidatosPaginados.every(
        (candidato) =>
          this.estaSeleccionado(candidato),
      )
    );
  }

  get totalPaginas() {
    return Math.max(
      1,
      Math.ceil(
        this.candidatosFiltrados.length /
          this.registrosPorPagina,
      ),
    );
  }

  get mensajeAccionesMasivas() {
    return this.seleccionados.size > 0
      ? `${this.seleccionados.size} candidatos seleccionados.`
      : 'Selecciona candidatos para habilitar acciones masivas.';
  }

  get candidatosPaginados() {
    const inicio =
      (this.paginaActual - 1) *
      this.registrosPorPagina;

    return this.candidatosFiltrados.slice(
      inicio,
      inicio + this.registrosPorPagina,
    );
  }

  limpiarFiltros() {
    if (this.enContextoSolicitud) {
      // Mantiene la solicitud seleccionada al limpiar los filtros secundarios.
      this.filtros = {
        ...this.filtrosIniciales(),
        idSolicitud: this.solicitudContexto?.codigo ?? '',
      };

      this.busquedaRapida = '';
      this.paginaActual = 1;
      return;
    }

    this.filtros =
      this.filtrosIniciales();

    this.busquedaRapida = '';

    this.paginaActual = 1;
  }

  buscar() {
    this.paginaActual = 1;
  }

  cambiarPagina(pagina: number) {
    this.paginaActual = Math.min(
      Math.max(pagina, 1),
      this.totalPaginas,
    );
  }

  cambiarRegistrosPorPagina(
    registros: number,
  ) {
    this.registrosPorPagina =
      registros;

    this.paginaActual = 1;
  }

  trackCandidato(
    _index: number,
    candidato: Candidato,
  ) {
    return candidato.idCandidato;
  }

  estaSeleccionado(
    candidato: Candidato,
  ) {
    return this.seleccionados.has(
      this.obtenerIdCandidato(candidato),
    );
  }

  alternarSeleccion(
    candidato: Candidato,
    seleccionado: boolean,
  ) {
    const id =
      this.obtenerIdCandidato(candidato);

    if (seleccionado) {
      this.seleccionados.add(id);
      return;
    }

    this.seleccionados.delete(id);
  }

  alternarSeleccionPagina(
    seleccionado: boolean,
  ) {
    this.candidatosPaginados.forEach(
      (candidato) => {
        this.alternarSeleccion(
          candidato,
          seleccionado,
        );
      },
    );
  }

  manejarAccionTabla(
    evento: DataTableActionEvent<Candidato>,
  ) {
    if (evento.action === 'ver') {
      const candidato = evento.row;

      const postulacion =
        this.obtenerPostulacionNavegacion(candidato);

      this.router.navigate(
        [
          '/candidatos/perfil',
          this.obtenerIdCandidato(candidato),
        ],
        {
          queryParams: {
            /**
             * Integración M3
             *
             * El perfil recibe cand_id por ruta.
             * Estos queryParams se mantienen temporalmente
             * para compatibilidad con la vista actual.
             *
             * El perfil deberá consultar sus postulaciones
             * directamente y permitir seleccionar una de ellas.
             */
            idSolicitud:
              postulacion?.codigoSolicitud ?? '',

            postulaciones:
              this.serializarPostulacionesPerfil(candidato),

            idPostulacion:
              postulacion?.idPostulacion ?? '',

            match:
              candidato.match,

            nombre:
              candidato.nombre,

            correo:
              candidato.correo,

            telefono:
              candidato.telefono,

            cargo:
              candidato.cargo,

            estado:
              candidato.estado,

            estadoUsuario:
              candidato.estadoUsuario,

            disponibilidad:
              candidato.disponibilidad,

            renta:
              candidato.renta,
          },
        },
      );

      return;
    }

    if (
      evento.action ===
      'agendar-entrevista'
    ) {
      this.abrirAgendaEntrevista([
        evento.row,
      ]);

      return;
    }

    if (
      evento.action ===
      'enviar-test'
    ) {
      const candidato = evento.row;

      const postulacion =
        this.obtenerPostulacionNavegacion(candidato);

      this.router.navigate(
        [
          '/candidatos/perfil',
          this.obtenerIdCandidato(candidato),
        ],
        {
          queryParams: {
            idSolicitud:
              postulacion?.codigoSolicitud ?? '',

            postulaciones:
              this.serializarPostulacionesPerfil(candidato),

            idPostulacion:
              postulacion?.idPostulacion ?? '',

            match:
              candidato.match,

            nombre:
              candidato.nombre,

            correo:
              candidato.correo,

            telefono:
              candidato.telefono,

            cargo:
              candidato.cargo,

            estado:
              candidato.estado,

            estadoUsuario:
              candidato.estadoUsuario,

            disponibilidad:
              candidato.disponibilidad,

            renta:
              candidato.renta,

            tab: 'evaluaciones',
          },
        },
      );

      return;
    }

    if (
      evento.action === 'desactivar'
    ) {
      this.abrirConfirmacionDesactivacion(
        evento.row,
      );

      return;
    }

    console.log(
      'Acción de candidato:',
      evento.action,
      evento.row,
    );
  }

  abrirConfirmacionDesactivacion(
    candidato: Candidato,
  ) {
    this.candidatoSeleccionadoDesactivacion =
      candidato;

    this.mostrarConfirmacionDesactivacion =
      true;
  }

  cerrarConfirmacionDesactivacion() {
    this.mostrarConfirmacionDesactivacion =
      false;

    this.candidatoSeleccionadoDesactivacion =
      null;
  }

  confirmarDesactivacionCandidato() {
    if (
      !this.candidatoSeleccionadoDesactivacion
    ) {
      return;
    }

    const candidato = this.candidatoSeleccionadoDesactivacion;

    this.candidatosService
      .desactivar(this.obtenerIdCandidato(candidato))
      .pipe(take(1))
      .subscribe({
        next: () => {
          candidato.estadoUsuario = 'Inactivo';

          this.seleccionados.delete(
            this.obtenerIdCandidato(candidato),
          );

          this.alerta = {
            tipo: 'success',
            variante: 'soft',
            mensaje:
              `${candidato.nombre} quedó con cuenta inactiva.`,
          };

          this.cerrarConfirmacionDesactivacion();
        },
        error: (error) => {
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(
              error,
              'No se pudo desactivar la cuenta del candidato.',
            ),
          };
        },
      });
  }

  cerrarAlerta() {
    this.alerta = null;
  }

  abrirAgendaMasiva() {
    const candidatos =
      this.candidatos.filter(
        (candidato) =>
          this.seleccionados.has(
            this.obtenerIdCandidato(candidato),
          ),
      );

    if (candidatos.length === 0) {
      return;
    }

    const solicitudComun =
      this.obtenerSolicitudComunAgenda(candidatos);

    if (!solicitudComun) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje:
          'Para agendar entrevistas masivas, selecciona candidatos asociados a una misma solicitud.',
      };
      return;
    }

    this.abrirAgendaEntrevista(
      candidatos,
      solicitudComun,
    );
  }

  prepararTestMasivo() {
    if (
      this.seleccionados.size === 0
    ) {
      return;
    }

    console.log(
      'Preparar test masivo para candidatos:',
      Array.from(this.seleccionados),
    );
  }

  /**
   * Integración M3 -> M5
   *
   * La entrevista realmente se agenda sobre una postulación,
   * no solamente sobre cand_id.
   *
   * El modal actual todavía recibe un único idSolicitud,
   * por eso se utiliza temporalmente la postulación resumen.
   *
   * Pendiente M5:
   * cuando un candidato tenga varias postulaciones, el modal
   * debe permitir seleccionar explícitamente cuál proceso
   * se está agendando antes de crear la entrevista.
   */
  abrirAgendaEntrevista(
    candidatos: Candidato[],
    solicitudComun?: PostulacionTabla,
  ) {
    this.candidatosAgenda =
      candidatos.map((candidato) => {
        const postulacion =
          solicitudComun
            ? candidato.postulaciones.find((item) => item.idSolicitud === solicitudComun.idSolicitud)
            : this.obtenerPostulacionPrincipal(candidato);

        return {
          id:
            this.obtenerIdCandidato(candidato),

          solicitudCandidatoId:
            postulacion?.idPostulacion,

          idSolicitud:
            postulacion?.codigoSolicitud ?? '',

          nombre:
            candidato.nombre,

          cargo:
            postulacion?.cargo ??
            candidato.cargo,
        };
      });

    this.mostrarModalAgenda = true;
  }

  cerrarAgendaEntrevista() {
    this.mostrarModalAgenda = false;
    this.candidatosAgenda = [];
  }

  actualizarCandidatosAgenda(
    candidatos: EntrevistaCandidatoSeleccionado[],
  ) {
    this.candidatosAgenda =
      candidatos;

    this.seleccionados =
      new Set(
        candidatos
          .map(
            (candidato) =>
              candidato.id,
          )
          .filter(
            (id): id is string =>
              Boolean(id),
          ),
      );
  }

  guardarAgendaEntrevista(
    payload: EntrevistaPayload,
  ) {
    const candidatos =
      this.candidatosAgenda;

    if (candidatos.length <= 1) {
      this.entrevistasService
        .crear(payload)
        .subscribe({
          next: () => {
            this.alerta = {
              tipo: 'success',
              variante: 'soft',
              mensaje:
                'Entrevista agendada correctamente.',
            };

            this.cerrarAgendaEntrevista();
          },

          error: (error) => {
            this.alerta = {
              tipo: 'danger',
              variante: 'soft',

              mensaje:
                obtenerMensajeError(
                  error,
                  'No se pudo agendar la entrevista. Intenta nuevamente.',
                ),
            };
          },
        });

      return;
    }

    const entrevistas =
      candidatos.map(
        (candidato) => ({
          ...payload,

          solicitudCandidatoId:
            candidato.solicitudCandidatoId,

          idSolicitud:
            candidato.idSolicitud,

          candidato:
            candidato.nombre,

          cargo:
            candidato.cargo,
        }),
      );

    this.entrevistasService
      .crearMasiva(entrevistas)
      .subscribe({
        next: () => {
          this.seleccionados =
            new Set<string>();

          this.alerta = {
            tipo: 'success',
            variante: 'soft',

            mensaje:
              `${entrevistas.length} entrevistas agendadas correctamente.`,
          };

          this.cerrarAgendaEntrevista();
        },

        error: (error) => {
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',

            mensaje:
              obtenerMensajeError(
                error,
                'No se pudieron agendar las entrevistas. Intenta nuevamente.',
              ),
          };
        },
      });
  }

  actualizarArchivosCv(
    files: File[],
  ) {
    this.archivosCv = files;
  }

  validarSolicitudCargaPorCodigo() {
    const codigoNormalizado = this.normalizarCodigoBusqueda(this.codigoSolicitudCarga);

    // Valida exclusivamente por código SOL; el cargo solo confirma la selección.
    this.solicitudCargaFueBuscada = codigoNormalizado.length > 0;

    if (!codigoNormalizado) {
      this.solicitudCargaSeleccionada = null;
      return;
    }

    this.solicitudCargaSeleccionada =
      this.solicitudesCargaDisponibles.find(
        (solicitud) => this.normalizarCodigoBusqueda(solicitud.codigo) === codigoNormalizado,
      ) ?? null;
  }

  limpiarSolicitudCarga() {
    // Permite cambiar la solicitud asociada sin afectar los CVs ya seleccionados.
    this.codigoSolicitudCarga = '';
    this.solicitudCargaSeleccionada = null;
    this.solicitudCargaFueBuscada = false;
  }

  private obtenerSolicitudComunAgenda(candidatos: Candidato[]) {
    const [primero] = candidatos;

    if (!primero) {
      return null;
    }

    return primero.postulaciones.find((postulacion) =>
      candidatos.every((candidato) =>
        candidato.postulaciones.some((item) => item.idSolicitud === postulacion.idSolicitud),
      ),
    ) ?? null;
  }

  procesarArchivosCv() {
    if (this.archivosCv.length === 0 || this.importandoCvs) {
      return;
    }

    // Backend aún no recibe solicitud asociada en importar CV; se conserva solo visualmente.
    this.importandoCvs = true;
    const cargasCv$ = this.archivosCv.map((archivo) =>
      this.candidatosService
        .subirCv(archivo)
        .pipe(
          map((resultado) => ({
            archivo: archivo.name,
            resultado,
            error: '',
          })),
          catchError((error) =>
            of({
              archivo: archivo.name,
              resultado: null,
              error: obtenerMensajeError(
                error,
                'No se pudo procesar este CV.',
              ),
            }),
          ),
        ),
    );

    forkJoin(cargasCv$)
      .pipe(
        take(1),
        finalize(() => {
          this.importandoCvs = false;
        }),
      )
      .subscribe({
        next: (cargas) => {
          const exitosas = cargas.filter((carga) => carga.resultado);
          const fallidas = cargas.filter((carga) => carga.error);
          const creadas = exitosas.filter((carga) => carga.resultado?.creado).length;
          const actualizadas = exitosas.filter((carga) => carga.resultado?.actualizado).length;
          const advertencias = exitosas.flatMap((carga) => [
            ...(carga.resultado?.advertencias ?? []),
            ...(carga.resultado?.warnings ?? []),
          ]);
          const errores = fallidas.map((carga) => `${carga.archivo}: ${carga.error}`);
          const partesMensaje = [
            `${exitosas.length} de ${cargas.length} CV(s) procesados`,
            creadas ? `${creadas} candidato(s) creado(s)` : '',
            actualizadas ? `${actualizadas} candidato(s) actualizado(s)` : '',
            fallidas.length ? `${fallidas.length} fallido(s)` : '',
          ].filter(Boolean);
          const detalles = [
            ...advertencias.slice(0, 2),
            ...errores.slice(0, 2),
          ];

          this.alerta = {
            tipo: fallidas.length || advertencias.length ? 'warning' : 'success',
            variante: 'soft',
            mensaje: detalles.length
              ? `${partesMensaje.join('. ')}. Detalle: ${detalles.join(' ')}`
              : `${partesMensaje.join('. ')}.`,
          };
          this.archivosCv = [];
          this.cargarCandidatos();
        },
        error: (error) => {
          this.alerta = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(
              error,
              'No se pudieron procesar los CVs seleccionados.',
            ),
          };
        },
      });
  }

  iniciales(nombre: string) {
    return nombre
      .split(' ')
      .slice(0, 2)
      .map((parte) => parte[0])
      .join('')
      .toUpperCase();
  }

  matchClase(candidato: Candidato) {
    const clases = ['match-ranking'];

    if (!candidato.matchDisponible) {
      return [...clases, 'is-unavailable'].join(' ');
    }

    if (candidato.match >= 75) {
      return [...clases, 'is-high'].join(' ');
    }

    if (candidato.match >= 55) {
      return [...clases, 'is-medium'].join(' ');
    }

    return [...clases, 'is-low'].join(' ');
  }

  estadoClase(estado: string) {
    return estado
      .toLowerCase()
      .normalize('NFD')
      .replace(
        /[\u0300-\u036f]/g,
        '',
      )
      .replace(/\s+/g, '-');
  }

  /**
   * Decisión UX/UI M3
   *
   * Evita sobrecargar horizontalmente la tabla cuando
   * un candidato participa en múltiples solicitudes.
   *
   * Ejemplos:
   *
   * SOL-XXXXXX
   * SOL-XXXXXX · SOL-YYYYYY
   * SOL-XXXXXX · SOL-YYYYYY · +2
   *
   * La información completa de las postulaciones se conserva
   * y se mostrará en el detalle/perfil del candidato.
   */
  formatearSolicitudes(
    postulaciones: PostulacionTabla[],
  ) {
    if (
      postulaciones.length === 0
    ) {
      return 'Sin solicitud';
    }

    const codigos =
      postulaciones
        .map(
          (postulacion) =>
            postulacion.codigoSolicitud,
        )
        .filter(Boolean);

    if (codigos.length === 0) {
      return 'Sin solicitud';
    }

    if (codigos.length <= 2) {
      return codigos.join(' · ');
    }

    return `${codigos[0]} · ${codigos[1]} · +${codigos.length - 2}`;
  }

  /**
   * Integración M3
   *
   * Las acciones relacionadas con la persona/perfil
   * deben usar cand_id.
   *
   * No utilizar idSolicitud o slcd_id para identificar
   * al candidato.
   */
  obtenerIdCandidato(
    candidato: Candidato,
  ) {
    return candidato.idCandidato;
  }

  /**
   * Decisión UX/UI M3
   *
   * La tabla necesita mostrar una única referencia de:
   * - match
   * - cargo
   * - estado
   * - renta
   * - fecha
   *
   * Cuando existen varias postulaciones, usamos la más reciente
   * exclusivamente como resumen visual del listado.
   *
   * Esto NO significa que sea la única postulación del candidato.
   */
  private obtenerPostulacionPrincipal(
    candidato: Candidato,
  ) {
    return (
      candidato.postulaciones[0] ??
      null
    );
  }

  private obtenerPostulacionNavegacion(candidato: Candidato) {
    // Al navegar desde contexto, usa la postulación de la solicitud actual.
    return this.obtenerPostulacionContexto(candidato) ?? this.obtenerPostulacionPrincipal(candidato);
  }

  private obtenerPostulacionContexto(candidato: Candidato) {
    const contexto = this.solicitudContexto;

    if (!contexto) {
      return null;
    }

    const codigo = this.normalizar(contexto.codigo);
    const id = Number(contexto.id);

    // La postulación se puede reconocer por id o por código, según lo disponible.
    return candidato.postulaciones.find((postulacion) =>
      (Number.isFinite(id) && postulacion.idSolicitud === id) ||
      this.normalizar(postulacion.codigoSolicitud) === codigo,
    ) ?? null;
  }

  private aplicarPostulacionContexto(candidato: Candidato) {
    const postulacion = this.obtenerPostulacionContexto(candidato);

    if (!postulacion) {
      return candidato;
    }

    // Presenta los datos de la postulación de esta solicitud como resumen de la fila.
    return {
      ...candidato,
      match: postulacion.match,
      matchDisponible: postulacion.matchDisponible,
      cargo: postulacion.cargo,
      fechaPostulacion: postulacion.fechaPostulacion,
      estado: postulacion.estado,
      renta: postulacion.renta,
    };
  }

  private ordenarPorMatch(candidatos: Candidato[]) {
    // Los candidatos sin match quedan al final sin convertir ausencia en 0%.
    return [...candidatos].sort((a, b) => {
      if (a.matchDisponible !== b.matchDisponible) {
        return a.matchDisponible ? -1 : 1;
      }

      if (!a.matchDisponible && !b.matchDisponible) {
        return a.nombre.localeCompare(b.nombre, 'es-CL', { sensitivity: 'base' });
      }

      return b.match - a.match;
    });
  }

  private get candidatosSolicitudContexto() {
    if (!this.enContextoSolicitud) {
      return this.candidatos;
    }

    return this.candidatos.filter((candidato) => Boolean(this.obtenerPostulacionContexto(candidato)));
  }

  private aplicarVistaDesdeRuta(params: ParamMap) {
    const vista = params.get('vista');

    // La misma ruta /candidatos alterna entre listado y carga por query param.
    this.vistaGeneral = vista === 'carga' ? 'carga' : 'listado';
  }

  private aplicarContextoSolicitudDesdeRuta(params = this.route.snapshot.queryParamMap) {
    if (params.get('origen') !== 'solicitud' && !params.get('solicitudId') && !params.get('solicitudCodigo')) {
      this.solicitudContexto = null;
      this.habilidadesSolicitudContexto = [];
      return;
    }

    const estadoDesdeQuery = params.get('solicitudEstado') ?? '';
    const contexto = (history.state?.solicitudContexto ?? {}) as Partial<SolicitudContextoCandidatos>;
    const solicitudId = params.get('solicitudId') ?? contexto.id ?? '';
    const solicitudCodigo = params.get('solicitudCodigo') ?? contexto.codigo ?? this.normalizarCodigoSolicitud(null, Number(solicitudId));

    // Detecta el ingreso desde Detalle de solicitud y fija el contexto visual.
    this.solicitudContexto = {
      id: solicitudId,
      codigo: solicitudCodigo,
      cargo: params.get('solicitudCargo') ?? contexto.cargo ?? '',
      estado: estadoDesdeQuery || contexto.estado || '',
    };

    this.filtros = {
      ...this.filtros,
      idSolicitud: solicitudCodigo,
    };
  }

  private completarContextoSolicitud(
    solicitudesPorId: Map<
      number,
      {
        codigo: string;
        cargo: string;
        estado: string;
        prioridad?: string;
        vacantes?: number;
      }
    >,
  ) {
    if (!this.solicitudContexto) {
      return;
    }

    const solicitud = solicitudesPorId.get(Number(this.solicitudContexto.id));

    if (!solicitud) {
      return;
    }

    // Completa metadata desde el listado disponible sin pedir endpoints nuevos.
    this.solicitudContexto = {
      ...this.solicitudContexto,
      codigo: solicitud.codigo || this.solicitudContexto.codigo,
      cargo: solicitud.cargo || this.solicitudContexto.cargo,
      estado: solicitud.estado || this.solicitudContexto.estado,
      prioridad: solicitud.prioridad || this.solicitudContexto.prioridad,
      vacantes: solicitud.vacantes ?? this.solicitudContexto.vacantes,
    };

    this.filtros = {
      ...this.filtros,
      idSolicitud: this.solicitudContexto.codigo,
    };
  }

  private obtenerHabilidadesSolicitudContexto() {
    const idSolicitud = this.solicitudContexto?.id;

    if (!idSolicitud) {
      return of([] as SolicitudHabilidadApi[]);
    }

    return this.solicitudesService.listarHabilidadesSolicitud(idSolicitud).pipe(
      timeout(5000),
      catchError((error) => {
        console.warn('No se pudieron cargar habilidades de la solicitud en contexto.', error);
        return of([] as SolicitudHabilidadApi[]);
      }),
    );
  }

  private obtenerHabilidadesCatalogoContexto() {
    if (!this.enContextoSolicitud) {
      return of([] as HabilidadCatalogoApi[]);
    }

    return this.catalogosService.listarHabilidades().pipe(
      timeout(5000),
      catchError((error) => {
        console.warn('No se pudo cargar el catálogo de habilidades para la solicitud en contexto.', error);
        return of([] as HabilidadCatalogoApi[]);
      }),
    );
  }

  private obtenerNivelesHabilidadContexto() {
    if (!this.enContextoSolicitud) {
      return of([] as NivelHabilidadCatalogoApi[]);
    }

    return this.catalogosService.listarNivelesHabilidadSeguro();
  }

  private aplicarHabilidadesSolicitudContexto(
    habilidadesSolicitud: SolicitudHabilidadApi[],
    habilidadesCatalogo: HabilidadCatalogoApi[],
    _nivelesHabilidadSolicitud: NivelHabilidadCatalogoApi[],
  ) {
    if (!this.enContextoSolicitud) {
      this.habilidadesSolicitudContexto = [];
      return;
    }

    const habilidadesPorId = new Map(
      habilidadesCatalogo.map((habilidad) => [
        habilidad.hab_id,
        habilidad.hab_nombre ?? `Habilidad #${habilidad.hab_id}`,
      ]),
    );

    const habilidadesVisibles = habilidadesSolicitud
      .filter((habilidad) => habilidad.solhb_es_excluyente !== false)
      .map((habilidad) => ({
        id: habilidad.solhb_habilidad_id,
        nombre: habilidadesPorId.get(habilidad.solhb_habilidad_id) ?? `Habilidad #${habilidad.solhb_habilidad_id}`,
      }));

    this.habilidadesSolicitudContexto = habilidadesVisibles.length > 0
      ? habilidadesVisibles
      : habilidadesSolicitud.map((habilidad) => ({
          id: habilidad.solhb_habilidad_id,
          nombre: habilidadesPorId.get(habilidad.solhb_habilidad_id) ?? `Habilidad #${habilidad.solhb_habilidad_id}`,
        }));
  }

  private serializarPostulacionesPerfil(
    candidato: Candidato,
  ) {
    if (candidato.postulaciones.length === 0) {
      return '';
    }

    return JSON.stringify(
      candidato.postulaciones.map((postulacion) => ({
        idPostulacion: postulacion.idPostulacion,
        idSolicitud: postulacion.idSolicitud,
        codigo: postulacion.codigoSolicitud,
        clienteEmpresa: '',
        cargo: postulacion.cargo,
        fecha: postulacion.fechaPostulacion,
        estado: postulacion.estado,
        match: postulacion.match,
        renta: postulacion.renta,
      })),
    );
  }

  /**
   * Integración M3
   *
   * Combina:
   *
   * - datos personales desde GET /candidatos
   * - postulaciones desde GET /candidatos/{candidate_id}/solicitudes
   * - solicitudes para obtener código SOL-XXX y cargo
   * - catálogos para traducir IDs a valores legibles
   *
   * Match, estado, renta y fecha pertenecen a la postulación.
   */
  private mapearCandidatoTabla(
    candidato: CandidatoApi,

    disponibilidadesPorId:
      Map<number, string>,

    postulacionesApi:
      PostulacionCandidatoApi[],

    solicitudesPorId: Map<
      number,
      {
        codigo: string;
        cargo: string;
        estado?: string;
      }
    >,

    estadosPorId:
      Map<number, string>,

    habilidadesApi:
      HabilidadCandidatoApi[],
  ): Candidato {
    const nombre =
      [
        candidato.cand_nombres,
        candidato.cand_apellido_paterno,
        candidato.cand_apellido_materno,
      ]
        .filter(Boolean)
        .join(' ') ||
      'Candidato sin nombre';

    /**
     * Integración M3
     *
     * Ordenamos primero las postulaciones por su fecha real
     * antes de transformarlas a datos de presentación.
     *
     * De esta forma candidato.postulaciones[0]
     * representa la postulación más reciente.
     */
    const postulacionesOrdenadas =
      [...postulacionesApi].sort(
        (a, b) =>
          this.fechaApiTimestamp(
            b.slcd_fecha_postulacion,
          ) -
          this.fechaApiTimestamp(
            a.slcd_fecha_postulacion,
          ),
      );

    const postulaciones:
      PostulacionTabla[] =
      postulacionesOrdenadas.map(
        (postulacion) => {
          const solicitud =
            solicitudesPorId.get(
              postulacion.slcd_solicitud_id,
            );

          const matchOriginal =
            postulacion.slcd_puntaje_compatibilidad;

          const matchNumero =
            Number(matchOriginal);

          const matchDisponible =
            matchOriginal !== null &&
            matchOriginal !== undefined &&
            matchOriginal !== '' &&
            Number.isFinite(matchNumero);

          const rentaNumero =
            Number(
              postulacion.slcd_pretension_renta ??
                0,
            );

          return {
            idPostulacion:
              postulacion.slcd_id,

            idSolicitud:
              postulacion.slcd_solicitud_id,

            /**
             * Integración M3
             *
             * Preferimos siempre sol_codigo obtenido de SolicitudesService.
             *
             * El fallback solamente evita dejar la tabla vacía
             * si la consulta de solicitudes falla.
             */
            codigoSolicitud:
              this.normalizarCodigoSolicitud(
                solicitud?.codigo,
                postulacion.slcd_solicitud_id,
              ),

            cargo:
              solicitud?.cargo ??
              candidato.cand_titulo ??
              'Sin cargo',

            match:
              matchDisponible
                ? matchNumero
                : 0,

            matchDisponible,

            renta:
              Number.isFinite(rentaNumero)
                ? rentaNumero
                : 0,

            fechaPostulacion:
              this.formatearFecha(
                postulacion.slcd_fecha_postulacion,
              ),

            fechaPostulacionRaw:
              postulacion.slcd_fecha_postulacion ??
              null,

            estado:
              estadosPorId.get(
                postulacion.slcd_estado_solicitud_candidato_id ??
                  0,
              ) ??
              'Sin estado',
          };
        },
      );

    /**
     * Decisión UX/UI M3
     *
     * La postulación más reciente es solamente el resumen
     * utilizado en las columnas simples de la tabla.
     */
    const principal =
      postulaciones[0];

    const habilidadPrincipal =
      this.obtenerHabilidadPrincipal(habilidadesApi);

    return {
      idCandidato:
        String(candidato.cand_id),

      postulaciones,

      match:
        principal?.match ?? 0,

      matchDisponible:
        principal?.matchDisponible ?? false,

      nombre,

      correo:
        candidato.cand_email ??
        'Sin correo',

      telefono:
        candidato.cand_telefono ??
        '',

      cargo:
        principal?.cargo ??
        candidato.cand_titulo ??
        'Sin cargo',

      fechaPostulacion:
        principal?.fechaPostulacion ??
        '',

      estado:
        principal?.estado ??
        'Sin postulación',

      estadoUsuario:
        candidato.cand_estado_usuario_id === 1
          ? 'Activo'
          : 'Inactivo',

      disponibilidad:
        disponibilidadesPorId.get(
          candidato.cand_disponibilidad_id ??
            0,
        ) ??
        'Sin disponibilidad',

      renta:
        principal?.renta ?? 0,

      nivel:
        habilidadPrincipal?.nivel ??
        this.niveles[0] ??
        'Sin nivel',

      experiencia:
        habilidadPrincipal?.experiencia ?? 0,
    };
  }

  private obtenerHabilidadPrincipal(
    habilidades: HabilidadCandidatoApi[],
  ) {
    const ordenadas = [...habilidades]
      .filter(
        (habilidad) =>
          habilidad.cdhb_nivel_habilidad_id != null ||
          habilidad.cdhb_anios_experiencia != null,
      )
      .sort(
        (a, b) =>
          Number(b.cdhb_anios_experiencia ?? 0) -
          Number(a.cdhb_anios_experiencia ?? 0),
      );

    const principal = ordenadas[0];

    if (!principal) {
      return null;
    }

    return {
      nivel:
        principal.nivel_habilidad?.nvhb_nombre ??
        this.niveles[0] ??
        'Sin nivel',
      experiencia:
        Number(principal.cdhb_anios_experiencia ?? 0),
    };
  }

  private filtrosIniciales():
    FiltrosCandidatos {
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

  private normalizar(
    valor: string,
  ) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(
        /[\u0300-\u036f]/g,
        '',
      );
  }

  private normalizarCodigoSolicitud(
    codigo?: string | null,
    solicitudId?: number | null,
  ) {
    const limpio = codigo?.trim();

    if (!limpio) {
      return solicitudId
        ? `SOL-${String(solicitudId).padStart(6, '0')}`
        : '';
    }

    const coincidencia = limpio.match(/^SOL-(\d+)$/i);

    if (!coincidencia) {
      return limpio;
    }

    return `SOL-${coincidencia[1].padStart(6, '0')}`;
  }

  private fechaApiTimestamp(
    fecha?: string | null,
  ) {
    if (!fecha) {
      return 0;
    }

    const timestamp =
      new Date(fecha).getTime();

    return Number.isNaN(timestamp)
      ? 0
      : timestamp;
  }

  private formatearFecha(
    fecha?: string | null,
  ) {
    if (!fecha) {
      return '';
    }

    const fechaNormalizada =
      new Date(fecha);

    return Number.isNaN(
      fechaNormalizada.getTime(),
    )
      ? fecha
      : new Intl.DateTimeFormat(
          'es-CL',
        ).format(
          fechaNormalizada,
        );
  }

  private normalizarCodigoBusqueda(valor: string) {
    return valor.trim().toUpperCase();
  }
}
