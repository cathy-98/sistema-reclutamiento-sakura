import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-page-header',
  imports: [CommonModule],
  templateUrl: './page-header.html',
  styleUrl: './page-header.scss',
})
export class PageHeader {
  @Input({ required: true }) title = '';
  @Input() subtitle = '';
  @Input() eyebrow = '';
  @Input() badge = '';
  @Input() imageSrc = '';
  @Input() imageAlt = '';

  readonly headerId = `page-header-${Math.random().toString(36).slice(2)}`;

  get titleId() {
    return `${this.headerId}-title`;
  }

  get subtitleId() {
    return `${this.headerId}-subtitle`;
  }
}
