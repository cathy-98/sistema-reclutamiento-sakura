import '@angular/compiler';
import { of } from 'rxjs';
import { describe, expect, it } from 'vitest';

import { EntrevistaFormModal } from './entrevista-form-modal';

describe('EntrevistaFormModal solicitud selector', () => {
  function crearComponente() {
    const catalogosService = {
      listarTiposEntrevista: () => of([]),
      listarUsuarios: () => of([]),
      listarEstadosSolicitudCandidatoSeguro: () => of([]),
    };
    const candidatosService = {
      listar: () => of([]),
      listarPorSolicitud: () => of([]),
      listarSolicitudes: () => of([]),
      obtenerPorId: () => of(null),
    };
    const solicitudesService = {
      listar: () => of([]),
    };

    return new EntrevistaFormModal(
      catalogosService as any,
      candidatosService as any,
      solicitudesService as any,
    );
  }

  it('no selecciona una solicitud solo por escribir una coincidencia parcial', () => {
    const component = crearComponente();
    component.solicitudes = [
      { id: 8, codigo: 'SOL-000008', cargo: 'QA Automation', estado: 'En entrevistas' },
    ] as any;
    component.solicitudSeleccionadaId = 8;
    component.postulacionesSolicitud = [{ slcd_id: 10 }] as any;
    component.postulacionesSeleccionadas = new Set([10]);

    component.actualizarCodigoSolicitudSeleccionada('8');

    expect(component.codigoSolicitudSeleccionada).toBe('8');
    expect(component.solicitudSeleccionadaId).toBeNull();
    expect(component.postulacionesSolicitud).toEqual([]);
    expect(component.postulacionesSeleccionadas.size).toBe(0);
  });

  it('actualiza solicitud y carga candidatos al seleccionar una opcion valida', () => {
    const component = crearComponente();
    component.solicitudes = [
      { id: 8, codigo: 'SOL-000008', cargo: 'QA Automation', estado: 'En entrevistas' },
    ] as any;

    component.seleccionarSolicitudAutocomplete(component.solicitudes[0]);

    expect(component.codigoSolicitudSeleccionada).toBe('SOL-000008');
    expect(component.solicitudSeleccionadaId).toBe(8);
  });

  it('no bloquea la edicion por la carga inicial de datos', () => {
    const component = crearComponente();
    component.cargandoDatos = true;

    component.actualizarCodigoSolicitudSeleccionada('SOL-000008');

    expect(component.codigoSolicitudSeleccionada).toBe('SOL-000008');
    expect(component.solicitudEditadaPorUsuario).toBe(true);
  });

  it('limpia candidatos precargados al editar la solicitud para permitir cambiarla', () => {
    const component = crearComponente();
    component.candidatos = [
      {
        id: '1',
        solicitudCandidatoId: 10,
        idSolicitud: 'SOL-000001',
        nombre: 'Candidato Demo',
        cargo: 'QA',
      },
    ];
    const cambios: unknown[] = [];
    component.candidatosChange.subscribe((valor) => cambios.push(valor));

    component.actualizarCodigoSolicitudSeleccionada('8');

    expect(component.candidatos).toEqual([]);
    expect(cambios).toEqual([[]]);
  });

  it('cambia al modo candidato y limpia la selección dependiente de solicitud', () => {
    const component = crearComponente();
    component.solicitudSeleccionadaId = 8;
    component.codigoSolicitudSeleccionada = 'SOL-000008';
    component.postulacionesSolicitud = [{ slcd_id: 10 }] as any;
    component.postulacionesSeleccionadas = new Set([10]);

    component.cambiarModoBusqueda('candidato');

    expect(component.modoBusqueda).toBe('candidato');
    expect(component.solicitudSeleccionadaId).toBeNull();
    expect(component.postulacionesSolicitud).toEqual([]);
    expect(component.postulacionesSeleccionadas.size).toBe(0);
  });

  it('filtra candidatos por nombre, apellido y correo', () => {
    const component = crearComponente();
    component.candidatosDisponibles = [
      { cand_id: 1, cand_nombres: 'Ana', cand_apellido_paterno: 'Pérez', cand_email: 'ana@example.com' },
      { cand_id: 2, cand_nombres: 'Bruno', cand_apellido_paterno: 'Soto', cand_email: 'bruno@example.com' },
    ];

    component.busquedaCandidato = 'perez';
    expect(component.candidatosFiltrados.map((item) => item.cand_id)).toEqual([1]);
    component.busquedaCandidato = 'bruno@example.com';
    expect(component.candidatosFiltrados.map((item) => item.cand_id)).toEqual([2]);
  });

  it('carga las postulaciones del candidato sin seleccionar ninguna automáticamente', () => {
    const candidatosService = {
      listar: () => of([]),
      listarPorSolicitud: () => of([]),
      listarSolicitudes: () => of([
        { slcd_id: 20, slcd_candidato_id: 4, slcd_solicitud_id: 8, slcd_estado_solicitud_candidato_id: 1 },
        { slcd_id: 21, slcd_candidato_id: 4, slcd_solicitud_id: 9, slcd_estado_solicitud_candidato_id: 3 },
      ]),
      obtenerPorId: () => of(null),
    };
    const catalogosService = {
      listarTiposEntrevista: () => of([]),
      listarUsuarios: () => of([]),
      listarEstadosSolicitudCandidatoSeguro: () => of([
        { essc_id: 1, essc_nombre: 'En revision' },
        { essc_id: 3, essc_nombre: 'Seleccionado' },
      ]),
    };
    const component = new EntrevistaFormModal(
      catalogosService as any,
      candidatosService as any,
      { listar: () => of([]) } as any,
    );
    component.modoBusqueda = 'candidato';
    component.solicitudesTodas = [
      { id: '8', codigo: 'SOL-000008', cargo: 'QA', estado: 'En entrevistas' },
      { id: '9', codigo: 'SOL-000009', cargo: 'Backend', estado: 'En publicación' },
    ] as any;
    component.estadosPostulacion = [
      { essc_id: 1, essc_nombre: 'En revision' },
      { essc_id: 3, essc_nombre: 'Seleccionado' },
    ];
    component.seleccionarCandidato({ cand_id: 4, cand_nombres: 'Cata', cand_apellido_paterno: 'Demo', cand_email: 'cata@example.com' });

    expect(component.postulacionesSeleccionadas.size).toBe(0);
    expect(component.postulacionesCandidato).toHaveLength(2);
    expect(component.postulacionesCandidatoDetalle[0].elegible).toBe(true);
    expect(component.postulacionesCandidatoDetalle[1].elegible).toBe(false);
  });

  it('permite una sola postulación elegible y mantiene el id del payload', () => {
    const component = crearComponente();
    component.modoBusqueda = 'candidato';
    component.solicitudesTodas = [
      { id: '8', codigo: 'SOL-000008', cargo: 'QA', estado: 'En entrevistas' },
    ] as any;
    component.estadosPostulacion = [{ essc_id: 1, essc_nombre: 'En revision' }];
    component.postulacionesCandidato = [
      { slcd_id: 20, slcd_candidato_id: 4, slcd_solicitud_id: 8, slcd_estado_solicitud_candidato_id: 1 },
    ];
    component.postulacionesSeleccionadas = new Set([20]);

    expect(component.postulacionesSeleccionadasIds).toEqual([20]);
    expect(component.codigoSolicitudResumen()).toBe('SOL-000008');
  });

  it('muestra el error de solicitud en el campo y no en el bloque general', () => {
    const component = crearComponente();

    expect(component.validarPaso('datos')).toBe(false);
    expect(component.errorSolicitud).toBe('Selecciona una solicitud para continuar');
    expect(component.errorEnvio).toBe('');
    expect(component.mensajeValidacionVisible).toBe('');
  });
});
