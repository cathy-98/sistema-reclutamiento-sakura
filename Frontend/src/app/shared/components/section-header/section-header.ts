import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-section-header',
  imports: [CommonModule],
  templateUrl: './section-header.html',
  styleUrl: './section-header.scss',
})
export class SectionHeader {
  @Input() title = '';
  @Input() description = '';
}
