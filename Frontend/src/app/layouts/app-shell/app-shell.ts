import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

interface MenuItem {
  label: string;
  route?: string;
  icon: string;
  children?: SubMenuItem[];
}

interface SubMenuItem {
  label: string;
  route?: string;
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

  menuItems: MenuItem[] = [
    {
      label: 'Inicio',
      icon: 'home',
      route: '/dashboard',
    },
    {
      label: 'Gestion de cuestionarios',
      icon: 'questionnaire',
      children: [
        { label: 'Creacion de test' },
      ],
    },
    {
      label: 'Gestion de solicitudes',
      icon: 'requests',
      children: [
        { label: 'Listado de solicitudes', route: '/solicitudes' },
      ],
    },
    {
      label: 'Candidatos',
      icon: 'users',
      route: '/candidatos',
    },
    {
      label: 'Gestion de entrevistas',
      icon: 'calendar',
    },
  ];

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
}
