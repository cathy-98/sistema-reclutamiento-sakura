import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, forkJoin, map, of, switchMap } from 'rxjs';
import { CatalogosService } from './catalogos.service';

// Modelos físicos/API esperados. Se usan como referencia para integrar contra backend/BD.
export interface PreguntaApi {
  preg_id: number;
  preg_texto_pregunta: string | null;
  preg_habilidad_id: number | null;
  preg_nivel_habilidad_id: number | null;
  preg_fecha_creacion: string | null;
  puntaje_base?: number | null;
  duracion_minutos?: number | null;
  opciones?: OpcionPreguntaApi[];
}

export interface PreguntaCreatePayload {
  preg_texto_pregunta: string;
  preg_habilidad_id: number;
  preg_nivel_habilidad_id: number;
}

export interface OpcionPreguntaApi {
  opcr_id: number;
  opcr_pregunta_id: number;
  opcr_texto_opcion: string;
  opcr_es_correcta: boolean;
}

export interface OpcionCreatePayload {
  opcr_texto_opcion: string;
  opcr_es_correcta: boolean;
}

export interface CuestionarioApi {
  cues_id: number;
  cues_nombre: string | null;
  cues_descripcion: string | null;
  cues_porcentaje_aprobacion: number | null;
  cues_solicitud_id: number | null;
  solicitud_codigo?: string | null;
  cantidad_preguntas?: number;
  puntaje_maximo?: number;
  duracion_minutos?: number;
}

export interface CuestionarioCreatePayload {
  cues_nombre: string;
  cues_descripcion?: string | null;
  cues_porcentaje_aprobacion: number;
  cues_solicitud_id: number;
}

export interface AsignacionMasivaCreatePayload {
  candidato_ids: number[];
  fecha_vencimiento: string;
}

export interface AsignacionMasivaApi {
  cuestionario_id: number;
  solicitud_id: number;
  fecha_vencimiento: string;
  total_candidatos_solicitud: number;
  total_solicitados: number;
  total_asignados: number;
  total_omitidos_ya_asignados: number;
  asignaciones: AsignacionCuestionarioApi[];
}

export interface EnvioCuestionarioBackendPayload {
  solicitudId: number;
  preguntaIds: number[];
  candidatoIds: number[];
  fechaVencimiento: string;
  nombre?: string;
  descripcion?: string | null;
  porcentajeAprobacion?: number;
}

export interface AsignacionCuestionarioApi {
  cdcu_id: number;
  cdcu_candidato_id: number;
  candidato_email?: string | null;
  cdcu_cuestionario_id: number;
  cuestionario_nombre?: string | null;
  cdcu_fecha_asignacion: string;
  cdcu_fecha_inicio?: string | null;
  cdcu_fecha_vencimiento: string;
  cdcu_fecha_resolucion?: string | null;
  cdcu_porcentaje_obtenido?: number | string | null;
  estado_id: number;
  estado_nombre: string;
  cdcu_tiempo_utilizado?: number | null;
  cdcu_permitir_reintento: boolean;
  cdcu_aprobado?: boolean | null;
  cantidad_preguntas: number;
  puntaje_maximo: number;
  duracion_minutos: number;
}

export interface AsignacionCuestionarioCandidatoApi {
  cdcu_id: number;
  cuestionario_id: number;
  cuestionario_nombre: string;
  cuestionario_descripcion?: string | null;
  porcentaje_aprobacion: number | string;
  solicitud_id: number;
  solicitud_codigo?: string | null;
  fecha_asignacion: string;
  fecha_inicio?: string | null;
  fecha_vencimiento: string;
  fecha_resolucion?: string | null;
  estado: string;
  cantidad_preguntas: number;
  puntaje_maximo: number;
  duracion_minutos: number;
  porcentaje_obtenido?: number | string | null;
  aprobado?: boolean | null;
  tiempo_utilizado?: number | null;
}

// Modelos de pantalla: nombres simples para la vista de banco y armado de test.
export interface TecnologiaCuestionario {
  id: number;
  nombre: string;
  categoriaId: number | null;
  categoriaNombre: string;
}

export interface NivelCuestionario {
  id: number;
  nombre: string;
  duracionMinutos: number;
}

export interface PreguntaCuestionario {
  id: string;
  texto: string;
  tecnologiaId: number;
  nivelId: number;
  fechaCreacion: string;
  respuestas: string[];
  respuestaCorrecta: number;
  duracionMinutos: number;
  duracionSegundos: number;
}

export interface PreguntaCuestionarioCreate {
  texto: string;
  tecnologiaId: number;
  nivelId: number;
  respuestas: string[];
  respuestaCorrecta: number;
  duracionMinutos: number;
  duracionSegundos: number;
}

@Injectable({
  providedIn: 'root',
})
export class CuestionariosService {
  private readonly apiUrl = '/api';

  constructor(
    private catalogosService: CatalogosService,
    private http: HttpClient,
  ) {}

  listarTecnologias() {
    // Integración catálogo de habilidades -> tecnologías disponibles agrupadas por categoría.
    return this.catalogosService.listarHabilidades().pipe(
      map((habilidades) =>
        habilidades.map((habilidad) => ({
          id: habilidad.hab_id,
          nombre: habilidad.hab_nombre ?? 'Tecnología sin nombre',
          categoriaId:
            habilidad.hab_categoria_habilidad_id ??
            habilidad.categoria?.cthb_id ??
            null,
          categoriaNombre:
            habilidad.categoria?.cthb_nombre ??
            'Sin categoría',
        }))
          .sort((a, b) =>
            `${a.categoriaNombre} ${a.nombre}`.localeCompare(
              `${b.categoriaNombre} ${b.nombre}`,
              'es-CL',
              { sensitivity: 'base' },
            ),
          ),
      ),
      catchError(() => of([])),
    );
  }

  listarNiveles() {
    // Integración catálogo de niveles de habilidad -> niveles y duración base de preguntas.
    return this.catalogosService.listarNivelesHabilidad().pipe(
      map((niveles) =>
        niveles.map((nivel) => ({
          id: nivel.nvhb_id,
          nombre: nivel.nvhb_nombre ?? 'Nivel sin nombre',
          duracionMinutos: nivel.nvhb_duracion ?? 45,
        })),
      ),
      catchError(() => of([])),
    );
  }

  listar() {
    return this.http
      .get<PreguntaApi[]>(`${this.apiUrl}/preguntas`)
      .pipe(map((preguntas) => preguntas.map((pregunta) => this.mapearPregunta(pregunta))));
  }

  listarCuestionarios() {
    return this.http.get<CuestionarioApi[]>(
      `${this.apiUrl}/cuestionarios`,
    );
  }

  listarAsignacionesCandidato(candidatoId: string | number) {
    return this.http.get<AsignacionCuestionarioApi[]>(
      `${this.apiUrl}/candidatos/${candidatoId}/cuestionarios`,
    );
  }

  listarAsignaciones(params: {
    cuestionarioId?: number;
    candidatoId?: number;
    estadoId?: number;
    aprobado?: boolean;
  } = {}) {
    const query = new URLSearchParams();

    if (params.cuestionarioId) {
      query.set('cuestionario_id', String(params.cuestionarioId));
    }
    if (params.candidatoId) {
      query.set('candidato_id', String(params.candidatoId));
    }
    if (params.estadoId) {
      query.set('estado_id', String(params.estadoId));
    }
    if (params.aprobado != null) {
      query.set('aprobado', String(params.aprobado));
    }

    const suffix = query.toString() ? `?${query.toString()}` : '';
    return this.http.get<AsignacionCuestionarioApi[]>(
      `${this.apiUrl}/asignaciones-cuestionario${suffix}`,
    );
  }

  obtenerResultadoAsignacion(asignacionId: string | number) {
    return this.http.get(`${this.apiUrl}/asignaciones-cuestionario/${asignacionId}/resultado`);
  }

  cancelarAsignacion(asignacionId: string | number) {
    return this.http.post<AsignacionCuestionarioApi>(
      `${this.apiUrl}/asignaciones-cuestionario/${asignacionId}/cancelar`,
      {},
    );
  }

  marcarErrorTecnico(asignacionId: string | number) {
    return this.http.post<AsignacionCuestionarioApi>(
      `${this.apiUrl}/asignaciones-cuestionario/${asignacionId}/error-tecnico`,
      {},
    );
  }

  habilitarReintento(asignacionId: string | number, fechaVencimiento: string) {
    return this.http.post<AsignacionCuestionarioApi>(
      `${this.apiUrl}/asignaciones-cuestionario/${asignacionId}/habilitar-reintento`,
      { fecha_vencimiento: fechaVencimiento },
    );
  }

  listarMisCuestionarios() {
    return this.http.get<AsignacionCuestionarioCandidatoApi[]>(
      `${this.apiUrl}/cuestionarios/me`,
    );
  }

  crear(payload: PreguntaCuestionarioCreate) {
    const preguntaPayload: PreguntaCreatePayload = {
      preg_texto_pregunta: payload.texto,
      preg_habilidad_id: payload.tecnologiaId,
      preg_nivel_habilidad_id: payload.nivelId,
    };

    return this.http.post<PreguntaApi>(`${this.apiUrl}/preguntas`, preguntaPayload).pipe(
      switchMap((pregunta) => {
        const opciones = payload.respuestas.map((respuesta, indice) =>
          this.http.post<OpcionPreguntaApi>(`${this.apiUrl}/preguntas/${pregunta.preg_id}/opciones`, {
            opcr_texto_opcion: respuesta,
            opcr_es_correcta: indice === payload.respuestaCorrecta,
          } satisfies OpcionCreatePayload),
        );

        return forkJoin(opciones).pipe(
          map((opcionesCreadas) =>
            this.mapearPregunta({
              ...pregunta,
              opciones: opcionesCreadas,
            }),
          ),
        );
      }),
    );
  }

  contarPorTecnologia() {
    return forkJoin({
      tecnologias: this.listarTecnologias(),
      preguntas: this.listar(),
    }).pipe(
      map(({ tecnologias, preguntas }) =>
        tecnologias.map((tecnologia) => ({
          tecnologia,
          cantidad: preguntas.filter((pregunta) => pregunta.tecnologiaId === tecnologia.id).length,
        })),
      ),
    );
  }

  crearCuestionario(payload: CuestionarioCreatePayload) {
    return this.http.post<CuestionarioApi>(`${this.apiUrl}/cuestionarios`, payload);
  }

  agregarPreguntaCuestionario(cuestionarioId: number, preguntaId: number) {
    return this.http.post<PreguntaApi[]>(
      `${this.apiUrl}/cuestionarios/${cuestionarioId}/preguntas/${preguntaId}`,
      {},
    );
  }

  asignarCuestionarioMasivo(cuestionarioId: number, payload: AsignacionMasivaCreatePayload) {
    return this.http.post<AsignacionMasivaApi>(
      `${this.apiUrl}/cuestionarios/${cuestionarioId}/asignar`,
      payload,
    );
  }

  crearYAsignarCuestionario(payload: EnvioCuestionarioBackendPayload) {
    return this.crearCuestionario({
      cues_nombre: payload.nombre ?? `Evaluacion tecnica solicitud ${payload.solicitudId}`,
      cues_descripcion: payload.descripcion ?? null,
      cues_porcentaje_aprobacion: payload.porcentajeAprobacion ?? 60,
      cues_solicitud_id: payload.solicitudId,
    }).pipe(
      switchMap((cuestionario) =>
        forkJoin(payload.preguntaIds.map((preguntaId) => this.agregarPreguntaCuestionario(cuestionario.cues_id, preguntaId))).pipe(
          switchMap(() =>
            this.asignarCuestionarioMasivo(cuestionario.cues_id, {
              candidato_ids: payload.candidatoIds,
              fecha_vencimiento: payload.fechaVencimiento,
            }),
          ),
        ),
      ),
    );
  }

  private mapearPregunta(pregunta: PreguntaApi): PreguntaCuestionario {
    const opciones = pregunta.opciones ?? [];
    const respuestaCorrecta = Math.max(0, opciones.findIndex((opcion) => opcion.opcr_es_correcta));

    return {
      id: String(pregunta.preg_id),
      texto: pregunta.preg_texto_pregunta ?? 'Pregunta sin texto',
      tecnologiaId: pregunta.preg_habilidad_id ?? 0,
      nivelId: pregunta.preg_nivel_habilidad_id ?? 0,
      fechaCreacion: this.formatearFecha(pregunta.preg_fecha_creacion),
      respuestas: opciones.map((opcion) => opcion.opcr_texto_opcion),
      respuestaCorrecta,
      duracionMinutos: pregunta.duracion_minutos ?? 0,
      duracionSegundos: 0,
    };
  }

  private formatearFecha(fecha: string | null) {
    if (!fecha) {
      return '';
    }

    const fechaParsed = new Date(fecha);
    return Number.isNaN(fechaParsed.getTime()) ? fecha : new Intl.DateTimeFormat('es-CL').format(fechaParsed);
  }
}
