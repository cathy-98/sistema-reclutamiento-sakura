import { ChangeDetectorRef, Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';
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
  private readonly mensajeCredencialesInvalidas = 'Correo o contraseña incorrectos.';

  email = '';
  password = '';
  cargando = false;
  alerta: AlertaUi | null = null;

  constructor(
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ingresar() {
    if (this.cargando) {
      return;
    }

    const email = this.email.trim();
    const password = this.password.trim();

    if (!email && !password) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Ingresa correo y contraseña para continuar.',
      };
      return;
    }

    if (!email) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Ingresa tu correo electrónico.',
      };
      return;
    }

    if (!this.esCorreoValido(email)) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Ingresa un correo electrónico válido.',
      };
      return;
    }

    if (!password) {
      this.alerta = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Ingresa tu contraseña.',
      };
      return;
    }

    this.cargando = true;
    this.alerta = null;

    this.authService.login({
      email,
      password,
    }).pipe(
      finalize(() => {
        this.cargando = false;
        this.cdr.detectChanges();
      })
    ).subscribe({
      next: (respuesta) => {
        // Integracion interna M3: principal_type=candidato entra al autoservicio /portal-candidato.
        const destino = respuesta.principal_type === 'candidato' ? '/portal-candidato' : '/dashboard';
        this.router.navigate([destino]);
      },
      error: (error) => {
        this.alerta = {
          tipo: 'danger',
          variante: 'soft',
          mensaje: this.obtenerMensajeLogin(error),
        };
      },
    });
  }

  cerrarAlerta() {
    this.alerta = null;
  }

  private esCorreoValido(email: string) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  private obtenerMensajeLogin(error: unknown) {
    if (typeof error === 'object' && error && 'status' in error && Number(error.status) === 401) {
      return this.mensajeCredencialesInvalidas;
    }

    if (typeof error === 'object' && error && 'name' in error && error.name === 'TimeoutError') {
      return 'No pudimos validar tus credenciales. Intenta nuevamente.';
    }

    return obtenerMensajeError(error, this.mensajeCredencialesInvalidas);
  }
}
