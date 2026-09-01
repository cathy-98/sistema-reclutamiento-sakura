import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { IconButton } from '../../../../../shared/components/icon-button/icon-button';
import { CandidatoPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-contact-line',
  imports: [CommonModule, FormsModule, IconButton],
  templateUrl: './candidate-contact-line.html',
  styleUrl: './candidate-contact-line.scss',
})
export class CandidateContactLine {
  @Input({ required: true }) candidato!: CandidatoPerfil;
  @Input() saving = false;
  @Input() error = '';
  @Output() saveContact = new EventEmitter<{ correo: string; telefono: string }>();

  editandoInformacion = false;
  correoEdicion = '';
  telefonoEdicion = '';
  errorLocal = '';

  iniciarEdicion() {
    this.correoEdicion = this.candidato.correo === 'Sin correo'
      ? ''
      : this.candidato.correo;
    this.telefonoEdicion = this.candidato.telefono === 'Sin teléfono'
      ? ''
      : this.candidato.telefono;
    this.errorLocal = '';
    this.editandoInformacion = true;
  }

  cancelarEdicion() {
    this.errorLocal = '';
    this.editandoInformacion = false;
  }

  guardarInformacion() {
    const correo = this.correoEdicion.trim();
    const telefono = this.telefonoEdicion.trim();

    if (!this.correoValido(correo)) {
      this.errorLocal = 'Ingresa un correo electrónico válido.';
      return;
    }

    this.errorLocal = '';
    this.saveContact.emit({ correo, telefono });
    this.editandoInformacion = false;
  }

  private correoValido(correo: string) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo);
  }
}
