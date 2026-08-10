import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export type EstadoCandidatoApi = 'En revision' | 'Contactado' | 'Entrevista' | 'Descartado' | 'Desactivado';

export interface CandidatoResumenApi {
  id: string;
  nombre: string;
  correo: string;
  telefono?: string;
  cargo?: string;
  estado: EstadoCandidatoApi;
  match?: number;
  idSolicitud?: string;
  fechaRegistro?: string;
}

export interface CandidatoPerfilApi extends CandidatoResumenApi {
  disponibilidad?: string;
  renta?: number;
  fechaNacimiento?: string;
  tituloProfesional?: string;
  resumenProfesional?: string;
  urlPerfil?: string;
  comuna?: string;
  direccion?: string;
}

export interface CandidatoVacantePayload {
  solicitudId: string;
  puntajeCompatibilidad?: number;
}

export interface CandidatoHabilidadPayload {
  habilidadId: number;
  nivelId?: number;
}

@Injectable({
  providedIn: 'root',
})
export class CandidatosService {
  private readonly apiUrl = 'http://localhost:8000/candidatos';

  constructor(private http: HttpClient) {}

  listar() {
    return this.http.get<CandidatoResumenApi[]>(this.apiUrl);
  }

  obtenerPorId(id: string) {
    return this.http.get<CandidatoPerfilApi>(`${this.apiUrl}/${id}`);
  }

  crear(payload: Partial<CandidatoPerfilApi>) {
    return this.http.post<CandidatoPerfilApi>(this.apiUrl, payload);
  }

  actualizar(id: string, payload: Partial<CandidatoPerfilApi>) {
    return this.http.put<CandidatoPerfilApi>(`${this.apiUrl}/${id}`, payload);
  }

  desactivar(id: string) {
    return this.http.patch<CandidatoPerfilApi>(`${this.apiUrl}/${id}/desactivar`, {});
  }

  subirCv(archivo: File) {
    const formData = new FormData();
    formData.append('archivo', archivo);
    return this.http.post<CandidatoPerfilApi>(`${this.apiUrl}/cv`, formData);
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
