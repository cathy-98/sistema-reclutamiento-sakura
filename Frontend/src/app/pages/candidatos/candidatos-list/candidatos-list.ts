import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import {
  catchError,
  finalize,
  forkJoin,
  map,
  of,
  switchMap,
  take,
  timeout,
} from 'rxjs';

import {
  EntrevistaPayload,
  EntrevistasService,
} from '../../../services/entrevistas.service';

import { CatalogosService } from '../../../services/catalogos.service';

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
export class CandidatosList implements OnInit {
  cargando = false;
  importandoCvs = false;
  errorCarga = '';
  alerta: AlertaUi | null = null;

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
      width: 90,
      type: 'match',
      value: (candidato) => `${candidato.match}%`,
      className: (candidato) =>
        this.matchClase(candidato.match),
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
        candidato.estadoUsuario !== 'Inactivo',
    },
  ];

  /**
   * Datos de respaldo para mantener la pantalla operativa
   * cuando el backend local no esté disponible.
   *
   * Integración M3:
   * incluso los datos mock respetan ahora la relación
   * Candidato -> múltiples Postulaciones.
   */
  private readonly candidatosRespaldo: Candidato[] = [
    {
      idCandidato: '1',

      postulaciones: [
        {
          idPostulacion: 1,
          idSolicitud: 21,
          codigoSolicitud: 'SOL-000021',
          cargo: 'Frontend',
          match: 90,
          renta: 800000,
          fechaPostulacion: '18/05/2025',
          fechaPostulacionRaw: '2025-05-18',
          estado: 'En revision',
        },
        {
          idPostulacion: 2,
          idSolicitud: 34,
          codigoSolicitud: 'SOL-000034',
          cargo: 'Frontend Senior',
          match: 84,
          renta: 950000,
          fechaPostulacion: '10/05/2025',
          fechaPostulacionRaw: '2025-05-10',
          estado: 'En entrevista',
        },
        {
          idPostulacion: 3,
          idSolicitud: 40,
          codigoSolicitud: 'SOL-000040',
          cargo: 'Angular Developer',
          match: 78,
          renta: 900000,
          fechaPostulacion: '03/05/2025',
          fechaPostulacionRaw: '2025-05-03',
          estado: 'En revision',
        },
      ],

      match: 90,
      nombre: 'Macarena Lopez',
      correo: 'macarena.lopez@mail.com',
      telefono: '+56 9 5634 8547',
      cargo: 'Frontend',
      fechaPostulacion: '18/05/2025',
      estado: 'En revision',
      estadoUsuario: 'Activo',
      disponibilidad: 'Inmediata',
      renta: 800000,
      nivel: 'Junior',
      experiencia: 4,
    },

    {
      idCandidato: '2',

      postulaciones: [
        {
          idPostulacion: 4,
          idSolicitud: 21,
          codigoSolicitud: 'SOL-000021',
          cargo: 'Frontend',
          match: 80,
          renta: 950000,
          fechaPostulacion: '18/05/2025',
          fechaPostulacionRaw: '2025-05-18',
          estado: 'En entrevista',
        },
      ],

      match: 80,
      nombre: 'Valentina Rojas',
      correo: 'valentina.rojas@mail.com',
      telefono: '+56 9 6721 1184',
      cargo: 'Frontend',
      fechaPostulacion: '18/05/2025',
      estado: 'En entrevista',
      estadoUsuario: 'Activo',
      disponibilidad: '2 semanas',
      renta: 950000,
      nivel: 'Senior',
      experiencia: 5,
    },

    {
      idCandidato: '3',

      postulaciones: [
        {
          idPostulacion: 5,
          idSolicitud: 19,
          codigoSolicitud: 'SOL-000019',
          cargo: 'Backend',
          match: 68,
          renta: 1200000,
          fechaPostulacion: '17/05/2025',
          fechaPostulacionRaw: '2025-05-17',
          estado: 'En entrevista',
        },
        {
          idPostulacion: 6,
          idSolicitud: 25,
          codigoSolicitud: 'SOL-000025',
          cargo: 'Backend Senior',
          match: 70,
          renta: 1300000,
          fechaPostulacion: '11/05/2025',
          fechaPostulacionRaw: '2025-05-11',
          estado: 'En revision',
        },
      ],

      match: 68,
      nombre: 'Diego Martinez',
      correo: 'diego.martinez@mail.com',
      telefono: '+56 9 7765 4402',
      cargo: 'Backend',
      fechaPostulacion: '17/05/2025',
      estado: 'En entrevista',
      estadoUsuario: 'Activo',
      disponibilidad: 'Inmediata',
      renta: 1200000,
      nivel: 'Senior',
      experiencia: 6,
    },

    {
      idCandidato: '4',

      postulaciones: [
        {
          idPostulacion: 7,
          idSolicitud: 18,
          codigoSolicitud: 'SOL-000018',
          cargo: 'UX Research',
          match: 55,
          renta: 900000,
          fechaPostulacion: '16/05/2025',
          fechaPostulacionRaw: '2025-05-16',
          estado: 'En revision',
        },
      ],

      match: 55,
      nombre: 'Camila Fuentes',
      correo: 'camila.fuentes@mail.com',
      telefono: '+56 9 3324 9811',
      cargo: 'UX Research',
      fechaPostulacion: '16/05/2025',
      estado: 'En revision',
      estadoUsuario: 'Activo',
      disponibilidad: '1 mes',
      renta: 900000,
      nivel: 'Semi senior',
      experiencia: 3,
    },

    {
      idCandidato: '5',

      postulaciones: [
        {
          idPostulacion: 8,
          idSolicitud: 17,
          codigoSolicitud: 'SOL-000017',
          cargo: 'QA Automation',
          match: 42,
          renta: 1100000,
          fechaPostulacion: '15/05/2025',
          fechaPostulacionRaw: '2025-05-15',
          estado: 'Descartado',
        },
      ],

      match: 42,
      nombre: 'Sebastian Araya',
      correo: 'sebastian.araya@mail.com',
      telefono: '+56 9 4218 7256',
      cargo: 'QA Automation',
      fechaPostulacion: '15/05/2025',
      estado: 'Descartado',
      estadoUsuario: 'Activo',
      disponibilidad: '2 semanas',
      renta: 1100000,
      nivel: 'Junior',
      experiencia: 2,
    },
  ];

  constructor(
    private currencyCl: CurrencyClPipe,
    private router: Router,
    private entrevistasService: EntrevistasService,
    private catalogosService: CatalogosService,
    private candidatosService: CandidatosService,
    private solicitudesService: SolicitudesService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.cargarCandidatos();
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
          }) => {
            if (candidatos.length === 0) {
              return of({
                candidatos,
                estados,
                disponibilidades,
                niveles,
                solicitudes,

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
              },
            ]),
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
            this.errorCarga =
              'No se pudo cargar candidatos reales. Se muestran datos de respaldo.';

            this.candidatos =
              this.candidatosRespaldo;

            this.cdr.detectChanges();

            return;
          }

          this.candidatos = candidatos.map(
            (candidato) =>
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
          );

          this.cdr.detectChanges();
        },

        error: (error) => {
          console.error(
            'Error inesperado cargando candidatos:',
            error,
          );

          this.errorCarga =
            'No se pudo cargar candidatos reales. Se muestran datos de respaldo.';

          this.candidatos =
            this.candidatosRespaldo;

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

    const match = Number(
      this.filtros.match,
    );

    const experiencia = Number(
      this.filtros.experiencia,
    );

    return this.candidatos.filter((candidato) => {
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
        candidato.postulaciones.some(
          (postulacion) =>
            postulacion.estado ===
            this.filtros.estado,
        );

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
        this.obtenerPostulacionPrincipal(
          candidato,
        );

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
        this.obtenerPostulacionPrincipal(
          candidato,
        );

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

    this.abrirAgendaEntrevista(
      candidatos,
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
  ) {
    this.candidatosAgenda =
      candidatos.map((candidato) => {
        const postulacion =
          this.obtenerPostulacionPrincipal(
            candidato,
          );

        return {
          id:
            this.obtenerIdCandidato(candidato),

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

  procesarArchivosCv() {
    if (this.archivosCv.length === 0 || this.importandoCvs) {
      return;
    }

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

  matchClase(match: number) {
    if (match >= 75) {
      return 'is-high';
    }

    if (match >= 55) {
      return 'is-medium';
    }

    return 'is-low';
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
   * SOL-000021
   * SOL-000021 · SOL-000034
   * SOL-000021 · SOL-000034 · +2
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

          const matchNumero =
            Number(
              postulacion.slcd_puntaje_compatibilidad ??
                0,
            );

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
              Number.isFinite(matchNumero)
                ? matchNumero
                : 0,

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
}
