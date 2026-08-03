import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../button/button';

@Component({
  selector: 'app-filter-panel',
  imports: [CommonModule, FormsModule, Button],
  templateUrl: './filter-panel.html',
  styleUrl: './filter-panel.scss',
})
export class FilterPanel {
  @Input() title = 'Buscar y filtrar';
  @Input() description = '';
  @Input() quickSearch = '';
  @Input() quickSearchLabel = 'Búsqueda rápida';
  @Input() quickSearchPlaceholder = 'Buscar';
  @Input() showQuickSearch = true;

  @Output() quickSearchChange = new EventEmitter<string>();
  @Output() search = new EventEmitter<void>();
  @Output() clear = new EventEmitter<void>();

  readonly panelId = `filter-panel-${Math.random().toString(36).slice(2)}`;

  get titleId() {
    return `${this.panelId}-title`;
  }

  updateQuickSearch(value: string) {
    this.quickSearch = value;
    this.quickSearchChange.emit(value);
    this.search.emit();
  }
}
