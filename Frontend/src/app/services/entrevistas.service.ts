import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { forkJoin, map, throwError } from 'rxjs';

export type EstadoEntrevista = string;
export type TipoEntrevista = string;


/**
 * Integración M5
 *
 * Modelo físico/API de entrevista recibido desde Backend.
 *
 * Backend puede devolver múltiples tipos asociados
 * a una misma entrevista.
 */
export interface CitaEntrevistaApi {
  ctev_id: number;
  ctev_solicitud_candidato_id: number | null;
  ctev_tipo_entrevista_id: number | null;
  ctev_estado_entrevista_id: number | null;
  ctev_fecha_hora_inicio: string | null;
  ctev_fecha_hora_fin: string | null;
  ctev_fecha_creacion?: string | null;
  ctev_enlace_reunion?: string | null;
  ctev_comentarios_convocatoria?: string | null;
  ctev_titulo_evento?: string | null;
}


export interface CitaEntrevistaPayload {
  ctev_solicitud_candidato_id: number;
  ctev_tipo_entrevista_id: number;
  ctev_estado_entrevista_id?: number | null;
  ctev_fecha_hora_inicio: string;
  ctev_fecha_hora_fin: string;
  ctev_enlace_reunion?: string | null;
  ctev_comentarios_convocatoria?: string | null;
  ctev_titulo_evento: string;
}


/**
 * Integración M5
 *
 * Representa cada tipo seleccionado desde el formulario.
 *
 * Ejemplo:
 *
 * {
 *   tipoEntrevistaId: 1,
 *   entrevistadorIds: [4, 7]
 * }
 */
export interface TipoEntrevistaPayload {
  tipoEntrevistaId: number;
  entrevistadorIds: number[];
}


export interface ProgramacionTipoEntrevistaPayload extends TipoEntrevistaPayload {
  nombreTipo: string;
  asunto: string;
  fecha: string;
  horaInicio: string;
  horaFin: string;
  duracion: string;
  linkReunion?: string;
  observacion?: string;
}


export interface EntrevistaApi {
  entrevista_id: number;
  solicitud_candidato_id: number;
  solicitud_id: number;

  solicitud_codigo?: string | null;
  solicitud_cargo?: string | null;
  cargo?: string | null;
  cargo_nombre?: string | null;
  vacante_cargo?: string | null;

  candidato_id?: number;
  candidato_nombre?: string;
  candidato_email?: string;

  estado_id?: number;
  estado_nombre?: string;
  estado?: string;

  fecha_hora_inicio: string;
  fecha_hora_fin: string;

  fecha_creacion?: string;
  fecha_actualizacion?: string | null;

  titulo_evento: string;

  enlace_reunion?: string | null;
  comentarios_convocatoria?: string | null;
  motivo_estado?: string | null;

  usuario_creador_id?: number | null;

  /**
   * Integración M5
   *
   * Una entrevista puede contener múltiples tipos.
   * Cada tipo puede tener distintos entrevistadores.
   */
  tipos?: {
    tipo_entrevista_id: number;
    nombre: string;
    descripcion?: string | null;

    entrevistadores?: {
      usuario_id: number;
      nombres: string;
      apellido_paterno: string;
      email: string;
    }[];
  }[];

  evaluaciones?: EvaluacionEntrevistaApi[];
}


export interface EvaluacionEntrevistaApi {
  evaluacion_id: number;
  entrevista_id: number;

  tipo_entrevista_id?: number | null;
  tipo_entrevista_nombre?: string | null;

  usuario_id?: number | null;
  usuario_nombre?: string | null;

  resultado_id: number;
  resultado_nombre: string;

  observacion?: string | null;

  fecha_creacion?: string | null;
  fecha_actualizacion?: string | null;
}


/**
 * Modelo visual utilizado por tablas y pantallas.
 */
export interface EntrevistaResumen {
  id: string;

  solicitudCandidatoId?: number;
  candidatoId?: number;

  idSolicitud: string;

  candidato: string;
  candidatoCorreo?: string;

  estado: EstadoEntrevista;

  /**
   * Se mantiene como string para la tabla.
   *
   * Ejemplo:
   * RRHH, Técnica
   */
  tipo: TipoEntrevista;

  /**
   * Resultado formateado por tipo/área.
   *
   * Ejemplo:
   * RRHH: Aprobado | Técnica: Pendiente
   */
  resultadoEntrevista: string;

  asunto: string;
  cargo: string;

  fecha: string;
  horaInicio: string;
  horaFin: string;

  entrevistador: string;

  linkReunion?: string;
  observacion?: string;

  estadoPostulacion?: string;
  estadoSolicitud?: string;
}


/**
 * Integración M5
 *
 * Payload utilizado desde la UI.
 *
 * "tiposEntrevista" es ahora la fuente principal para creación.
 *
 * tipoEntrevistaId y entrevistadorIds se mantienen temporalmente
 * para compatibilidad con pantallas antiguas.
 */
export interface EntrevistaPayload {
  solicitudCandidatoId?: number;

  solicitudesCandidatosIds?: number[];

  tiposEntrevista?: TipoEntrevistaPayload[];

  /**
   * Decisión UX/UI M5
   *
   * Cuando cada tipo necesita agenda propia, la UI crea
   * una entrevista independiente por cada programación.
   */
  programacionesPorTipo?: ProgramacionTipoEntrevistaPayload[];

  /**
   * Compatibilidad legacy.
   */
  tipoEntrevistaId?: number;
  entrevistadorIds?: number[];

  idSolicitud: string;

  candidato: string;

  /**
   * Texto visual.
   *
   * Puede contener:
   * "RRHH, Técnica"
   */
  tipo: TipoEntrevista;

  asunto: string;
  cargo: string;

  fecha: string;
  horaInicio: string;
  horaFin: string;

  entrevistador: string;

  linkReunion?: string;
  observacion?: string;
}


/**
 * Payload real esperado por POST /entrevistas.
 */
interface EntrevistaCreateRequest {
  solicitud_candidato_id: number;

  fecha_hora_inicio: string;
  fecha_hora_fin: string;

  titulo_evento: string;

  enlace_reunion?: string | null;

  comentarios_convocatoria?: string | null;

  /**
   * Integración M5
   *
   * Backend soporta múltiples tipos.
   */
  tipos: {
    tipo_entrevista_id: number;
    usuarios_ids: number[];
  }[];
}


/**
 * Payload real esperado por agenda masiva.
 */
interface EntrevistaMasivaCreateRequest
  extends Omit<
    EntrevistaCreateRequest,
    'solicitud_candidato_id'
  > {
  solicitudes_candidatos_ids: number[];
}


@Injectable({
  providedIn: 'root',
})
export class EntrevistasService {
  private readonly apiUrl = '/api';

  constructor(
    private http: HttpClient,
  ) {}


  /**
   * Integración M5
   *
   * Listado administrativo de entrevistas.
   *
   * Backend incluye tipos y evaluaciones para poder
   * mostrar resultado por área.
   */
  listar() {
    return this.http
      .get<EntrevistaApi[]>(
        `${this.apiUrl}/entrevistas`,
      )
      .pipe(
        map((entrevistas) =>
          entrevistas.map(
            (entrevista) =>
              this.mapearResumen(
                entrevista,
              ),
          ),
        ),
      );
  }


  listarEvaluaciones(
    entrevistaId:
      string | number,
  ) {
    return this.http.get<
      EvaluacionEntrevistaApi[]
    >(
      `${this.apiUrl}/entrevistas/${entrevistaId}/evaluaciones`,
    );
  }


  obtener(
    entrevistaId:
      string | number,
  ) {
    return this.http.get<EntrevistaApi>(
      `${this.apiUrl}/entrevistas/${entrevistaId}`,
    );
  }


  listarPorCandidato(
    candidatoId: string,
  ) {
    return this.http.get<
      EntrevistaApi[]
    >(
      `${this.apiUrl}/candidatos/${candidatoId}/entrevistas`,
    );
  }


  listarMisEntrevistas() {
    return this.http.get<
      EntrevistaApi[]
    >(
      `${this.apiUrl}/candidatos/me/entrevistas`,
    );
  }


  /**
   * Integración M5
   *
   * Creación individual.
   *
   * crearPayloadApi transforma el modelo UI
   * al contrato real Backend.
   */
  crear(
    payload: EntrevistaPayload,
  ) {
    if (
      (
        payload.programacionesPorTipo ??
        []
      ).length > 0
    ) {
      return this.crearPorTipo(
        payload,
      ).pipe(
        map((entrevistas) =>
          entrevistas[0],
        ),
      );
    }

    const body =
      this.crearPayloadApi(
        payload,
      );

    if (!body) {
      return throwError(
        () =>
          new Error(
            'Faltan IDs reales de postulación, tipos de entrevista o entrevistadores.',
          ),
      );
    }

    return this.http
      .post<EntrevistaApi>(
        `${this.apiUrl}/entrevistas`,
        body,
      )
      .pipe(
        map((entrevista) =>
          this.mapearResumen(
            entrevista,
          ),
        ),
      );
  }


  /**
   * Integración M5
   *
   * Backend no soporta fecha/link/título por item dentro de tipos[].
   * Para agendas distintas se crea una cita independiente por tipo.
   */
  crearPorTipo(
    payload:
      EntrevistaPayload,
  ) {
    const bodies =
      this.crearPayloadsPorTipoApi(
        payload,
      );

    if (bodies.length === 0) {
      return throwError(
        () =>
          new Error(
            'Faltan programaciones completas por tipo de entrevista.',
          ),
      );
    }

    return forkJoin(
      bodies.map((body) =>
        this.http.post<EntrevistaApi>(
          `${this.apiUrl}/entrevistas`,
          body,
        ),
      ),
    ).pipe(
      map((entrevistas) =>
        entrevistas.map((entrevista) =>
          this.mapearResumen(
            entrevista,
          ),
        ),
      ),
    );
  }


  /**
   * Integración M5
   *
   * Agenda masiva:
   * utiliza el mismo conjunto de tipos/entrevistadores
   * para todas las postulaciones seleccionadas.
   */
  crearMasiva(
    payloads:
      EntrevistaPayload[],
  ) {
    const primero =
      payloads[0];

    if (
      (
        primero?.programacionesPorTipo ??
        []
      ).length > 0
    ) {
      return this.crearMasivaPorTipo(
        payloads,
      );
    }

    const solicitudesCandidatosIds =
      payloads
        .map(
          (payload) =>
            payload.solicitudCandidatoId,
        )
        .filter(
          (
            id,
          ): id is number =>
            typeof id ===
              'number' &&
            id > 0,
        );

    if (
      !primero ||
      solicitudesCandidatosIds.length !==
        payloads.length
    ) {
      return throwError(
        () =>
          new Error(
            'Faltan IDs reales de postulación para la agenda masiva.',
          ),
      );
    }

    const base =
      this.crearPayloadApi(
        primero,
      );

    if (!base) {
      return throwError(
        () =>
          new Error(
            'Faltan tipos de entrevista o entrevistadores.',
          ),
      );
    }

    const body:
      EntrevistaMasivaCreateRequest =
      {
        solicitudes_candidatos_ids:
          solicitudesCandidatosIds,

        fecha_hora_inicio:
          base.fecha_hora_inicio,

        fecha_hora_fin:
          base.fecha_hora_fin,

        titulo_evento:
          base.titulo_evento,

        enlace_reunion:
          base.enlace_reunion,

        comentarios_convocatoria:
          base.comentarios_convocatoria,

        tipos:
          base.tipos,
      };

    return this.http
      .post<{
        entrevistas:
          EntrevistaApi[];
      }>(
        `${this.apiUrl}/entrevistas/agendar-masivo`,
        body,
      )
      .pipe(
        map((respuesta) =>
          respuesta.entrevistas.map(
            (entrevista) =>
              this.mapearResumen(
                entrevista,
              ),
          ),
        ),
      );
  }


  /**
   * Integración M5
   *
   * Agenda masiva con agendas por tipo:
   * se llama /entrevistas/agendar-masivo una vez por tipo,
   * con un único tipo en tipos[] y su horario propio.
   */
  crearMasivaPorTipo(
    payloads:
      EntrevistaPayload[],
  ) {
    const primero =
      payloads[0];

    const solicitudesCandidatosIds =
      payloads
        .map((payload) =>
          payload.solicitudCandidatoId,
        )
        .filter(
          (
            id,
          ): id is number =>
            typeof id === 'number' &&
            id > 0,
        );

    if (
      !primero ||
      solicitudesCandidatosIds.length !==
        payloads.length
    ) {
      return throwError(
        () =>
          new Error(
            'Faltan IDs reales de postulación para la agenda masiva.',
          ),
      );
    }

    const bodies =
      this.crearPayloadsPorTipoApi(
        primero,
      );

    if (bodies.length === 0) {
      return throwError(
        () =>
          new Error(
            'Faltan programaciones completas por tipo de entrevista.',
          ),
      );
    }

    return forkJoin(
      bodies.map((base) => {
        const body:
          EntrevistaMasivaCreateRequest =
          {
            solicitudes_candidatos_ids:
              solicitudesCandidatosIds,
            fecha_hora_inicio:
              base.fecha_hora_inicio,
            fecha_hora_fin:
              base.fecha_hora_fin,
            titulo_evento:
              base.titulo_evento,
            enlace_reunion:
              base.enlace_reunion,
            comentarios_convocatoria:
              base.comentarios_convocatoria,
            tipos:
              base.tipos,
          };

        return this.http.post<{
          entrevistas:
            EntrevistaApi[];
        }>(
          `${this.apiUrl}/entrevistas/agendar-masivo`,
          body,
        );
      }),
    ).pipe(
      map((respuestas) =>
        respuestas.flatMap((respuesta) =>
          respuesta.entrevistas.map((entrevista) =>
            this.mapearResumen(
              entrevista,
            ),
          ),
        ),
      ),
    );
  }


  /**
   * Actualización de información básica de entrevista.
   */
  actualizarEntrevista(
    entrevistaId:
      string | number,

    payload: {
      titulo_evento?: string;
      enlace_reunion?:
        string | null;
      comentarios_convocatoria?:
        string | null;
    },
  ) {
    return this.http.patch<
      EntrevistaApi
    >(
      `${this.apiUrl}/entrevistas/${entrevistaId}`,
      payload,
    );
  }


  /**
   * Integración M5
   *
   * Evaluación por tipo.
   *
   * La evaluación NO es global para toda la entrevista.
   */
  crearEvaluacion(
    entrevistaId:
      string | number,

    tipoId:
      string | number,

    payload: {
      nombre_resultado_id:
        number;

      observacion?:
        string | null;
    },
  ) {
    return this.http.post<
      EvaluacionEntrevistaApi
    >(
      `${this.apiUrl}/entrevistas/${entrevistaId}/tipos/${tipoId}/evaluar`,
      payload,
    );
  }


  actualizarEvaluacion(
    entrevistaId:
      string | number,

    tipoId:
      string | number,

    payload: {
      nombre_resultado_id?:
        number;

      observacion?:
        string | null;
    },
  ) {
    return this.http.patch<
      EvaluacionEntrevistaApi
    >(
      `${this.apiUrl}/entrevistas/${entrevistaId}/tipos/${tipoId}/evaluacion`,
      payload,
    );
  }


  /**
   * Integración M5
   *
   * Reprogramación persistente.
   *
   * La UI debe impedir fechas anteriores a hoy.
   * Backend sigue validando el contrato final.
   */
  reprogramar(
    id: string,
    fecha: string,
    horaInicio: string,
    horaFin: string,
    observacion: string,
  ) {
    return this.http
      .post<EntrevistaApi>(
        `${this.apiUrl}/entrevistas/${id}/reprogramar`,
        {
          fecha_hora_inicio:
            this.unirFechaHora(
              fecha,
              horaInicio,
            ),

          fecha_hora_fin:
            this.unirFechaHora(
              fecha,
              horaFin,
            ),

          motivo:
            observacion,
        },
      )
      .pipe(
        map((entrevista) =>
          this.mapearResumen(
            entrevista,
          ),
        ),
      );
  }


  /**
   * Integración M5
   *
   * Cancelación persistente.
   */
  cancelar(
    id: string,
    observacion: string,
  ) {
    return this.http
      .post<EntrevistaApi>(
        `${this.apiUrl}/entrevistas/${id}/cancelar`,
        {
          motivo:
            observacion,
        },
      )
      .pipe(
        map((entrevista) =>
          this.mapearResumen(
            entrevista,
          ),
        ),
      );
  }


  /**
   * Integración M5
   *
   * Pendiente -> Confirmada.
   */
  confirmar(
    id: string,
  ) {
    return this.http
      .post<EntrevistaApi>(
        `${this.apiUrl}/entrevistas/${id}/confirmar`,
        {},
      )
      .pipe(
        map((entrevista) =>
          this.mapearResumen(
            entrevista,
          ),
        ),
      );
  }


  /**
   * Integración M5
   *
   * Marca la entrevista como No asistió.
   */
  noAsistio(
    id: string,
    motivo: string,
  ) {
    return this.http
      .post<EntrevistaApi>(
        `${this.apiUrl}/entrevistas/${id}/no-asistio`,
        {
          motivo,
        },
      )
      .pipe(
        map((entrevista) =>
          this.mapearResumen(
            entrevista,
          ),
        ),
      );
  }


  /**
   * Integración M5
   *
   * Marca la entrevista como Realizada.
   *
   * Una vez realizada, la UI puede habilitar
   * evaluación por cada tipo asociado.
   */
  realizar(
    id: string,
  ) {
    return this.http
      .post<EntrevistaApi>(
        `${this.apiUrl}/entrevistas/${id}/realizar`,
        {},
      )
      .pipe(
        map((entrevista) =>
          this.mapearResumen(
            entrevista,
          ),
        ),
      );
  }


  /**
   * ---------------------------------------------------------
   * MAPEO VISUAL
   * ---------------------------------------------------------
   */

  private mapearResumen(
    entrevista:
      EntrevistaApi,
  ): EntrevistaResumen {
    const inicio =
      this.separarFechaHora(
        entrevista.fecha_hora_inicio,
      );

    const fin =
      this.separarFechaHora(
        entrevista.fecha_hora_fin,
      );

    const tipos =
      this.nombresTipos(
        entrevista,
      );

    return {
      id:
        String(
          entrevista.entrevista_id,
        ),

      solicitudCandidatoId:
        entrevista.solicitud_candidato_id,

      candidatoId:
        entrevista.candidato_id,

      idSolicitud:
        entrevista.solicitud_codigo ??
        `SOL-${String(
          entrevista.solicitud_id,
        ).padStart(
          6,
          '0',
        )}`,

      candidato:
        entrevista.candidato_nombre ??
        entrevista.candidato_email ??
        'Candidato sin nombre',

      candidatoCorreo:
        entrevista.candidato_email ??
        undefined,

      estado:
        entrevista.estado_nombre ??
        entrevista.estado ??
        'Sin estado',

      tipo:
        tipos ||
        'Sin tipo',

      resultadoEntrevista:
        this.formatearResultados(
          entrevista,
        ),

      asunto:
        entrevista.titulo_evento ||
        'Entrevista',

      cargo:
        entrevista.solicitud_cargo ??
        entrevista.cargo ??
        entrevista.cargo_nombre ??
        entrevista.vacante_cargo ??
        'Sin cargo',

      fecha:
        inicio.fecha,

      horaInicio:
        inicio.hora,

      horaFin:
        fin.hora,

      entrevistador:
        this.formatearEntrevistadores(
          entrevista,
        ) ||
        'Sin entrevistador',

      linkReunion:
        entrevista.enlace_reunion ??
        undefined,

      observacion:
        entrevista.comentarios_convocatoria ??
        undefined,
    };
  }


  /**
   * Integración M5
   *
   * Devuelve todos los tipos sin duplicados.
   *
   * Ejemplo:
   * RRHH, Técnica
   */
  private nombresTipos(
    entrevista:
      EntrevistaApi,
  ) {
    const nombres = [
      ...(
        entrevista.tipos?.map(
          (tipo) =>
            tipo.nombre,
        ) ?? []
      ),

      ...(
        entrevista.evaluaciones?.map(
          (evaluacion) =>
            evaluacion.tipo_entrevista_nombre,
        ) ?? []
      ),
    ].filter(
      (
        nombre,
      ): nombre is string =>
        Boolean(nombre),
    );

    return Array.from(
      new Set(nombres),
    ).join(', ');
  }


  /**
   * Integración M5
   *
   * Consolida entrevistadores de todos los tipos
   * para la vista resumen.
   */
  private formatearEntrevistadores(
    entrevista:
      EntrevistaApi,
  ) {
    const nombres =
      entrevista.tipos
        ?.flatMap(
          (tipo) =>
            tipo.entrevistadores ??
            [],
        )
        .map(
          (entrevistador) =>
            [
              entrevistador.nombres,
              entrevistador.apellido_paterno,
            ]
              .filter(Boolean)
              .join(' '),
        )
        .filter(Boolean) ??
      [];

    return Array.from(
      new Set(nombres),
    ).join(', ');
  }


  /**
   * Integración M5
   *
   * Formatea resultados por tipo/área.
   *
   * Ejemplo:
   *
   * RRHH: Aprobado | Técnica: No aprobado
   */
  private formatearResultados(
    entrevista:
      EntrevistaApi,
  ) {
    const evaluaciones =
      entrevista.evaluaciones ??
      [];

    if (
      (
        entrevista.tipos?.length ??
        0
      ) === 0 &&
      evaluaciones.length === 0
    ) {
      return 'Sin resultado';
    }

    const tipos =
      entrevista.tipos ?? [];

    if (tipos.length === 0) {
      return evaluaciones
        .map(
          (evaluacion) => {
            const tipo =
              evaluacion.tipo_entrevista_nombre ||
              'Sin tipo';

            const usuario =
              evaluacion.usuario_nombre
                ? ` - ${evaluacion.usuario_nombre}`
                : '';

            return `${tipo}: ${evaluacion.resultado_nombre}${usuario}`;
          },
        )
        .join(' | ');
    }

    return tipos
      .map((tipo) => {
        const evaluacionesTipo =
          evaluaciones.filter(
            (evaluacion) =>
              evaluacion.tipo_entrevista_id ===
              tipo.tipo_entrevista_id,
          );

        // Integración M5: "Pendiente" indica ausencia de evaluación para el tipo, no un resultado global inventado.
        if (
          evaluacionesTipo.length ===
          0
        ) {
          return `${tipo.nombre}: Pendiente`;
        }

        const resultados =
          evaluacionesTipo
            .map((evaluacion) => {
              const usuario =
                evaluacion.usuario_nombre
                  ? ` - ${evaluacion.usuario_nombre}`
                  : '';

              return `${evaluacion.resultado_nombre}${usuario}`;
            })
            .join(', ');

        return `${tipo.nombre}: ${resultados}`;
      })
      .join(' | ');
  }


  private separarFechaHora(
    valor?:
      string | null,
  ) {
    if (!valor) {
      return {
        fecha: 'Sin fecha',
        hora: 'Sin hora',
      };
    }

    const fecha =
      new Date(valor);

    if (
      Number.isNaN(
        fecha.getTime(),
      )
    ) {
      const [
        soloFecha,
        soloHora =
          'Sin hora',
      ] =
        valor.split('T');

      return {
        fecha:
          soloFecha ||
          'Sin fecha',

        hora:
          soloHora.slice(
            0,
            5,
          ) ||
          'Sin hora',
      };
    }

    return {
      fecha:
        fecha
          .toISOString()
          .slice(
            0,
            10,
          ),

      hora:
        fecha
          .toTimeString()
          .slice(
            0,
            5,
          ),
    };
  }


  private unirFechaHora(
    fecha: string,
    hora: string,
  ) {
    return `${fecha}T${hora}:00`;
  }


  /**
   * ---------------------------------------------------------
   * PAYLOAD API M5
   * ---------------------------------------------------------
   *
   * Convierte el modelo visual de Angular al contrato real:
   *
   * {
   *   solicitud_candidato_id: 14,
   *   tipos: [
   *     {
   *       tipo_entrevista_id: 1,
   *       usuarios_ids: [4]
   *     },
   *     {
   *       tipo_entrevista_id: 2,
   *       usuarios_ids: [7, 8]
   *     }
   *   ]
   * }
   */
  private crearPayloadApi(
    payload:
      EntrevistaPayload,
  ):
    EntrevistaCreateRequest | null {
    const solicitudCandidatoId =
      payload.solicitudCandidatoId;

    if (
      !solicitudCandidatoId
    ) {
      return null;
    }


    /**
     * Integración M5
     *
     * Fuente principal:
     * tiposEntrevista[]
     */
    let tipos =
      payload.tiposEntrevista
        ?.filter(
          (tipo) =>
            tipo.tipoEntrevistaId >
              0 &&
            tipo.entrevistadorIds.length >
              0,
        )
        .map(
          (tipo) => ({
            tipo_entrevista_id:
              tipo.tipoEntrevistaId,

            usuarios_ids:
              tipo.entrevistadorIds,
          }),
        ) ?? [];


    /**
     * Compatibilidad temporal.
     *
     * Si una pantalla antigua todavía envía
     * tipoEntrevistaId + entrevistadorIds,
     * se transforma al nuevo arreglo.
     */
    if (
      tipos.length === 0 &&
      payload.tipoEntrevistaId &&
      (
        payload.entrevistadorIds ??
        []
      ).length >
        0
    ) {
      tipos = [
        {
          tipo_entrevista_id:
            payload.tipoEntrevistaId,

          usuarios_ids:
            payload.entrevistadorIds ??
            [],
        },
      ];
    }


    if (
      tipos.length === 0
    ) {
      return null;
    }


    return {
      solicitud_candidato_id:
        solicitudCandidatoId,

      fecha_hora_inicio:
        this.unirFechaHora(
          payload.fecha,
          payload.horaInicio,
        ),

      fecha_hora_fin:
        this.unirFechaHora(
          payload.fecha,
          payload.horaFin,
        ),

      titulo_evento:
        payload.asunto,

      enlace_reunion:
        payload.linkReunion ||
        null,

      comentarios_convocatoria:
        payload.observacion ||
        null,

      tipos,
    };
  }


  private crearPayloadsPorTipoApi(
    payload:
      EntrevistaPayload,
  ) {
    const solicitudCandidatoId =
      payload.solicitudCandidatoId;

    if (!solicitudCandidatoId) {
      return [];
    }

    return (
      payload.programacionesPorTipo ??
      []
    )
      .filter(
        (programacion) =>
          programacion.tipoEntrevistaId > 0 &&
          programacion.entrevistadorIds.length > 0 &&
          Boolean(programacion.fecha) &&
          Boolean(programacion.horaInicio) &&
          Boolean(programacion.horaFin) &&
          Boolean(programacion.asunto?.trim()),
      )
      .map(
        (programacion):
          EntrevistaCreateRequest => ({
          solicitud_candidato_id:
            solicitudCandidatoId,
          fecha_hora_inicio:
            this.unirFechaHora(
              programacion.fecha,
              programacion.horaInicio,
            ),
          fecha_hora_fin:
            this.unirFechaHora(
              programacion.fecha,
              programacion.horaFin,
            ),
          titulo_evento:
            programacion.asunto.trim(),
          enlace_reunion:
            programacion.linkReunion ||
            null,
          comentarios_convocatoria:
            programacion.observacion ||
            null,
          tipos: [
            {
              tipo_entrevista_id:
                programacion.tipoEntrevistaId,
              usuarios_ids:
                programacion.entrevistadorIds,
            },
          ],
        }),
      );
  }
}
