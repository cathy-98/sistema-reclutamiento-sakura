import { HttpClient, HttpParams, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';

export type ClasificacionInforme = 'APROBADO' | 'PENDIENTE' | 'NO_APROBADO';

export interface EvaluacionTecnicaResumenApi {
  cuestionario_id: number;
  cuestionario: string;
  porcentaje?: number | null;
  aprobado?: boolean | null;
  estado?: string | null;
}

export interface EvaluacionEntrevistaResumenApi {
  entrevista_id: number;
  tipo_id?: number | null;
  tipo?: string | null;
  entrevistador_id?: number | null;
  entrevistador?: string | null;
  resultado: string;
  observacion?: string | null;
}

export interface CandidatoInformeApi {
  solicitud_candidato_id: number;
  solicitud_id: number;
  solicitud_codigo?: string | null;
  solicitud_titulo?: string | null;
  candidato_id: number;
  candidato_nombre: string;
  candidato_email: string;
  candidato_telefono?: string | null;
  cargo_id?: number | null;
  cargo?: string | null;
  disponibilidad_id?: number | null;
  disponibilidad?: string | null;
  match?: number | null;
  estado_postulacion?: string | null;
  clasificacion: ClasificacionInforme;
  clasificacion_sugerida: boolean;
  motivo_clasificacion: string[];
  tecnologias: string[];
  tecnicas: EvaluacionTecnicaResumenApi[];
  entrevistas: EvaluacionEntrevistaResumenApi[];
  puede_enviar_rechazo: boolean;
  puede_enviar_directivos: boolean;
}

export interface CandidateListResponseApi {
  total: number;
  items: CandidatoInformeApi[];
}

export interface DocumentoInformeApi {
  documento_id: number;
  solicitud_candidato_id: number;
  tipo_documento: string;
  nombre_archivo: string;
  fecha_generacion: string;
  hash_sha256: string;
}

export interface DirectivosPreviewApi {
  destinatarios: string[];
  cc: string[];
  asunto: string;
  cuerpo: string;
  candidatos: CandidatoInformeApi[];
  adjuntos: DocumentoInformeApi[];
}

@Injectable({ providedIn: 'root' })
export class InformesService {
  private readonly apiUrl = '/api/informes';

  constructor(private http: HttpClient) {}

  listarCandidatos(params: {
    clasificacion?: ClasificacionInforme;
    nombre?: string;
    skip?: number;
    limit?: number;
  } = {}) {
    let httpParams = new HttpParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        httpParams = httpParams.set(key, String(value));
      }
    });

    return this.http.get<CandidateListResponseApi>(`${this.apiUrl}/candidatos`, { params: httpParams });
  }

  generarResumen(solicitudCandidatoId: number) {
    return this.http.post<DocumentoInformeApi>(
      `${this.apiUrl}/candidatos/${solicitudCandidatoId}/resumen`,
      {},
    );
  }

  generarCvCorporativo(solicitudCandidatoId: number) {
    return this.http.post<DocumentoInformeApi>(
      `${this.apiUrl}/candidatos/${solicitudCandidatoId}/cv-corporativo`,
      {},
    );
  }

  descargarDocumento(documentoId: number) {
    return this.http.get(`${this.apiUrl}/documentos/${documentoId}/descargar`, {
      observe: 'response',
      responseType: 'blob',
    });
  }

  descargarCvCorporativoMasivo(solicitudCandidatoIds: number[]) {
    return this.http.post(`${this.apiUrl}/candidatos/cv-corporativo-masivo/descargar`, {
      solicitud_candidato_ids: solicitudCandidatoIds,
    }, {
      observe: 'response',
      responseType: 'blob',
    });
  }

  descargarResumenMasivo(solicitudCandidatoIds: number[]) {
    return this.http.post(`${this.apiUrl}/candidatos/resumen-masivo/descargar`, {
      solicitud_candidato_ids: solicitudCandidatoIds,
    }, {
      observe: 'response',
      responseType: 'blob',
    });
  }

  prepararDirectivos(payload: {
    solicitudCandidatoIds: number[];
    destinatarios: string[];
    cc: string[];
    asunto?: string | null;
    cuerpo?: string | null;
  }) {
    return this.http.post<DirectivosPreviewApi>(`${this.apiUrl}/directivos/preparar`, this.directivosPayload(payload));
  }

  enviarDirectivos(payload: {
    solicitudCandidatoIds: number[];
    destinatarios: string[];
    cc: string[];
    asunto?: string | null;
    cuerpo?: string | null;
  }) {
    return this.http.post(`${this.apiUrl}/directivos/enviar`, this.directivosPayload(payload));
  }

  descargarBlob(respuesta: HttpResponse<Blob>, nombreFallback: string) {
    const blob = respuesta.body;
    if (!blob) {
      return;
    }

    const nombre = this.nombreArchivo(respuesta) || nombreFallback;
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = nombre;
    enlace.click();
    URL.revokeObjectURL(url);
  }

  private directivosPayload(payload: {
    solicitudCandidatoIds: number[];
    destinatarios: string[];
    cc: string[];
    asunto?: string | null;
    cuerpo?: string | null;
  }) {
    return {
      solicitud_candidato_ids: payload.solicitudCandidatoIds,
      destinatarios: payload.destinatarios,
      cc: payload.cc,
      asunto: payload.asunto || null,
      cuerpo: payload.cuerpo || null,
    };
  }

  private nombreArchivo(respuesta: HttpResponse<Blob>) {
    const contentDisposition = respuesta.headers.get('Content-Disposition') ?? '';
    const match = /filename="?([^"]+)"?/i.exec(contentDisposition);
    return match?.[1];
  }
}
