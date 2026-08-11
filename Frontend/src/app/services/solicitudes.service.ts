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

@Injectable({
  providedIn: 'root',
})
export class SolicitudesService {
  private readonly apiUrl = 'http://localhost:8000/solicitudes';
  private readonly clientePendiente = 'Cliente pendiente';

  constructor(
    private http: HttpClient,
    private catalogosService: CatalogosService,
  ) {}

  listar() {
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
          this.mapearSolicitudResumen(solicitud, {
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
    return this.http.get<SolicitudApi>(`${this.apiUrl}/${id}`);
  }

  crear(payload: SolicitudCreatePayload) {
    return this.http.post<SolicitudApi>(`${this.apiUrl}/`, payload);
  }

  actualizar(id: string, payload: SolicitudUpdatePayload) {
    return this.http.patch<SolicitudApi>(`${this.apiUrl}/${id}`, payload);
  }

  cambiarEstado(id: string, estado: EstadoSolicitud, observacion: string) {
    return this.http.patch<any>(`${this.apiUrl}/${id}/estado`, {
      sol_estado_solicitud_id: estado === 'Cancelada' ? 4 : 1,
      observacion,
    });
  }

  agregarHabilidades(id: string, habilidades: SolicitudHabilidadPayload[]) {
    return this.http.post(`${this.apiUrl}/${id}/habilidades`, habilidades);
  }

  eliminarHabilidad(id: string, habilidadId: number) {
    return this.http.delete(`${this.apiUrl}/${id}/habilidades/${habilidadId}`);
  }

  private mapearSolicitudResumen(
    solicitud: SolicitudApi,
    catalogos: {
      cargosPorId: Map<number, string>;
      usuariosPorId: Map<number, string>;
      prioridadesPorId: Map<number, string>;
      estadosPorId: Map<number, string>;
    },
  ): SolicitudResumen {
    return {
      id: String(solicitud.sol_id),
      codigo: solicitud.sol_codigo || `Solicitud ${solicitud.sol_id}`,
      nombre: solicitud.sol_titulo || 'Sin nombre',
      // No existe endpoint de clientes reutilizable; queda neutro hasta integrar esa fuente real.
      cliente: this.clientePendiente,
      cargo: this.obtenerNombre(catalogos.cargosPorId, solicitud.sol_cargo_id, 'Cargo pendiente'),
      vacantes: solicitud.sol_cantidad_vacantes ?? 0,
      responsable: this.obtenerNombre(catalogos.usuariosPorId, solicitud.sol_usuario_asignado_id, 'Sin asignar'),
      seleccion: this.formatearRangoFechas(
        solicitud.sol_fecha_inicio_busqueda,
        solicitud.sol_fecha_cierre_busqueda,
      ),
      inicioEmpleo: this.formatearFecha(solicitud.sol_fecha_inicio_cliente),
      prioridad: this.obtenerNombre(
        catalogos.prioridadesPorId,
        solicitud.sol_prioridad_id,
        'Sin prioridad',
      ) as PrioridadSolicitud,
      estado: this.normalizarEstado(
        this.obtenerNombre(catalogos.estadosPorId, solicitud.sol_estado_solicitud_id, 'Sin estado'),
      ),
      observacion: solicitud.sol_observacion || 'Sin observación',
    };
  }

  private obtenerNombre(catalogo: Map<number, string>, id: number | null | undefined, fallback: string) {
    if (id == null) {
      return fallback;
    }

    return catalogo.get(id) || fallback;
  }

  private nombreUsuario(usuario: UsuarioCatalogoApi) {
    return [usuario.usr_nombres, usuario.usr_apellido_paterno, usuario.usr_apellido_materno]
      .filter(Boolean)
      .join(' ') || usuario.usr_email;
  }

  private formatearRangoFechas(inicio?: string | null, fin?: string | null) {
    const inicioFormateado = this.formatearFecha(inicio);
    const finFormateado = this.formatearFecha(fin);

    if (inicioFormateado === 'Sin fecha' && finFormateado === 'Sin fecha') {
      return 'Sin fechas';
    }

    return `${inicioFormateado} - ${finFormateado}`;
  }

  private formatearFecha(fecha?: string | null) {
    if (!fecha) {
      return 'Sin fecha';
    }

    const fechaNormalizada = new Date(fecha);

    if (Number.isNaN(fechaNormalizada.getTime())) {
      return 'Sin fecha';
    }

    return new Intl.DateTimeFormat('es-CL').format(fechaNormalizada);
  }

  private normalizarEstado(estado: string): EstadoSolicitud {
    if (estado === 'En Curso') {
      return 'En curso';
    }

    if (estado === 'Cancelado') {
      return 'Cancelada';
    }

    if (estado === 'Cerrado') {
      return 'Cerrada';
    }

    return estado;
  }
}
