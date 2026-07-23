import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-match-score',
  imports: [CommonModule],
  templateUrl: './match-score.html',
  styleUrl: './match-score.scss',
})
export class MatchScore {
  @Input() value: string | number = '';
  @Input() scoreClass = '';
}
