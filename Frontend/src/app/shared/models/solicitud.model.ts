export type PrioridadSolicitud = 'Alta' | 'Media' | 'Baja';
export type EstadoSolicitud = 'Pendiente' | 'En curso' | 'Cerrada' | 'Cancelada';

export interface SolicitudResumen {
  id: string;
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

