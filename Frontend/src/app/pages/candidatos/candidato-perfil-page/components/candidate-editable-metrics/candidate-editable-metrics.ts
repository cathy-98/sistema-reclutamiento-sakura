import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { take } from 'rxjs';
import { IconButton } from '../../../../../shared/components/icon-button/icon-button';
import { MatchScore } from '../../../../../shared/components/match-score/match-score';
import { CatalogosService } from '../../../../../services/catalogos.service';
import { CandidatoPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-editable-metrics',
  imports: [CommonModule, FormsModule, IconButton, MatchScore],
  templateUrl: './candidate-editable-metrics.html',
  styleUrl: './candidate-editable-metrics.scss',
})
export class CandidateEditableMetrics implements OnInit {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() matchClass = '';
  @Output() rentaSave = new EventEmitter<number>();
  @Output() disponibilidadSave = new EventEmitter<string>();
  public disponibilidades: string[] = ['Inmediata', '15 días', '30 días', 'A convenir'];
  editandoRenta = false;
  editandoDisponibilidad = false;
  rentaEdicion = 0;
  disponibilidadEdicion = '';
  errorRenta = '';
  errorDisponibilidad = '';

  constructor(private catalogosService: CatalogosService) {}

  ngOnInit() {
    this.cargarCatalogoDisponibilidades();
  }

  get rentaFormateada() {
    return `$${this.candidato.renta.toLocaleString('es-CL')} CLP líquidos`;
  }

  get rentaEdicionFormateada() {
    return `$${this.rentaEdicion.toLocaleString('es-CL')} CLP líquidos`;
  }

  iniciarEdicionRenta() {
    this.rentaEdicion = this.candidato.renta;
    this.errorRenta = '';
    this.editandoRenta = true;
  }

  cancelarEdicionRenta() {
    this.errorRenta = '';
    this.editandoRenta = false;
  }

  guardarRenta() {
    const renta = Number(this.rentaEdicion);

    if (!Number.isFinite(renta) || renta < 0) {
      this.errorRenta = 'La renta esperada debe ser un monto igual o mayor a cero.';
      return;
    }

    this.rentaSave.emit(Math.round(renta));
    this.errorRenta = '';
    this.editandoRenta = false;
  }

  iniciarEdicionDisponibilidad() {
    this.disponibilidadEdicion = this.candidato.disponibilidad;
    this.errorDisponibilidad = '';
    this.editandoDisponibilidad = true;
  }

  cancelarEdicionDisponibilidad() {
    this.errorDisponibilidad = '';
    this.editandoDisponibilidad = false;
  }

  guardarDisponibilidad() {
    const disponibilidad = this.disponibilidadEdicion.trim();

    if (!disponibilidad) {
      this.errorDisponibilidad = 'Selecciona una disponibilidad.';
      return;
    }

    this.disponibilidadSave.emit(disponibilidad);
    this.errorDisponibilidad = '';
    this.editandoDisponibilidad = false;
  }

  cargarCatalogoDisponibilidades() {
    // M3 catalogos: GET /catalogos/disponibilidades -> selector Disponibilidad del perfil.
    // Si el catalogo falla, CatalogosService devuelve [] y se mantienen las opciones locales.
    this.catalogosService
      .listarDisponibilidadesSeguro()
      .pipe(take(1))
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
