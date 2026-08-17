import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService, RolUsuario } from '../services/auth.service';

export const authGuard: CanActivateFn = (route) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.estaAutenticado()) {
    return router.createUrlTree(['/login']);
  }

  const rolesPermitidos = route.data?.['roles'] as RolUsuario[] | undefined;

  if (!rolesPermitidos?.length || authService.tieneRol(rolesPermitidos)) {
    return true;
  }

  // Integracion interna M3: candidatos autenticados no deben caer en dashboard interno.
  return router.createUrlTree([
    authService.obtenerPrincipalType() === 'candidato' ? '/portal-candidato' : '/dashboard',
  ]);
};
