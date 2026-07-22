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

    if (status >= 500) {
      return 'Ocurrió un error en el servidor.';
    }
  }

  return mensajePorDefecto;
}

