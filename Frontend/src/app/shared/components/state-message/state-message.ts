import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Button } from '../button/button';

export type StateMessageType = 'loading' | 'empty' | 'error';

@Component({
  selector: 'app-state-message',
  imports: [CommonModule, Button],
  templateUrl: './state-message.html',
  styleUrl: './state-message.scss',
})
export class StateMessage {
  @Input() type: StateMessageType = 'empty';
  @Input() title = '';
  @Input() message = '';
  @Input() actionLabel = '';

  @Output() action = new EventEmitter<void>();
}
