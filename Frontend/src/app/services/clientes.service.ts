import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';

export interface ClienteListParams {
  q?: string;
  empresa_id?: number;
  skip?: number;
  limit?: number;
}

export interface EmpresaApi {
  emp_id: number;
  emp_nombre?: string | null;
  emp_identificacion?: string | null;
}

export interface EmpresaCreatePayload {
  emp_nombre: string;
  emp_identificacion?: string | null;
}

export interface ClienteApi {
  cli_id: number;
  cli_nombre: string;
  cli_cargo_empresa_id?: number | null;
  cli_area_empresa_id?: number | null;
  cli_empresa_id?: number | null;
  cli_email?: string | null;
  cli_email2?: string | null;
  cli_telefono1?: string | null;
  cli_telefono2?: string | null;
}

export interface ClienteCreatePayload {
  cli_nombre: string;
  cli_empresa_id: number;
  cli_cargo_empresa_id?: number | null;
  cli_area_empresa_id?: number | null;
  cli_email?: string | null;
  cli_email2?: string | null;
  cli_telefono1?: string | null;
  cli_telefono2?: string | null;
}

@Injectable({
  providedIn: 'root',
})
export class ClientesService {
  private readonly apiUrl = '/api/clientes';

  constructor(private http: HttpClient) {}

  listarClientes(params?: ClienteListParams) {
    return this.http.get<ClienteApi[]>(this.apiUrl, { params: this.crearParams(params) });
  }

  listarEmpresas(params?: Omit<ClienteListParams, 'empresa_id'>) {
    return this.http.get<EmpresaApi[]>(`${this.apiUrl}/empresas`, { params: this.crearParams(params) });
  }

  crearEmpresa(payload: EmpresaCreatePayload) {
    return this.http.post<EmpresaApi>(`${this.apiUrl}/empresas`, payload);
  }

  crearCliente(payload: ClienteCreatePayload) {
    return this.http.post<ClienteApi>(this.apiUrl, payload);
  }

  obtenerCliente(id: number) {
    return this.http.get<ClienteApi>(`${this.apiUrl}/${id}`);
  }

  obtenerEmpresa(id: number) {
    return this.http.get<EmpresaApi>(`${this.apiUrl}/empresas/${id}`);
  }

  private crearParams(params?: ClienteListParams | Omit<ClienteListParams, 'empresa_id'>) {
    let httpParams = new HttpParams();

    if (!params) {
      return httpParams;
    }

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        httpParams = httpParams.set(key, String(value));
      }
    });

    return httpParams;
  }
}
