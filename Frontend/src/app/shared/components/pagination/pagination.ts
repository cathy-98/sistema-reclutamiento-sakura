import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-pagination',
  imports: [CommonModule, FormsModule],
  templateUrl: './pagination.html',
  styleUrl: './pagination.scss',
})
export class Pagination {
  @Input() page = 1;
  @Input() pageSize = 5;
  @Input() total = 0;
  @Input() visibleCount = 0;
  @Input() pageSizeOptions = [5, 10, 25];

  @Output() pageChange = new EventEmitter<number>();
  @Output() pageSizeChange = new EventEmitter<number>();

  get totalPages() {
    return Math.max(1, Math.ceil(this.total / this.pageSize));
  }

  changePage(page: number) {
    this.pageChange.emit(Math.min(Math.max(page, 1), this.totalPages));
  }

  changePageSize(size: number) {
    this.pageSizeChange.emit(size);
  }
}
