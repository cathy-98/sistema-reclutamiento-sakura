import {
  PreguntaApi,
  PreguntaCreatePayload,
  PreguntaCuestionario,
  PreguntaCuestionarioCreate,
} from '../../services/cuestionarios.service';

export interface RespuestaPreguntaApi {
  oprs_id: number;
  oprs_texto?: string | null;
  oprs_es_correcta?: boolean | null;
}

export interface PreguntaDetalleApi extends PreguntaApi {
  respuestas?: RespuestaPreguntaApi[];
  nvhb_duracion?: number | null;
}

export interface PreguntaCreateApiPayload extends PreguntaCreatePayload {
  respuestas?: Array<{
    oprs_texto: string;
    oprs_es_correcta: boolean;
  }>;
}

// Mapeo API -> pantalla: mantiene preguntas y respuestas separadas de la nomenclatura preg_*/oprs_*.
export function mapearPreguntaCuestionario(pregunta: PreguntaDetalleApi): PreguntaCuestionario {
  const respuestas = pregunta.respuestas ?? [];
  const indiceCorrecta = respuestas.findIndex((respuesta) => respuesta.oprs_es_correcta);

  return {
    id: String(pregunta.preg_id),
    texto: pregunta.preg_texto_pregunta ?? '',
    tecnologiaId: pregunta.preg_habilidad_id ?? 0,
    nivelId: pregunta.preg_nivel_habilidad_id ?? 0,
    fechaCreacion: formatearFecha(pregunta.preg_fecha_creacion),
    respuestas: respuestas.map((respuesta) => respuesta.oprs_texto ?? ''),
    respuestaCorrecta: indiceCorrecta >= 0 ? indiceCorrecta : 0,
    duracionMinutos: pregunta.nvhb_duracion ?? 45,
    duracionSegundos: 0,
  };
}

// Mapeo pantalla -> API: prepara el POST futuro con IDs de catalogos reales.
export function mapearPreguntaCreatePayload(payload: PreguntaCuestionarioCreate): PreguntaCreateApiPayload {
  return {
    preg_texto_pregunta: payload.texto,
    preg_habilidad_id: payload.tecnologiaId,
    preg_nivel_habilidad_id: payload.nivelId,
    respuestas: payload.respuestas.map((respuesta, index) => ({
      oprs_texto: respuesta,
      oprs_es_correcta: index === payload.respuestaCorrecta,
    })),
  };
}

function formatearFecha(fecha?: string | null) {
  if (!fecha) {
    return 'Sin fecha';
  }

  const fechaNormalizada = new Date(fecha);
  return Number.isNaN(fechaNormalizada.getTime())
    ? fecha
    : new Intl.DateTimeFormat('es-CL').format(fechaNormalizada);
}
