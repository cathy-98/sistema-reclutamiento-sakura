import { CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  Output,
} from '@angular/core';

import { Avatar } from '../avatar/avatar';
import {
  IconButton,
  IconButtonName,
} from '../icon-button/icon-button';
import { MatchScore } from '../match-score/match-score';
import { Pagination } from '../pagination/pagination';
import { StateMessage } from '../state-message/state-message';
import { StatusBadge } from '../status-badge/status-badge';

export type DataTableColumnType =
  | 'text'
  | 'badge'
  | 'match'
  | 'person'
  | 'stack';

export type DataTableActionIcon =
  IconButtonName;

export interface DataTableColumn<T> {
  key: string;
  label: string;
  width: number;
  type?: DataTableColumnType;
  sortable?: boolean;
  wrap?: boolean;
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
  disabledReason?: (row: T) => string;
}

export interface DataTableActionEvent<T> {
  action: string;
  row: T;
}

@Component({
  selector: 'app-data-table',
  imports: [
    CommonModule,
    Avatar,
    IconButton,
    MatchScore,
    Pagination,
    StateMessage,
    StatusBadge,
  ],
  templateUrl: './data-table.html',
  styleUrl: './data-table.scss',
})
export class DataTable<T> {
  @Input({ required: true }) title = '';
  @Input() subtitle = '';

  @Input() hideHeader =
    false;

  @Input() emptyTitle =
    'No hay registros para mostrar';

  @Input() emptyMessage =
    'Ajusta los filtros o limpia la búsqueda para volver al listado completo.';

  @Input() loading = false;

  @Input() loadingMessage =
    'Cargando registros...';

  @Input() errorMessage = '';

  @Input() columns:
    DataTableColumn<T>[] = [];

  @Input() rows: T[] = [];

  @Input() total = 0;

  @Input() page = 1;

  @Input() pageSize = 5;

  @Input() pageSizeOptions = [
    5,
    10,
    25,
  ];

  @Input() hidePagination = false;

  @Input() selectable = true;

  @Input() selectedIds =
    new Set<string>();

  @Input({ required: true })
  rowId: (row: T) => string =
    () => '';

  @Input() actions:
    DataTableAction<T>[] = [];

  @Input() compactActions =
    false;

  @Input() clickableRows =
    false;

  @Output()
  selectedIdsChange =
    new EventEmitter<Set<string>>();

  @Output()
  pageChange =
    new EventEmitter<number>();

  @Output()
  pageSizeChange =
    new EventEmitter<number>();

  @Output()
  actionClick =
    new EventEmitter<
      DataTableActionEvent<T>
    >();

  @Output()
  rowClick =
    new EventEmitter<T>();

  @Output()
  clear =
    new EventEmitter<void>();

  @Output()
  retry =
    new EventEmitter<void>();

  readonly tableId =
    `table-${Math.random()
      .toString(36)
      .slice(2)}`;

  /**
   * UX/UI DataTable
   *
   * Guarda el rowId de la fila cuyo menú
   * secundario se encuentra abierto.
   *
   * Solo puede existir un menú abierto
   * al mismo tiempo.
   */
  openActionMenuRowId = '';
  actionMenuPosition:
    {
      top: number;
      left: number;
      width: number;
      opensUp: boolean;
    } | null = null;

  sortKey = '';

  sortDirection:
    'asc' | 'desc' = 'asc';

  get titleId() {
    return `${this.tableId}-title`;
  }

  get descriptionId() {
    return `${this.tableId}-description`;
  }

  get visibleColumns() {
    return this.columns;
  }

  get totalPages() {
    return Math.max(
      1,
      Math.ceil(
        this.total /
          this.pageSize,
      ),
    );
  }

  get allVisibleSelected() {
    return (
      this.rows.length > 0 &&
      this.rows.every(
        (row) =>
          this.isSelected(row),
      )
    );
  }

  get sortedRows() {
    return this.sortedAllRows;
  }

  get visibleRowCount() {
    return this.sortedRows.length;
  }

  get sortedAllRows() {
    if (!this.sortKey) {
      return this.rows;
    }

    const column =
      this.columns.find(
        (item) =>
          item.key ===
          this.sortKey,
      );

    if (!column) {
      return this.rows;
    }

    return [...this.rows].sort(
      (a, b) => {
        const valueA =
          this.valorOrden(
            a,
            column,
          );

        const valueB =
          this.valorOrden(
            b,
            column,
          );

        const result =
          valueA.localeCompare(
            valueB,
            'es-CL',
            {
              numeric: true,
              sensitivity:
                'base',
            },
          );

        return this
          .sortDirection ===
          'asc'
          ? result
          : -result;
      },
    );
  }

  get hasActions() {
    return (
      this.actions.length > 0
    );
  }

  get tableMinWidth() {
    const selectableWidth =
      this.selectable
        ? 52
        : 0;

    const actionsWidth =
      this.hasActions
        ? this.actionsColumnWidth
        : 0;

    const columnsWidth =
      this.columns.reduce(
        (total, column) =>
          total +
          column.width,
        0,
      );

    return `${selectableWidth + columnsWidth + actionsWidth}px`;
  }

  get actionsColumnWidth() {
    return this.compactActions
      ? 112
      : 172;
  }

  columnValue(
    row: T,
    column: DataTableColumn<T>,
  ) {
    if (column.value) {
      return column.value(
        row,
      );
    }

    const record =
      row as Record<
        string,
        unknown
      >;

    const value =
      record[column.key];

    return typeof value ===
      'string' ||
      typeof value ===
        'number'
      ? value
      : '';
  }

  secondaryValue(
    row: T,
    column: DataTableColumn<T>,
  ) {
    return column.secondaryValue
      ? column.secondaryValue(
          row,
        )
      : '';
  }

  cellClass(
    row: T,
    column: DataTableColumn<T>,
  ) {
    return column.className
      ? column.className(row)
      : '';
  }

  cellTitle(
    row: T,
    column: DataTableColumn<T>,
  ) {
    return column.title
      ? column.title(row)
      : String(
          this.columnValue(
            row,
            column,
          ),
        );
  }

  isSortable(
    column: DataTableColumn<T>,
  ) {
    return (
      column.sortable !==
      false
    );
  }

  columnStyle(
    column: DataTableColumn<T>,
  ) {
    const style:
      Record<string, string> =
      {
        width: `${column.width}px`,
        minWidth: `${column.width}px`,
      };

    if (
      column.sticky ===
      'left'
    ) {
      style['left'] =
        `${this.leftOffset(column)}px`;
    }

    if (
      column.sticky ===
      'right'
    ) {
      style['right'] =
        `${this.rightOffset(column)}px`;
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
      width:
        `${this.actionsColumnWidth}px`,

      minWidth:
        `${this.actionsColumnWidth}px`,

      maxWidth:
        `${this.actionsColumnWidth}px`,

      right: '0',
    };
  }

  isSelected(row: T) {
    return this.selectedIds.has(
      this.rowId(row),
    );
  }

  toggleRow(
    row: T,
    selected: boolean,
  ) {
    const next =
      new Set(
        this.selectedIds,
      );

    const id =
      this.rowId(row);

    if (selected) {
      next.add(id);
    } else {
      next.delete(id);
    }

    this.selectedIds =
      next;

    this.selectedIdsChange.emit(
      next,
    );
  }

  emitRowClick(row: T) {
    if (!this.clickableRows) {
      return;
    }

    this.rowClick.emit(row);
  }

  toggleVisibleRows(
    selected: boolean,
  ) {
    const next =
      new Set(
        this.selectedIds,
      );

    this.rows.forEach(
      (row) => {
        const id =
          this.rowId(row);

        if (selected) {
          next.add(id);
        } else {
          next.delete(id);
        }
      },
    );

    this.selectedIds =
      next;

    this.selectedIdsChange.emit(
      next,
    );
  }

  changePage(
    page: number,
  ) {
    /**
     * UX/UI DataTable
     *
     * Al cambiar de página cerramos cualquier menú abierto
     * para evitar estados flotantes fuera de contexto.
     */
    this.closeActionMenu();

    this.pageChange.emit(
      Math.min(
        Math.max(
          page,
          1,
        ),
        this.totalPages,
      ),
    );
  }

  changePageSize(
    size: number,
  ) {
    this.closeActionMenu();

    this.pageSizeChange.emit(
      size,
    );
  }

  toggleSort(
    column:
      DataTableColumn<T>,
  ) {
    if (
      !this.isSortable(
        column,
      )
    ) {
      return;
    }

    this.closeActionMenu();

    if (
      this.sortKey ===
      column.key
    ) {
      this.sortDirection =
        this.sortDirection ===
        'asc'
          ? 'desc'
          : 'asc';

      return;
    }

    this.sortKey =
      column.key;

    this.sortDirection =
      'asc';
  }

  sortLabel(
    column:
      DataTableColumn<T>,
  ) {
    if (
      !this.isSortable(
        column,
      )
    ) {
      return null;
    }

    if (
      this.sortKey !==
      column.key
    ) {
      return 'Ordenar';
    }

    return this
      .sortDirection ===
      'asc'
      ? 'Ascendente'
      : 'Descendente';
  }

  visibleAction(
    action:
      DataTableAction<T>,
    row: T,
  ) {
    return action.visible
      ? action.visible(row)
      : true;
  }

  disabledAction(
    action:
      DataTableAction<T>,
    row: T,
  ) {
    return action.disabled
      ? action.disabled(row)
      : false;
  }

  actionTooltip(
    action:
      DataTableAction<T>,
    row: T,
  ) {
    return this.disabledAction(action, row) && action.disabledReason
      ? action.disabledReason(row)
      : action.label;
  }

  /**
   * Acción estándar utilizada por botones visibles.
   *
   * También asegura que el menú contextual quede cerrado
   * después de ejecutar una acción.
   */
  emitAction(
    action:
      DataTableAction<T>,
    row: T,
  ) {
    this.closeActionMenu();

    this.actionClick.emit({
      action: action.id,
      row,
    });
  }

  /**
   * UX/UI DataTable
   *
   * Ejecuta una opción del menú secundario y lo cierra.
   * El stopPropagation evita que el click llegue al
   * listener global antes de terminar la acción.
   */
  emitActionAndClose(
    action:
      DataTableAction<T>,
    row: T,
    event: MouseEvent,
  ) {
    event.stopPropagation();

    if (
      this.disabledAction(
        action,
        row,
      )
    ) {
      return;
    }

    this.closeActionMenu();

    this.actionClick.emit({
      action: action.id,
      row,
    });
  }

  visibleActions(row: T) {
    return this.actions.filter(
      (action) =>
        this.visibleAction(
          action,
          row,
        ),
    );
  }

  primaryRowAction(
    row: T,
  ) {
    return this.visibleActions(
      row,
    )[0];
  }

  secondaryRowActions(
    row: T,
  ) {
    return this.visibleActions(
      row,
    ).slice(1);
  }

  /**
   * UX/UI DataTable
   *
   * Abre/cierra el menú de acciones de una fila.
   *
   * Si se abre otro menú, el anterior queda cerrado
   * porque openActionMenuRowId solo admite un rowId.
   */
  toggleActionMenu(
    row: T,
    event: MouseEvent,
  ) {
    event.stopPropagation();

    const id =
      this.rowId(row);

    if (
      this.openActionMenuRowId ===
      id
    ) {
      this.closeActionMenu();
      return;
    }

    this.openActionMenuRowId = id;
    this.positionActionMenu(
      event.currentTarget as HTMLElement,
    );
  }

  isActionMenuOpen(
    row: T,
  ) {
    return (
      this.openActionMenuRowId ===
      this.rowId(row)
    );
  }

  /**
   * UX/UI DataTable
   *
   * Click fuera del menú:
   * cualquier click en el documento cierra la opción
   * secundaria actualmente abierta.
   *
   * Los clicks dentro de .row-menu utilizan stopPropagation
   * desde el template.
   */
  @HostListener(
    'document:click',
  )
  handleDocumentClick() {
    this.closeActionMenu();
  }

  @HostListener('document:keydown.escape')
  handleEscape() {
    this.closeActionMenu();
  }

  @HostListener('window:resize')
  @HostListener('window:scroll')
  handleViewportChange() {
    this.closeActionMenu();
  }

  trackRow = (
    _index: number,
    row: T,
  ) => this.rowId(row);

  trackColumn = (
    _index: number,
    column:
      DataTableColumn<T>,
  ) => column.key;

  trackAction = (
    _index: number,
    action:
      DataTableAction<T>,
  ) => action.id;

  /**
   * Cierre centralizado del menú para evitar
   * repetir asignaciones a string vacío.
   */
  private closeActionMenu() {
    this.openActionMenuRowId =
      '';
    this.actionMenuPosition =
      null;
  }

  private positionActionMenu(
    trigger: HTMLElement,
  ) {
    const menuWidth = 230;
    const menuEstimatedHeight = 160;
    const gap = 6;
    const padding = 12;
    const triggerRect =
      trigger.getBoundingClientRect();
    const viewportHeight =
      window.innerHeight;
    const viewportWidth =
      window.innerWidth;
    const spaceBelow =
      viewportHeight -
      triggerRect.bottom;
    const opensUp =
      spaceBelow <
      menuEstimatedHeight + gap;
    const top = opensUp
      ? Math.max(
          padding,
          triggerRect.top -
            menuEstimatedHeight -
            gap,
        )
      : triggerRect.bottom + gap;
    const left = Math.min(
      Math.max(
        padding,
        triggerRect.right -
          menuWidth,
      ),
      viewportWidth -
        menuWidth -
        padding,
    );

    // El menú se posiciona contra el viewport para escapar del overflow de la tabla.
    this.actionMenuPosition = {
      top,
      left,
      width: menuWidth,
      opensUp,
    };
  }

  private valorOrden(
    row: T,
    column:
      DataTableColumn<T>,
  ) {
    return `${this.columnValue(
      row,
      column,
    )} ${this.secondaryValue(
      row,
      column,
    )}`.trim();
  }

  private leftOffset(
    column:
      DataTableColumn<T>,
  ) {
    const selectableWidth =
      this.selectable
        ? 52
        : 0;

    const index =
      this.columns.indexOf(
        column,
      );

    const previousSticky =
      this.columns
        .slice(0, index)
        .filter(
          (item) =>
            item.sticky ===
            'left',
        );

    return (
      selectableWidth +
      previousSticky.reduce(
        (total, item) =>
          total +
          item.width,
        0,
      )
    );
  }

  private rightOffset(
    column:
      DataTableColumn<T>,
  ) {
    const actionsWidth =
      this.hasActions
        ? this.actionsColumnWidth
        : 0;

    const index =
      this.columns.indexOf(
        column,
      );

    const nextSticky =
      this.columns
        .slice(index + 1)
        .filter(
          (item) =>
            item.sticky ===
            'right',
        );

    return (
      actionsWidth +
      nextSticky.reduce(
        (total, item) =>
          total +
          item.width,
        0,
      )
    );
  }
}
