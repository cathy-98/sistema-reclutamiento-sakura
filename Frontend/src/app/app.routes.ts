import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { authGuard } from './guards/auth.guard';
import { AppShell } from './layouts/app-shell/app-shell';
import { SolicitudesList } from './pages/solicitudes/solicitudes-list/solicitudes-list';
import { SolicitudForm } from './pages/solicitudes/solicitud-form/solicitud-form';

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
        component: Dashboard
      },
      {
        path: 'solicitudes',
        component: SolicitudesList
      },
      {
        path: 'solicitudes/nueva',
        component: SolicitudForm
      },
      {
        path: 'solicitudes/:id/editar',
        component: SolicitudForm
      }
    ]
  }
];
