import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { authGuard } from './guards/auth.guard';
import { AppShell } from './layouts/app-shell/app-shell';
import { CandidatosList } from './pages/candidatos/candidatos-list/candidatos-list';
import { SolicitudesList } from './pages/solicitudes/solicitudes-list/solicitudes-list';
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
        path: 'candidatos',
        component: CandidatosList,
        data: { roles: ['Administrador', 'Reclutador'] }
      },
      {
        path: 'solicitudes',
        component: SolicitudesList,
        data: { roles: ['Administrador', 'Reclutador'] }
      },
    ]
  }
];
