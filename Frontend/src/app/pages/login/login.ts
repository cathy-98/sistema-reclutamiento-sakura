import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  email = '';
  password = '';

  constructor(
    private http: HttpClient,
    private router: Router
  ) {}

  ingresar() {
    this.http.post('http://localhost:8000/api/auth/login', {
      email: this.email,
      password: this.password,
    }).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: () => {
        alert('Correo o contraseña incorrectos');
      },
    });
  }
}
