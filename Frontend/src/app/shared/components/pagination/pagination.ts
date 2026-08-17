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

  get pageItems(): Array<number | 'ellipsis'> {
    const totalPages = this.totalPages;

    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_item, index) => index + 1);
    }

    const pages = new Set<number>([1, totalPages]);
    const start = Math.max(2, this.page - 1);
    const end = Math.min(totalPages - 1, this.page + 1);

    for (let page = start; page <= end; page += 1) {
      pages.add(page);
    }

    if (this.page <= 3) {
      pages.add(2);
      pages.add(3);
      pages.add(4);
    }

    if (this.page >= totalPages - 2) {
      pages.add(totalPages - 3);
      pages.add(totalPages - 2);
      pages.add(totalPages - 1);
    }

    const orderedPages = Array.from(pages).sort((a, b) => a - b);
    const items: Array<number | 'ellipsis'> = [];

    orderedPages.forEach((page, index) => {
      const previous = orderedPages[index - 1];

      if (previous && page - previous > 1) {
        items.push('ellipsis');
      }

      items.push(page);
    });

    return items;
  }

  changePage(page: number) {
    this.pageChange.emit(Math.min(Math.max(page, 1), this.totalPages));
  }

  changePageSize(size: number) {
    this.pageSizeChange.emit(size);
  }

  trackPageItem(index: number, item: number | 'ellipsis') {
    return `${item}-${index}`;
  }
}
