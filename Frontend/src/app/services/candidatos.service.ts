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
  private readonly apiUrl = '/candidatos';

  constructor(private http: HttpClient) {}

  listar() {
    // Integración pendiente: reemplazar por mapeo cand_* -> modelo de pantalla cuando backend exponga /candidatos.
    return this.http.get<CandidatoResumen[]>(this.apiUrl);
  }

  obtenerPorId(id: string) {
    // Integración pendiente: el detalle debe alinearse con la respuesta real de backend/BD.
    return this.http.get<CandidatoPerfil>(`${this.apiUrl}/${id}`);
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
    return this.http.post<CandidatoPerfil>(`${this.apiUrl}/cv`, formData);
  }

  vincularVacante(candidatoId: string, payload: CandidatoVacantePayload) {
    return this.http.post(`${this.apiUrl}/${candidatoId}/postulaciones`, payload);
  }

  agregarHabilidad(candidatoId: string, payload: CandidatoHabilidadPayload) {
    return this.http.post(`${this.apiUrl}/${candidatoId}/habilidades`, payload);
  }

  eliminarHabilidad(candidatoId: string, habilidadId: number) {
    return this.http.delete(`${this.apiUrl}/${candidatoId}/habilidades/${habilidadId}`);
  }
}
