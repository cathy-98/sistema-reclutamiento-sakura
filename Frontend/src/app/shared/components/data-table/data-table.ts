import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

export type DataTableColumnType = 'text' | 'badge' | 'match' | 'person' | 'stack';
export type DataTableActionIcon = 'eye' | 'download' | 'calendar' | 'edit' | 'cancel';

export interface DataTableColumn<T> {
  key: string;
  label: string;
  width: number;
  type?: DataTableColumnType;
  sticky?: 'left' | 'right';
  value?: (row: T) => string | number;
  secondaryValue?: (row: T) => string | number;
  className?: (row: T) => string;
  title?: (row: T) => string;
}

export interface DataTableAction<T> {
  id: string;
  label: string;
  icon: DataTableActionIcon;
  visible?: (row: T) => boolean;
  disabled?: (row: T) => boolean;
}

export interface DataTableActionEvent<T> {
  action: string;
  row: T;
}

@Component({
  selector: 'app-data-table',
  imports: [CommonModule, FormsModule],
  templateUrl: './data-table.html',
  styleUrl: './data-table.scss',
})
export class DataTable<T> {
  @Input({ required: true }) title = '';
  @Input() subtitle = '';
  @Input() emptyTitle = 'No hay registros para mostrar';
  @Input() emptyMessage = 'Ajusta los filtros o limpia la búsqueda para volver al listado completo.';
  @Input() loading = false;
  @Input() loadingMessage = 'Cargando registros...';
  @Input() errorMessage = '';
  @Input() columns: DataTableColumn<T>[] = [];
  @Input() rows: T[] = [];
  @Input() total = 0;
  @Input() page = 1;
  @Input() pageSize = 5;
  @Input() pageSizeOptions = [5, 10, 25];
  @Input() selectable = true;
  @Input() selectedIds = new Set<string>();
  @Input({ required: true }) rowId: (row: T) => string = () => '';
  @Input() actions: DataTableAction<T>[] = [];

  @Output() selectedIdsChange = new EventEmitter<Set<string>>();
  @Output() pageChange = new EventEmitter<number>();
  @Output() pageSizeChange = new EventEmitter<number>();
  @Output() actionClick = new EventEmitter<DataTableActionEvent<T>>();
  @Output() clear = new EventEmitter<void>();
  @Output() retry = new EventEmitter<void>();

  get visibleColumns() {
    return this.columns;
  }

  get totalPages() {
    return Math.max(1, Math.ceil(this.total / this.pageSize));
  }

  get allVisibleSelected() {
    return this.rows.length > 0 && this.rows.every((row) => this.isSelected(row));
  }

  get hasActions() {
    return this.actions.length > 0;
  }

  get tableMinWidth() {
    const selectableWidth = this.selectable ? 52 : 0;
    const actionsWidth = this.hasActions ? 172 : 0;
    const columnsWidth = this.columns.reduce((total, column) => total + column.width, 0);
    return `${selectableWidth + columnsWidth + actionsWidth}px`;
  }

  columnValue(row: T, column: DataTableColumn<T>) {
    if (column.value) {
      return column.value(row);
    }

    const record = row as Record<string, unknown>;
    const value = record[column.key];
    return typeof value === 'string' || typeof value === 'number' ? value : '';
  }

  secondaryValue(row: T, column: DataTableColumn<T>) {
    return column.secondaryValue ? column.secondaryValue(row) : '';
  }

  cellClass(row: T, column: DataTableColumn<T>) {
    return column.className ? column.className(row) : '';
  }

  cellTitle(row: T, column: DataTableColumn<T>) {
    return column.title ? column.title(row) : String(this.columnValue(row, column));
  }

  columnStyle(column: DataTableColumn<T>) {
    const style: Record<string, string> = {
      width: `${column.width}px`,
      minWidth: `${column.width}px`,
      maxWidth: `${column.width}px`,
    };

    if (column.sticky === 'left') {
      style['left'] = `${this.leftOffset(column)}px`;
    }

    if (column.sticky === 'right') {
      style['right'] = `${this.rightOffset(column)}px`;
    }

    return style;
  }

  selectColumnStyle() {
    return {
      width: '52px',
      minWidth: '52px',
      maxWidth: '52px',
      left: '0',
    };
  }

  actionsColumnStyle() {
    return {
      width: '172px',
      minWidth: '172px',
      maxWidth: '172px',
      right: '0',
    };
  }

  isSelected(row: T) {
    return this.selectedIds.has(this.rowId(row));
  }

  toggleRow(row: T, selected: boolean) {
    const next = new Set(this.selectedIds);
    const id = this.rowId(row);

    if (selected) {
      next.add(id);
    } else {
      next.delete(id);
    }

    this.selectedIds = next;
    this.selectedIdsChange.emit(next);
  }

  toggleVisibleRows(selected: boolean) {
    const next = new Set(this.selectedIds);

    this.rows.forEach((row) => {
      const id = this.rowId(row);

      if (selected) {
        next.add(id);
      } else {
        next.delete(id);
      }
    });

    this.selectedIds = next;
    this.selectedIdsChange.emit(next);
  }

  changePage(page: number) {
    this.pageChange.emit(Math.min(Math.max(page, 1), this.totalPages));
  }

  changePageSize(size: number) {
    this.pageSizeChange.emit(size);
  }

  visibleAction(action: DataTableAction<T>, row: T) {
    return action.visible ? action.visible(row) : true;
  }

  disabledAction(action: DataTableAction<T>, row: T) {
    return action.disabled ? action.disabled(row) : false;
  }

  emitAction(action: DataTableAction<T>, row: T) {
    this.actionClick.emit({ action: action.id, row });
  }

  trackRow = (_index: number, row: T) => this.rowId(row);
  trackColumn = (_index: number, column: DataTableColumn<T>) => column.key;
  trackAction = (_index: number, action: DataTableAction<T>) => action.id;

  private leftOffset(column: DataTableColumn<T>) {
    const selectableWidth = this.selectable ? 52 : 0;
    const index = this.columns.indexOf(column);
    const previousSticky = this.columns.slice(0, index).filter((item) => item.sticky === 'left');
    return selectableWidth + previousSticky.reduce((total, item) => total + item.width, 0);
  }

  private rightOffset(column: DataTableColumn<T>) {
    const actionsWidth = this.hasActions ? 172 : 0;
    const index = this.columns.indexOf(column);
    const nextSticky = this.columns.slice(index + 1).filter((item) => item.sticky === 'right');
    return actionsWidth + nextSticky.reduce((total, item) => total + item.width, 0);
  }
}
