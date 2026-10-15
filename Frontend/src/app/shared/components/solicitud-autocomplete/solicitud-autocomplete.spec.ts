import '@angular/compiler';
import { describe, expect, it, vi } from 'vitest';

import { SolicitudAutocomplete } from './solicitud-autocomplete';

describe('SolicitudAutocomplete', () => {
  const solicitudes = [
    { id: 8, codigo: 'SOL-000008', cargo: 'QA Automation' },
    { id: 18, codigo: 'SOL-000018', cargo: 'Analista QA' },
  ];

  function crearComponente() {
    const component = new SolicitudAutocomplete();
    component.solicitudes = solicitudes;
    component.inputElement = {
      nativeElement: {
        getBoundingClientRect: () => ({
          x: 32,
          y: 48,
          top: 48,
          right: 352,
          bottom: 92,
          left: 32,
          width: 320,
          height: 44,
          toJSON: () => ({}),
        }),
      },
    } as any;

    return component;
  }

  it('muestra coincidencias al escribir un numero parcial sin requerir perder foco', () => {
    const component = crearComponente();

    component.actualizar('8');

    expect(component.abierto).toBe(true);
    expect(component.opciones.map((solicitud) => solicitud.codigo)).toContain('SOL-000008');
    expect(component.panelStyle['top']).toBe('97px');
    expect(component.panelStyle['width']).toBe('320px');
  });

  it('selecciona una solicitud con Enter y emite la opcion elegida', () => {
    const component = crearComponente();
    const seleccion = vi.fn();
    component.selected.subscribe(seleccion);

    component.actualizar('SOL-000008');
    component.manejarTecla({
      key: 'Enter',
      preventDefault: vi.fn(),
    } as unknown as KeyboardEvent);

    expect(seleccion).toHaveBeenCalledWith(solicitudes[0]);
    expect(component.value).toBe('SOL-000008');
    expect(component.abierto).toBe(false);
  });

  it('selecciona con mouse antes de que el input pierda foco', () => {
    const component = crearComponente();
    const seleccion = vi.fn();
    const evento = {
      preventDefault: vi.fn(),
      stopPropagation: vi.fn(),
    } as unknown as MouseEvent;
    component.selected.subscribe(seleccion);

    component.seleccionarConMouse(evento, solicitudes[0]);

    expect(evento.preventDefault).toHaveBeenCalled();
    expect(evento.stopPropagation).toHaveBeenCalled();
    expect(seleccion).toHaveBeenCalledWith(solicitudes[0]);
    expect(component.value).toBe('SOL-000008');
    expect(component.abierto).toBe(false);
  });
});
