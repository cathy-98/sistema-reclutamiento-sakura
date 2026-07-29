import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-avatar',
  templateUrl: './avatar.html',
  styleUrl: './avatar.scss',
})
export class Avatar {
  @Input() initials = '';
  @Input() label = '';
}
