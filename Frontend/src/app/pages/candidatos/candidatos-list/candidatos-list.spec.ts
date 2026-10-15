import { of, Subject, throwError } from 'rxjs';
import { CurrencyClPipe } from '../../../shared/pipes/currency-cl.pipe';
import { CandidatosList } from './candidatos-list';

function crearComponente(
  informesOverrides: Record<string, unknown> = {},
  candidatosOverrides: Record<string, unknown> = {},
) {
  const informesService = {
    enviarCorreosCandidatos: () => of([]),
    listarPlantillas: () => of([]),
    ...informesOverrides,
  };
  const candidatosService = {
    descargarCvOriginal: () => of({ body: new Blob(['cv']), headers: { get: () => 'attachment; filename="cv.pdf"' } }),
    ...candidatosOverrides,
  };
  return new CandidatosList(
    new CurrencyClPipe(),
    candidatosService as never,
    { queryParamMap: of(new Map()) } as never,
    {} as never,
    {} as never,
    {} as never,
    {} as never,
    informesService as never,
    { detectChanges: () => undefined } as never,
  ) as unknown as CandidatosList & {
    estadoCargaCvArchivo: (carga: unknown, solicitud: unknown | null) => {
      estado: string;
      etiqueta?: string;
      mensaje: string;
      detalles?: Array<{ title: string; messages: string[] }>;
    };
    estadoCargaCvError: (carga: unknown) => {
      estado: string;
      etiqueta?: string;
      mensaje: string;
    };
  };
}

function plantilla(tipo: string, nombre = tipo, asunto = `Asunto ${tipo}`, cuerpo = `Hola {nombre} ${tipo}`) {
  return {
    plantilla_id: Math.floor(Math.random() * 1000),
    tipo,
    nombre,
    asunto,
    cuerpo,
    activa: true,
  };
}

function cargaProcesada(advertencias: string[] = []) {
  return {
    clave: 'cv.pdf-1-1',
    archivo: 'cv.pdf',
    resultado: {
      candidato: { cand_id: 1 },
      creado: true,
      actualizado: false,
      advertencias,
    },
    asociacion: null,
    error: '',
    errorAsociacion: '',
    sinConfirmacion: false,
  };
}

function configurarCorreoContextual(componente: any, cantidad = 1) {
  componente.mostrarModalCorreo = true;
  componente.solicitudContexto = { id: '1', codigo: 'SOL-1', cargo: 'Backend', estado: 'En Curso' };
  componente.seleccionados = new Set(Array.from({ length: cantidad }, (_, index) => String(index + 1)));
  componente.candidatos = Array.from({ length: cantidad }, (_, index) => ({
    idCandidato: String(index + 1),
    nombre: `Candidato ${index + 1}`,
    correo: `candidato${index + 1}@example.com`,
    postulaciones: [{
      idPostulacion: 10 + index,
      idSolicitud: 1,
      codigoSolicitud: 'SOL-1',
      cargo: 'Backend',
      estado: 'En revision',
    }],
  }));
  componente.asuntoCorreo = 'Hola';
  componente.cuerpoCorreo = 'Mensaje';
}

function candidatoCorreo(
  id: string,
  postulaciones: Array<{ idPostulacion: number; idSolicitud: number; codigoSolicitud: string; cargo: string }>,
) {
  return {
    idCandidato: id,
    nombre: `Candidato ${id}`,
    correo: `candidato${id}@example.com`,
    telefono: '',
    cargo: postulaciones[0]?.cargo ?? 'Sin postulación',
    match: 0,
    matchDisponible: false,
    renta: null,
    fechaPostulacion: '',
    estado: postulaciones.length > 0 ? 'En revision' : 'Sin postulación',
    estadoUsuario: 'Activo',
    disponibilidad: '',
    nivel: 'Sin información',
    experiencia: null,
    habilidades: [],
    postulaciones: postulaciones.map((postulacion) => ({
      ...postulacion,
      estado: 'En revision',
      match: 0,
      matchDisponible: false,
      renta: null,
      fechaPostulacion: '',
      fechaPostulacionRaw: null,
    })),
  };
}

function configurarCambioEstadoMasivo(
  componente: any,
  cambiarEstadoPostulacion: jasmine.Spy,
) {
  const postulaciones = [
    { idPostulacion: 101, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend', estado: 'En revision' },
    { idPostulacion: 102, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend', estado: 'En revision' },
  ];
  const candidatos = [
    { idCandidato: '1', nombre: 'Candidato Uno', postulaciones: [postulaciones[0]] },
    { idCandidato: '2', nombre: 'Candidato Dos', postulaciones: [postulaciones[1]] },
  ];

  componente.candidatos = candidatos;
  componente.seleccionados = new Set(['1', '2']);
  componente.solicitudContexto = { id: '1', codigo: 'SOL-1', cargo: 'Backend', estado: 'En Curso' };
  componente.estadoMasivoSeleccionado = 'En entrevista';
  componente.estados = ['En revisión', 'En entrevista'];
  componente.estadosPostulacionPorNombre = new Map([['en entrevista', 2]]);
  componente.candidatosService = { cambiarEstadoPostulacion };
  componente.cargarCandidatos = jasmine.createSpy('cargarCandidatos');
  componente.cerrarModalEstadoMasivo = jasmine.createSpy('cerrarModalEstadoMasivo');
  Object.defineProperty(componente, 'candidatosSeleccionados', {
    configurable: true,
    get: () => candidatos,
  });
  Object.defineProperty(componente, 'postulacionesSeleccionadasContexto', {
    configurable: true,
    get: () => postulaciones,
  });
  Object.defineProperty(componente, 'enContextoSolicitud', {
    configurable: true,
    value: true,
  });
  Object.defineProperty(componente, 'seleccionEstadosMixtos', {
    configurable: true,
    value: false,
  });
}

describe('CandidatosList cambio masivo de estado', () => {
  it('cierra el modal y limpia la selección cuando todas las actualizaciones tienen éxito', () => {
    const cambiarEstadoPostulacion = jasmine.createSpy('cambiarEstadoPostulacion').and.returnValue(of({}));
    const componente = crearComponente({}, { cambiarEstadoPostulacion }) as any;
    configurarCambioEstadoMasivo(componente, cambiarEstadoPostulacion);

    componente.actualizarEstadoMasivo();

    expect(cambiarEstadoPostulacion).toHaveBeenCalledTimes(2);
    expect(componente.seleccionados.size).toBe(0);
    expect(componente.cerrarModalEstadoMasivo).toHaveBeenCalled();
    expect(componente.alerta.mensaje).toBe('2 candidatos actualizados correctamente.');
  });

  it('conserva seleccionados los candidatos fallidos y mantiene abierto el modal en un éxito parcial', () => {
    const cambiarEstadoPostulacion = jasmine.createSpy('cambiarEstadoPostulacion').and.callFake((id: number) =>
      id === 101
        ? of({})
        : throwError(() => new Error('Estado bloqueado')),
    );
    const componente = crearComponente({}, { cambiarEstadoPostulacion }) as any;
    configurarCambioEstadoMasivo(componente, cambiarEstadoPostulacion);

    componente.actualizarEstadoMasivo();

    expect(componente.seleccionados).toEqual(new Set(['2']));
    expect(componente.cerrarModalEstadoMasivo).not.toHaveBeenCalled();
    expect(componente.errorEstadoMasivo).toContain('Candidato Dos');
    expect(componente.alerta.mensaje).toContain('completó parcialmente');
    expect(componente.cargarCandidatos).toHaveBeenCalled();
  });

  it('conserva todos los candidatos seleccionados y muestra error total cuando todas fallan', () => {
    const cambiarEstadoPostulacion = jasmine.createSpy('cambiarEstadoPostulacion').and.returnValue(
      throwError(() => new Error('Estado bloqueado')),
    );
    const componente = crearComponente({}, { cambiarEstadoPostulacion }) as any;
    configurarCambioEstadoMasivo(componente, cambiarEstadoPostulacion);

    componente.actualizarEstadoMasivo();

    expect(componente.seleccionados).toEqual(new Set(['1', '2']));
    expect(componente.cerrarModalEstadoMasivo).not.toHaveBeenCalled();
    expect(componente.errorEstadoMasivo).toContain('Candidato Uno');
    expect(componente.errorEstadoMasivo).toContain('Candidato Dos');
    expect(componente.alerta.mensaje).toBe('No se pudo actualizar ningún candidato seleccionado.');
  });
});

describe('CandidatosList feedback de carga CV', () => {
  it('muestra procesamiento exitoso sin observaciones', () => {
    const estado = crearComponente().estadoCargaCvArchivo(cargaProcesada([]), null);

    expect(estado.estado).toBe('procesado');
    expect(estado.etiqueta).toBe('CV procesado correctamente');
    expect(estado.detalles).toEqual([]);
  });

  it('agrupa warnings de mapeo conservando el mensaje original', () => {
    const warning = 'No se detectaron habilidades persistibles: no hubo un valor válido, inequívoco y asociado a un contexto confiable.';
    const estado = crearComponente().estadoCargaCvArchivo(cargaProcesada([warning]), null);

    expect(estado.estado).toBe('observado');
    expect(estado.etiqueta).toBe('CV procesado con observaciones');
    expect(estado.detalles).toContainEqual({
      title: 'Mapeo de información',
      messages: [warning],
    });
  });

  it('agrupa nombre inferido como revision manual', () => {
    const warning = 'Nombre inferido desde la parte local del correo; revisar manualmente.';
    const estado = crearComponente().estadoCargaCvArchivo(cargaProcesada([warning]), null);

    expect(estado.detalles).toContainEqual({
      title: 'Revisión manual',
      messages: [warning],
    });
  });

  it('agrupa fallo de asociacion a solicitud sin tratarlo como error de CV', () => {
    const carga = {
      ...cargaProcesada([]),
      errorAsociacion: 'El CV fue procesado, pero no se pudo asociar el candidato a la solicitud.',
    };
    const estado = crearComponente().estadoCargaCvArchivo(carga, { codigo: 'SOL-1' });

    expect(estado.estado).toBe('observado');
    expect(estado.detalles).toContainEqual({
      title: 'Asociación a solicitud',
      messages: ['El CV fue procesado, pero no se pudo asociar el candidato a la solicitud.'],
    });
  });

  it('agrupa advertencias de requisitos excluyentes', () => {
    const carga = {
      ...cargaProcesada([]),
      asociacion: {
        evaluacion: {
          advertencia: 'El candidato fue asociado, pero no cumple todos los requisitos excluyentes.',
          habilidades_faltantes: [{ habilidad: 'Angular', motivo: 'Nivel insuficiente' }],
        },
      },
    };
    const estado = crearComponente().estadoCargaCvArchivo(carga, { codigo: 'SOL-1' });

    expect(estado.detalles).toContainEqual({
      title: 'Requisitos',
      messages: [
        'El candidato fue asociado, pero no cumple todos los requisitos excluyentes.',
        'Angular: Nivel insuficiente',
      ],
    });
  });

  it('mantiene warnings desconocidos en fallback neutral', () => {
    const warning = 'Advertencia futura del Backend sin categoría conocida.';
    const estado = crearComponente().estadoCargaCvArchivo(cargaProcesada([warning]), null);

    expect(estado.detalles).toContainEqual({
      title: 'Observaciones generales',
      messages: [warning],
    });
  });

  it('separa error bloqueante de procesamiento con observaciones', () => {
    const estado = crearComponente().estadoCargaCvError({
      error: 'No fue posible identificar un correo electrónico en el CV',
      sinConfirmacion: false,
    });

    expect(estado.estado).toBe('error');
    expect(estado.etiqueta).toBe('No se pudo procesar el CV');
    expect(estado.mensaje).toBe('No fue posible identificar un correo electrónico en el CV');
  });

  it('mantiene resultados independientes en carga multiple', () => {
    const componente = crearComponente();
    const correcto = componente.estadoCargaCvArchivo(cargaProcesada([]), null);
    const observado = componente.estadoCargaCvArchivo(
      cargaProcesada(['No se detectaron estudios persistibles: no hubo institución o carrera válida, inequívoca y asociada a contexto académico.']),
      null,
    );
    const error = componente.estadoCargaCvError({
      error: 'No se pudo procesar el CV. Intenta nuevamente.',
      sinConfirmacion: false,
    });

    expect(correcto.estado).toBe('procesado');
    expect(observado.estado).toBe('observado');
    expect(error.estado).toBe('error');
  });
});

describe('CandidatosList correo masivo', () => {
  it('con 0 seleccionados no abre modal ni aviso', () => {
    const componente = crearComponente() as any;
    componente.seleccionados = new Set();

    componente.abrirModalCorreo();

    expect(componente.mostrarModalCorreo).toBeFalse();
    expect(componente.mostrarAvisoSolicitudCorreo).toBeFalse();
  });

  it('permite abrir redacción con 1 candidato en contexto de solicitud', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente, 1);
    componente.mostrarModalCorreo = false;

    componente.abrirModalCorreo();

    expect(componente.mostrarModalCorreo).toBeTrue();
    expect(componente.contextoModalCorreo).toBe('1 candidato seleccionado · SOL-1 · Backend');
    expect(componente.postulacionesSeleccionadasCorreo.map((p: any) => p.idPostulacion)).toEqual([10]);
  });

  it('desde solicitud contextual abre redacción directamente sin pedir solicitud', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente, 2);
    componente.mostrarModalCorreo = false;

    componente.abrirModalCorreo();

    expect(componente.mostrarAvisoSolicitudCorreo).toBeFalse();
    expect(componente.mostrarModalCorreo).toBeTrue();
    expect(componente.contextoModalCorreo).toBe('2 candidatos seleccionados · SOL-1 · Backend');
  });

  it('desde gestión general con 1 candidato y 1 postulación abre redacción directamente', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.seleccionados = new Set(['1']);
    componente.candidatos = [candidatoCorreo('1', [{ idPostulacion: 10, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' }])];

    componente.abrirModalCorreo();

    expect(componente.mostrarAvisoSolicitudCorreo).toBeFalse();
    expect(componente.mostrarModalCorreo).toBeTrue();
    expect(componente.contextoModalCorreo).toBe('1 candidato seleccionado · SOL-1 · Backend');
    expect(componente.postulacionesSeleccionadasCorreo.map((p: any) => p.idPostulacion)).toEqual([10]);
  });

  it('desde gestión general con 1 candidato y 2 postulaciones solicita elegir proceso existente', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.seleccionados = new Set(['1']);
    componente.candidatos = [
      candidatoCorreo('1', [
        { idPostulacion: 10, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' },
        { idPostulacion: 20, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX' },
      ]),
    ];

    componente.abrirModalCorreo();

    expect(componente.mostrarAvisoSolicitudCorreo).toBeTrue();
    expect(componente.mostrarModalCorreo).toBeFalse();
    expect(componente.opcionesSolicitudCorreo.map((opcion: any) => opcion.codigo)).toEqual(['SOL-1', 'SOL-2']);
  });

  it('seleccionar proceso existente resuelve contexto sin crear asociación', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.seleccionados = new Set(['1']);
    componente.candidatos = [
      candidatoCorreo('1', [
        { idPostulacion: 10, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' },
        { idPostulacion: 20, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX' },
      ]),
    ];

    componente.abrirModalCorreo();
    componente.seleccionarSolicitudCorreo(componente.opcionesSolicitudCorreo[1]);

    expect(componente.mostrarAvisoSolicitudCorreo).toBeFalse();
    expect(componente.mostrarModalCorreo).toBeTrue();
    expect(componente.postulacionesSeleccionadasCorreo.map((p: any) => p.idPostulacion)).toEqual([20]);
  });

  it('1 candidato sin postulación no abre correo ni muestra solicitudes arbitrarias', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.seleccionados = new Set(['1']);
    componente.candidatos = [candidatoCorreo('1', [])];

    componente.abrirModalCorreo();

    expect(componente.mostrarAvisoSolicitudCorreo).toBeFalse();
    expect(componente.mostrarModalCorreo).toBeFalse();
    expect(componente.opcionesSolicitudCorreo).toEqual([]);
    expect(componente.alerta.mensaje).toContain('no tiene una postulación asociada');
  });

  it('el aviso lleva al filtro de solicitud sin asociar candidatos', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.seleccionados = new Set(['1', '2']);
    componente.mostrarAvisoSolicitudCorreo = true;

    componente.irAFiltroSolicitudCorreo();

    expect(componente.mostrarAvisoSolicitudCorreo).toBeFalse();
    expect(Array.from(componente.seleccionados)).toEqual([]);
    expect(componente.alerta.mensaje).toContain('Selecciona una solicitud en los filtros');
  });

  it('filtrar por solicitud muestra solo candidatos ya asociados a ese proceso', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.solicitudesCargaDisponibles = [
      { id: '1', codigo: 'SOL-1', cargo: 'Backend', estado: 'En Curso', prioridad: 'Alta', vacantes: 1 },
    ];
    componente.filtros.idSolicitud = 'SOL-1';
    componente.busquedaEjecutada = true;
    componente.candidatos = [
      candidatoCorreo('1', [{ idPostulacion: 10, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' }]),
      candidatoCorreo('2', [{ idPostulacion: 20, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX' }]),
      candidatoCorreo('3', []),
    ];

    expect(componente.candidatosFiltrados.map((c: any) => c.idCandidato)).toEqual(['1']);
  });

  it('con filtro de solicitud abre modal final y resuelve slcd_id de ese contexto', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.solicitudesCargaDisponibles = [
      { id: '2', codigo: 'SOL-2', cargo: 'UX', estado: 'En Curso', prioridad: 'Media', vacantes: 1 },
    ];
    componente.filtros.idSolicitud = 'SOL-2';
    componente.seleccionados = new Set(['1']);
    componente.candidatos = [
      candidatoCorreo('1', [
        { idPostulacion: 10, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' },
        { idPostulacion: 20, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX' },
      ]),
    ];

    componente.abrirModalCorreo();

    expect(componente.mostrarModalCorreo).toBeTrue();
    expect(componente.contextoModalCorreo).toBe('1 candidato seleccionado · SOL-2 · UX');
    expect(componente.postulacionesSeleccionadasCorreo.map((p: any) => p.idPostulacion)).toEqual([20]);
  });

  it('con filtro de solicitud permite 1 seleccionado y habilita envío con asunto y cuerpo', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.solicitudesCargaDisponibles = [
      { id: '2', codigo: 'SOL-2', cargo: 'UX', estado: 'En Curso', prioridad: 'Media', vacantes: 1 },
    ];
    componente.filtros.idSolicitud = 'SOL-2';
    componente.seleccionados = new Set(['1']);
    componente.candidatos = [
      candidatoCorreo('1', [{ idPostulacion: 20, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX' }]),
    ];

    componente.abrirModalCorreo();
    componente.asuntoCorreo = 'Hola';
    componente.cuerpoCorreo = 'Mensaje';

    expect(componente.puedeEnviarCorreoMasivo).toBeTrue();
  });

  it('con 1 seleccionado sin contexto global usa su postulación única', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.seleccionados = new Set(['1']);
    componente.candidatos = [
      candidatoCorreo('1', [{ idPostulacion: 20, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX' }]),
    ];

    componente.abrirModalCorreo();

    expect(componente.mostrarAvisoSolicitudCorreo).toBeFalse();
    expect(componente.mostrarModalCorreo).toBeTrue();
    expect(componente.postulacionesSeleccionadasCorreo.map((p: any) => p.idPostulacion)).toEqual([20]);
  });

  it('N candidatos sin contexto y única solicitud común resuelve contexto común', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.seleccionados = new Set(['1', '2']);
    componente.candidatos = [
      candidatoCorreo('1', [{ idPostulacion: 10, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' }]),
      candidatoCorreo('2', [{ idPostulacion: 11, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' }]),
    ];

    componente.abrirModalCorreo();

    expect(componente.mostrarAvisoSolicitudCorreo).toBeFalse();
    expect(componente.mostrarModalCorreo).toBeTrue();
    expect(componente.postulacionesSeleccionadasCorreo.map((p: any) => p.idPostulacion)).toEqual([10, 11]);
  });

  it('N candidatos sin contexto y múltiples solicitudes comunes solicita contexto', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.seleccionados = new Set(['1', '2']);
    componente.candidatos = [
      candidatoCorreo('1', [
        { idPostulacion: 10, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' },
        { idPostulacion: 20, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX' },
      ]),
      candidatoCorreo('2', [
        { idPostulacion: 11, idSolicitud: 1, codigoSolicitud: 'SOL-1', cargo: 'Backend' },
        { idPostulacion: 21, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX' },
      ]),
    ];

    componente.abrirModalCorreo();

    expect(componente.mostrarAvisoSolicitudCorreo).toBeTrue();
    expect(componente.mostrarModalCorreo).toBeFalse();
    expect(componente.opcionesSolicitudCorreo.map((opcion: any) => opcion.codigo)).toEqual(['SOL-1', 'SOL-2']);
  });

  it('cambiar solicitud limpia selección anterior', () => {
    const componente = crearComponente() as any;
    componente.solicitudContexto = null;
    componente.solicitudesCargaDisponibles = [
      { id: '1', codigo: 'SOL-1', cargo: 'Backend', estado: 'En Curso', prioridad: 'Alta', vacantes: 1 },
      { id: '2', codigo: 'SOL-2', cargo: 'UX', estado: 'En Curso', prioridad: 'Media', vacantes: 1 },
    ];
    componente.filtros.idSolicitud = 'SOL-1';
    componente.seleccionados = new Set(['1']);

    componente.seleccionarFiltroSolicitud(componente.solicitudesCargaDisponibles[1]);

    expect(Array.from(componente.seleccionados)).toEqual([]);
    expect(componente.alerta.mensaje).toBe('Al cambiar de solicitud se limpió la selección actual.');
  });

  it('habilita envío solo con postulación contextual, asunto y mensaje', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente);

    expect(componente.puedeEnviarCorreoMasivo).toBeTrue();
  });

  it('envío con 1 usa exactamente su solicitud_candidato_id', () => {
    const enviarCorreosCandidatos = jasmine.createSpy('enviarCorreosCandidatos').and.returnValue(of([
      { solicitud_candidato_id: 10, tipo: 'CONTACTO', destinatario: 'uno@example.com', estado: 'ENVIADO' },
    ]));
    const componente = crearComponente({ enviarCorreosCandidatos }) as any;
    configurarCorreoContextual(componente, 1);

    componente.enviarCorreoCandidatos();

    expect(enviarCorreosCandidatos).toHaveBeenCalledWith(jasmine.objectContaining({
      solicitudCandidatoIds: [10],
    }));
  });

  it('envío con varios usa los solicitud_candidato_id correspondientes', () => {
    const enviarCorreosCandidatos = jasmine.createSpy('enviarCorreosCandidatos').and.returnValue(of([
      { solicitud_candidato_id: 10, tipo: 'CONTACTO', destinatario: 'uno@example.com', estado: 'ENVIADO' },
      { solicitud_candidato_id: 11, tipo: 'CONTACTO', destinatario: 'dos@example.com', estado: 'ENVIADO' },
    ]));
    const componente = crearComponente({ enviarCorreosCandidatos }) as any;
    configurarCorreoContextual(componente, 2);

    componente.enviarCorreoCandidatos();

    expect(enviarCorreosCandidatos).toHaveBeenCalledWith(jasmine.objectContaining({
      solicitudCandidatoIds: [10, 11],
    }));
  });

  it('muestra cantidad, solicitud y cargo en el contexto del modal', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente, 2);

    expect(componente.contextoModalCorreo).toBe('2 candidatos seleccionados · SOL-1 · Backend');
  });

  it('mantiene destinatarios como datos separados y escaneables', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente, 3);

    expect(componente.destinatariosCorreoDetalle.length).toBe(3);
    expect(componente.destinatariosCorreoDetalle[0]).toEqual(jasmine.objectContaining({
      nombre: 'Candidato 1',
      correo: 'candidato1@example.com',
      noEnviable: false,
    }));
  });

  it('soporta muchos destinatarios sin cambiar la colección visible', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente, 12);

    expect(componente.destinatariosCorreoDetalle.length).toBe(12);
  });

  it('consulta plantillas desde Backend al abrir el modal final', () => {
    const listarPlantillas = jasmine.createSpy('listarPlantillas').and.returnValue(of([
      plantilla('CONTACTO', 'Contacto inicial', 'Asunto contacto', 'Hola {nombre}'),
    ]));
    const componente = crearComponente({ listarPlantillas }) as any;
    configurarCorreoContextual(componente);
    componente.mostrarModalCorreo = false;

    componente.abrirModalCorreo();

    expect(listarPlantillas).toHaveBeenCalled();
    expect(componente.plantillasCorreoDisponibles.map((p: any) => p.tipo)).toEqual(['CONTACTO']);
  });

  it('muestra solo plantillas compatibles para candidatos', () => {
    const componente = crearComponente() as any;

    const resultado = componente.filtrarPlantillasCorreoCandidatos([
      plantilla('CONTACTO', 'Contacto inicial'),
      plantilla('AVANCE', 'Avance del proceso'),
      plantilla('SELECCION', 'Selección'),
      plantilla('DIRECTIVOS', 'Directivos'),
      plantilla('RECHAZO', 'Rechazo'),
      plantilla('AGRADECIMIENTO', 'Agradecimiento'),
    ]);

    expect(resultado.disponibles.map((p: any) => p.tipo)).toEqual(['CONTACTO', 'AVANCE', 'SELECCION']);
    expect(resultado.excluidas.map((p: any) => p.tipo)).toContain('DIRECTIVOS');
    expect(resultado.excluidas.map((p: any) => p.tipo)).toContain('RECHAZO');
    expect(resultado.excluidas.map((p: any) => p.tipo)).toContain('AGRADECIMIENTO');
  });

  it('no ofrece plantillas con variables sin contexto del modal general', () => {
    const componente = crearComponente() as any;

    const resultado = componente.filtrarPlantillasCorreoCandidatos([
      plantilla('INVITACION', 'Invitación', 'Invitación', 'Fecha: {{params.fecha}} Hora: {{params.hora}}'),
    ]);

    expect(resultado.disponibles).toEqual([]);
    expect(resultado.excluidas[0].motivo).toContain('{{params.fecha}}');
    expect(resultado.excluidas[0].motivo).toContain('{{params.hora}}');
  });

  it('no muestra explicación técnica por plantillas excluidas internamente', () => {
    const componente = crearComponente() as any;
    componente.plantillasCorreoExcluidas = [
      { tipo: 'INVITACION', nombre: 'INVITACIONENTREVISTA', motivo: 'variables sin contexto: {{params.fecha}}' },
    ];

    expect(componente.avisoPlantillasCorreo).toBe('');
  });

  it('seleccionar plantilla carga asunto y cuerpo editables', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente);
    componente.plantillasCorreo = [
      plantilla('CONTACTO', 'Contacto inicial', 'Asunto desde BD', 'Cuerpo desde BD {nombre}'),
    ];
    componente.aplicarPlantillaCorreo();

    expect(componente.asuntoCorreo).toBe('Asunto desde BD');
    expect(componente.cuerpoCorreo).toBe('Cuerpo desde BD {nombre}');
    componente.asuntoCorreo = 'Asunto editado';
    componente.cuerpoCorreo = 'Cuerpo editado';
    expect(componente.asuntoCorreo).toBe('Asunto editado');
    expect(componente.cuerpoCorreo).toBe('Cuerpo editado');
  });

  it('mantiene Manual disponible si falla carga de plantillas', () => {
    const componente = crearComponente({
      listarPlantillas: () => throwError(() => new Error('fallo')),
    }) as any;
    configurarCorreoContextual(componente);
    componente.mostrarModalCorreo = false;

    componente.abrirModalCorreo();

    expect(componente.plantillaCorreo).toBe('manual');
    expect(componente.errorPlantillasCorreo).toBe('No se pudieron cargar las plantillas. Puedes continuar con Manual.');
  });

  it('usa sintaxis de variables compatible con el renderer Backend', () => {
    const componente = crearComponente() as any;
    const resultado = componente.filtrarPlantillasCorreoCandidatos([
      plantilla('CONTACTO', 'Contacto inicial', 'Proceso {codigo_solicitud}', 'Hola {{params.nombre}} para {cargo}'),
    ]);

    expect(resultado.disponibles.length).toBe(1);
    componente.plantillaCorreo = 'CONTACTO';
    componente.plantillasCorreo = resultado.disponibles;
    componente.aplicarPlantillaCorreo();

    expect(componente.cuerpoCorreo).toContain('{{params.nombre}}');
    expect(componente.asuntoCorreo).toContain('{codigo_solicitud}');
    expect(componente.cuerpoCorreo).toContain('{cargo}');
    expect(componente.cuerpoCorreo).not.toContain('{{Solicitud}}');
    expect(componente.cuerpoCorreo).not.toContain('{{Cargo}}');
  });

  it('seleccionar plantilla no cambia estado de postulación', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente);
    const estadoOriginal = componente.candidatos[0].postulaciones[0].estado;
    componente.plantillasCorreo = [
      plantilla('SELECCION', 'Selección', 'Seleccionado', 'Has sido seleccionado {nombre}'),
    ];
    componente.plantillaCorreo = 'SELECCION';

    componente.aplicarPlantillaCorreo();

    expect(componente.candidatos[0].postulaciones[0].estado).toBe(estadoOriginal);
  });

  it('explica cuando falta asunto', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente);
    componente.asuntoCorreo = '';

    expect(componente.puedeEnviarCorreoMasivo).toBeFalse();
    expect(componente.motivoEnvioCorreoDeshabilitado).toBe('Ingresa un asunto para continuar.');
  });

  it('explica cuando falta mensaje', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente);
    componente.cuerpoCorreo = '';

    expect(componente.puedeEnviarCorreoMasivo).toBeFalse();
    expect(componente.motivoEnvioCorreoDeshabilitado).toBe('Ingresa un mensaje para continuar.');
  });

  it('bloquea doble envío durante loading', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente);
    componente.enviandoCorreo = true;

    expect(componente.puedeEnviarCorreoMasivo).toBeFalse();
  });

  it('bloquea envío si no hay postulación contextual inequívoca', () => {
    const componente = crearComponente() as any;
    componente.mostrarModalCorreo = true;
    componente.solicitudContexto = { id: '1', codigo: 'SOL-1', cargo: 'Backend', estado: 'En Curso' };
    componente.seleccionados = new Set(['1']);
    componente.candidatos = [{
      idCandidato: '1',
      nombre: 'Catherine',
      correo: 'cathy@example.com',
      postulaciones: [{ idPostulacion: 20, idSolicitud: 2, codigoSolicitud: 'SOL-2', cargo: 'UX', estado: 'En revision' }],
    }];
    componente.asuntoCorreo = 'Hola';
    componente.cuerpoCorreo = 'Mensaje';

    expect(componente.puedeEnviarCorreoMasivo).toBeFalse();
    expect(componente.candidatosCorreoSinPostulacionContextual.length).toBe(1);
    expect(componente.motivoEnvioCorreoDeshabilitado).toBe('Uno o más candidatos no tienen una postulación válida en esta solicitud.');
  });

  it('clasifica éxito total', () => {
    const componente = crearComponente() as any;
    componente.resultadosCorreo = [
      { solicitud_candidato_id: 10, tipo: 'CONTACTO', destinatario: 'ok@example.com', estado: 'ENVIADO' },
    ];

    expect(componente.resumenResultadosCorreo).toBe('1 de 1 correos enviados.');
    expect(componente.estadoResultadosCorreo).toBe('success');
  });

  it('mantiene modal abierto y muestra resultado parcial', () => {
    const componente = crearComponente() as any;
    componente.mostrarModalCorreo = true;
    componente.resultadosCorreo = [
      { solicitud_candidato_id: 10, tipo: 'CONTACTO', destinatario: 'ok@example.com', estado: 'ENVIADO' },
      { solicitud_candidato_id: 11, tipo: 'CONTACTO', destinatario: 'err@example.com', estado: 'ERROR', error: 'SMTP' },
    ];

    expect(componente.resumenResultadosCorreo).toBe('1 de 2 correos enviados.');
    expect(componente.estadoResultadosCorreo).toBe('partial');
    expect(componente.mostrarModalCorreo).toBeTrue();
  });

  it('muestra motivo amigable para error individual', () => {
    const componente = crearComponente() as any;
    const mensaje = componente.mensajeResultadoCorreo({
      solicitud_candidato_id: 11,
      tipo: 'CONTACTO',
      destinatario: 'err@example.com',
      estado: 'ERROR',
      error: 'SMTP',
    });

    expect(mensaje).toBe('No enviado: el servicio de correo no pudo completar el envío.');
  });

  it('impide reenvío accidental cuando ya hay resultados', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente);
    componente.resultadosCorreo = [
      { solicitud_candidato_id: 10, tipo: 'CONTACTO', destinatario: 'ok@example.com', estado: 'ENVIADO' },
    ];

    expect(componente.puedeEnviarCorreoMasivo).toBeFalse();
  });

  it('no muestra solicitud pendiente por destinatario en el modal final', () => {
    const componente = crearComponente() as any;
    configurarCorreoContextual(componente);

    expect(componente.destinatariosCorreoDetalle[0].motivo).not.toContain('Selecciona una solicitud');
  });
});

describe('CandidatosList descarga de CV original', () => {
  it('expone la acción con la etiqueta correcta solo cuando hay CV registrado', () => {
    const componente = crearComponente() as any;
    const accion = componente.acciones.find((item: any) => item.id === 'descargar-cv');
    const conCv = { idCandidato: '7', cvUrls: 'storage/cv/7.pdf' };
    const sinCv = { idCandidato: '8', cvUrls: null };

    expect(accion.label).toBe('Descargar CV original');
    expect(accion.visible(conCv)).toBeTrue();
    expect(accion.visible(sinCv)).toBeFalse();
  });

  it('conecta descargar-cv con el servicio usando el candidato seleccionado', () => {
    const descargarCvOriginal = jasmine.createSpy('descargarCvOriginal').and.returnValue(
      of({ body: new Blob(['cv']), headers: { get: () => 'attachment; filename="cv.pdf"' } }),
    );
    const componente = crearComponente({}, { descargarCvOriginal }) as any;

    componente.manejarAccionTabla({ action: 'descargar-cv', row: { idCandidato: '42' } });

    expect(descargarCvOriginal).toHaveBeenCalledWith('42');
    expect(componente.descargandoCvOriginal.size).toBe(0);
  });

  it('evita solicitudes duplicadas mientras la descarga sigue pendiente', () => {
    const descarga = new Subject<any>();
    const descargarCvOriginal = jasmine.createSpy('descargarCvOriginal').and.returnValue(descarga);
    const componente = crearComponente({}, { descargarCvOriginal }) as any;
    const evento = { action: 'descargar-cv', row: { idCandidato: '42' } };

    componente.manejarAccionTabla(evento);
    componente.manejarAccionTabla(evento);

    expect(descargarCvOriginal).toHaveBeenCalledTimes(1);
    expect(componente.descargandoCvOriginal.has('42')).toBeTrue();

    descarga.error(new Error('CV no disponible'));

    expect(componente.descargandoCvOriginal.size).toBe(0);
    expect(componente.alerta).toBeTruthy();
  });
});
