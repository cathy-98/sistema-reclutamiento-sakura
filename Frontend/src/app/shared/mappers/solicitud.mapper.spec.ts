import { describe, expect, it } from 'vitest';

import { SolicitudApi } from '../models/solicitud.model';
import { mapearSolicitudResumen, SolicitudResumenCatalogos } from './solicitud.mapper';

const catalogos: SolicitudResumenCatalogos = {
  cargosPorId: new Map(),
  clientesPorId: new Map(),
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
});
