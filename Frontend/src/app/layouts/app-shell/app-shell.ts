import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { AuthService, PermisoUsuario, RolUsuario } from '../../services/auth.service';

interface MenuItem {
  label: string;
  route?: string;
  queryParams?: Record<string, string>;
  icon: string;
  roles?: RolUsuario[];
  permissions?: PermisoUsuario[];
  children?: SubMenuItem[];
}

interface SubMenuItem {
  label: string;
  route?: string;
  queryParams?: Record<string, string>;
  roles?: RolUsuario[];
  permissions?: PermisoUsuario[];
}

@Component({
  selector: 'app-shell',
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app-shell.html',
  styleUrl: './app-shell.scss',
})
export class AppShell {
  menuAbierto = true;
  submenuAbierto: string | null = null;
  menuItemsVisibles: MenuItem[] = [];

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.actualizarMenuItemsVisibles();
    this.abrirSubmenuActivo();

    this.router.events
      .pipe(filter((event): event is NavigationEnd => event instanceof NavigationEnd))
      .subscribe(() => {
        this.actualizarMenuItemsVisibles();
        this.abrirSubmenuActivo();
      });
  }

  menuItems: MenuItem[] = [
    // M1 RBAC visual: este menu no llama endpoints; consume permisos guardados desde GET /auth/me.
    // Backend valida de nuevo cada accion, por eso ocultar aqui es solo una ayuda de UX.
    {
      label: 'Inicio',
      icon: 'home',
      route: '/dashboard',
      roles: ['Administrador', 'Reclutador', 'Entrevistador'],
    },
    {
      label: 'Mi portal',
      icon: 'users',
      route: '/portal-candidato',
      roles: ['Candidato'],
    },
    {
      label: 'Gestion de cuestionarios',
      icon: 'questionnaire',
      roles: ['Administrador', 'Reclutador'],
      permissions: ['CUEST_VIEW'],
      children: [
        { label: 'Banco de preguntas', route: '/cuestionarios/banco', roles: ['Administrador', 'Reclutador'], permissions: ['CUEST_VIEW'] },
        { label: 'Armar y enviar cuestionario', route: '/cuestionarios/test', roles: ['Administrador', 'Reclutador'], permissions: ['CUEST_CREATE'] },
        { label: 'Asignaciones', route: '/cuestionarios/asignaciones', roles: ['Administrador', 'Reclutador'], permissions: ['CUEST_VIEW'] },
      ],
    },
    {
      label: 'Gestion de solicitudes',
      icon: 'requests',
      roles: ['Administrador', 'Reclutador'],
      permissions: ['SOL_VIEW'],
      children: [
        { label: 'Listado de solicitudes', route: '/solicitudes', roles: ['Administrador', 'Reclutador'], permissions: ['SOL_VIEW'] },
      ],
    },
    {
      label: 'Gestión de candidatos',
      icon: 'users',
      roles: ['Administrador', 'Reclutador'],
      permissions: ['CAN_VIEW'],
      children: [
        { label: 'Listado de candidatos', route: '/candidatos', queryParams: { vista: 'listado' }, roles: ['Administrador', 'Reclutador'], permissions: ['CAN_VIEW'] },
        { label: 'Carga de candidatos', route: '/candidatos', queryParams: { vista: 'carga' }, roles: ['Administrador', 'Reclutador'], permissions: ['CAN_VIEW'] },
      ],
    },
    {
      label: 'Gestion de entrevistas',
      icon: 'calendar',
      roles: ['Administrador', 'Reclutador', 'Entrevistador'],
      permissions: ['INT_VIEW'],
      children: [
        { label: 'Listado de entrevistas', route: '/entrevistas', roles: ['Administrador', 'Reclutador', 'Entrevistador'], permissions: ['INT_VIEW'] },
        { label: 'Agenda de entrevistas', route: '/agenda-entrevistas', roles: ['Administrador', 'Reclutador', 'Entrevistador'], permissions: ['INT_VIEW'] },
      ],
    },
    {
      label: 'Informes al Cliente',
      icon: 'requests',
      route: '/informes-cliente',
      roles: ['Administrador', 'Reclutador'],
      permissions: ['REP_VIEW'],
    },

  ];

  actualizarMenuItemsVisibles() {
    this.menuItemsVisibles = this.menuItems
      .filter((item) => this.puedeVerItem(item.roles, item.permissions))
      .map((item) => ({
        ...item,
        children: item.children?.filter((child) => this.puedeVerItem(child.roles, child.permissions)),
      }));
  }

  trackMenuItem(_index: number, item: MenuItem) {
    return item.route ?? item.label;
  }

  trackSubMenuItem(_index: number, item: SubMenuItem) {
    return `${item.route ?? item.label}:${JSON.stringify(item.queryParams ?? {})}`;
  }

  alternarMenu() {
    this.menuAbierto = !this.menuAbierto;
  }

  abrirMenuSiEstaCerrado() {
    if (!this.menuAbierto) {
      this.menuAbierto = true;
    }
  }

  alternarSubmenu(item: MenuItem) {
    if (!item.children?.length) {
      return;
    }

    this.abrirMenuSiEstaCerrado();
    this.submenuAbierto = this.submenuAbierto === item.label ? null : item.label;
  }

  estaSubmenuAbierto(item: MenuItem) {
    return this.submenuAbierto === item.label;
  }

  estaItemActivo(item: MenuItem) {
    if (item.route) {
      return this.router.isActive(item.route, {
        paths: item.route === '/dashboard' ? 'exact' : 'subset',
        queryParams: 'ignored',
        fragment: 'ignored',
        matrixParams: 'ignored',
      });
    }

    return item.children?.some((child) => child.route && this.router.isActive(child.route, {
      paths: 'subset',
      queryParams: 'ignored',
      fragment: 'ignored',
      matrixParams: 'ignored',
    })) ?? false;
  }

  estaSubMenuItemActivo(item: SubMenuItem) {
    if (!item.route) {
      return false;
    }

    const queryParams = item.queryParams ?? {};

    // Distingue las vistas Listado/Carga aunque ambas reutilicen /candidatos.
    if (!this.router.isActive(item.route, {
      paths: 'exact',
      queryParams: Object.keys(queryParams).length > 0 ? 'subset' : 'ignored',
      fragment: 'ignored',
      matrixParams: 'ignored',
    })) {
      return false;
    }

    const actuales = this.router.routerState.snapshot.root.queryParams;

    return Object.entries(queryParams).every(([key, value]) => actuales[key] === value);
  }

  cerrarSesion() {
    this.authService.eliminarToken();
    this.router.navigate(['/login']);
  }

  private puedeVerItem(roles?: RolUsuario[], permissions?: PermisoUsuario[]) {
    return this.authService.puedeAcceder(roles, permissions);
  }

  private abrirSubmenuActivo() {
    const itemActivo = this.menuItemsVisibles.find((item) => item.children?.some((child) => (
      child.route && this.router.isActive(child.route, {
        paths: 'subset',
        queryParams: 'ignored',
        fragment: 'ignored',
        matrixParams: 'ignored',
      })
    )));

    if (itemActivo) {
      this.submenuAbierto = itemActivo.label;
    }
  }
}
