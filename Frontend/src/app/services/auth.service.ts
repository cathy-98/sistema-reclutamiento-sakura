import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  usuario: string;
  rol: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly apiUrl = 'http://localhost:8000/api/auth/login';
  private readonly tokenKey = 'sakura_access_token';
  private readonly usuarioKey = 'sakura_usuario';
  private readonly rolKey = 'sakura_rol';
  private readonly nombresVisibles: Record<string, string> = {
    fvaldesm: 'Felipe Valdes',
    cathy98: 'Cathy',
  };

  constructor(private http: HttpClient) {}

  login(credenciales: LoginRequest) {
    return this.http.post<LoginResponse>(this.apiUrl, credenciales);
  }

  guardarSesion(respuesta: LoginResponse) {
    localStorage.setItem(this.tokenKey, respuesta.access_token);
    localStorage.setItem(this.usuarioKey, respuesta.usuario);
    localStorage.setItem(this.rolKey, respuesta.rol);
  }

  guardarToken(token: string) {
    localStorage.setItem(this.tokenKey, token);
  }

  obtenerToken() {
    return localStorage.getItem(this.tokenKey);
  }

  obtenerUsuario() {
    return localStorage.getItem(this.usuarioKey);
  }

  obtenerRol() {
    return localStorage.getItem(this.rolKey);
  }

  obtenerNombreVisible() {
    const usuario = this.obtenerUsuario();

    if (!usuario) {
      return 'usuario';
    }

    return this.nombresVisibles[usuario] ?? usuario;
  }

  obtenerRolVisible() {
    return this.obtenerRol() ?? '';
  }

  eliminarToken() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.usuarioKey);
    localStorage.removeItem(this.rolKey);
  }

  estaAutenticado() {
    return this.obtenerToken() !== null;
  }
}
