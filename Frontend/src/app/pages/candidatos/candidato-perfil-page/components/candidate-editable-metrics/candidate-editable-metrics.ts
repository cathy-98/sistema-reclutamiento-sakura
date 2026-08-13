import { CommonModule } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { catchError, of, take, timeout } from 'rxjs';
import { MatchScore } from '../../../../../shared/components/match-score/match-score';
import { CatalogosService } from '../../../../../services/catalogos.service';
import { CandidatoPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-editable-metrics',
  imports: [CommonModule, FormsModule, MatchScore],
  templateUrl: './candidate-editable-metrics.html',
  styleUrl: './candidate-editable-metrics.scss',
})
export class CandidateEditableMetrics implements OnInit {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() matchClass = '';
  public disponibilidades: string[] = ['Inmediata', '15 días', '30 días', 'A convenir'];

  constructor(private catalogosService: CatalogosService) {}

  ngOnInit() {
    this.cargarCatalogoDisponibilidades();
  }

  get rentaFormateada() {
    return `$${this.candidato.renta.toLocaleString('es-CL')} CLP líquidos`;
  }

  get rentaInput() {
    return this.candidato.renta;
  }

  set rentaInput(value: number) {
    this.candidato.renta = Number(value) || 0;
  }

  cargarCatalogoDisponibilidades() {
    // Integración catálogo de disponibilidades -> selector "Disponibilidad" del perfil candidato.
    this.catalogosService
      .listarDisponibilidades()
      .pipe(timeout(4000), catchError(() => of([])), take(1))
      .subscribe((disponibilidades) => {
        const opciones = disponibilidades
          .map((disponibilidad) => disponibilidad.disp_nombre)
          .filter((nombre): nombre is string => Boolean(nombre));

        if (opciones.length > 0) {
          this.disponibilidades = opciones;
        }
      });
  }
}
