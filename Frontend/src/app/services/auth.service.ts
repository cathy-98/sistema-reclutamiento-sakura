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

export type RolUsuario = 'Administrador' | 'Reclutador' | 'Candidato' | 'Entrevistador';

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
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly loginTimeoutMs = 20000;
  private readonly perfilLoginTimeoutMs = 3000;
  private readonly authApiUrl = '/api/auth';
  private readonly apiUrl = `${this.authApiUrl}/login`;
  private readonly usuariosApiUrl = '/api/usuarios';
  private readonly tokenKey = 'sakura_access_token';
  private readonly nombreKey = 'sakura_nombre';
  private readonly rolKey = 'sakura_rol';
  private readonly principalTypeKey = 'sakura_principal_type';
  private readonly rolesPorId: Record<number, RolUsuario> = {
    1: 'Administrador',
    2: 'Reclutador',
    3: 'Candidato',
    4: 'Entrevistador',
  };

  constructor(private http: HttpClient) {}

  login(credenciales: LoginRequest) {
    // Integracion interna M3: POST /auth/login retorna principal_type para separar usuario/candidato.
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

  guardarSesion(respuesta: LoginResponse) {
    localStorage.setItem(this.tokenKey, respuesta.access_token);
    localStorage.setItem(this.principalTypeKey, respuesta.principal_type);

    if (respuesta.principal_type === 'candidato') {
      localStorage.setItem(this.rolKey, 'Candidato');
    }
  }

  cargarPerfilActual() {
    const principalType = this.obtenerPrincipalType();

    if (principalType === 'candidato') {
      return this.cargarPerfilCandidato();
    }

    return this.cargarPerfilUsuario();
  }

  cargarPerfilUsuario() {
    // Integracion interna M3: GET /auth/me devuelve el usuario interno actual desde el Bearer token.
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
    // Integracion interna M3: GET /auth/me con principal_type=candidato devuelve datos del candidato autenticado.
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
      }),
      catchError(() => of(null))
    );
  }

  guardarPerfil(perfil: UsuarioPerfilResponse) {
    // Mapeo API -> sesión front: traduce usr_* a nombre/rol visible en la interfaz.
    const nombreCompleto = [
      perfil.usr_nombres,
      perfil.usr_apellido_paterno,
      perfil.usr_apellido_materno,
    ]
      .filter(Boolean)
      .join(' ');

    localStorage.setItem(this.nombreKey, nombreCompleto || perfil.usr_email);

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

  eliminarToken() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.nombreKey);
    localStorage.removeItem(this.rolKey);
    localStorage.removeItem(this.principalTypeKey);
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
}
