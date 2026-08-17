import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { AuthService, RolUsuario } from '../../services/auth.service';

interface MenuItem {
  label: string;
  route?: string;
  icon: string;
  roles?: RolUsuario[];
  children?: SubMenuItem[];
}

interface SubMenuItem {
  label: string;
  route?: string;
  roles?: RolUsuario[];
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
      children: [
        { label: 'Banco de preguntas', route: '/cuestionarios/banco', roles: ['Administrador', 'Reclutador'] },
        { label: 'Armar y enviar test', route: '/cuestionarios/test', roles: ['Administrador', 'Reclutador'] },
      ],
    },
    {
      label: 'Gestion de solicitudes',
      icon: 'requests',
      roles: ['Administrador', 'Reclutador'],
      children: [
        { label: 'Listado de solicitudes', route: '/solicitudes', roles: ['Administrador', 'Reclutador'] },
      ],
    },
    {
      label: 'Candidatos',
      icon: 'users',
      route: '/candidatos',
      roles: ['Administrador', 'Reclutador'],
    },
    {
      label: 'Gestion de entrevistas',
      icon: 'calendar',
      roles: ['Administrador', 'Reclutador', 'Entrevistador'],
      children: [
        { label: 'Listado de entrevistas', route: '/entrevistas', roles: ['Administrador', 'Reclutador', 'Entrevistador'] },
        { label: 'Agenda de entrevistas', route: '/agenda-entrevistas', roles: ['Administrador', 'Reclutador', 'Entrevistador'] },
      ],
    },
    {
      label: 'Informes al Cliente',
      icon: 'requests',
      route: '/informes-cliente',
      roles: ['Administrador', 'Reclutador'],
    },

  ];

  actualizarMenuItemsVisibles() {
    this.menuItemsVisibles = this.menuItems
      .filter((item) => this.puedeVerItem(item.roles))
      .map((item) => ({
        ...item,
        children: item.children?.filter((child) => this.puedeVerItem(child.roles)),
      }));
  }

  trackMenuItem(_index: number, item: MenuItem) {
    return item.route ?? item.label;
  }

  trackSubMenuItem(_index: number, item: SubMenuItem) {
    return item.route ?? item.label;
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

  cerrarSesion() {
    this.authService.eliminarToken();
    this.router.navigate(['/login']);
  }

  private puedeVerItem(roles?: RolUsuario[]) {
    return !roles?.length || this.authService.tieneRol(roles);
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
