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

  constructor(private http: HttpClient) {}

  login(credenciales: LoginRequest) {
    return this.http.post<LoginResponse>(this.apiUrl, credenciales);
  }
}
