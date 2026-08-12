export type PrioridadSolicitud = 'Alta' | 'Media' | 'Baja';
export type EstadoSolicitud = 'Pendiente' | 'En curso' | 'Cerrada' | 'Cancelada' | string;

// Modelo de integración: mantiene la misma nomenclatura que entrega backend/BD.
export interface SolicitudApi {
  sol_id: number;
  sol_codigo?: string | null;
  sol_titulo?: string | null;
  sol_descripcion?: string | null;
  sol_observacion?: string | null;
  sol_cantidad_vacantes?: number | null;
  sol_salario_min?: number | null;
  sol_salario_max?: number | null;
  sol_fecha_inicio_busqueda?: string | null;
  sol_fecha_cierre_busqueda?: string | null;
  sol_fecha_inicio_cliente?: string | null;
  sol_hora_inicio_jornada?: string | null;
  sol_hora_fin_jornada?: string | null;
  sol_cargo_id?: number | null;
  sol_prioridad_id?: number | null;
  sol_cliente_id?: number | null;
  sol_usuario_creador_id?: number | null;
  sol_usuario_asignado_id?: number | null;
  sol_modalidad_id?: number | null;
  sol_estado_solicitud_id?: number | null;
  sol_tipo_contrato_id?: number | null;
  habilidades?: SolicitudHabilidadApi[];
}

export interface SolicitudHabilidadApi {
  solhb_id: number;
  solhb_solicitud_id: number;
  solhb_habilidad_id: number;
  solhb_nivel_habilidad_id?: number | null;
  solhb_anios_experiencia_req?: number | null;
  solhb_es_excluyente?: boolean | null;
}

// Payload de integración: se envía a la API con los nombres que espera backend.
export interface SolicitudHabilidadPayload {
  solhb_habilidad_id: number;
  solhb_nivel_habilidad_id?: number | null;
  solhb_anios_experiencia_req: number;
  solhb_es_excluyente: boolean;
}

// Payload de integración: crear solicitud usa nombres sol_* para evitar traducciones al enviar.
export interface SolicitudCreatePayload {
  sol_codigo: string;
  sol_titulo: string;
  sol_descripcion?: string | null;
  sol_cantidad_vacantes?: number | null;
  sol_salario_min?: number | null;
  sol_salario_max?: number | null;
  sol_fecha_inicio_busqueda?: string | null;
  sol_fecha_cierre_busqueda?: string | null;
  sol_fecha_inicio_cliente?: string | null;
  sol_hora_inicio_jornada?: string | null;
  sol_hora_fin_jornada?: string | null;
  sol_cargo_id?: number | null;
  sol_prioridad_id?: number | null;
  sol_cliente_id: number;
  sol_usuario_creador_id: number;
  sol_usuario_asignado_id?: number | null;
  sol_modalidad_id?: number | null;
  sol_estado_solicitud_id?: number | null;
  sol_tipo_contrato_id?: number | null;
  habilidades?: SolicitudHabilidadPayload[];
}

// Payload de integración: editar solicitud conserva los campos reales del backend.
export interface SolicitudUpdatePayload {
  sol_titulo?: string | null;
  sol_descripcion?: string | null;
  sol_cantidad_vacantes?: number | null;
  sol_salario_min?: number | null;
  sol_salario_max?: number | null;
  sol_fecha_inicio_busqueda?: string | null;
  sol_fecha_cierre_busqueda?: string | null;
  sol_fecha_inicio_cliente?: string | null;
  sol_hora_inicio_jornada?: string | null;
  sol_hora_fin_jornada?: string | null;
  sol_cargo_id?: number | null;
  sol_prioridad_id?: number | null;
  sol_cliente_id?: number | null;
  sol_usuario_asignado_id?: number | null;
  sol_modalidad_id?: number | null;
  sol_estado_solicitud_id?: number | null;
  sol_tipo_contrato_id?: number | null;
}

// Modelo de pantalla: nombres simples usados por tablas/componentes del front.
export interface SolicitudResumen {
  id: string;
  codigo: string;
  nombre: string;
  cliente: string;
  cargo: string;
  vacantes: number;
  responsable: string;
  seleccion: string;
  inicioEmpleo: string;
  prioridad: PrioridadSolicitud;
  estado: EstadoSolicitud;
  observacion: string;
}
