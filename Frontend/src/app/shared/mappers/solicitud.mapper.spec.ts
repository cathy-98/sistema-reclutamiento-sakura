import { describe, expect, it } from 'vitest';

import { SolicitudApi } from '../models/solicitud.model';
import { mapearSolicitudResumen, SolicitudResumenCatalogos } from './solicitud.mapper';

const catalogos: SolicitudResumenCatalogos = {
  cargosPorId: new Map(),
  clientesPorId: new Map(),
  empresasPorClienteId: new Map(),
  usuariosPorId: new Map(),
  prioridadesPorId: new Map(),
  estadosPorId: new Map(),
};

function solicitudBase(overrides: Partial<SolicitudApi> = {}): SolicitudApi {
  return {
    sol_id: 2,
    sol_codigo: 'SOL-000002',
    sol_titulo: 'Solicitud dos',
    sol_descripcion: null,
    sol_observacion: null,
    ...overrides,
  };
}

describe('mapearSolicitudResumen', () => {
  it('usa sol_descripcion como descripcion visible en el listado', () => {
    const resumen = mapearSolicitudResumen(
      solicitudBase({
        sol_descripcion: 'Descripcion cargada desde el formulario.',
        sol_observacion: null,
      }),
      catalogos,
    );

    expect(resumen.descripcion).toBe('Descripcion cargada desde el formulario.');
  });

  it('mantiene sol_descripcion como fuente aunque sol_observacion tenga texto', () => {
    const resumen = mapearSolicitudResumen(
      solicitudBase({
        sol_descripcion: 'Descripcion de la solicitud.',
        sol_observacion: 'Observacion operacional.',
      }),
      catalogos,
    );

    expect(resumen.descripcion).toBe('Descripcion de la solicitud.');
  });

  it('muestra fallback cuando sol_descripcion esta vacia', () => {
    const resumen = mapearSolicitudResumen(
      solicitudBase({
        sol_descripcion: '   ',
        sol_observacion: '',
      }),
      catalogos,
    );

    expect(resumen.descripcion).toBe('Sin descripción');
  });

  it('mantiene cliente solicitante y empresa cliente como datos separados', () => {
    const resumen = mapearSolicitudResumen(
      solicitudBase({ sol_cliente_id: 8 }),
      {
        ...catalogos,
        clientesPorId: new Map([[8, 'Jade Garcia']]),
        empresasPorClienteId: new Map([[8, 'Banco de Chile']]),
      },
    );

    expect(resumen.cliente).toBe('Jade Garcia');
    expect(resumen.empresaCliente).toBe('Banco de Chile');
  });

  it('normaliza ids de catalogo aunque lleguen como texto', () => {
    const resumen = mapearSolicitudResumen(
      solicitudBase({
        sol_prioridad_id: '1' as unknown as number,
        sol_estado_solicitud_id: '2' as unknown as number,
      }),
      {
        ...catalogos,
        prioridadesPorId: new Map([[1, 'Alta']]),
        estadosPorId: new Map([[2, 'En Curso']]),
      },
    );

    expect(resumen.prioridad).toBe('Alta');
    expect(resumen.estado).toBe('En Curso');
  });
});
