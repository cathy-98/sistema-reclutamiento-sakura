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
  cand_url_1?: string | string[] | null;
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
  etcd_id?: number;
  etcd_institucion_id?: number | null;
  etcd_carrera_id?: number | null;
  etcd_nivel_educacional_id?: number | null;
  etcd_fecha_inicio?: string | null;
  etcd_fecha_fin?: string | null;
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
  expl_id?: number;
  expl_empresa_id?: number | null;
  expl_cargo_id?: number | null;
  expl_fecha_inicio?: string | null;
  expl_fecha_fin?: string | null;
  expl_descripcion_funciones?: string | null;
  cdex_id?: number;
  cdex_empresa?: string | null;
  cdex_cargo?: string | null;
  cdex_fecha_inicio?: string | null;
  cdex_fecha_fin?: string | null;
  cdex_descripcion?: string | null;
  empresa?: { emp_nombre?: string | null } | null;
  cargo?: { crgo_nombre?: string | null } | null;
  habilidades_ids?: number[];
}

export interface CursoCandidatoApi {
  curs_id?: number;
  curs_candidato_id?: number;
  curs_nombre_curso?: string | null;
  curs_institucion_id?: number | null;
  curs_es_certificado?: boolean | null;
  curs_anio_curso?: number | null;
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

export interface IdiomaCandidatoApi {
  cdio_id: number;
  cdio_candidato_id: number;
  cdio_idioma_id: number;
  cdio_nivel_idioma_id: number;
  idioma?: { idio_id: number; idio_nombre: string | null } | null;
  nivel_idioma?: {
    nvid_id: number;
    nvid_codigo: string | null;
    nvid_nombre: string | null;
    nvid_grupo: string | null;
    nvid_es_generico: boolean;
  } | null;
}

export interface CandidatoPerfilCompletoApi extends CandidatoApi {
  direccion?: DireccionCandidatoApi | null;
  habilidades?: HabilidadCandidatoApi[];
  estudios?: EstudioCandidatoApi[];
  experiencias?: ExperienciaCandidatoApi[];
  cursos?: CursoCandidatoApi[];
  solicitudes?: PostulacionCandidatoApi[];
}

export interface ImportCvResponse {
  candidato: CandidatoPerfilCompletoApi;
  creado: boolean;
  actualizado: boolean;
  password_temporal?: string | null;
  cv_ruta_guardada?: string | null;
  advertencias?: string[];
  warnings?: string[];
}

export interface DireccionCandidatoPayload {
  drcd_comuna_id?: number | null;
  drcd_calle?: string | null;
  drcd_numero?: number | string | null;
  drcd_dpto_oficina?: string | null;
}

export interface EstudioCandidatoPayload {
  etcd_nivel_educacional_id?: number | null;
  etcd_institucion_id?: number | null;
  etcd_carrera_id?: number | null;
  etcd_fecha_inicio?: string | null;
  etcd_fecha_fin?: string | null;
}

export interface ExperienciaCandidatoPayload {
  expl_empresa_id?: number | null;
  expl_cargo_id?: number | null;
  expl_descripcion_funciones?: string | null;
  expl_fecha_inicio?: string | null;
  expl_fecha_fin?: string | null;
  habilidades_ids?: number[];
}

export interface CursoCandidatoPayload {
  curs_nombre_curso?: string | null;
  curs_institucion_id?: number | null;
  curs_es_certificado?: boolean | null;
  curs_anio_curso?: number | null;
}

export interface IdiomaCandidatoPayload {
  cdio_idioma_id: number;
  cdio_nivel_idioma_id: number;
}

export interface IdiomaCandidatoUpdatePayload {
  cdio_nivel_idioma_id: number;
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

  actualizarMiPerfil(payload: Partial<CandidatoApi>) {
    return this.http.patch<CandidatoPerfilCompletoApi>(`${this.apiUrl}/me`, payload);
  }

  listarSolicitudes(id: string) {
    // Integracion interna M3: GET /candidatos/{id}/solicitudes para postulaciones administrativas.
    return this.http.get<PostulacionCandidatoApi[]>(`${this.apiUrl}/${id}/solicitudes`);
  }

  listarPorSolicitud(solicitudId: string | number) {
    // Integracion M3/M5: una solicitud puede tener muchos candidatos postulados.
    return this.http.get<PostulacionCandidatoApi[]>(`/api/solicitudes/${solicitudId}/candidatos`);
  }

  listarMisSolicitudes() {
    // Integracion interna M3 autoservicio: GET /candidatos/me/solicitudes sin exponer cand_id.
    return this.http.get<PostulacionCandidatoApi[]>(`${this.apiUrl}/me/solicitudes`);
  }

  listarIdiomas(id: string) {
    // Integracion M3: GET /candidatos/{id}/idiomas para datos adicionales del perfil.
    return this.http.get<IdiomaCandidatoApi[]>(`${this.apiUrl}/${id}/idiomas`);
  }

  listarMisIdiomas() {
    // Integracion M3 autoservicio: GET /candidatos/me/idiomas.
    return this.http.get<IdiomaCandidatoApi[]>(`${this.apiUrl}/me/idiomas`);
  }

  crear(payload: Partial<CandidatoApi>) {
    return this.http.post<CandidatoPerfil>(this.apiUrl, payload);
  }

  actualizar(id: string, payload: Partial<CandidatoApi>) {
    return this.http.patch<CandidatoPerfilCompletoApi>(`${this.apiUrl}/${id}`, payload);
  }

  desactivar(id: string) {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  subirCv(archivo: File) {
    const formData = new FormData();
    formData.append('file', archivo);
    // Integracion interna M3: POST /candidatos/importar-cv importa/actualiza candidato desde un CV.
    return this.http.post<ImportCvResponse>(`${this.apiUrl}/importar-cv`, formData);
  }

  subirCvs(archivos: File[]) {
    const formData = new FormData();
    archivos.forEach((archivo) => formData.append('files', archivo));
    return this.http.post<ImportCvResponse[]>(`${this.apiUrl}/importar-cvs`, formData);
  }

  vincularVacante(candidatoId: string, payload: CandidatoVacantePayload) {
    // Integracion interna M3: POST /solicitudes/{solicitud_id}/candidatos/{candidato_id}.
    return this.http.post(`/api/solicitudes/${payload.slcd_solicitud_id}/candidatos/${candidatoId}`, payload);
  }

  agregarHabilidad(candidatoId: string, payload: CandidatoHabilidadPayload) {
    return this.http.post(`${this.apiUrl}/${candidatoId}/habilidades`, payload);
  }

  listarHabilidades(candidatoId: string | number) {
    return this.http.get<HabilidadCandidatoApi[]>(`${this.apiUrl}/${candidatoId}/habilidades`);
  }

  actualizarHabilidad(candidatoId: string | number, habilidadId: string | number, payload: Partial<CandidatoHabilidadPayload>) {
    return this.http.patch<HabilidadCandidatoApi>(`${this.apiUrl}/${candidatoId}/habilidades/${habilidadId}`, payload);
  }

  eliminarHabilidad(candidatoId: string, habilidadId: number) {
    return this.http.delete(`${this.apiUrl}/${candidatoId}/habilidades/${habilidadId}`);
  }

  listarEstudios(candidatoId: string | number) {
    return this.http.get<EstudioCandidatoApi[]>(`${this.apiUrl}/${candidatoId}/estudios`);
  }

  agregarEstudio(candidatoId: string | number, payload: EstudioCandidatoPayload) {
    return this.http.post<EstudioCandidatoApi>(`${this.apiUrl}/${candidatoId}/estudios`, payload);
  }

  actualizarEstudio(candidatoId: string | number, estudioId: string | number, payload: EstudioCandidatoPayload) {
    return this.http.patch<EstudioCandidatoApi>(`${this.apiUrl}/${candidatoId}/estudios/${estudioId}`, payload);
  }

  eliminarEstudio(candidatoId: string | number, estudioId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/${candidatoId}/estudios/${estudioId}`);
  }

  listarExperiencias(candidatoId: string | number) {
    return this.http.get<ExperienciaCandidatoApi[]>(`${this.apiUrl}/${candidatoId}/experiencias`);
  }

  agregarExperiencia(candidatoId: string | number, payload: ExperienciaCandidatoPayload) {
    return this.http.post<ExperienciaCandidatoApi>(`${this.apiUrl}/${candidatoId}/experiencias`, payload);
  }

  actualizarExperiencia(candidatoId: string | number, experienciaId: string | number, payload: ExperienciaCandidatoPayload) {
    return this.http.patch<ExperienciaCandidatoApi>(`${this.apiUrl}/${candidatoId}/experiencias/${experienciaId}`, payload);
  }

  eliminarExperiencia(candidatoId: string | number, experienciaId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/${candidatoId}/experiencias/${experienciaId}`);
  }

  listarCursos(candidatoId: string | number) {
    return this.http.get<CursoCandidatoApi[]>(`${this.apiUrl}/${candidatoId}/cursos`);
  }

  agregarCurso(candidatoId: string | number, payload: CursoCandidatoPayload) {
    return this.http.post<CursoCandidatoApi>(`${this.apiUrl}/${candidatoId}/cursos`, payload);
  }

  actualizarCurso(candidatoId: string | number, cursoId: string | number, payload: CursoCandidatoPayload) {
    return this.http.patch<CursoCandidatoApi>(`${this.apiUrl}/${candidatoId}/cursos/${cursoId}`, payload);
  }

  eliminarCurso(candidatoId: string | number, cursoId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/${candidatoId}/cursos/${cursoId}`);
  }

  listarDirecciones(candidatoId: string | number) {
    return this.http.get<DireccionCandidatoApi[]>(`${this.apiUrl}/${candidatoId}/direcciones`);
  }

  actualizarDireccionPropia(payload: DireccionCandidatoPayload) {
    return this.http.put<DireccionCandidatoApi>(`${this.apiUrl}/me/direccion`, payload);
  }

  eliminarDireccionPropia() {
    return this.http.delete<void>(`${this.apiUrl}/me/direccion`);
  }

  agregarIdioma(candidatoId: string | number, payload: IdiomaCandidatoPayload) {
    return this.http.post<IdiomaCandidatoApi>(`${this.apiUrl}/${candidatoId}/idiomas`, payload);
  }

  actualizarIdioma(candidatoId: string | number, idiomaCandidatoId: string | number, payload: IdiomaCandidatoUpdatePayload) {
    return this.http.patch<IdiomaCandidatoApi>(`${this.apiUrl}/${candidatoId}/idiomas/${idiomaCandidatoId}`, payload);
  }

  eliminarIdioma(candidatoId: string | number, idiomaCandidatoId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/${candidatoId}/idiomas/${idiomaCandidatoId}`);
  }

  agregarMiHabilidad(payload: CandidatoHabilidadPayload) {
    return this.http.post<HabilidadCandidatoApi>(`${this.apiUrl}/me/habilidades`, payload);
  }

  actualizarMiHabilidad(habilidadId: string | number, payload: Partial<CandidatoHabilidadPayload>) {
    return this.http.patch<HabilidadCandidatoApi>(`${this.apiUrl}/me/habilidades/${habilidadId}`, payload);
  }

  eliminarMiHabilidad(habilidadId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/me/habilidades/${habilidadId}`);
  }

  agregarMiEstudio(payload: EstudioCandidatoPayload) {
    return this.http.post<EstudioCandidatoApi>(`${this.apiUrl}/me/estudios`, payload);
  }

  actualizarMiEstudio(estudioId: string | number, payload: EstudioCandidatoPayload) {
    return this.http.patch<EstudioCandidatoApi>(`${this.apiUrl}/me/estudios/${estudioId}`, payload);
  }

  eliminarMiEstudio(estudioId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/me/estudios/${estudioId}`);
  }

  agregarMiExperiencia(payload: ExperienciaCandidatoPayload) {
    return this.http.post<ExperienciaCandidatoApi>(`${this.apiUrl}/me/experiencias`, payload);
  }

  actualizarMiExperiencia(experienciaId: string | number, payload: ExperienciaCandidatoPayload) {
    return this.http.patch<ExperienciaCandidatoApi>(`${this.apiUrl}/me/experiencias/${experienciaId}`, payload);
  }

  eliminarMiExperiencia(experienciaId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/me/experiencias/${experienciaId}`);
  }

  agregarMiCurso(payload: CursoCandidatoPayload) {
    return this.http.post<CursoCandidatoApi>(`${this.apiUrl}/me/cursos`, payload);
  }

  actualizarMiCurso(cursoId: string | number, payload: CursoCandidatoPayload) {
    return this.http.patch<CursoCandidatoApi>(`${this.apiUrl}/me/cursos/${cursoId}`, payload);
  }

  eliminarMiCurso(cursoId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/me/cursos/${cursoId}`);
  }

  agregarMiIdioma(payload: IdiomaCandidatoPayload) {
    return this.http.post<IdiomaCandidatoApi>(`${this.apiUrl}/me/idiomas`, payload);
  }

  actualizarMiIdioma(idiomaCandidatoId: string | number, payload: IdiomaCandidatoUpdatePayload) {
    return this.http.patch<IdiomaCandidatoApi>(`${this.apiUrl}/me/idiomas/${idiomaCandidatoId}`, payload);
  }

  eliminarMiIdioma(idiomaCandidatoId: string | number) {
    return this.http.delete<void>(`${this.apiUrl}/me/idiomas/${idiomaCandidatoId}`);
  }

  actualizarPostulacion(
    postulacionId: string | number,
    payload: {
      slcd_pretension_renta?: number | null;
      slcd_puntaje_compatibilidad?: number | null;
      slcd_observaciones?: string | null;
    },
  ) {
    return this.http.patch<PostulacionCandidatoApi>(
      `/api/postulaciones/${postulacionId}`,
      payload,
    );
  }

  cambiarEstadoPostulacion(
    postulacionId: string | number,
    payload: {
      estado_id: number;
      motivo_rechazo_id?: number | null;
      observaciones?: string | null;
    },
  ) {
    return this.http.patch<PostulacionCandidatoApi>(
      `/api/postulaciones/${postulacionId}/estado`,
      payload,
    );
  }
}
