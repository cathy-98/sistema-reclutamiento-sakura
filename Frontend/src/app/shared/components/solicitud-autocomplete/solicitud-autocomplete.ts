import { CommonModule } from '@angular/common';
import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import {
  SolicitudAutocompleteOption,
  buscarSolicitudesReales,
  etiquetaSolicitud,
} from '../../utils/solicitud-autocomplete';

@Component({
  selector: 'app-solicitud-autocomplete',
  imports: [CommonModule, FormsModule],
  templateUrl: './solicitud-autocomplete.html',
  styleUrl: './solicitud-autocomplete.scss',
})
export class SolicitudAutocomplete {
  @Input() id = '';
  @Input() name = '';
  @Input() value = '';
  @Input() placeholder = 'Ej. SOL-000001';
  @Input() disabled = false;
  @Input() required = false;
  @Input() solicitudes: SolicitudAutocompleteOption[] = [];
  @Input() selectedId: string | number | null = null;
  @Input() noResultsMessage = 'No se encontraron solicitudes.';

  @Output() valueChange = new EventEmitter<string>();
  @Output() selected = new EventEmitter<SolicitudAutocompleteOption | null>();

  abierto = false;
  opcionActiva = 0;
  fueEditado = false;
  readonly fallbackInputId = `solicitud-autocomplete-${Math.random().toString(36).slice(2)}`;

  get inputId() {
    return this.id || this.fallbackInputId;
  }

  get opciones() {
    return buscarSolicitudesReales(this.solicitudes, this.value);
  }

  get mostrarSinResultados() {
    return this.abierto && this.value.trim().length > 0 && this.opciones.length === 0;
  }

  get mostrarOpciones() {
    return this.abierto && this.opciones.length > 0;
  }

  etiqueta(solicitud: SolicitudAutocompleteOption) {
    return etiquetaSolicitud(solicitud) || solicitud.codigo || `Solicitud ${solicitud.id}`;
  }

  estaSeleccionada(solicitud: SolicitudAutocompleteOption) {
    return (
      this.selectedId != null &&
      (
        String(this.selectedId) === String(solicitud.id) ||
        String(this.selectedId) === String(solicitud.codigo)
      )
    );
  }

  actualizar(valor: string) {
    this.value = valor;
    this.fueEditado = true;
    this.abierto = Boolean(valor.trim());
    this.opcionActiva = 0;
    this.valueChange.emit(valor);

    if (!valor.trim()) {
      this.selected.emit(null);
    }
  }

  enfocar() {
    this.abierto = Boolean(this.value.trim());
  }

  seleccionar(solicitud: SolicitudAutocompleteOption) {
    this.value = solicitud.codigo?.trim() ?? '';
    this.abierto = false;
    this.fueEditado = false;
    this.valueChange.emit(this.value);
    this.selected.emit(solicitud);
  }

  manejarTecla(evento: KeyboardEvent) {
    if (!this.abierto && ['ArrowDown', 'ArrowUp'].includes(evento.key)) {
      this.abierto = this.opciones.length > 0;
    }

    if (!this.abierto) {
      return;
    }

    if (evento.key === 'ArrowDown') {
      evento.preventDefault();
      this.opcionActiva = Math.min(this.opcionActiva + 1, this.opciones.length - 1);
    }

    if (evento.key === 'ArrowUp') {
      evento.preventDefault();
      this.opcionActiva = Math.max(this.opcionActiva - 1, 0);
    }

    if (evento.key === 'Enter' && this.opciones[this.opcionActiva]) {
      evento.preventDefault();
      this.seleccionar(this.opciones[this.opcionActiva]);
    }

    if (evento.key === 'Escape') {
      this.abierto = false;
    }
  }

  @HostListener('document:click')
  cerrar() {
    this.abierto = false;
  }
}
