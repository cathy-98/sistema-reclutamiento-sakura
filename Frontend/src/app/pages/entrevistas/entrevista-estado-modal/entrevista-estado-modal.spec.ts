import '@angular/compiler';
import { describe, expect, it, vi } from 'vitest';

import { EntrevistaEstadoModal } from './entrevista-estado-modal';

describe('EntrevistaEstadoModal resultados por tipo', () => {
  function crearComponente() {
    const component = new EntrevistaEstadoModal();
    component.usuarioActualId = 7;
    component.modo = 'gestionar';
    component.resultados = [
      { nore_id: 1, nore_nombre: 'Aprobado' },
      { nore_id: 2, nore_nombre: 'No aprobado' },
    ] as any;
    component.entrevista = {
      id: '12',
      idSolicitud: 'SOL-000008',
      candidato: 'Candidata QA',
      estado: 'Realizada',
      tipo: 'Tecnica, Operacional',
      resultadoEntrevista: 'Sin resultado',
      asunto: 'Entrevista QA',
      cargo: 'QA',
      fecha: '2026-10-14',
      horaInicio: '10:00',
      horaFin: '11:00',
      entrevistador: 'Entrevistador',
      estadoPostulacion: 'En entrevista',
      estadoSolicitud: 'En Entrevistas',
    };
    component.detalle = {
      entrevista_id: 12,
      solicitud_candidato_id: 22,
      solicitud_id: 8,
      estado_nombre: 'Realizada',
      fecha_hora_inicio: '2026-10-14T10:00:00',
      fecha_hora_fin: '2026-10-14T11:00:00',
      titulo_evento: 'Entrevista QA',
      tipos: [
        {
          tipo_entrevista_id: 1,
          nombre: 'Tecnica',
          entrevistadores: [
            { usuario_id: 7, nombres: 'Ana', apellido_paterno: 'Perez', email: 'ana@example.com' },
          ],
        },
        {
          tipo_entrevista_id: 2,
          nombre: 'Operacional',
          entrevistadores: [
            { usuario_id: 7, nombres: 'Ana', apellido_paterno: 'Perez', email: 'ana@example.com' },
          ],
        },
        {
          tipo_entrevista_id: 3,
          nombre: 'RRHH',
          entrevistadores: [
            { usuario_id: 9, nombres: 'Luis', apellido_paterno: 'Diaz', email: 'luis@example.com' },
          ],
        },
      ],
      evaluaciones: [
        {
          evaluacion_id: 50,
          entrevista_id: 12,
          tipo_entrevista_id: 1,
          tipo_entrevista_nombre: 'Tecnica',
          usuario_id: 7,
          usuario_nombre: 'Ana Perez',
          resultado_id: 1,
          resultado_nombre: 'Aprobado',
          observacion: 'Buen desempeño',
        },
        {
          evaluacion_id: 51,
          entrevista_id: 12,
          tipo_entrevista_id: 3,
          tipo_entrevista_nombre: 'RRHH',
          usuario_id: 9,
          usuario_nombre: 'Luis Diaz',
          resultado_id: 2,
          resultado_nombre: 'No aprobado',
          observacion: 'Observacion de otro entrevistador',
        },
      ],
    } as any;
    component.ngOnChanges({
      entrevista: {
        currentValue: component.entrevista,
        previousValue: null,
        firstChange: true,
        isFirstChange: () => true,
      },
    } as any);

    return component;
  }

  it('solo habilita tipos asignados al usuario actual', () => {
    const component = crearComponente();

    expect(component.tiposEvaluables.map((tipo) => tipo.tipo_entrevista_id)).toEqual([1, 2]);
    expect(component.tieneFeedbackHabilitado).toBe(true);
  });

  it('precarga la evaluacion propia sin tomar evaluaciones de otros usuarios', () => {
    const component = crearComponente();

    expect(component.evaluacionTipo(1)).toMatchObject({
      resultadoId: 1,
      observacion: 'Buen desempeño',
      existe: true,
    });
    expect(component.evaluacionTipo(2)).toMatchObject({
      resultadoId: null,
      observacion: '',
      existe: false,
    });
  });

  it('emite POST/PATCH solo para tipos evaluables con resultado seleccionado', () => {
    const component = crearComponente();
    const guardar = vi.fn();
    component.guardarEvaluaciones.subscribe(guardar);

    component.evaluacionTipo(2).resultadoId = 2;
    component.evaluacionTipo(2).observacion = 'Observacion operacional';
    component.enviar();

    expect(guardar).toHaveBeenCalledWith([
      {
        tipoId: 1,
        existe: true,
        nombreResultadoId: 1,
        observacion: 'Buen desempeño',
      },
      {
        tipoId: 2,
        existe: false,
        nombreResultadoId: 2,
        observacion: 'Observacion operacional',
      },
    ]);
  });
});
