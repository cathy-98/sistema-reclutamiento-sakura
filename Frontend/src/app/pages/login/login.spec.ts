import '@angular/compiler';
import { throwError } from 'rxjs';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { Login } from './login';

describe('Login', () => {
  let component: Login;
  let authService: { login: ReturnType<typeof vi.fn> };
  let router: { navigate: ReturnType<typeof vi.fn> };
  let cdr: { detectChanges: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    authService = { login: vi.fn() };
    router = { navigate: vi.fn() };
    cdr = { detectChanges: vi.fn() };
    component = new Login(authService as never, router as never, cdr as never);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('muestra advertencia cuando faltan correo y contraseña', () => {
    component.ingresar();

    expect(component.alerta?.tipo).toBe('warning');
    expect(component.alerta?.mensaje).toBe('Ingresa correo y contraseña para continuar.');
    expect(authService.login).not.toHaveBeenCalled();
  });

  it('valida el formato del correo antes de autenticar', () => {
    component.email = 'correo-invalido';
    component.password = 'Clave123!';

    component.ingresar();

    expect(component.alerta?.tipo).toBe('warning');
    expect(component.alerta?.mensaje).toBe('Ingresa un correo electrónico válido.');
    expect(authService.login).not.toHaveBeenCalled();
  });

  it('usa un mensaje unico para correo o contraseña incorrectos', () => {
    authService.login.mockReturnValue(
      throwError(() => ({
        status: 401,
        error: { detail: 'Credenciales incorrectas' },
      }))
    );
    component.email = 'persona@sakura.cl';
    component.password = 'ClaveIncorrecta123!';

    component.ingresar();

    expect(component.alerta?.tipo).toBe('danger');
    expect(component.alerta?.mensaje).toBe('Correo o contraseña incorrectos.');
    expect(component.cargando).toBe(false);
    expect(cdr.detectChanges).toHaveBeenCalled();
  });

  it('no muestra mensaje tecnico de servidor si el login agota tiempo', () => {
    authService.login.mockReturnValue(
      throwError(() => ({
        name: 'TimeoutError',
      }))
    );
    component.email = 'persona@sakura.cl';
    component.password = 'Clave123!';

    component.ingresar();

    expect(component.alerta?.tipo).toBe('danger');
    expect(component.alerta?.mensaje).toBe('No pudimos validar tus credenciales. Intenta nuevamente.');
    expect(component.cargando).toBe(false);
  });

  it('no reenvia el formulario si ya esta cargando', () => {
    component.cargando = true;
    component.email = 'persona@sakura.cl';
    component.password = 'Clave123!';

    component.ingresar();

    expect(authService.login).not.toHaveBeenCalled();
  });
});
