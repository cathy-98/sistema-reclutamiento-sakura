export type PerfilTab = 'experiencia' | 'estudios' | 'postulaciones' | 'match' | 'evaluaciones' | 'documentos' | 'observaciones';

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
  rut: string;
  fechaNacimiento: string;
  fechaRegistro: string;
  tituloProfesional: string;
  estadoUsuario: string;
  resumenProfesional: string;
  urlPerfil: string;
  enlaces: EnlacePerfil[];
  idiomas: string[];
  comuna: string;
  direccion: string;
}

export interface EnlacePerfil {
  tipo: string;
  url: string;
  texto: string;
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
  fecha: string;
}

export type PostulacionPerfil = [string, string, string, string, string];

export interface EntrevistaPerfilResumen {
  titulo: string;
  solicitud: string;
  clienteEmpresa: string;
  fecha: string;
  hora: string;
  estado: string;
}

export interface EtapaSeleccion {
  id?: string;
  solicitud?: string;
  etapa: string;
  estado: string;
  fecha: string;
  entrevistador: string;
  tipoEntrevista: string;
  tipos: {
    id: number;
    nombre: string;
    entrevistadoresIds: number[];
  }[];
  evaluaciones: {
    id: number;
    tipoId?: number | null;
    tipoNombre?: string | null;
    usuarioId?: number | null;
    usuarioNombre?: string | null;
    resultadoId: number;
    resultado: string;
    observacion?: string | null;
  }[];
  observacionEntrevista: string;
  observaciones: string;
  resultadoEntrevista: string;
}

export type HabilidadComparada = [string, string, string, string, string, string, string, string];
export type DocumentoPerfil = [string, string, string, string];
export type ObservacionPerfil = [string, string, string, string];
export type EvaluacionTecnicaPerfil = [string, string, string, string, string];
