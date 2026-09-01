export function obtenerMensajeError(error: unknown, mensajePorDefecto: string) {
  if (typeof error === 'object' && error && 'name' in error && error.name === 'TimeoutError') {
    return 'El servidor está tardando más de lo esperado. Intenta nuevamente.';
  }

  if (typeof error === 'object' && error && 'status' in error) {
    const status = Number(error.status);

    if (status === 0) {
      return 'No pudimos conectar con el servidor. Revisa tu conexión o intenta nuevamente.';
    }

    const detalle = obtenerDetalleBackend(error);

    if (detalle) {
      return humanizarMensajeApi(detalle, status);
    }

    if (status === 400 || status === 422) {
      return 'Revisa los datos ingresados. Hay información incompleta o no válida.';
    }

    if (status === 401) {
      return 'Tu sesión expiró o no es válida. Vuelve a iniciar sesión.';
    }

    if (status === 403) {
      return 'No tienes permisos para realizar esta acción.';
    }

    if (status === 404) {
      return 'No encontramos el registro solicitado. Puede haber sido eliminado o actualizado.';
    }

    if (status === 409) {
      return 'No se pudo completar la acción porque entra en conflicto con información existente.';
    }

    if (status >= 500) {
      return 'Ocurrió un error en el servidor. Intenta nuevamente en unos minutos.';
    }
  }

  return mensajePorDefecto;
}

function obtenerDetalleBackend(error: unknown): string | null {
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
    return detail.trim() || null;
  }

  if (typeof detail === 'object' && detail && 'message' in detail && typeof detail.message === 'string') {
    return detail.message.trim() || null;
  }

  if (Array.isArray(detail)) {
    const mensajes = detail.map(obtenerMensajeValidacion).filter(Boolean);
    return mensajes.length ? mensajes.join(' ') : null;
  }

  return null;
}

function obtenerMensajeValidacion(item: unknown) {
  if (typeof item !== 'object' || !item) {
    return null;
  }

  const loc = 'loc' in item && Array.isArray(item.loc) ? item.loc : [];
  const field = obtenerCampoDesdeLoc(loc);
  const msg = 'msg' in item && typeof item.msg === 'string' ? item.msg : null;

  if (!msg) {
    return null;
  }

  const mensaje = traducirValidacionPydantic(msg);
  return field ? `${traducirCampo(field)}: ${mensaje}` : mensaje;
}

function obtenerCampoDesdeLoc(loc: unknown[]) {
  const partes = loc.filter((parte) => typeof parte === 'string' || typeof parte === 'number');
  const campo = partes[partes.length - 1];
  return campo === undefined ? null : String(campo);
}

function humanizarMensajeApi(detalle: string, status: number) {
  const normalizado = limpiarTexto(detalle);
  const exacto = MENSAJES_EXACTOS[normalizado.toLocaleLowerCase('es-CL')];

  if (exacto) {
    return exacto;
  }

  for (const regla of REGLAS_MENSAJES) {
    const resultado = regla(normalizado, status);

    if (resultado) {
      return resultado;
    }
  }

  return reemplazarCamposTecnicos(normalizado);
}

function limpiarTexto(texto: string) {
  return texto.replace(/\s+/g, ' ').trim();
}

function reemplazarCamposTecnicos(texto: string) {
  let salida = texto;

  for (const [campo, etiqueta] of Object.entries(CAMPOS_API)) {
    salida = salida.replace(new RegExp(`\\b${escaparRegex(campo)}\\b`, 'g'), etiqueta);
  }

  return salida;
}

function traducirCampo(campo: string) {
  return CAMPOS_API[campo] ?? reemplazarCamposTecnicos(campo.replace(/_/g, ' '));
}

function traducirValidacionPydantic(mensaje: string) {
  const normalizado = limpiarTexto(mensaje).toLocaleLowerCase('es-CL');

  if (normalizado.includes('field required')) {
    return 'Campo obligatorio.';
  }

  if (normalizado.includes('input should be a valid email') || normalizado.includes('value is not a valid email')) {
    return 'Ingresa un correo electrónico válido.';
  }

  if (normalizado.includes('string should have at least')) {
    return 'Debe tener más caracteres.';
  }

  if (normalizado.includes('string should have at most')) {
    return 'Debe tener menos caracteres.';
  }

  if (normalizado.includes('input should be greater than')) {
    return 'Debe ser mayor que el mínimo permitido.';
  }

  if (normalizado.includes('input should be a valid integer')) {
    return 'Ingresa un número válido.';
  }

  return reemplazarCamposTecnicos(mensaje);
}

function escaparRegex(valor: string) {
  return valor.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

const CAMPOS_API: Record<string, string> = {
  area_id: 'Área',
  cand_apellido_materno: 'Apellido materno',
  cand_apellido_paterno: 'Apellido paterno',
  cand_disponibilidad_id: 'Disponibilidad',
  cand_dv: 'DV del RUT',
  cand_email: 'Correo del candidato',
  cand_fecha_nacimiento: 'Fecha de nacimiento',
  cand_nombres: 'Nombre del candidato',
  cand_password: 'Contraseña del candidato',
  cand_rut_sin_dv: 'RUT',
  cand_titulo: 'Título profesional',
  candidato_id: 'Candidato',
  candidato_ids: 'Candidatos',
  cargo_id: 'Cargo',
  cdhb_habilidad_id: 'Habilidad',
  cdhb_nivel_habilidad_id: 'Nivel de habilidad',
  cli_email: 'Correo principal del cliente',
  cli_email2: 'Correo secundario del cliente',
  cli_empresa_id: 'Empresa cliente',
  cli_telefono1: 'Teléfono principal del cliente',
  cli_telefono2: 'Teléfono secundario del cliente',
  esusr_id: 'Estado de usuario',
  etcd_fecha_fin: 'Fecha de término del estudio',
  etcd_fecha_inicio: 'Fecha de inicio del estudio',
  expl_fecha_fin: 'Fecha de término de la experiencia',
  expl_fecha_inicio: 'Fecha de inicio de la experiencia',
  habilidades_ids: 'Habilidades',
  id_area: 'Área',
  id_cargo: 'Cargo',
  id_cliente: 'Cliente solicitante',
  id_empresa_cliente: 'Empresa cliente',
  id_modalidad: 'Modalidad',
  id_prioridad: 'Prioridad',
  id_tipo_contrato: 'Tipo de contrato',
  motivo_rechazo_id: 'Motivo de rechazo',
  password_actual: 'Contraseña actual',
  password_nueva: 'Nueva contraseña',
  permiso_ids: 'Permisos',
  rol_id: 'Rol',
  sol_fecha_cierre: 'Fecha de cierre',
  sol_fecha_inicio: 'Fecha de inicio',
  sol_hora_fin_jornada: 'Hora de fin de jornada',
  sol_hora_inicio_jornada: 'Hora de inicio de jornada',
  sol_salario_max: 'Salario máximo',
  sol_salario_min: 'Salario mínimo',
  solhb_habilidad_id: 'Habilidad',
  solhb_nivel_habilidad_id: 'Nivel de habilidad',
  slcd_solicitud_id: 'Solicitud',
  usr_area_id: 'Área',
  usr_contrasena: 'Contraseña',
  usr_dv: 'DV del RUT',
  usr_email: 'Correo del usuario',
  usr_estado_usuario_id: 'Estado del usuario',
  usr_rol_id: 'Rol',
  usr_rut_sin_dv: 'RUT',
};

const MENSAJES_EXACTOS: Record<string, string> = {
  'autenticación requerida': 'Inicia sesión para continuar.',
  'candidato asociado al token no existe': 'No encontramos el perfil de candidato asociado a tu sesión.',
  'candidato inactivo, bloqueado o eliminado': 'La cuenta del candidato está inactiva. Contacta a un administrador.',
  'cli_email y cli_email2 deben ser diferentes': 'Los correos del cliente deben ser diferentes.',
  'cli_telefono1 y cli_telefono2 deben ser diferentes': 'Los teléfonos del cliente deben ser diferentes.',
  'credenciales incorrectas': 'Correo o contraseña incorrectos.',
  'el correo electrónico ya está registrado como candidato': 'Este correo ya está registrado como candidato. Busca el perfil existente antes de crear uno nuevo.',
  'el correo pertenece a un candidato y no puede utilizarse como usuario interno': 'Este correo ya pertenece a un candidato. Usa otro correo para crear el usuario interno.',
  'el correo pertenece a un usuario interno del sistema': 'Este correo ya pertenece a un usuario interno. Usa otro correo para el candidato.',
  'el cuestionario se encuentra vencido': 'Este cuestionario venció y ya no se puede responder.',
  'el cuestionario ya fue finalizado': 'Este cuestionario ya fue finalizado.',
  'el permiso no está asignado al rol': 'Ese permiso no está asignado al rol seleccionado.',
  'el reclutador asignado debe estar activo': 'El reclutador asignado debe tener una cuenta activa.',
  'el usuario asignado debe tener rol reclutador': 'El usuario asignado debe tener rol Reclutador.',
  'este recurso requiere autenticación de candidato': 'Debes iniciar sesión como candidato para acceder a este recurso.',
  'este recurso requiere una cuenta de candidato': 'Esta acción requiere una cuenta de candidato.',
  'este recurso requiere una cuenta de usuario interno': 'Esta acción requiere una cuenta de usuario interno.',
  'formato no soportado. use pdf, docx o txt': 'El archivo debe estar en formato PDF, DOCX o TXT.',
  'habilidades_ids contiene valores duplicados': 'Seleccionaste una habilidad más de una vez.',
  'inhabilitado y descartado requieren motivo_rechazo_id': 'Selecciona un motivo de rechazo para inhabilitar o descartar al candidato.',
  'la comuna indicada no existe': 'La comuna seleccionada ya no está disponible. Actualiza el catálogo e intenta nuevamente.',
  'la contraseña actual no es correcta': 'La contraseña actual no es correcta.',
  'la fecha de cierre de búsqueda no puede ser anterior a la fecha de inicio': 'La fecha de cierre no puede ser anterior a la fecha de inicio.',
  'la fecha de vencimiento debe ser futura': 'La fecha de vencimiento debe ser posterior a la fecha y hora actual.',
  'la habilidad indicada no existe': 'La habilidad seleccionada ya no está disponible. Actualiza el catálogo e intenta nuevamente.',
  'la hora de inicio de jornada debe ser anterior a la hora de fin': 'La hora de inicio debe ser anterior a la hora de término.',
  'la nueva contraseña debe ser distinta de la actual': 'La nueva contraseña debe ser distinta de la actual.',
  'la nueva contraseña debe ser distinta de la contraseña actual': 'La nueva contraseña debe ser distinta de la actual.',
  'la nueva fecha de vencimiento debe ser futura': 'La nueva fecha de vencimiento debe ser posterior a la fecha y hora actual.',
  'la operación viola una restricción de integridad o unicidad': 'No se pudo guardar porque ya existe información relacionada o duplicada.',
  'la opción no pertenece a la pregunta': 'La opción seleccionada no corresponde a esa pregunta.',
  'la pregunta debe tener al menos dos opciones': 'Agrega al menos dos opciones para guardar la pregunta.',
  'la pregunta debe tener exactamente una opción correcta': 'Marca exactamente una opción correcta.',
  'la pregunta no puede estar vacía': 'Escribe el enunciado de la pregunta.',
  'la pregunta no pertenece al cuestionario asignado': 'La pregunta no pertenece a este cuestionario.',
  'la pregunta ya pertenece al cuestionario': 'Esta pregunta ya fue agregada al cuestionario.',
  'la solicitud indicada no existe': 'La solicitud seleccionada ya no está disponible. Actualiza el listado e intenta nuevamente.',
  'la solicitud no posee estado configurado': 'La solicitud no tiene un estado configurado. Contacta a un administrador.',
  'la solicitud no posee habilidades excluyentes; revise la integridad del registro': 'La solicitud no tiene habilidades excluyentes. Agrega una antes de evaluar candidatos.',
  'las preguntas solo están disponibles mientras el cuestionario está en progreso': 'Solo puedes ver las preguntas mientras el cuestionario está en progreso.',
  'motivo_rechazo_id solo corresponde a inhabilitado o descartado': 'El motivo de rechazo solo aplica al inhabilitar o descartar un candidato.',
  'nivel de habilidad no existe': 'El nivel de habilidad seleccionado ya no está disponible. Actualiza el catálogo e intenta nuevamente.',
  'no fue posible identificar nombres y apellido en el cv': 'No pudimos identificar el nombre completo en el CV. Puedes ingresarlo manualmente.',
  'no fue posible identificar un correo electrónico en el cv': 'No encontramos un correo electrónico en el CV. Puedes ingresarlo manualmente o subir un archivo actualizado.',
  'no puede asignar un cuestionario sin preguntas': 'Agrega al menos una pregunta antes de asignar este cuestionario.',
  'no puede cambiar la solicitud de un cuestionario ya asignado': 'No puedes cambiar la solicitud de un cuestionario que ya fue asignado.',
  'no puede darse de baja a sí mismo': 'No puedes desactivar tu propia cuenta.',
  'no puede eliminar el cliente porque posee solicitudes asociadas': 'No puedes eliminar este cliente porque tiene solicitudes asociadas.',
  'no puede eliminar el rol porque está asignado a uno o más usuarios': 'No puedes eliminar este rol porque tiene usuarios asignados.',
  'no puede eliminar la única opción correcta de una pregunta utilizada': 'No puedes eliminar la única opción correcta de una pregunta que ya fue utilizada.',
  'no puede eliminar un cuestionario que posee asignaciones': 'No puedes eliminar este cuestionario porque tiene asignaciones.',
  'no puede finalizar un cuestionario en estado pendiente': 'Primero inicia el cuestionario para poder finalizarlo.',
  'no puede modificar opciones de una pregunta con evaluaciones asignadas': 'No puedes modificar opciones de una pregunta que ya tiene evaluaciones asignadas.',
  'no puede modificar preguntas de un cuestionario que ya fue asignado': 'No puedes modificar las preguntas de un cuestionario que ya fue asignado.',
  'no puede quitar la última habilidad excluyente de la solicitud': 'La solicitud debe mantener al menos una habilidad excluyente.',
  'no puede responder un cuestionario en progreso': 'Solo puedes responder el cuestionario mientras está en progreso.',
  'no se puede eliminar la empresa porque posee clientes asociados': 'No puedes eliminar esta empresa porque tiene clientes asociados.',
  'no se puede eliminar la última habilidad excluyente de la solicitud': 'La solicitud debe mantener al menos una habilidad excluyente.',
  'no se puede repetir una habilidad dentro de la solicitud': 'No repitas habilidades dentro de la misma solicitud.',
  'opción no encontrada': 'No encontramos la opción seleccionada. Actualiza la información e intenta nuevamente.',
  'permisos insuficientes': 'No tienes permisos suficientes para realizar esta acción.',
  'permiso_ids no puede contener ids duplicados': 'Seleccionaste un permiso más de una vez.',
  'pregunta no encontrada': 'No encontramos la pregunta seleccionada. Actualiza la información e intenta nuevamente.',
  'postulación no encontrada': 'No encontramos la postulación solicitada. Puede haber sido eliminada o actualizada.',
  'se requiere rol administrador': 'Necesitas rol Administrador para realizar esta acción.',
  'sol_salario_min no puede ser mayor que sol_salario_max': 'El salario mínimo no puede ser mayor que el salario máximo.',
  'solo puede finalizar un cuestionario en progreso': 'Solo puedes finalizar el cuestionario mientras está en progreso.',
  'solo puede habilitar reintento cuando el estado es error tecnico': 'Solo puedes habilitar un reintento cuando la evaluación está en Error Técnico.',
  'solo puede responder un cuestionario en progreso': 'Solo puedes responder el cuestionario mientras está en progreso.',
  'token inválido o expirado': 'Tu sesión expiró o no es válida. Vuelve a iniciar sesión.',
  'toda solicitud debe incluir al menos una habilidad excluyente': 'Deja al menos una habilidad obligatoria.',
  'toda solicitud debe tener al menos una habilidad excluyente': 'Deja al menos una habilidad obligatoria.',
  'usuario inactivo, bloqueado o eliminado': 'Tu cuenta está inactiva. Contacta a un administrador.',
  'usr_rut_sin_dv y usr_dv deben informarse juntos': 'Ingresa el RUT junto con su DV.',
};

const REGLAS_MENSAJES: Array<(mensaje: string, status: number) => string | null> = [
  (mensaje) => {
    const match = mensaje.match(/^(.+?) con ID \d+ no encontrad[oa]$/i);
    return match ? `No encontramos ${normalizarEntidad(match[1])}. Puede haber sido eliminado o actualizado.` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^(.+?) \d+ no existe$/i);
    return match ? `${capitalizar(normalizarEntidad(match[1]))} seleccionado ya no está disponible. Actualiza el catálogo e intenta nuevamente.` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^No existe el estado de (.+?) '(.+?)'/i);
    return match ? `El estado "${match[2]}" no existe en el catálogo de ${normalizarEntidad(match[1])}.` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^No existe estado de postulación '(.+?)'$/i);
    return match ? `El estado de postulación "${match[1]}" no existe en el catálogo.` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^Permisos inexistentes: (.+)$/i);
    return match ? `Hay permisos que ya no existen en el catálogo: ${match[1]}.` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^Las habilidades (.+) ya están asociadas a la solicitud$/i);
    return match ? `Algunas habilidades seleccionadas ya están asociadas a la solicitud: ${match[1]}.` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^Transición no permitida: (.+?) -> (.+)$/i);
    return match ? `No puedes cambiar el estado de "${match[1]}" a "${match[2]}". Revisa el flujo antes de continuar.` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^Solo se permiten entrevistas y evaluaciones cuando la postulación está en estado 'En entrevista'\. Estado actual de la postulación: '(.+?)'$/i);
    return match ? `Esta entrevista no se puede gestionar porque la postulación está en estado "${match[1]}".` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^Debe informar una observación para pasar a (.+)$/i);
    return match ? `Agrega una observación para cambiar la solicitud a "${match[1]}".` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^No puede cancelar una asignación en estado (.+)$/i);
    return match ? `No puedes cancelar una asignación en estado "${match[1]}".` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^No puede iniciar un cuestionario en estado (.+)$/i);
    return match ? `No puedes iniciar un cuestionario en estado "${match[1]}".` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^Para leer DOCX instale python-docx$/i);
    return match ? 'No se pudo leer el archivo DOCX. Contacta a soporte para revisar la configuración.' : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^La librería 'python-docx' no está instalada/i);
    return match ? 'No se pudo leer el archivo DOCX. Contacta a soporte para revisar la configuración.' : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^No se pudo extraer el texto del archivo (PDF|DOCX)/i);
    return match ? `No pudimos leer el texto del archivo ${match[1].toUpperCase()}. Prueba con un archivo más claro o en otro formato.` : null;
  },
  (mensaje) => {
    const match = mensaje.match(/^No se pudo procesar el CV: No se encontró un correo electrónico válido/i);
    return match ? 'No encontramos un correo electrónico en el CV. Puedes ingresarlo manualmente o subir un archivo actualizado.' : null;
  },
  (mensaje, status) => {
    if (status === 403 && /inactivo|bloqueado|eliminado/i.test(mensaje)) {
      return reemplazarCamposTecnicos(mensaje);
    }

    return null;
  },
];

function normalizarEntidad(entidad: string) {
  const valor = reemplazarCamposTecnicos(entidad).trim().toLocaleLowerCase('es-CL');
  const entidades: Record<string, string> = {
    area: 'el área',
    asignación: 'la asignación',
    candidato: 'el candidato',
    cargo: 'el cargo',
    cliente: 'el cliente',
    comuna: 'la comuna',
    cuestionario: 'el cuestionario',
    empresa: 'la empresa',
    entrevista: 'la entrevista',
    estado: 'el estado',
    habilidad: 'la habilidad',
    institución: 'la institución',
    nivel: 'el nivel',
    permiso: 'el permiso',
    postulación: 'la postulación',
    pregunta: 'la pregunta',
    rol: 'el rol',
    solicitud: 'la solicitud',
    usuario: 'el usuario',
  };

  return entidades[valor] ?? `el registro "${entidad.trim()}"`;
}

function capitalizar(texto: string) {
  return texto.charAt(0).toLocaleUpperCase('es-CL') + texto.slice(1);
}
