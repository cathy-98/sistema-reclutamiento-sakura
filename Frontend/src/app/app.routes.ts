import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Dashboard } from './pages/dashboard/dashboard';
import { authGuard } from './guards/auth.guard';
import { AppShell } from './layouts/app-shell/app-shell';
import { CandidatosList } from './pages/candidatos/candidatos-list/candidatos-list';
import { SolicitudesList } from './pages/Solicitudes/solicitudes-list/solicitudes-list';
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
        path: 'candidatos',
        component: CandidatosList
      },
      {
  path: 'solicitudes',
  component: SolicitudesList
},
    ]
  }
];
