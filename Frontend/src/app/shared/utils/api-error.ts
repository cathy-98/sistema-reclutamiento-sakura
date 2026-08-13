export function obtenerMensajeError(error: unknown, mensajePorDefecto: string) {
  if (typeof error === 'object' && error && 'name' in error && error.name === 'TimeoutError') {
    return 'El servidor está tardando demasiado en responder. Intenta nuevamente.';
  }

  if (typeof error === 'object' && error && 'status' in error) {
    const status = Number(error.status);

    if (status === 0) {
      return 'No se pudo conectar con el backend.';
    }

    if (status === 401) {
      return 'Tu sesión no es válida o expiró.';
    }

    if (status === 403) {
      return 'No tienes permisos para realizar esta acción.';
    }

    const detalle = obtenerDetalleBackend(error);

    if (detalle) {
      return detalle;
    }

    if (status >= 500) {
      return 'Ocurrió un error en el servidor.';
    }
  }

  return mensajePorDefecto;
}

function obtenerDetalleBackend(error: unknown) {
  if (typeof error !== 'object' || !error || !('error' in error)) {
    return null;
  }

  const body = error.error;

  if (typeof body === 'string') {
    return body;
  }

  if (typeof body !== 'object' || !body || !('detail' in body)) {
    return null;
  }

  const detail = body.detail;

  if (typeof detail === 'string') {
    return detail;
  }

  if (typeof detail === 'object' && detail && 'message' in detail && typeof detail.message === 'string') {
    return detail.message;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item !== 'object' || !item) {
          return null;
        }

        const loc = 'loc' in item && Array.isArray(item.loc) ? item.loc.join('.') : null;
        const msg = 'msg' in item && typeof item.msg === 'string' ? item.msg : null;

        if (!msg) {
          return null;
        }

        return loc ? `${loc}: ${msg}` : msg;
      })
      .filter(Boolean)
      .join(' · ');
  }

  return null;
}
