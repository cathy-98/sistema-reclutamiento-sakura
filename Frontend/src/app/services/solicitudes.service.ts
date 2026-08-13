import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, forkJoin, map, of, timeout } from 'rxjs';
import { CatalogosService, UsuarioCatalogoApi } from './catalogos.service';
import { ClienteApi, ClientesService } from './clientes.service';
import {
  EstadoSolicitud,
  PrioridadSolicitud,
  SolicitudApi,
  SolicitudCreatePayload,
  SolicitudHabilidadPayload,
  SolicitudResumen,
  SolicitudUpdatePayload,
} from '../shared/models/solicitud.model';
import { mapearSolicitudResumen } from '../shared/mappers/solicitud.mapper';

@Injectable({
  providedIn: 'root',
})
export class SolicitudesService {
  private readonly apiUrl = '/api/solicitudes';

  constructor(
    private http: HttpClient,
    private catalogosService: CatalogosService,
    private clientesService: ClientesService,
  ) {}

  listar() {
    return forkJoin({
      solicitudes: this.http.get<SolicitudApi[]>(`${this.apiUrl}/`).pipe(timeout(3000)),
      clientes: this.clientesService.listarClientes().pipe(timeout(4000), catchError(() => of([]))),
      empresas: this.clientesService.listarEmpresas().pipe(timeout(4000), catchError(() => of([]))),
      cargos: this.catalogosService.listarCargos().pipe(timeout(4000), catchError(() => of([]))),
      usuarios: this.catalogosService.listarUsuarios().pipe(timeout(4000), catchError(() => of([]))),
      prioridades: this.catalogosService.listarPrioridadesSolicitud().pipe(timeout(4000), catchError(() => of([]))),
      estados: this.catalogosService.listarEstadosSolicitud().pipe(timeout(4000), catchError(() => of([]))),
    }).pipe(
      map(({ solicitudes, clientes, empresas, cargos, usuarios, prioridades, estados }) =>
        this.mapearSolicitudes(solicitudes, {
          clientes,
          empresas,
          cargos,
          usuarios,
          prioridades,
          estados,
        }),
      ),
    );
  }

  obtenerPorId(id: string) {
    // Integración: el detalle queda en formato SolicitudApi para rellenar formularios con campos sol_*.
    return this.http.get<SolicitudApi>(`${this.apiUrl}/${id}`);
  }

  crear(payload: SolicitudCreatePayload) {
    // Integración: el payload ya viene adaptado a backend/BD, por eso se envía directo.
    return this.http.post<SolicitudApi>(`${this.apiUrl}/`, payload);
  }

  actualizar(id: string, payload: SolicitudUpdatePayload) {
    // Integración: PATCH usa los mismos nombres sol_* que espera el backend.
    return this.http.patch<SolicitudApi>(`${this.apiUrl}/${id}`, payload);
  }

  cambiarEstado(id: string, estado: EstadoSolicitud, observacion: string) {
    return this.http.patch<any>(`${this.apiUrl}/${id}/estado`, {
      sol_estado_solicitud_id: estado === 'Cancelado' ? 4 : 1,
      observacion,
    });
  }

  agregarHabilidades(id: string, habilidades: SolicitudHabilidadPayload[]) {
    return this.http.post(`${this.apiUrl}/${id}/habilidades`, habilidades);
  }

  eliminarHabilidad(id: string, habilidadId: number) {
    return this.http.delete(`${this.apiUrl}/${id}/habilidades/${habilidadId}`);
  }

  private nombreUsuario(usuario: UsuarioCatalogoApi) {
    return [usuario.usr_nombres, usuario.usr_apellido_paterno, usuario.usr_apellido_materno]
      .filter(Boolean)
      .join(' ') || usuario.usr_email;
  }

  private nombreCliente(cliente: ClienteApi, empresasPorId: Map<number, string>) {
    const empresa = cliente.cli_empresa_id ? empresasPorId.get(cliente.cli_empresa_id) : null;
    return empresa ? `${cliente.cli_nombre} - ${empresa}` : cliente.cli_nombre;
  }

  private mapearSolicitudes(
    solicitudes: SolicitudApi[],
    catalogos?: {
      clientes: ClienteApi[];
      empresas: { emp_id: number; emp_nombre?: string | null }[];
      cargos: { crgo_id: number; crgo_nombre?: string | null }[];
      usuarios: UsuarioCatalogoApi[];
      prioridades: { prsol_id: number; prsol_nombre?: string | null }[];
      estados: { essl_id: number; essl_nombre?: string | null }[];
    },
  ) {
    const empresasPorId = new Map((catalogos?.empresas ?? []).map((empresa) => [empresa.emp_id, empresa.emp_nombre ?? 'Empresa sin nombre']));
    const clientesPorId = new Map(
      (catalogos?.clientes ?? []).map((cliente) => [cliente.cli_id, this.nombreCliente(cliente, empresasPorId)]),
    );
    const cargosPorId = new Map((catalogos?.cargos ?? []).map((cargo) => [cargo.crgo_id, cargo.crgo_nombre ?? 'Cargo sin nombre']));
    const usuariosPorId = new Map((catalogos?.usuarios ?? []).map((usuario) => [usuario.usr_id, this.nombreUsuario(usuario)]));
    const prioridadesPorId = new Map(
      (catalogos?.prioridades ?? []).map((prioridad) => [prioridad.prsol_id, prioridad.prsol_nombre ?? 'Sin prioridad']),
    );
    const estadosPorId = new Map((catalogos?.estados ?? []).map((estado) => [estado.essl_id, estado.essl_nombre ?? 'Sin estado']));

    return solicitudes.map((solicitud) =>
      mapearSolicitudResumen(solicitud, {
        cargosPorId,
        clientesPorId,
        usuariosPorId,
        prioridadesPorId,
        estadosPorId,
      }),
    );
  }
}
