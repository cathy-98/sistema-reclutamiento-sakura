import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../button/button';

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
    this.quickSearchChange.emit(value);
    this.search.emit();
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
}
