import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { authGuard } from './guards/auth.guard';
import { AppShell } from './layouts/app-shell/app-shell';
export const routes: Routes = [
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  },
  {
    path: 'login',
    component: Login
  },
  {
    path: '',
    component: AppShell,
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        component: Dashboard,
        data: { roles: ['Administrador', 'Reclutador', 'Entrevistador'] }
      },
      {
        path: 'candidatos/perfil/:id',
        loadComponent: () =>
          import('./pages/candidatos/candidato-perfil-page/candidato-perfil-page').then((m) => m.CandidatoPerfilPage),
        data: { roles: ['Administrador', 'Reclutador'] }
      },
      {
        path: 'candidatos',
        loadComponent: () =>
          import('./pages/candidatos/candidatos-list/candidatos-list').then((m) => m.CandidatosList),
        data: { roles: ['Administrador', 'Reclutador'] }
      },
      {
        path: 'solicitudes',
        loadComponent: () =>
          import('./pages/solicitudes/solicitudes-list/solicitudes-list').then((m) => m.SolicitudesList),
        data: { roles: ['Administrador', 'Reclutador'] }
      },
      {
        path: 'entrevistas',
        loadComponent: () =>
          import('./pages/entrevistas/entrevistas-list/entrevistas-list').then((m) => m.EntrevistasList),
        data: { roles: ['Administrador', 'Reclutador', 'Entrevistador'] }
      },
    ]
  }
];
