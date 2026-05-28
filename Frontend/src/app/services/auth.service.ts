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

  constructor(private http: HttpClient) {}

  login(credenciales: LoginRequest) {
    return this.http.post<LoginResponse>(this.apiUrl, credenciales);
  }

  guardarToken(token: string) {
    localStorage.setItem(this.tokenKey, token);
  }

  obtenerToken() {
    return localStorage.getItem(this.tokenKey);
  }

  eliminarToken() {
    localStorage.removeItem(this.tokenKey);
  }

  estaAutenticado() {
    return this.obtenerToken() !== null;
  }
}
