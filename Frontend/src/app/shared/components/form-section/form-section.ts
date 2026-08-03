import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-form-section',
  imports: [CommonModule],
  templateUrl: './form-section.html',
  styleUrl: './form-section.scss',
})
export class FormSection {
  @Input() step = '';
  @Input() title = '';
  @Input() description = '';

  readonly sectionId = `form-section-${Math.random().toString(36).slice(2)}`;

  get titleId() {
    return `${this.sectionId}-title`;
  }

  get descriptionId() {
    return `${this.sectionId}-description`;
  }
}
