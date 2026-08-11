import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface CargoCatalogoApi {
  crgo_id: number;
  crgo_nombre: string | null;
  crgo_descripcion?: string | null;
}

export interface PrioridadSolicitudCatalogoApi {
  prsol_id: number;
  prsol_nombre: string | null;
  prsol_descripcion?: string | null;
}

export interface EstadoSolicitudCatalogoApi {
  essl_id: number;
  essl_nombre: string | null;
  essl_descripcion?: string | null;
}

export interface ModalidadCatalogoApi {
  mdld_id: number;
  mdld_nombre: string | null;
  mdld_descripcion?: string | null;
}

export interface HabilidadCatalogoApi {
  hab_id: number;
  hab_nombre: string | null;
  hab_descripcion?: string | null;
}

export interface NivelHabilidadCatalogoApi {
  nvhb_id: number;
  nvhb_nombre: string | null;
  nvhb_descripcion?: string | null;
  nvhb_puntaje_base?: number | null;
  nvhb_duracion?: number | null;
}

export interface UsuarioCatalogoApi {
  usr_id: number;
  usr_nombres: string;
  usr_apellido_paterno: string;
  usr_apellido_materno?: string | null;
  usr_email: string;
}

@Injectable({
  providedIn: 'root',
})
export class CatalogosService {
  private readonly apiUrl = 'http://localhost:8000/catalogos';
  private readonly usuariosApiUrl = 'http://localhost:8000/usuarios';

  constructor(private http: HttpClient) {}

  listarCargos() {
    return this.http.get<CargoCatalogoApi[]>(`${this.apiUrl}/cargos`);
  }

  listarUsuarios() {
    return this.http.get<UsuarioCatalogoApi[]>(`${this.usuariosApiUrl}/`);
  }

  listarPrioridadesSolicitud() {
    return this.http.get<PrioridadSolicitudCatalogoApi[]>(`${this.apiUrl}/prioridades-solicitud`);
  }

  listarEstadosSolicitud() {
    return this.http.get<EstadoSolicitudCatalogoApi[]>(`${this.apiUrl}/estados-solicitud`);
  }

  listarModalidades() {
    return this.http.get<ModalidadCatalogoApi[]>(`${this.apiUrl}/modalidades`);
  }

  listarHabilidades() {
    return this.http.get<HabilidadCatalogoApi[]>(`${this.apiUrl}/habilidades`);
  }

  listarNivelesHabilidad() {
    return this.http.get<NivelHabilidadCatalogoApi[]>(`${this.apiUrl}/niveles-habilidad`);
  }
}
