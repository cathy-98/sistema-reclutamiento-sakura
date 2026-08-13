import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, forkJoin, map, of, timeout } from 'rxjs';
import { CatalogosService, UsuarioCatalogoApi } from './catalogos.service';
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
  private readonly apiUrl = '/solicitudes';

  constructor(
    private http: HttpClient,
    private catalogosService: CatalogosService,
  ) {}

  listar() {
    // Integración: se consultan solicitudes y catálogos con nomenclatura backend/BD.
    // El mapeo a SolicitudResumen ocurre al final para alimentar la tabla del front.
    return forkJoin({
      solicitudes: this.http.get<SolicitudApi[]>(`${this.apiUrl}/`),
      cargos: this.catalogosService.listarCargos().pipe(
        timeout(4000),
        catchError(() => of([])),
      ),
      usuarios: this.catalogosService.listarUsuarios().pipe(
        timeout(4000),
        catchError(() => of([])),
      ),
      prioridades: this.catalogosService.listarPrioridadesSolicitud().pipe(
        timeout(4000),
        catchError(() => of([])),
      ),
      estados: this.catalogosService.listarEstadosSolicitud().pipe(
        timeout(4000),
        catchError(() => of([])),
      ),
    }).pipe(
      map(({ solicitudes, cargos, usuarios, prioridades, estados }) => {
        const cargosPorId = new Map(cargos.map((cargo) => [cargo.crgo_id, cargo.crgo_nombre ?? 'Cargo sin nombre']));
        const usuariosPorId = new Map(usuarios.map((usuario) => [usuario.usr_id, this.nombreUsuario(usuario)]));
        const prioridadesPorId = new Map(
          prioridades.map((prioridad) => [prioridad.prsol_id, prioridad.prsol_nombre ?? 'Sin prioridad']),
        );
        const estadosPorId = new Map(estados.map((estado) => [estado.essl_id, estado.essl_nombre ?? 'Sin estado']));

        return solicitudes.map((solicitud) =>
          mapearSolicitudResumen(solicitud, {
            cargosPorId,
            usuariosPorId,
            prioridadesPorId,
            estadosPorId,
          }),
        );
      }),
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
}
