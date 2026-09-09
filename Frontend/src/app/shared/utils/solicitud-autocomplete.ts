export interface SolicitudAutocompleteOption {
  id: string | number;
  codigo?: string | null;
  cargo?: string | null;
  nombre?: string | null;
  cliente?: string | null;
  empresaCliente?: string | null;
}

export function etiquetaSolicitud(solicitud: SolicitudAutocompleteOption) {
  return [
    solicitud.codigo?.trim(),
    solicitud.cargo?.trim() || solicitud.nombre?.trim(),
  ].filter(Boolean).join(' · ');
}

export function buscarSolicitudesReales<T extends SolicitudAutocompleteOption>(
  solicitudes: T[],
  valor: string,
  limite = 8,
) {
  const busqueda = valor.trim();

  if (!busqueda) {
    return [];
  }

  return solicitudes
    .filter((solicitud) => coincideSolicitud(solicitud, busqueda))
    .slice(0, limite);
}

export function resolverSolicitudReal<T extends SolicitudAutocompleteOption>(
  solicitudes: T[],
  valor: string,
) {
  const busqueda = valor.trim();

  if (!busqueda) {
    return null;
  }

  return solicitudes.find((solicitud) =>
    codigoSolicitudEquivale(solicitud.codigo, busqueda),
  ) ?? null;
}

export function coincideSolicitud(
  solicitud: SolicitudAutocompleteOption,
  valor: string,
) {
  const busqueda = normalizarTexto(valor);

  if (!busqueda) {
    return true;
  }

  return (
    codigoSolicitudCoincide(solicitud.codigo, valor) ||
    normalizarTexto(etiquetaSolicitud(solicitud)).includes(busqueda) ||
    normalizarTexto(solicitud.cliente ?? '').includes(busqueda) ||
    normalizarTexto(solicitud.empresaCliente ?? '').includes(busqueda)
  );
}

export function codigoSolicitudCoincide(
  codigoReal?: string | null,
  valorBusqueda?: string | null,
) {
  const codigo = normalizarCodigoSolicitudBusqueda(codigoReal);
  const busqueda = normalizarCodigoSolicitudBusqueda(valorBusqueda);

  if (!busqueda) {
    return true;
  }

  if (!codigo) {
    return false;
  }

  if (normalizarTexto(codigo).includes(normalizarTexto(busqueda))) {
    return true;
  }

  const numeroCodigo = obtenerNumeroSolicitud(codigo);
  const numeroBusqueda = obtenerNumeroSolicitud(busqueda);

  return Boolean(
    numeroCodigo &&
    numeroBusqueda &&
    Number(numeroCodigo) === Number(numeroBusqueda),
  );
}

function codigoSolicitudEquivale(
  codigoReal?: string | null,
  valorBusqueda?: string | null,
) {
  const codigo = normalizarCodigoSolicitudBusqueda(codigoReal);
  const busqueda = normalizarCodigoSolicitudBusqueda(valorBusqueda);

  if (!codigo || !busqueda) {
    return false;
  }

  if (codigo === busqueda) {
    return true;
  }

  const numeroCodigo = obtenerNumeroSolicitud(codigo);
  const numeroBusqueda = obtenerNumeroSolicitud(busqueda);

  return Boolean(
    numeroCodigo &&
    numeroBusqueda &&
    Number(numeroCodigo) === Number(numeroBusqueda),
  );
}

export function normalizarCodigoSolicitudBusqueda(valor?: string | null) {
  const limpio = valor?.trim().toUpperCase() ?? '';

  if (!limpio) {
    return '';
  }

  const coincidencia = limpio.match(/^(?:SOL-?)?(\d+)$/);

  return coincidencia
    ? `SOL-${coincidencia[1]}`
    : limpio;
}

export function normalizarTexto(valor: string) {
  return valor
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function obtenerNumeroSolicitud(valor: string) {
  return valor.match(/^SOL-(\d+)$/i)?.[1] ?? '';
}
