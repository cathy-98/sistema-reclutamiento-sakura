import { CommonModule } from '@angular/common';
import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../button/button';
import {
  SolicitudAutocompleteOption,
  buscarSolicitudesReales,
} from '../../utils/solicitud-autocomplete';

@Component({
  selector: 'app-filter-panel',
  imports: [
    CommonModule,
    FormsModule,
    Button,
  ],
  templateUrl: './filter-panel.html',
  styleUrl: './filter-panel.scss',
})
export class FilterPanel {
  @Input() title = 'Buscar y filtrar';
  @Input() description = '';

  /**
   * Búsqueda rápida
   *
   * Se mantiene siempre independiente de los filtros avanzados
   * para priorizar la búsqueda directa en listados extensos.
   */
  @Input() quickSearch = '';
  @Input() quickSearchLabel = 'Búsqueda rápida';
  @Input() quickSearchPlaceholder = 'Buscar';
  @Input() showQuickSearch = true;
  @Input() quickSearchSolicitudes: SolicitudAutocompleteOption[] = [];

  /**
   * Mejora UX/UI - panel de filtros colapsable
   *
   * Por defecto permanece desactivado para mantener
   * compatibilidad con los módulos que ya utilizan
   * este componente.
   *
   * M3 puede habilitarlo mediante:
   *
   * [collapsible]="true"
   * [filtersExpanded]="false"
   */
  @Input() collapsible = false;

  /**
   * Define si los filtros específicos están visibles.
   *
   * Si collapsible = false, el contenido se muestra
   * siempre aunque filtersExpanded sea false.
   */
  @Input() filtersExpanded = true;

  @Input() filtersButtonLabel = 'Filtros';

  @Output() quickSearchChange =
    new EventEmitter<string>();
  @Output() quickSearchSolicitudSelected =
    new EventEmitter<SolicitudAutocompleteOption>();

  @Output() search =
    new EventEmitter<void>();

  @Output() clear =
    new EventEmitter<void>();

  /**
   * Permite que un componente padre conozca
   * si el panel de filtros avanzados fue abierto/cerrado.
   */
  @Output() filtersExpandedChange =
    new EventEmitter<boolean>();

  readonly panelId =
    `filter-panel-${Math.random().toString(36).slice(2)}`;
  quickSearchSuggestionsOpen = false;
  quickSearchActiveSuggestion = 0;

  get titleId() {
    return `${this.panelId}-title`;
  }

  get filtersId() {
    return `${this.panelId}-filters`;
  }

  /**
   * UX/UI
   *
   * La búsqueda rápida filtra inmediatamente mientras
   * el usuario escribe, manteniendo el comportamiento
   * actual del componente.
   */
  updateQuickSearch(value: string) {
    this.quickSearch = value;
    this.quickSearchSuggestionsOpen = Boolean(
      value.trim() && this.quickSearchSolicitudes.length > 0,
    );
    this.quickSearchActiveSuggestion = 0;
    this.quickSearchChange.emit(value);
    this.search.emit();
  }

  get quickSearchSolicitudOptions() {
    return buscarSolicitudesReales(
      this.quickSearchSolicitudes,
      this.quickSearch,
    );
  }

  get showQuickSearchSolicitudOptions() {
    return (
      this.quickSearchSuggestionsOpen &&
      this.quickSearchSolicitudOptions.length > 0
    );
  }

  get showQuickSearchSolicitudEmpty() {
    return (
      this.quickSearchSuggestionsOpen &&
      this.quickSearch.trim().length > 0 &&
      this.quickSearchSolicitudOptions.length === 0
    );
  }

  focusQuickSearch() {
    this.quickSearchSuggestionsOpen = Boolean(
      this.quickSearch.trim() &&
      this.quickSearchSolicitudes.length > 0,
    );
  }

  selectQuickSearchSolicitud(solicitud: SolicitudAutocompleteOption) {
    const codigo = solicitud.codigo?.trim() ?? '';

    if (!codigo) {
      return;
    }

    this.quickSearch = codigo;
    this.quickSearchSuggestionsOpen = false;
    this.quickSearchChange.emit(codigo);
    this.quickSearchSolicitudSelected.emit(solicitud);
    this.search.emit();
  }

  handleQuickSearchKeydown(event: KeyboardEvent) {
    if (
      !this.quickSearchSuggestionsOpen &&
      ['ArrowDown', 'ArrowUp'].includes(event.key)
    ) {
      this.quickSearchSuggestionsOpen =
        this.quickSearchSolicitudOptions.length > 0;
    }

    if (!this.quickSearchSuggestionsOpen) {
      return;
    }

    if (event.key === 'ArrowDown') {
      event.preventDefault();
      this.quickSearchActiveSuggestion = Math.min(
        this.quickSearchActiveSuggestion + 1,
        this.quickSearchSolicitudOptions.length - 1,
      );
    }

    if (event.key === 'ArrowUp') {
      event.preventDefault();
      this.quickSearchActiveSuggestion = Math.max(
        this.quickSearchActiveSuggestion - 1,
        0,
      );
    }

    if (
      event.key === 'Enter' &&
      this.quickSearchSolicitudOptions[this.quickSearchActiveSuggestion]
    ) {
      event.preventDefault();
      this.selectQuickSearchSolicitud(
        this.quickSearchSolicitudOptions[this.quickSearchActiveSuggestion],
      );
    }

    if (event.key === 'Escape') {
      this.quickSearchSuggestionsOpen = false;
    }
  }

  /**
   * UX/UI
   *
   * Muestra u oculta únicamente los filtros específicos.
   * La búsqueda rápida permanece siempre disponible.
   */
  toggleFilters() {
    if (!this.collapsible) {
      return;
    }

    this.filtersExpanded =
      !this.filtersExpanded;

    this.filtersExpandedChange.emit(
      this.filtersExpanded,
    );
  }

  /**
   * Determina si el contenido avanzado debe verse.
   *
   * Cuando collapsible está desactivado se conserva
   * el comportamiento histórico del componente.
   */
  get showFilters() {
    return (
      !this.collapsible ||
      this.filtersExpanded
    );
  }

  @HostListener('document:click')
  closeQuickSearchSuggestions() {
    this.quickSearchSuggestionsOpen = false;
  }
}
