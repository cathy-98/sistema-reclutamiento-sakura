import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

interface MenuItem {
  label: string;
  route: string;
  icon: string;
}

@Component({
  selector: 'app-shell',
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app-shell.html',
  styleUrl: './app-shell.scss',
})
export class AppShell {
  menuAbierto = true;

  menuItems: MenuItem[] = [
    { label: 'Bienvenida', route: '/dashboard', icon: 'home' },
    { label: 'Gestion de solicitudes', route: '/admin/solicitudes', icon: 'requests' },
    { label: 'Informes', route: '/informes', icon: 'reports' },
    { label: 'Creacion de test', route: '/tests', icon: 'tools' },
    { label: 'Candidatos', route: '/candidatos', icon: 'users' },
    { label: 'Gestion de entrevistas', route: '/entrevistas', icon: 'calendar' },
  ];

  alternarMenu() {
    this.menuAbierto = !this.menuAbierto;
  }

  abrirMenuSiEstaCerrado() {
    if (!this.menuAbierto) {
      this.menuAbierto = true;
    }
  }
}
