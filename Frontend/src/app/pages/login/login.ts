import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
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
    this.cargando = true;
    this.error = '';

    this.authService.login({
      email: this.email,
      password: this.password,
    }).subscribe({
      next: () => {
        this.cargando = false;
        this.router.navigate(['/dashboard']);
      },
      error: () => {
        this.cargando = false;
        this.error = 'Correo o contraseña incorrectos';
      },
    });
  }
}
