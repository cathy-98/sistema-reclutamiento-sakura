import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

interface Tecnologia {
  nombre: string;
  nivel: 'Junior' | 'Semi Senior' | 'Senior';
  experiencia: string;
}

@Component({
  selector: 'app-solicitud-form',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './solicitud-form.html',
  styleUrl: './solicitud-form.scss',
})
export class SolicitudForm {
  idSolicitud = 'REQ-021';
  esEdicion = false;
  cantidadVacantes = 4;
  observaciones = '';
  tecnologias: Tecnologia[] = [
    { nombre: 'JavaScript', nivel: 'Junior', experiencia: '2 años' },
    { nombre: 'React', nivel: 'Junior', experiencia: '2 años' },
    { nombre: 'Node.js', nivel: 'Semi Senior', experiencia: '3 años' },
  ];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
  ) {
    const id = this.route.snapshot.paramMap.get('id');
    this.esEdicion = id !== null;
    this.idSolicitud = id?.replace('Req-', 'REQ-') ?? 'REQ-021';
  }

  cambiarVacantes(cambio: number) {
    this.cantidadVacantes = Math.max(1, this.cantidadVacantes + cambio);
  }

  agregarTecnologia() {
    this.tecnologias = [
      ...this.tecnologias,
      { nombre: 'Nueva tecnología', nivel: 'Junior', experiencia: '1 año' },
    ];
  }

  eliminarTecnologia(index: number) {
    this.tecnologias = this.tecnologias.filter((_tecnologia, i) => i !== index);
  }

  guardar() {
    void this.router.navigate(['/solicitudes']);
  }

  trackTecnologia(index: number) {
    return index;
  }
}
