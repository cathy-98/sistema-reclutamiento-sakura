import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { PageHeader } from '../../shared/components/page-header/page-header';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule, PageHeader],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  usuario = 'usuario';
  rol = '';

  constructor(private authService: AuthService) {
    this.actualizarDatosSesion();

    this.authService.cargarPerfilUsuario().subscribe(() => {
      this.actualizarDatosSesion();
    });
  }

  private actualizarDatosSesion() {
    this.usuario = this.authService.obtenerNombreVisible();
    this.rol = this.authService.obtenerRolVisible();
  }
}
