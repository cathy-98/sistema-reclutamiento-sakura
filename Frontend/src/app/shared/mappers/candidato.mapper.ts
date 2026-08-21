import {
  CandidatoApi,
  CandidatoPerfil,
  CandidatoResumen,
  EstadoSolicitudCandidatoApi,
} from '../../services/candidatos.service';

export interface CandidatoResumenApi extends CandidatoApi {
  cand_apellidos?: string | null;
  cand_rut_sin_dv?: number | null;
  cand_dv?: number | string | null;
  solicitud_codigo?: string | null;
  cargo_nombre?: string | null;
  estado_postulacion?: EstadoSolicitudCandidatoApi | null;
  estado_usuario_nombre?: string | null;
  disponibilidad_nombre?: string | null;
  slcd_fecha_postulacion?: string | null;
  slcd_pretension_renta?: number | null;
  slcd_puntaje_compatibilidad?: number | string | null;
}

export interface CandidatoPerfilApi extends CandidatoResumenApi {
  direccion?: {
    drcd_calle?: string | null;
    drcd_numero?: number | string | null;
    drcd_dpto_oficina?: string | null;
    drcd_depto_oficina?: string | null;
    comuna?: { nombre?: string | null; cmn_nombre?: string | null } | null;
  } | null;
  disponibilidad?: { nombre?: string | null; disp_nombre?: string | null } | null;
}

// Mapeo API -> pantalla: concentra diferencias entre BD SQL y schemas actuales del backend.
export function mapearCandidatoResumen(candidato: CandidatoResumenApi): CandidatoResumen {
  return {
    id: String(candidato.cand_id),
    nombre: obtenerNombreCompleto(candidato),
    correo: candidato.cand_email ?? 'Sin correo',
    telefono: candidato.cand_telefono ?? undefined,
    cargo: candidato.cargo_nombre ?? undefined,
    estado: candidato.estado_postulacion ?? 'En revision',
    estadoUsuario: candidato.estado_usuario_nombre ?? undefined,
    match: normalizarNumero(candidato.slcd_puntaje_compatibilidad),
    idSolicitud: candidato.solicitud_codigo ?? undefined,
    fechaPostulacion: formatearFecha(candidato.slcd_fecha_postulacion),
    fechaRegistro: formatearFecha(candidato.cand_fecha_creacion),
  };
}

// Mapeo API -> perfil: arma los campos compuestos que la vista no deberia calcular.
export function mapearCandidatoPerfil(candidato: CandidatoPerfilApi): CandidatoPerfil {
  const resumen = mapearCandidatoResumen(candidato);
  const direccion = candidato.direccion;
  const comuna = direccion?.comuna?.nombre ?? direccion?.comuna?.cmn_nombre ?? undefined;
  const calleNumero = [direccion?.drcd_calle, direccion?.drcd_numero].filter(Boolean).join(' ');

  return {
    ...resumen,
    disponibilidad: (
      candidato.disponibilidad?.nombre ??
      candidato.disponibilidad?.disp_nombre ??
      candidato.disponibilidad_nombre ??
      undefined
    ),
    renta: candidato.slcd_pretension_renta ?? undefined,
    rut: formatearRut(candidato.cand_rut_sin_dv, candidato.cand_dv),
    fechaNacimiento: formatearFecha(candidato.cand_fecha_nacimiento),
    tituloProfesional: candidato.cand_titulo ?? undefined,
    resumenProfesional: candidato.cand_resumen_profesional ?? undefined,
    urlPerfil: extraerLinkedinUrl(candidato.cand_url_1),
    comuna,
    direccion: [calleNumero, direccion?.drcd_dpto_oficina ?? direccion?.drcd_depto_oficina]
      .filter(Boolean)
      .join(', '),
  };
}

function obtenerNombreCompleto(candidato: CandidatoResumenApi) {
  return [
    candidato.cand_nombres,
    candidato.cand_apellidos,
    candidato.cand_apellido_paterno,
    candidato.cand_apellido_materno,
  ]
    .filter(Boolean)
    .join(' ') || 'Candidato sin nombre';
}

function formatearRut(rut?: number | null, dv?: number | string | null) {
  if (rut == null || dv == null) {
    return undefined;
  }

  return `${rut}-${dv}`;
}

function formatearFecha(fecha?: string | null) {
  if (!fecha) {
    return undefined;
  }

  const fechaNormalizada = new Date(fecha);
  return Number.isNaN(fechaNormalizada.getTime())
    ? fecha
    : new Intl.DateTimeFormat('es-CL').format(fechaNormalizada);
}

function normalizarNumero(valor?: number | string | null) {
  if (valor == null || valor === '') {
    return undefined;
  }

  const numero = Number(valor);
  return Number.isNaN(numero) ? undefined : numero;
}

export function extraerLinkedinUrl(valor?: string | string[] | null) {
  if (!valor) {
    return undefined;
  }

  const urls = (Array.isArray(valor) ? valor.join(';') : valor)
    .split(/[\s,;|]+/)
    .map((item) => item.trim().replace(/[).,\];]+$/g, ''))
    .filter(Boolean);

  const linkedin = urls.find((item) => /(^https?:\/\/)?(www\.)?linkedin\.com\//i.test(item));

  if (!linkedin) {
    return undefined;
  }

  return /^https?:\/\//i.test(linkedin) ? linkedin : `https://${linkedin}`;
}
