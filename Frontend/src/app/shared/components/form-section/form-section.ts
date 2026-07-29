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
}
