import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
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
