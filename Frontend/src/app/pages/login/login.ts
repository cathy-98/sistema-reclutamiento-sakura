import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Alert } from '../../shared/components/alert/alert';
import { AuthService } from '../../services/auth.service';
import { obtenerMensajeError } from '../../shared/utils/api-error';

@Component({
  selector: 'app-login',
  imports: [FormsModule, Alert],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  email = '';
  password = '';
  cargando = false;
  error = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ingresar() {
    const email = this.email.trim();
    const password = this.password.trim();

    if (!email || !password) {
      this.error = 'Ingresa correo y contraseña para continuar';
      return;
    }

    this.cargando = true;
    this.error = '';

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
        this.error = obtenerMensajeError(error, 'Correo o contraseña incorrectos');
      },
    });
  }
}
