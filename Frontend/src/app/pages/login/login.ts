import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AlertRegion } from '../../shared/components/alert-region/alert-region';
import { AuthService } from '../../services/auth.service';
import { AlertaUi } from '../../shared/models/alerta-ui.model';
import { obtenerMensajeError } from '../../shared/utils/api-error';

@Component({
  selector: 'app-login',
  imports: [FormsModule, AlertRegion],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  email = '';
  password = '';
  cargando = false;
  alerta: AlertaUi | null = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ingresar() {
    const email = this.email.trim();
    const password = this.password.trim();

    if (!email || !password) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Ingresa correo y contraseña para continuar',
      };
      return;
    }

    this.cargando = true;
    this.alerta = null;

    this.authService.login({
      email,
      password,
    }).subscribe({
      next: () => {
        this.cargando = false;
        this.router.navigate(['/dashboard']);
      },
      error: (error) => {
        this.cargando = false;
        this.alerta = {
          tipo: 'danger',
          variante: 'soft',
          mensaje: obtenerMensajeError(error, 'Correo o contraseña incorrectos'),
        };
      },
    });
  }

  cerrarAlerta() {
    this.alerta = null;
  }
}
