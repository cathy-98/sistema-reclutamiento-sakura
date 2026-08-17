import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export type EstadoSolicitudCandidatoApi =
  | 'En revision'
  | 'En entrevista'
  | 'Inhabilitado'
  | 'Seleccionado'
  | 'Descartado'
  | 'Contratado';

// Modelo físico/API esperado para candidatos: usar estos nombres cand_* cuando exista el endpoint real.
export interface CandidatoApi {
  cand_id: number;
  cand_email: string | null;
  cand_nombres: string | null;
  cand_apellido_paterno: string | null;
  cand_apellido_materno?: string | null;
  cand_fecha_nacimiento?: string | null;
  cand_telefono?: string | null;
  cand_disponibilidad_id?: number | null;
  cand_resumen_profesional?: string | null;
  cand_fecha_creacion?: string | null;
  cand_url_1?: string | null;
  cand_titulo?: string | null;
  cand_estado_usuario_id?: number | null;
  cand_rut_sin_dv?: number | null;
  cand_dv?: number | string | null;
  cand_cv_urls?: string | null;
}

export interface DireccionCandidatoApi {
  drcd_id?: number;
  drcd_candidato_id?: number;
  drcd_comuna_id?: number | null;
  drcd_calle?: string | null;
  drcd_numero?: number | string | null;
  drcd_dpto_oficina?: string | null;
}

export interface HabilidadCandidatoApi {
  cdhb_id?: number;
  cdhb_habilidad_id?: number | null;
  cdhb_nivel_habilidad_id?: number | null;
  cdhb_anios_experiencia?: number | null;
  habilidad?: { hab_nombre?: string | null } | null;
  nivel_habilidad?: { nvhb_nombre?: string | null } | null;
}

export interface EstudioCandidatoApi {
  cdet_id?: number;
  cdet_institucion_id?: number | null;
  cdet_carrera_id?: number | null;
  cdet_nivel_educacional_id?: number | null;
  cdet_fecha_inicio?: string | null;
  cdet_fecha_fin?: string | null;
  cdet_descripcion?: string | null;
  institucion?: { inst_nombre?: string | null } | null;
  carrera?: { crra_nombre?: string | null } | null;
  nivel_educacional?: { nved_nombre?: string | null } | null;
}

export interface ExperienciaCandidatoApi {
  cdex_id?: number;
  cdex_empresa?: string | null;
  cdex_cargo?: string | null;
  cdex_fecha_inicio?: string | null;
  cdex_fecha_fin?: string | null;
  cdex_descripcion?: string | null;
}

export interface CursoCandidatoApi {
  cdcu_id?: number;
  cdcu_nombre?: string | null;
  cdcu_institucion?: string | null;
  cdcu_fecha_inicio?: string | null;
  cdcu_fecha_fin?: string | null;
}

export interface PostulacionCandidatoApi {
  slcd_id: number;
  slcd_candidato_id: number;
  slcd_solicitud_id: number;
  slcd_pretension_renta?: number | null;
  slcd_puntaje_compatibilidad?: number | string | null;
  slcd_estado_solicitud_candidato_id?: number | null;
  slcd_fecha_postulacion?: string | null;
  slcd_observaciones?: string | null;
  slcd_motivo_rechazo_id?: number | null;
}

export interface CandidatoPerfilCompletoApi extends CandidatoApi {
  direccion?: DireccionCandidatoApi | null;
  habilidades?: HabilidadCandidatoApi[];
  estudios?: EstudioCandidatoApi[];
  experiencias?: ExperienciaCandidatoApi[];
  cursos?: CursoCandidatoApi[];
  solicitudes?: PostulacionCandidatoApi[];
}

// Modelo de pantalla actual: se mantiene separado para no mezclar UI con nombres de BD.
export interface CandidatoResumen {
  id: string;
  nombre: string;
  correo: string;
  telefono?: string;
  cargo?: string;
  estado: EstadoSolicitudCandidatoApi;
  estadoUsuario?: string;
  match?: number;
  idSolicitud?: string;
  fechaPostulacion?: string;
  fechaRegistro?: string;
}

export interface CandidatoPerfil extends CandidatoResumen {
  disponibilidad?: string;
  renta?: number;
  rut?: string;
  fechaNacimiento?: string;
  tituloProfesional?: string;
  resumenProfesional?: string;
  urlPerfil?: string;
  comuna?: string;
  direccion?: string;
}

export interface CandidatoVacantePayload {
  slcd_solicitud_id: number;
  slcd_puntaje_compatibilidad?: number;
}

export interface CandidatoHabilidadPayload {
  cdhb_habilidad_id: number;
  cdhb_nivel_habilidad_id?: number;
  cdhb_anios_experiencia?: number;
}

@Injectable({
  providedIn: 'root',
})
export class CandidatosService {
  private readonly apiUrl = '/api/candidatos';

  constructor(private http: HttpClient) {}

  listar() {
    // Integracion interna M3: GET /candidatos lista candidatos para usuarios internos.
    return this.http.get<CandidatoApi[]>(this.apiUrl);
  }

  obtenerPorId(id: string) {
    // Integracion interna M3: GET /candidatos/{id} mantiene compatibilidad con ficha base.
    return this.http.get<CandidatoPerfilCompletoApi>(`${this.apiUrl}/${id}`);
  }

  obtenerPerfilCompleto(id: string) {
    // Integracion interna M3: GET /candidatos/{id}/perfil-completo para vista administrativa.
    return this.http.get<CandidatoPerfilCompletoApi>(`${this.apiUrl}/${id}/perfil-completo`);
  }

  obtenerMiPerfilCompleto() {
    // Integracion interna M3 autoservicio: GET /candidatos/me/perfil-completo usa cand_id desde JWT.
    return this.http.get<CandidatoPerfilCompletoApi>(`${this.apiUrl}/me/perfil-completo`);
  }

  listarSolicitudes(id: string) {
    // Integracion interna M3: GET /candidatos/{id}/solicitudes para postulaciones administrativas.
    return this.http.get<PostulacionCandidatoApi[]>(`${this.apiUrl}/${id}/solicitudes`);
  }

  listarMisSolicitudes() {
    // Integracion interna M3 autoservicio: GET /candidatos/me/solicitudes sin exponer cand_id.
    return this.http.get<PostulacionCandidatoApi[]>(`${this.apiUrl}/me/solicitudes`);
  }

  crear(payload: Partial<CandidatoApi>) {
    // Integración pendiente: adaptar payload a nombres cand_* antes de conectar el endpoint real.
    return this.http.post<CandidatoPerfil>(this.apiUrl, payload);
  }

  actualizar(id: string, payload: Partial<CandidatoApi>) {
    // Integración pendiente: PUT debe enviar campos cand_* cuando exista el backend.
    return this.http.put<CandidatoPerfil>(`${this.apiUrl}/${id}`, payload);
  }

  desactivar(id: string) {
    return this.http.patch<CandidatoPerfil>(`${this.apiUrl}/${id}/desactivar`, {});
  }

  subirCv(archivo: File) {
    const formData = new FormData();
    formData.append('archivo', archivo);
    // Integracion interna M3: POST /candidatos/importar-cv importa/actualiza candidato desde un CV.
    return this.http.post<CandidatoPerfilCompletoApi>(`${this.apiUrl}/importar-cv`, formData);
  }

  vincularVacante(candidatoId: string, payload: CandidatoVacantePayload) {
    // Integracion interna M3: POST /solicitudes/{solicitud_id}/candidatos/{candidato_id}.
    return this.http.post(`/api/solicitudes/${payload.slcd_solicitud_id}/candidatos/${candidatoId}`, payload);
  }

  agregarHabilidad(candidatoId: string, payload: CandidatoHabilidadPayload) {
    return this.http.post(`${this.apiUrl}/${candidatoId}/habilidades`, payload);
  }

  eliminarHabilidad(candidatoId: string, habilidadId: number) {
    return this.http.delete(`${this.apiUrl}/${candidatoId}/habilidades/${habilidadId}`);
  }
}
