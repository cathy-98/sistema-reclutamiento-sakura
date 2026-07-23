import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
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

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  menuItems: MenuItem[] = [
    {
      label: 'Inicio',
      icon: 'home',
      route: '/dashboard',
      roles: ['Administrador', 'Reclutador', 'Entrevistador'],
    },
    {
      label: 'Gestion de cuestionarios',
      icon: 'questionnaire',
      roles: ['Administrador', 'Reclutador'],
      children: [
        { label: 'Creacion de test', roles: ['Administrador', 'Reclutador'] },
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
      roles: ['Administrador', 'Entrevistador'],
    },
  ];

  get menuItemsVisibles() {
    return this.menuItems
      .filter((item) => this.puedeVerItem(item.roles))
      .map((item) => ({
        ...item,
        children: item.children?.filter((child) => this.puedeVerItem(child.roles)),
      }));
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

  cerrarSesion() {
    this.authService.eliminarToken();
    this.router.navigate(['/login']);
  }

  private puedeVerItem(roles?: RolUsuario[]) {
    return !roles?.length || this.authService.tieneRol(roles);
  }
}
