import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, map, of, switchMap, tap, timeout } from 'rxjs';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
  principal_type: 'usuario' | 'candidato';
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ForgotPasswordResponse {
  message: string;
}

export interface ResetPasswordRequest {
  token: string;
  nueva_contrasena: string;
}

export interface ChangePasswordRequest {
  password_actual: string;
  password_nueva: string;
}

export type RolUsuario = 'Administrador' | 'Reclutador' | 'Candidato' | 'Entrevistador';
export type PermisoUsuario = string;

interface TokenPayload {
  sub?: string;
  email?: string;
  usuario_id?: number;
  rol_id?: number;
  principal_type?: 'usuario' | 'candidato';
  exp?: number;
}

interface UsuarioPerfilResponse {
  usr_nombres: string;
  usr_apellido_paterno: string;
  usr_apellido_materno?: string | null;
  usr_email: string;
  usr_rol_id?: number | null;
  rol?: {
    rol_id: number;
    rol_nombre: string;
  } | null;
  permisos?: string[];
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  // M1 Autenticacion/Usuarios/RBAC - endpoints consumidos desde frontend:
  // POST /auth/login: autentica usuario interno o candidato y entrega JWT + principal_type.
  // GET /auth/me: recupera perfil actual; en usuarios internos tambien trae permisos del rol.
  // POST /auth/change-password: cambio de contrasena autenticado.
  // POST /auth/forgot-password: solicita recuperacion; respuesta generica anti-enumeracion.
  // POST /auth/reset-password: restablece contrasena por token de recuperacion.
  // GET /usuarios/{id}: fallback historico si /auth/me no estuviera disponible.
  private readonly loginTimeoutMs = 20000;
  private readonly perfilLoginTimeoutMs = 3000;
  private readonly authApiUrl = '/api/auth';
  private readonly apiUrl = `${this.authApiUrl}/login`;
  private readonly usuariosApiUrl = '/api/usuarios';
  private readonly tokenKey = 'sakura_access_token';
  private readonly nombreKey = 'sakura_nombre';
  private readonly rolKey = 'sakura_rol';
  private readonly principalTypeKey = 'sakura_principal_type';
  private readonly permisosKey = 'sakura_permisos';
  private readonly rolesPorId: Record<number, RolUsuario> = {
    1: 'Administrador',
    2: 'Reclutador',
    3: 'Candidato',
    4: 'Entrevistador',
  };

  constructor(private http: HttpClient) {}

  login(credenciales: LoginRequest) {
    // M1 Login: llama POST /auth/login y luego hidrata la sesion con /auth/me.
    // El principal_type decide si la navegacion continua como usuario interno o candidato.
    return this.http.post<LoginResponse>(this.apiUrl, credenciales).pipe(
      timeout(this.loginTimeoutMs),
      tap((respuesta) => this.guardarSesion(respuesta)),
      switchMap((respuesta) =>
        this.cargarPerfilActual().pipe(
          timeout(this.perfilLoginTimeoutMs),
          catchError(() => of(null)),
          map(() => respuesta)
        )
      )
    );
  }

  solicitarRecuperacionPassword(payload: ForgotPasswordRequest) {
    // M1 Recuperacion: POST /auth/forgot-password.
    // La UI permanece oculta hasta completar QA SMTP/correo, pero la integracion queda lista.
    return this.http.post<ForgotPasswordResponse>(`${this.authApiUrl}/forgot-password`, payload);
  }

  restablecerPassword(payload: ResetPasswordRequest) {
    // M1 Recuperacion: POST /auth/reset-password.
    // Frontend debe tratar 410 como token expirado y 400 como token invalido/usado.
    return this.http.post<void>(`${this.authApiUrl}/reset-password`, payload);
  }

  cambiarPassword(payload: ChangePasswordRequest) {
    // M1 Cambio de contrasena: POST /auth/change-password con Bearer token.
    // Backend valida password_actual y que password_nueva sea distinta.
    return this.http.post<void>(`${this.authApiUrl}/change-password`, payload);
  }

  guardarSesion(respuesta: LoginResponse) {
    // Sesion M1: persiste JWT, tipo de identidad y limpia permisos hasta leer /auth/me.
    localStorage.setItem(this.tokenKey, respuesta.access_token);
    localStorage.setItem(this.principalTypeKey, respuesta.principal_type);
    this.guardarPermisos([]);

    if (respuesta.principal_type === 'candidato') {
      localStorage.setItem(this.rolKey, 'Candidato');
    }
  }

  cargarPerfilActual() {
    // Perfil M1: centraliza la carga post-login segun principal_type.
    const principalType = this.obtenerPrincipalType();

    if (principalType === 'candidato') {
      return this.cargarPerfilCandidato();
    }

    return this.cargarPerfilUsuario();
  }

  cargarPerfilUsuario() {
    // M1 Usuario interno: GET /auth/me devuelve usr_*, rol y permisos calculados por backend.
    // Fallback backend anterior: si /auth/me no existe, consulta /usuarios/{id} usando el payload viejo.
    return this.http.get<UsuarioPerfilResponse>(`${this.authApiUrl}/me`).pipe(
      tap((perfil) => this.guardarPerfil(perfil)),
      catchError(() => {
        const usuarioId = this.obtenerUsuarioIdDesdeToken();

        if (!usuarioId) {
          return of(null);
        }

        return this.http.get<UsuarioPerfilResponse>(`${this.usuariosApiUrl}/${usuarioId}`).pipe(
          tap((perfil) => this.guardarPerfil(perfil)),
          catchError(() => of(null))
        );
      })
    );
  }

  cargarPerfilCandidato() {
    // M1/M3 Candidato: GET /auth/me con principal_type=candidato devuelve datos de autoservicio.
    // Candidato no usa permisos RBAC de usuario interno.
    return this.http.get<any>(`${this.authApiUrl}/me`).pipe(
      tap((perfil) => {
        const candidato = perfil?.candidato ?? perfil;
        const nombreCompleto = [
          candidato?.cand_nombres,
          candidato?.cand_apellido_paterno,
          candidato?.cand_apellido_materno,
        ]
          .filter(Boolean)
          .join(' ');

        localStorage.setItem(this.nombreKey, nombreCompleto || candidato?.cand_email || 'Candidato');
        localStorage.setItem(this.rolKey, 'Candidato');
        this.guardarPermisos([]);
      }),
      catchError(() => of(null))
    );
  }

  guardarPerfil(perfil: UsuarioPerfilResponse) {
    // M1 Perfil de usuario: traduce usr_* a nombre/rol visible y guarda permisos reales del backend.
    // Estos permisos alimentan guard, menu y acciones sin reemplazar la validacion final del backend.
    const nombreCompleto = [
      perfil.usr_nombres,
      perfil.usr_apellido_paterno,
      perfil.usr_apellido_materno,
    ]
      .filter(Boolean)
      .join(' ');

    localStorage.setItem(this.nombreKey, nombreCompleto || perfil.usr_email);
    this.guardarPermisos(perfil.permisos ?? []);

    if (perfil.rol?.rol_nombre) {
      localStorage.setItem(this.rolKey, perfil.rol.rol_nombre);
      return;
    }

    if (perfil.usr_rol_id && this.rolesPorId[perfil.usr_rol_id]) {
      localStorage.setItem(this.rolKey, this.rolesPorId[perfil.usr_rol_id]);
    }
  }

  guardarToken(token: string) {
    localStorage.setItem(this.tokenKey, token);
  }

  obtenerToken() {
    return localStorage.getItem(this.tokenKey);
  }

  obtenerPayload(): TokenPayload | null {
    const token = this.obtenerToken();

    if (!token) {
      return null;
    }

    try {
      const payload = token.split('.')[1];
      const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
      return JSON.parse(json) as TokenPayload;
    } catch {
      return null;
    }
  }

  obtenerUsuario() {
    const payload = this.obtenerPayload();
    return payload?.email ?? payload?.sub ?? '';
  }

  obtenerRol() {
    const rolGuardado = localStorage.getItem(this.rolKey);

    if (rolGuardado) {
      return rolGuardado as RolUsuario;
    }

    const rolId = this.obtenerPayload()?.rol_id;
    return rolId ? this.rolesPorId[rolId] ?? `Rol ${rolId}` : '';
  }

  obtenerPrincipalType() {
    return localStorage.getItem(this.principalTypeKey) ?? this.obtenerPayload()?.principal_type ?? 'usuario';
  }

  obtenerPermisos() {
    // M1 RBAC: permisos almacenados desde /auth/me, por ejemplo USR_VIEW, SOL_CREATE, CAN_VIEW.
    try {
      const permisos = JSON.parse(localStorage.getItem(this.permisosKey) ?? '[]');
      return Array.isArray(permisos) ? permisos.filter((permiso) => typeof permiso === 'string') : [];
    } catch {
      return [];
    }
  }

  obtenerNombreVisible() {
    const nombreGuardado = localStorage.getItem(this.nombreKey);

    if (nombreGuardado) {
      return nombreGuardado;
    }

    const payload = this.obtenerPayload();
    return payload?.sub || 'usuario';
  }

  obtenerRolVisible() {
    return this.obtenerRol() ?? '';
  }

  obtenerUsuarioId() {
    return this.obtenerUsuarioIdDesdeToken();
  }

  tieneRol(rolesPermitidos: RolUsuario[]) {
    const rol = this.obtenerRol();
    return rolesPermitidos.includes(rol as RolUsuario);
  }

  tienePermiso(permisosPermitidos: PermisoUsuario[], matchAll = false) {
    // M1 RBAC: helper para acciones/botones. matchAll=true exige todos los permisos declarados.
    if (!permisosPermitidos.length) {
      return true;
    }

    const permisosActuales = new Set(this.obtenerPermisos());
    return matchAll
      ? permisosPermitidos.every((permiso) => permisosActuales.has(permiso))
      : permisosPermitidos.some((permiso) => permisosActuales.has(permiso));
  }

  puedeAcceder(rolesPermitidos?: RolUsuario[], permisosPermitidos?: PermisoUsuario[], matchAll = false) {
    // M1 RBAC frontend: prioriza permisos reales cuando existen; mantiene roles como respaldo transitorio.
    // El backend sigue siendo la autoridad final y puede devolver 403 aunque la UI habilite una accion.
    const tieneRolesDeclarados = Boolean(rolesPermitidos?.length);
    const tienePermisosDeclarados = Boolean(permisosPermitidos?.length);
    const permisosActuales = this.obtenerPermisos();

    if (tienePermisosDeclarados && permisosActuales.length) {
      return this.tienePermiso(permisosPermitidos ?? [], matchAll);
    }

    if (tieneRolesDeclarados) {
      return this.tieneRol(rolesPermitidos ?? []);
    }

    return true;
  }

  eliminarToken() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.nombreKey);
    localStorage.removeItem(this.rolKey);
    localStorage.removeItem(this.principalTypeKey);
    localStorage.removeItem(this.permisosKey);
  }

  estaAutenticado() {
    const payload = this.obtenerPayload();

    if (!payload?.exp) {
      return this.obtenerToken() !== null;
    }

    return payload.exp * 1000 > Date.now();
  }

  private obtenerUsuarioIdDesdeToken() {
    const payload = this.obtenerPayload();
    const idDesdeSub = Number(payload?.sub);

    if (payload?.usuario_id) {
      return payload.usuario_id;
    }

    return Number.isNaN(idDesdeSub) ? null : idDesdeSub;
  }

  private guardarPermisos(permisos: string[]) {
    localStorage.setItem(this.permisosKey, JSON.stringify([...new Set(permisos)]));
  }
}
