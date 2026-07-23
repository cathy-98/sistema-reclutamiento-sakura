import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export type IconButtonName = 'eye' | 'download' | 'calendar' | 'edit' | 'cancel';

@Component({
  selector: 'app-icon-button',
  imports: [CommonModule],
  templateUrl: './icon-button.html',
  styleUrl: './icon-button.scss',
})
export class IconButton {
  @Input() icon: IconButtonName = 'eye';
  @Input() label = '';
  @Input() disabled = false;
  @Input() type: 'button' | 'submit' = 'button';

  @Output() pressed = new EventEmitter<void>();
}
