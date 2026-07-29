import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-form-field',
  imports: [CommonModule],
  templateUrl: './form-field.html',
  styleUrl: './form-field.scss',
})
export class FormField {
  @Input() label = '';
  @Input() hint = '';
  @Input() error = '';
  @Input() required = false;
}
