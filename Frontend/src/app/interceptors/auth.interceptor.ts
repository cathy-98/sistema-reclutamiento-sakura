import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const token = authService.obtenerToken();
  // M1 Integracion JWT: todo endpoint backend bajo /api recibe Authorization: Bearer <access_token>.
  // Esto cubre /auth/me, /auth/change-password, /usuarios/* y el resto de modulos protegidos.
  const esApiBackend = req.url.startsWith('/api') || req.url.startsWith('http://localhost:8000');
  const esLogin = req.url.includes('/auth/login');

  if (!token || !esApiBackend) {
    return next(req).pipe(
      catchError((error) => {
        // M1 Sesion expirada/invalida: ante 401 en API protegida se limpia sesion y vuelve a login.
        // /auth/login queda excluido para que la pantalla muestre "credenciales incorrectas".
        if (error instanceof HttpErrorResponse && error.status === 401 && !esLogin) {
          authService.eliminarToken();
          router.navigate(['/login']);
        }

        return throwError(() => error);
      })
    );
  }

  const requestConToken = req.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`,
    },
  });

  return next(requestConToken).pipe(
    catchError((error) => {
      // M1 Autoridad backend: 403 se propaga para que la pantalla muestre "sin permiso";
      // 401 invalida la sesion local porque el token ya no sirve o expiro.
      if (error instanceof HttpErrorResponse && error.status === 401 && !esLogin) {
        authService.eliminarToken();
        router.navigate(['/login']);
      }

      return throwError(() => error);
    })
  );
};
