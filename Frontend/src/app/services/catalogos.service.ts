import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface CatalogoListParams {
  q?: string;
  skip?: number;
  limit?: number;
  pais_id?: number;
  region_id?: number;
  tipo_institucion_id?: number;
  rol_id?: number;
  estado_id?: number;
  area_id?: number;
}

export type CatalogoPath =
  | 'paises'
  | 'regiones'
  | 'comunas'
  | 'tipos-institucion'
  | 'instituciones'
  | 'carreras'
  | 'niveles-educacionales'
  | 'habilidades'
  | 'niveles-habilidad'
  | 'cargos'
  | 'modalidades'
  | 'tipos-contrato'
  | 'disponibilidades'
  | 'estados-solicitud'
  | 'prioridades-solicitud'
  | 'estados-solicitud-candidato'
  | 'motivos-rechazo'
  | 'estados-cuestionario-candidato'
  | 'estados-entrevista'
  | 'tipos-entrevista'
  | 'nombres-resultado';

export interface CargoCatalogoApi {
  crgo_id: number;
  crgo_nombre: string | null;
  crgo_descripcion?: string | null;
}

export interface PaisCatalogoApi {
  pais_id: number;
  pais_nombre: string | null;
}

export interface RegionCatalogoApi {
  reg_id: number;
  reg_pais_id?: number | null;
  reg_nombre: string | null;
}

export interface CiudadCatalogoApi {
  ciu_id: number;
  ciu_region_id?: number | null;
  ciu_nombre: string | null;
}

export interface ComunaCatalogoApi {
  com_id: number;
  com_region_id?: number | null;
  com_ciudad_id?: number | null;
  com_nombre: string | null;
}

export interface TipoInstitucionCatalogoApi {
  tint_id: number;
  tint_tipo_institucion: string | null;
}

export interface InstitucionCatalogoApi {
  inst_id: number;
  inst_nombre: string | null;
  inst_tipo_institucion_id?: number | null;
}

export interface CarreraCatalogoApi {
  crra_id: number;
  crra_nombre: string | null;
}

export interface NivelEducacionalCatalogoApi {
  nved_id: number;
  nved_nombre: string | null;
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

export interface TipoContratoCatalogoApi {
  tpct_id: number;
  tpct_nombre: string | null;
  tpct_descripcion?: string | null;
}

export interface DisponibilidadCatalogoApi {
  disp_id: number;
  disp_nombre: string | null;
}

export interface EstadoSolicitudCandidatoCatalogoApi {
  essc_id: number;
  essc_nombre: string | null;
  essc_descripcion?: string | null;
}

export interface MotivoRechazoCatalogoApi {
  mtrc_id: number;
  mtrc_nombre: string | null;
  mtrc_descripcion?: string | null;
}

export interface EstadoCuestionarioCandidatoCatalogoApi {
  escc_id: number;
  escc_nombre: string | null;
}

export interface EstadoEntrevistaCatalogoApi {
  esev_id: number;
  esev_nombre: string | null;
  esev_descripcion?: string | null;
}

export interface TipoEntrevistaCatalogoApi {
  tpet_id: number;
  tpet_nombre: string | null;
  tpet_descripcion?: string | null;
}

export interface NombreResultadoCatalogoApi {
  nore_id: number;
  nore_nombre: string | null;
}

export interface RolCatalogoApi {
  rol_id: number;
  rol_nombre: string;
  rol_descripcion?: string | null;
  permisos?: PermisoCatalogoApi[];
}

export interface PermisoCatalogoApi {
  per_id: number;
  per_nombre: string;
  per_descripcion?: string | null;
}

export interface AreaCatalogoApi {
  area_id: number;
  area_nombre: string | null;
  area_descripcion?: string | null;
}

export interface EstadoUsuarioCatalogoApi {
  esusr_id: number;
  esusr_nombre: string;
  esusr_descripcion?: string | null;
}

export interface UsuarioCatalogoApi {
  usr_id: number;
  usr_nombres: string;
  usr_apellido_paterno: string;
  usr_apellido_materno?: string | null;
  usr_email: string;
  usr_rol_id?: number | null;
  usr_estado_usuario_id?: number | null;
  usr_area_id?: number | null;
  rol?: { rol_id: number; rol_nombre: string } | null;
  area?: AreaCatalogoApi | null;
  estado?: EstadoUsuarioCatalogoApi | null;
  permisos?: string[];
}

@Injectable({
  providedIn: 'root',
})
export class CatalogosService {
  private readonly apiUrl = '/catalogos';
  private readonly usuariosApiUrl = '/usuarios';

  constructor(private http: HttpClient) {}

  listarCatalogo<T>(path: CatalogoPath, params?: CatalogoListParams) {
    return this.http.get<T[]>(`${this.apiUrl}/${path}`, { params: this.crearParams(params) });
  }

  obtenerCatalogo<T>(path: CatalogoPath, id: number) {
    return this.http.get<T>(`${this.apiUrl}/${path}/${id}`);
  }

  crearCatalogo<T, P extends object>(path: CatalogoPath, payload: P) {
    return this.http.post<T>(`${this.apiUrl}/${path}`, payload);
  }

  reemplazarCatalogo<T, P extends object>(path: CatalogoPath, id: number, payload: P) {
    return this.http.put<T>(`${this.apiUrl}/${path}/${id}`, payload);
  }

  actualizarCatalogo<T, P extends object>(path: CatalogoPath, id: number, payload: P) {
    return this.http.patch<T>(`${this.apiUrl}/${path}/${id}`, payload);
  }

  eliminarCatalogo(path: CatalogoPath, id: number) {
    return this.http.delete<void>(`${this.apiUrl}/${path}/${id}`);
  }

  listarPaises(params?: CatalogoListParams) {
    return this.listarCatalogo<PaisCatalogoApi>('paises', params);
  }

  listarRegiones(params?: CatalogoListParams) {
    return this.listarCatalogo<RegionCatalogoApi>('regiones', params);
  }

  listarCiudades(regionId?: number) {
    return this.http.get<CiudadCatalogoApi[]>(`${this.apiUrl}/ciudades`, {
      params: this.crearParams(regionId ? { region_id: regionId } : undefined),
    });
  }

  listarComunas(params?: CatalogoListParams) {
    return this.listarCatalogo<ComunaCatalogoApi>('comunas', params);
  }

  listarTiposInstitucion(params?: CatalogoListParams) {
    return this.listarCatalogo<TipoInstitucionCatalogoApi>('tipos-institucion', params);
  }

  listarInstituciones(params?: CatalogoListParams) {
    return this.listarCatalogo<InstitucionCatalogoApi>('instituciones', params);
  }

  listarCarreras(params?: CatalogoListParams) {
    return this.listarCatalogo<CarreraCatalogoApi>('carreras', params);
  }

  listarNivelesEducacionales(params?: CatalogoListParams) {
    return this.listarCatalogo<NivelEducacionalCatalogoApi>('niveles-educacionales', params);
  }

  listarCargos() {
    // Integración: los catálogos se consumen con la nomenclatura real del backend/BD.
    return this.http.get<CargoCatalogoApi[]>(`${this.apiUrl}/cargos`);
  }

  listarUsuarios() {
    // Integración: usuarios viene desde /usuarios con campos usr_*.
    return this.http.get<UsuarioCatalogoApi[]>(`${this.usuariosApiUrl}/`);
  }

  listarRoles() {
    return this.http.get<RolCatalogoApi[]>(`${this.usuariosApiUrl}/roles`);
  }

  listarPermisos() {
    return this.http.get<PermisoCatalogoApi[]>(`${this.usuariosApiUrl}/permisos`);
  }

  listarAreas() {
    return this.http.get<AreaCatalogoApi[]>(`${this.usuariosApiUrl}/areas`);
  }

  listarEstadosUsuario() {
    return this.http.get<EstadoUsuarioCatalogoApi[]>(`${this.usuariosApiUrl}/estados`);
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

  listarTiposContrato() {
    return this.http.get<TipoContratoCatalogoApi[]>(`${this.apiUrl}/tipos-contrato`);
  }

  listarDisponibilidades() {
    return this.http.get<DisponibilidadCatalogoApi[]>(`${this.apiUrl}/disponibilidades`);
  }

  listarHabilidades() {
    return this.http.get<HabilidadCatalogoApi[]>(`${this.apiUrl}/habilidades`);
  }

  listarNivelesHabilidad() {
    return this.http.get<NivelHabilidadCatalogoApi[]>(`${this.apiUrl}/niveles-habilidad`);
  }

  listarEstadosSolicitudCandidato(params?: CatalogoListParams) {
    return this.listarCatalogo<EstadoSolicitudCandidatoCatalogoApi>('estados-solicitud-candidato', params);
  }

  listarMotivosRechazo(params?: CatalogoListParams) {
    return this.listarCatalogo<MotivoRechazoCatalogoApi>('motivos-rechazo', params);
  }

  listarEstadosCuestionarioCandidato(params?: CatalogoListParams) {
    return this.listarCatalogo<EstadoCuestionarioCandidatoCatalogoApi>('estados-cuestionario-candidato', params);
  }

  listarEstadosEntrevista(params?: CatalogoListParams) {
    return this.listarCatalogo<EstadoEntrevistaCatalogoApi>('estados-entrevista', params);
  }

  listarTiposEntrevista(params?: CatalogoListParams) {
    return this.listarCatalogo<TipoEntrevistaCatalogoApi>('tipos-entrevista', params);
  }

  listarNombresResultado(params?: CatalogoListParams) {
    return this.listarCatalogo<NombreResultadoCatalogoApi>('nombres-resultado', params);
  }

  private crearParams(params?: CatalogoListParams) {
    let httpParams = new HttpParams();

    Object.entries(params ?? {}).forEach(([clave, valor]) => {
      if (valor !== undefined && valor !== null && valor !== '') {
        httpParams = httpParams.set(clave, String(valor));
      }
    });

    return httpParams;
  }
}
