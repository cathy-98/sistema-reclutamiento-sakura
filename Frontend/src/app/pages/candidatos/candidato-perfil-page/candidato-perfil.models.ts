export type PerfilTab = 'experiencia' | 'estudios' | 'postulaciones' | 'match' | 'documentos' | 'observaciones';

export interface CandidatoPerfil {
  idSolicitud: string;
  match: number;
  nombre: string;
  correo: string;
  telefono: string;
  cargo: string;
  estado: string;
  disponibilidad: string;
  renta: number;
  fechaNacimiento: string;
  fechaRegistro: string;
  tituloProfesional: string;
  estadoUsuario: string;
  resumenProfesional: string;
  urlPerfil: string;
  comuna: string;
  direccion: string;
}

export interface ExperienciaPerfil {
  empresa: string;
  cargo: string;
  fecha: string;
  descripcion: string;
  tags: string[];
}

export interface EstudioPerfil {
  titulo: string;
  institucion: string;
  estado: string;
  fecha: string;
}

export type PostulacionPerfil = [string, string, string, string, string];

export interface EtapaSeleccion {
  etapa: string;
  estado: string;
  fecha: string;
  entrevistador: string;
  resultado: string;
  observaciones: string;
}

export type HabilidadComparada = [string, string, string, string, string, string, string, string];
export type DocumentoPerfil = [string, string, string];
export type ObservacionPerfil = [string, string, string, string];
