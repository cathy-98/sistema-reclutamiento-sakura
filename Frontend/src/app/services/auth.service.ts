import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, map, of, switchMap, tap } from 'rxjs';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface TokenPayload {
  sub?: string;
  usuario_id?: number;
  rol_id?: number;
  exp?: number;
}

interface UsuarioPerfilResponse {
  usr_nombres: string;
  usr_apellido_paterno: string;
  usr_apellido_materno?: string | null;
  usr_email: string;
  rol?: {
    rol_id: number;
    rol_nombre: string;
  } | null;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly apiUrl = 'http://localhost:8000/auth/login';
  private readonly usuariosApiUrl = 'http://localhost:8000/usuarios';
  private readonly tokenKey = 'sakura_access_token';
  private readonly nombreKey = 'sakura_nombre';
  private readonly rolKey = 'sakura_rol';
  private readonly rolesPorId: Record<number, string> = {
    1: 'Administrador',
    2: 'Reclutador',
    3: 'Entrevistador',
  };

  constructor(private http: HttpClient) {}

  login(credenciales: LoginRequest) {
    return this.http.post<LoginResponse>(this.apiUrl, credenciales).pipe(
      tap((respuesta) => this.guardarSesion(respuesta)),
      switchMap((respuesta) => this.cargarPerfilUsuario().pipe(map(() => respuesta)))
    );
  }

  guardarSesion(respuesta: LoginResponse) {
    localStorage.setItem(this.tokenKey, respuesta.access_token);
  }

  cargarPerfilUsuario() {
    const usuarioId = this.obtenerPayload()?.usuario_id;

    if (!usuarioId) {
      return of(null);
    }

    return this.http.get<UsuarioPerfilResponse>(`${this.usuariosApiUrl}/${usuarioId}`).pipe(
      tap((perfil) => this.guardarPerfil(perfil)),
      catchError(() => of(null))
    );
  }

  guardarPerfil(perfil: UsuarioPerfilResponse) {
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
    return this.obtenerPayload()?.sub ?? '';
  }

  obtenerRol() {
    const rolGuardado = localStorage.getItem(this.rolKey);

    if (rolGuardado) {
      return rolGuardado;
    }

    const rolId = this.obtenerPayload()?.rol_id;
    return rolId ? this.rolesPorId[rolId] ?? `Rol ${rolId}` : '';
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

  eliminarToken() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.nombreKey);
    localStorage.removeItem(this.rolKey);
  }

  estaAutenticado() {
    const payload = this.obtenerPayload();

    if (!payload?.exp) {
      return this.obtenerToken() !== null;
    }

    return payload.exp * 1000 > Date.now();
  }
}
