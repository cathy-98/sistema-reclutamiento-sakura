import '@angular/compiler';
import { of, Subject } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { InformesCliente } from './informes-cliente';
import { InformesService } from '../../services/informes.service';
import { CandidatosService } from '../../services/candidatos.service';

describe('InformesCliente', () => {
  let component: InformesCliente;
  let informesService: {
    listarCandidatos: ReturnType<typeof vi.fn>;
    prepararDirectivos: ReturnType<typeof vi.fn>;
    enviarDirectivos: ReturnType<typeof vi.fn>;
    prepararRechazos: ReturnType<typeof vi.fn>;
    enviarRechazos: ReturnType<typeof vi.fn>;
    enviarCorreosCandidatos: ReturnType<typeof vi.fn>;
    listarPlantillas: ReturnType<typeof vi.fn>;
    descargarCvCorporativoMasivo: ReturnType<typeof vi.fn>;
    descargarResumenMasivo: ReturnType<typeof vi.fn>;
    obtenerInformeComparativoDatos: ReturnType<typeof vi.fn>;
    descargarInformeComparativoPdf: ReturnType<typeof vi.fn>;
    descargarInformeComparativoDocx: ReturnType<typeof vi.fn>;
    generarCvCorporativo: ReturnType<typeof vi.fn>;
    generarResumen: ReturnType<typeof vi.fn>;
    descargarDocumento: ReturnType<typeof vi.fn>;
    descargarBlob: ReturnType<typeof vi.fn>;
  };
  let candidatosService: {
    listarPorSolicitud: ReturnType<typeof vi.fn>;
  };

  interface InformeOverrides {
    solicitudCandidatoId?: number;
    solicitudId?: number;
    idSolicitud?: string;
    match?: number;
    nombre?: string;
    correo?: string;
    telefono?: string;
    cargo?: string;
    estado?: string;
    clasificacion?: 'APROBADO' | 'PENDIENTE' | 'NO_APROBADO';
    aprobado?: boolean;
    puedeEnviarDirectivos?: boolean;
    puedeEnviarRechazo?: boolean;
  }

  const plantillaSeleccion = {
    plantilla_id: 9,
    tipo: 'SELECCION',
    nombre: 'Selección',
    asunto: 'Seleccionado para {cargo}',
    cuerpo: 'Hola {nombre}, avanzamos con {codigo_solicitud}.',
    activa: true,
  };

  const informe = (overrides: InformeOverrides = {}) => ({
    id: String(overrides.solicitudCandidatoId ?? 101),
    solicitudCandidatoId: overrides.solicitudCandidatoId ?? 101,
    solicitudId: overrides.solicitudId ?? 1,
    idSolicitud: overrides.idSolicitud ?? 'SOL-001',
    match: overrides.match ?? 92,
    nombre: overrides.nombre ?? 'Candidata QA',
    correo: overrides.correo ?? 'candidata@example.com',
    telefono: overrides.telefono ?? '900000001',
    cargo: overrides.cargo ?? 'Backend',
    empresa: 'No informado',
    nivel: 'Python',
    experiencia: 'QA',
    resultadoEntrevista: 'Aprobado',
    detalleResultado: 'Aprobado',
    motivoM6: 'Aprobado',
    estado: overrides.estado ?? 'Seleccionado',
    disponibilidad: 'Inmediata',
    clasificacion: overrides.clasificacion ?? 'APROBADO',
    aprobado: overrides.aprobado ?? true,
    puedeEnviarDirectivos: overrides.puedeEnviarDirectivos ?? true,
    puedeEnviarRechazo: overrides.puedeEnviarRechazo ?? false,
    entrevistas: [],
  });

  beforeEach(() => {
    informesService = {
      listarCandidatos: vi.fn(),
      prepararDirectivos: vi.fn(),
      enviarDirectivos: vi.fn(),
      prepararRechazos: vi.fn(),
      enviarRechazos: vi.fn(),
      enviarCorreosCandidatos: vi.fn(),
      listarPlantillas: vi.fn(),
      descargarCvCorporativoMasivo: vi.fn(),
      descargarResumenMasivo: vi.fn(),
      obtenerInformeComparativoDatos: vi.fn(),
      descargarInformeComparativoPdf: vi.fn(),
      descargarInformeComparativoDocx: vi.fn(),
      generarCvCorporativo: vi.fn(),
      generarResumen: vi.fn(),
      descargarDocumento: vi.fn(),
      descargarBlob: vi.fn(),
    };

    informesService.listarCandidatos.mockReturnValue(of({ total: 0, items: [] }));
    informesService.prepararDirectivos.mockReturnValue(of({
      destinatarios: ['admin@example.com'],
      cc: [],
      asunto: 'Directivos',
      cuerpo: 'Resumen',
      candidatos: [],
      adjuntos: [],
    }));
    informesService.enviarDirectivos.mockReturnValue(of([]));
    informesService.prepararRechazos.mockReturnValue(of({
      items: [
        {
          solicitud_candidato_id: 505,
          destinatario: 'rechazo@example.com',
          asunto: 'Cierre',
          cuerpo: 'Mensaje de cierre',
        },
      ],
    }));
    informesService.enviarRechazos.mockReturnValue(of([
      {
        notificacion_id: 2,
        solicitud_candidato_id: 505,
        tipo: 'RECHAZO',
        destinatario: 'rechazo@example.com',
        asunto: 'Cierre',
        estado: 'ENVIADO',
      },
    ]));
    informesService.enviarCorreosCandidatos.mockReturnValue(of([
      {
        notificacion_id: 1,
        solicitud_candidato_id: 101,
        tipo: 'SELECCION',
        destinatario: 'candidata@example.com',
        asunto: 'Seleccionado',
        estado: 'ENVIADO',
      },
    ]));
    informesService.listarPlantillas.mockReturnValue(of([plantillaSeleccion]));
    informesService.obtenerInformeComparativoDatos.mockReturnValue(of({
      solicitud: {
        solicitud_id: 1,
        codigo: 'SOL-001',
        cargo: 'Backend',
        empresa: 'Cliente',
        vacantes: 2,
        area: 'TI',
        modalidad: 'Remota',
      },
      habilidades_requeridas: [],
      candidatos: [
        {
          solicitud_candidato_id: 101,
          candidato_id: 1,
          nombre: 'Candidata QA',
          correo: 'candidata@example.com',
          pretension_renta: null,
          disponibilidad: 'Inmediata',
          observacion_operacional: null,
          observacion_tecnica: null,
          observaciones_pendientes_definicion: [],
          tecnologias_excluyentes: [],
          tecnologias_no_excluyentes: [],
        },
      ],
    }));
    informesService.descargarInformeComparativoPdf.mockReturnValue(of({
      body: new Blob(['pdf']),
      headers: { get: () => null },
    }));
    informesService.descargarInformeComparativoDocx.mockReturnValue(of({
      body: new Blob(['docx']),
      headers: { get: () => null },
    }));
    candidatosService = {
      listarPorSolicitud: vi.fn().mockReturnValue(of([])),
    };

    component = new InformesCliente(
      informesService as unknown as InformesService,
      candidatosService as unknown as CandidatosService,
    );
  });

  it('crea el componente', () => {
    expect(component).toBeTruthy();
  });

  it('mantiene el botón superior en el flujo DIRECTIVOS', () => {
    component.informes = [informe()];
    component.destinatariosResumen = 'admin@example.com';

    component.generarInforme();

    expect(component.mostrarResumenAdministrador).toBe(true);
    expect(component.mostrarModalCorreoCandidatos).toBe(false);
    expect(informesService.prepararDirectivos).toHaveBeenCalledWith(expect.objectContaining({
      solicitudCandidatoIds: [101],
      destinatarios: ['admin@example.com'],
    }));
    expect(informesService.enviarCorreosCandidatos).not.toHaveBeenCalled();
  });

  it('requiere selección para enviar correo masivo en Aprobados', () => {
    component.informes = [informe()];
    component.vistaActiva = 'aprobados';
    component.seleccionados = new Set<string>();

    component.enviarCorreoMasivo();

    expect(component.mostrarModalCorreoCandidatos).toBe(false);
    expect(component.alerta?.mensaje).toContain('Selecciona candidatos aprobados');
    expect(informesService.enviarCorreosCandidatos).not.toHaveBeenCalled();
  });

  it('envía correo masivo de Aprobados con solicitud_candidato_id y tipo SELECCION', () => {
    component.informes = [
      informe({ solicitudCandidatoId: 101, nombre: 'Uno' }),
      informe({ solicitudCandidatoId: 202, nombre: 'Dos' }),
    ];
    component.vistaActiva = 'aprobados';
    component.seleccionados = new Set(['101', '202']);

    component.enviarCorreoMasivo();
    component.enviarCorreoCandidatosAprobados();

    expect(component.plantillaCorreoCandidato).toBe('SELECCION');
    expect(informesService.enviarCorreosCandidatos).toHaveBeenCalledWith({
      solicitudCandidatoIds: [101, 202],
      tipo: 'SELECCION',
      asunto: 'Seleccionado para {cargo}',
      cuerpo: 'Hola {nombre}, avanzamos con {codigo_solicitud}.',
    });
    expect(informesService.enviarDirectivos).not.toHaveBeenCalled();
  });

  it('en Aprobados ofrece solo la plantilla SELECCION para correo al candidato', () => {
    const plantillas = [
      { ...plantillaSeleccion, tipo: 'CONTACTO', nombre: 'CONTACTO INICIAL' },
      { ...plantillaSeleccion, tipo: 'AVANCE', nombre: 'AVANCE PROCESO' },
      { ...plantillaSeleccion, tipo: 'INVITACION', nombre: 'INVITACIONENTREVISTA', cuerpo: 'Fecha: {{params.fecha}}' },
      plantillaSeleccion,
    ];

    const disponibles = (component as any).filtrarPlantillasCorreoCandidatos(plantillas);

    expect(disponibles.map((plantilla: any) => plantilla.tipo)).toEqual(['SELECCION']);
  });

  it('actualiza asunto y mensaje inmediatamente al cambiar entre plantillas del mismo tipo', () => {
    component.plantillasCorreoCandidatos = [
      {
        ...plantillaSeleccion,
        plantilla_id: 9,
        nombre: 'Selección A',
        asunto: 'Asunto A',
        cuerpo: 'Cuerpo A',
      },
      {
        ...plantillaSeleccion,
        plantilla_id: 10,
        nombre: 'Selección B',
        asunto: 'Asunto B',
        cuerpo: 'Cuerpo B',
      },
    ];

    component.seleccionarPlantillaCorreoCandidato(9);
    expect(component.asuntoCorreoCandidatos).toBe('Asunto A');
    expect(component.cuerpoCorreoCandidatos).toBe('Cuerpo A');

    component.seleccionarPlantillaCorreoCandidato(10);
    expect(component.plantillaCorreoCandidatoId).toBe(10);
    expect(component.asuntoCorreoCandidatos).toBe('Asunto B');
    expect(component.cuerpoCorreoCandidatos).toBe('Cuerpo B');
    expect(component.puedeEnviarCorreoCandidatos).toBe(false);
  });

  it('limpia asunto y mensaje inmediatamente al seleccionar plantilla manual', () => {
    component.plantillasCorreoCandidatos = [plantillaSeleccion];
    component.seleccionarPlantillaCorreoCandidato(9);

    component.seleccionarPlantillaCorreoCandidato(0);

    expect(component.plantillaCorreoCandidato).toBe('manual');
    expect(component.plantillaCorreoCandidatoId).toBe(0);
    expect(component.asuntoCorreoCandidatos).toBe('');
    expect(component.cuerpoCorreoCandidatos).toBe('');
  });

  it('prepara correos de cierre inmediatamente al cambiar la plantilla por id', () => {
    component.candidatosCorreoSeleccionados = [
      informe({
        solicitudCandidatoId: 505,
        clasificacion: 'NO_APROBADO',
        aprobado: false,
        puedeEnviarRechazo: true,
      }),
    ];
    component.plantillasCorreoCierre = [
      {
        ...plantillaSeleccion,
        plantilla_id: 11,
        tipo: 'RECHAZO',
        nombre: 'Rechazo formal',
      },
      {
        ...plantillaSeleccion,
        plantilla_id: 12,
        tipo: 'AGRADECIMIENTO',
        nombre: 'Agradecimiento',
      },
    ];

    component.seleccionarPlantillaCorreoCierre(11);
    expect(component.plantillaCorreoCierreId).toBe(11);
    expect(component.tipoCorreoCierre).toBe('RECHAZO');
    expect(informesService.prepararRechazos).toHaveBeenLastCalledWith({
      solicitudCandidatoIds: [505],
      tipo: 'RECHAZO',
    });

    component.seleccionarPlantillaCorreoCierre(12);
    expect(component.plantillaCorreoCierreId).toBe(12);
    expect(component.tipoCorreoCierre).toBe('AGRADECIMIENTO');
    expect(component.itemsCorreoCierre).toEqual([
      {
        solicitud_candidato_id: 505,
        destinatario: 'rechazo@example.com',
        asunto: 'Cierre',
        cuerpo: 'Mensaje de cierre',
      },
    ]);
    expect(informesService.prepararRechazos).toHaveBeenLastCalledWith({
      solicitudCandidatoIds: [505],
      tipo: 'AGRADECIMIENTO',
    });
  });

  it('la acción individual usa el candidato correcto y no abre DIRECTIVOS', () => {
    const row = informe({ solicitudCandidatoId: 303, nombre: 'Fila' });
    component.informes = [row];

    component.manejarAccionTabla({ action: 'enviar-correo', row });
    component.enviarCorreoCandidatosAprobados();

    expect(component.mostrarModalCorreoCandidatos).toBe(true);
    expect(component.mostrarResumenAdministrador).toBe(false);
    expect(informesService.enviarCorreosCandidatos).toHaveBeenCalledWith(expect.objectContaining({
      solicitudCandidatoIds: [303],
      tipo: 'SELECCION',
    }));
    expect(informesService.prepararDirectivos).not.toHaveBeenCalled();
  });

  it('la acción individual descarga el comparativo con todos los candidatos de la solicitud', () => {
    const row = informe({ solicitudCandidatoId: 303, solicitudId: 7, nombre: 'Fila' });
    component.informes = [
      row,
      informe({ solicitudCandidatoId: 404, solicitudId: 7, idSolicitud: 'SOL-001', nombre: 'Otra fila' }),
    ];
    candidatosService.listarPorSolicitud.mockReturnValue(of([
      {
        slcd_id: 303,
        slcd_candidato_id: 30,
        slcd_solicitud_id: 7,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: null,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
      {
        slcd_id: 404,
        slcd_candidato_id: 40,
        slcd_solicitud_id: 7,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: null,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
    ]));

    component.manejarAccionTabla({ action: 'descargar-informe-pdf', row });

    expect(component.solicitudComparativoId).toBe(7);
    expect(candidatosService.listarPorSolicitud).toHaveBeenCalledWith(7);
    expect(informesService.obtenerInformeComparativoDatos).not.toHaveBeenCalled();
    expect(informesService.descargarInformeComparativoPdf).toHaveBeenCalledWith({
      solicitud_id: 7,
      solicitud_candidato_ids: [303, 404],
    });
    expect(informesService.descargarBlob).toHaveBeenCalled();
    expect(informesService.generarResumen).not.toHaveBeenCalled();
    expect(informesService.descargarResumenMasivo).not.toHaveBeenCalled();
  });

  it('descarga informe comparativo Word con todos los candidatos de la solicitud seleccionada', () => {
    component.informes = [
      informe({ solicitudCandidatoId: 101, solicitudId: 1, nombre: 'Uno' }),
      informe({ solicitudCandidatoId: 202, solicitudId: 1, nombre: 'Dos' }),
    ];
    component.actualizarSeleccionInformes(new Set(['101']));
    candidatosService.listarPorSolicitud.mockReturnValue(of([
      {
        slcd_id: 101,
        slcd_candidato_id: 11,
        slcd_solicitud_id: 1,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: 90,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
      {
        slcd_id: 202,
        slcd_candidato_id: 22,
        slcd_solicitud_id: 1,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: 80,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
    ]));

    component.descargarInformeComparativoMasivo('docx');

    expect(candidatosService.listarPorSolicitud).toHaveBeenCalledWith(1);
    expect(informesService.descargarInformeComparativoDocx).toHaveBeenCalledWith({
      solicitud_id: 1,
      solicitud_candidato_ids: [101, 202],
    });
    expect(informesService.descargarBlob).toHaveBeenCalled();
    expect(informesService.descargarResumenMasivo).not.toHaveBeenCalled();
  });

  it('bloquea informe comparativo si la selección mezcla solicitudes', () => {
    component.informes = [
      informe({ solicitudCandidatoId: 101, solicitudId: 1, idSolicitud: 'SOL-1' }),
      informe({ solicitudCandidatoId: 202, solicitudId: 2, idSolicitud: 'SOL-2' }),
    ];
    component.actualizarSeleccionInformes(new Set(['101', '202']));

    component.descargarInformeComparativoMasivo('pdf');

    expect(component.alerta?.mensaje).toContain('Elige una sola solicitud');
    expect(informesService.descargarInformeComparativoPdf).not.toHaveBeenCalled();
    expect(informesService.descargarInformeComparativoDocx).not.toHaveBeenCalled();
  });

  it('muestra la cantidad de candidatos que incluirá al seleccionar solicitud en el filtro', () => {
    component.informes = [
      informe({ solicitudCandidatoId: 101, solicitudId: 1, idSolicitud: 'SOL-1', nombre: 'Uno' }),
      informe({ solicitudCandidatoId: 202, solicitudId: 1, idSolicitud: 'SOL-1', nombre: 'Dos' }),
    ];
    candidatosService.listarPorSolicitud.mockReturnValue(of([
      {
        slcd_id: 101,
        slcd_candidato_id: 11,
        slcd_solicitud_id: 1,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: 90,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
      {
        slcd_id: 202,
        slcd_candidato_id: 22,
        slcd_solicitud_id: 1,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: 80,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
    ]));

    component.seleccionarFiltroSolicitud({ id: 1, codigo: 'SOL-1', cargo: 'Backend' });

    expect(candidatosService.listarPorSolicitud).toHaveBeenCalledWith(1);
    expect(component.candidatosComparativoSolicitud.map((item) => item.solicitudCandidatoId)).toEqual([101, 202]);
    expect(component.mensajeInformeComparativo).toContain('El informe incluirá 2 candidatos de SOL-1');
  });

  it('carga el contexto comparativo apenas se selecciona un candidato', () => {
    const respuesta = new Subject<any[]>();
    component.informes = [
      informe({ solicitudCandidatoId: 101, solicitudId: 1, idSolicitud: 'SOL-1', nombre: 'Uno' }),
    ];
    candidatosService.listarPorSolicitud.mockReturnValue(respuesta.asObservable());

    component.actualizarSeleccionInformes(new Set(['101']));

    expect(candidatosService.listarPorSolicitud).toHaveBeenCalledWith(1);
    expect(component.cargandoCandidatosComparativo).toBe(true);
    expect(component.mensajeInformeComparativo).toContain('Preparando informe comparativo');

    respuesta.next([
      {
        slcd_id: 101,
        slcd_candidato_id: 11,
        slcd_solicitud_id: 1,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: 90,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
    ]);
    respuesta.complete();

    expect(component.cargandoCandidatosComparativo).toBe(false);
    expect(component.mensajeInformeComparativo).toContain('El informe incluirá 1 candidato de SOL-1');
  });

  it('ignora respuestas antiguas si se cambia rápidamente de candidato', () => {
    const primeraRespuesta = new Subject<any[]>();
    const segundaRespuesta = new Subject<any[]>();
    component.informes = [
      informe({ solicitudCandidatoId: 101, solicitudId: 1, idSolicitud: 'SOL-1', nombre: 'Uno' }),
      informe({ solicitudCandidatoId: 202, solicitudId: 2, idSolicitud: 'SOL-2', nombre: 'Dos' }),
    ];
    candidatosService.listarPorSolicitud
      .mockReturnValueOnce(primeraRespuesta.asObservable())
      .mockReturnValueOnce(segundaRespuesta.asObservable());

    component.actualizarSeleccionInformes(new Set(['101']));
    component.actualizarSeleccionInformes(new Set(['202']));

    primeraRespuesta.next([
      {
        slcd_id: 101,
        slcd_candidato_id: 11,
        slcd_solicitud_id: 1,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: 90,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
    ]);
    primeraRespuesta.complete();

    expect(component.solicitudComparativoId).toBe(2);
    expect(component.cargandoCandidatosComparativo).toBe(true);
    expect(component.candidatosComparativoSolicitud).toEqual([]);

    segundaRespuesta.next([
      {
        slcd_id: 202,
        slcd_candidato_id: 22,
        slcd_solicitud_id: 2,
        slcd_pretension_renta: null,
        slcd_puntaje_compatibilidad: 80,
        slcd_estado_solicitud_candidato_id: null,
        slcd_fecha_postulacion: null,
        slcd_observaciones: null,
        slcd_motivo_rechazo_id: null,
      },
    ]);
    segundaRespuesta.complete();

    expect(component.cargandoCandidatosComparativo).toBe(false);
    expect(component.candidatosComparativoSolicitud.map((item) => item.solicitudCandidatoId)).toEqual([202]);
    expect(component.mensajeInformeComparativo).toContain('SOL-2');
  });

  it('bloquea la descarga cuando la solicitud no tiene candidatos asociados', () => {
    component.informes = [
      informe({ solicitudCandidatoId: 101, solicitudId: 1, idSolicitud: 'SOL-1' }),
    ];
    candidatosService.listarPorSolicitud.mockReturnValue(of([]));

    component.seleccionarFiltroSolicitud({ id: 1, codigo: 'SOL-1', cargo: 'Backend' });

    component.descargarInformeComparativoMasivo('pdf');

    expect(component.puedeDescargarInformeComparativo).toBe(false);
    expect(component.alerta?.mensaje).toContain('no tiene candidatos asociados');
    expect(informesService.descargarInformeComparativoPdf).not.toHaveBeenCalled();
  });

  it('Pendientes no habilita comunicación de cierre', () => {
    component.informes = [informe({
      solicitudCandidatoId: 404,
      clasificacion: 'PENDIENTE',
      aprobado: false,
      puedeEnviarDirectivos: false,
    })];
    component.vistaActiva = 'pendientes';
    component.seleccionados = new Set(['404']);

    expect(component.puedeAbrirCorreoAprobadosMasivo).toBe(false);
    component.enviarCorreoMasivo();

    expect(component.mostrarModalCorreoCandidatos).toBe(false);
    expect(informesService.enviarCorreosCandidatos).not.toHaveBeenCalled();
  });

  it('No aprobados no dispara rechazo ni agradecimiento automáticamente', () => {
    component.informes = [informe({
      solicitudCandidatoId: 505,
      clasificacion: 'NO_APROBADO',
      aprobado: false,
      puedeEnviarDirectivos: false,
      puedeEnviarRechazo: true,
      estado: 'Descartado',
    })];
    component.vistaActiva = 'no-aprobados';
    component.seleccionados = new Set(['505']);

    component.enviarCorreoMasivo();

    expect(component.mostrarModalCorreoCandidatos).toBe(true);
    expect(informesService.prepararRechazos).not.toHaveBeenCalled();
    expect(informesService.enviarCorreosCandidatos).not.toHaveBeenCalled();
    expect(informesService.enviarDirectivos).not.toHaveBeenCalled();
  });

  it('No aprobados elegible puede preparar y enviar correo de cierre', () => {
    component.informes = [informe({
      solicitudCandidatoId: 505,
      clasificacion: 'NO_APROBADO',
      aprobado: false,
      puedeEnviarDirectivos: false,
      puedeEnviarRechazo: true,
      estado: 'Descartado',
    })];
    component.vistaActiva = 'no-aprobados';
    component.seleccionados = new Set(['505']);

    component.enviarCorreoMasivo();
    component.seleccionarTipoCorreoCierre('RECHAZO');
    component.enviarCorreoCandidatos();

    expect(informesService.prepararRechazos).toHaveBeenCalledWith({
      solicitudCandidatoIds: [505],
      tipo: 'RECHAZO',
    });
    expect(informesService.enviarRechazos).toHaveBeenCalledWith([
      {
        tipo: 'RECHAZO',
        solicitudCandidatoId: 505,
        asunto: 'Cierre',
        cuerpo: 'Mensaje de cierre',
      },
    ]);
    expect(informesService.enviarDirectivos).not.toHaveBeenCalled();
    expect(informesService.enviarCorreosCandidatos).not.toHaveBeenCalled();
  });

  it('No aprobado en entrevista no elegible no puede recibir rechazo', () => {
    component.informes = [informe({
      solicitudCandidatoId: 707,
      clasificacion: 'NO_APROBADO',
      aprobado: false,
      puedeEnviarDirectivos: false,
      puedeEnviarRechazo: false,
      estado: 'En entrevista',
    })];
    component.vistaActiva = 'no-aprobados';
    component.seleccionados = new Set(['707']);

    component.enviarCorreoMasivo();

    expect(component.mostrarModalCorreoCandidatos).toBe(false);
    expect(component.alerta?.mensaje).toContain('todavía no tienen habilitada');
    expect(informesService.prepararRechazos).not.toHaveBeenCalled();
    expect(informesService.enviarRechazos).not.toHaveBeenCalled();
  });

  it('selección múltiple completamente elegible permite continuar', () => {
    component.informes = [
      informe({
        solicitudCandidatoId: 801,
        clasificacion: 'NO_APROBADO',
        aprobado: false,
        puedeEnviarDirectivos: false,
        puedeEnviarRechazo: true,
      }),
      informe({
        solicitudCandidatoId: 802,
        clasificacion: 'NO_APROBADO',
        aprobado: false,
        puedeEnviarDirectivos: false,
        puedeEnviarRechazo: true,
      }),
    ];
    component.vistaActiva = 'no-aprobados';
    component.seleccionados = new Set(['801', '802']);

    component.enviarCorreoMasivo();

    expect(component.mostrarModalCorreoCandidatos).toBe(true);
    expect(component.candidatosCorreoSeleccionados.map((item) => item.solicitudCandidatoId)).toEqual([801, 802]);
  });

  it('selección mixta no envía parcialmente', () => {
    component.informes = [
      informe({
        solicitudCandidatoId: 901,
        clasificacion: 'NO_APROBADO',
        aprobado: false,
        puedeEnviarDirectivos: false,
        puedeEnviarRechazo: true,
      }),
      informe({
        solicitudCandidatoId: 902,
        clasificacion: 'NO_APROBADO',
        aprobado: false,
        puedeEnviarDirectivos: false,
        puedeEnviarRechazo: false,
        estado: 'En entrevista',
      }),
    ];
    component.vistaActiva = 'no-aprobados';
    component.seleccionados = new Set(['901', '902']);

    component.enviarCorreoMasivo();

    expect(component.mostrarModalCorreoCandidatos).toBe(false);
    expect(component.alerta?.mensaje).toContain('todavía no tienen habilitada');
    expect(informesService.prepararRechazos).not.toHaveBeenCalled();
    expect(informesService.enviarRechazos).not.toHaveBeenCalled();
    expect(informesService.enviarCorreosCandidatos).not.toHaveBeenCalled();
  });

  it('no crea ni modifica postulaciones al enviar correo a aprobados', () => {
    component.informes = [informe({ solicitudCandidatoId: 606 })];
    component.vistaActiva = 'aprobados';
    component.seleccionados = new Set(['606']);

    component.enviarCorreoMasivo();
    component.enviarCorreoCandidatosAprobados();

    const payload = informesService.enviarCorreosCandidatos.mock.calls.at(-1)?.[0] as any;
    expect(Object.keys(payload).sort()).toEqual(['asunto', 'cuerpo', 'solicitudCandidatoIds', 'tipo']);
    expect(payload.solicitudCandidatoIds).toEqual([606]);
  });
});
