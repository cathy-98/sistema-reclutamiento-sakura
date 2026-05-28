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

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ingresar() {
    this.cargando = true;

    this.authService.login({
      email: this.email,
      password: this.password,
    }).subscribe({
      next: (respuesta) => {
        this.authService.guardarSesion(respuesta);
        this.cargando = false;
        this.router.navigate(['/dashboard']);
      },
      error: () => {
        this.cargando = false;
        alert('Correo o contraseña incorrectos');
      },
    });
  }
}
