import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService, PermisoUsuario, RolUsuario } from '../services/auth.service';

export const authGuard: CanActivateFn = (route) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // M1 Navegacion protegida: sin JWT vigente, cualquier ruta privada vuelve a /login.
  if (!authService.estaAutenticado()) {
    return router.createUrlTree(['/login']);
  }

  // M1 RBAC frontend: las rutas pueden declarar roles y/o permissions.
  // Si /auth/me ya cargo permisos, se usan como criterio principal; roles quedan como respaldo.
  const rolesPermitidos = route.data?.['roles'] as RolUsuario[] | undefined;
  const permisosPermitidos = route.data?.['permissions'] as PermisoUsuario[] | undefined;

  if (authService.puedeAcceder(rolesPermitidos, permisosPermitidos)) {
    return true;
  }

  // Integracion interna M3: candidatos autenticados no deben caer en dashboard interno.
  return router.createUrlTree([
    authService.obtenerPrincipalType() === 'candidato' ? '/portal-candidato' : '/dashboard',
  ]);
};
