import { describe, expect, it } from 'vitest';

import { obtenerMensajeError } from './api-error';

describe('obtenerMensajeError', () => {
  it('humaniza conflictos de correos duplicados', () => {
    const mensaje = obtenerMensajeError(
      { status: 409, error: { detail: 'El correo electrónico ya está registrado como candidato' } },
      'Error'
    );

    expect(mensaje).toBe('Este correo ya está registrado como candidato. Busca el perfil existente antes de crear uno nuevo.');
  });

  it('humaniza referencias a catalogos inexistentes', () => {
    const mensaje = obtenerMensajeError(
      { status: 422, error: { detail: 'Cliente 12 no existe' } },
      'Error'
    );

    expect(mensaje).toBe('El cliente seleccionado ya no está disponible. Actualiza el catálogo e intenta nuevamente.');
  });

  it('traduce campos tecnicos en validaciones de FastAPI', () => {
    const mensaje = obtenerMensajeError(
      {
        status: 422,
        error: {
          detail: [
            { loc: ['body', 'sol_salario_min'], msg: 'field required' },
            { loc: ['body', 'cand_email'], msg: 'Input should be a valid email' },
          ],
        },
      },
      'Error'
    );

    expect(mensaje).toBe('Salario mínimo: Campo obligatorio. Correo del candidato: Ingresa un correo electrónico válido.');
  });

  it('humaniza reglas de flujo de solicitudes', () => {
    const mensaje = obtenerMensajeError(
      { status: 409, error: { detail: 'Transición no permitida: Abierta -> Cerrada' } },
      'Error'
    );

    expect(mensaje).toBe('No puedes cambiar el estado de "Abierta" a "Cerrada". Revisa el flujo antes de continuar.');
  });

  it('humaniza errores de cuestionario vencido', () => {
    const mensaje = obtenerMensajeError(
      { status: 409, error: { detail: 'El cuestionario se encuentra vencido' } },
      'Error'
    );

    expect(mensaje).toBe('Este cuestionario venció y ya no se puede responder.');
  });

  it('usa mensajes generales mejores cuando no hay detalle de backend', () => {
    expect(obtenerMensajeError({ status: 404, error: {} }, 'Error')).toBe(
      'No encontramos el registro solicitado. Puede haber sido eliminado o actualizado.'
    );
  });
});
