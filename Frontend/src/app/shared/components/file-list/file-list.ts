import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Button } from '../button/button';

@Component({
  selector: 'app-file-list',
  imports: [CommonModule, Button],
  templateUrl: './file-list.html',
  styleUrl: './file-list.scss',
})
export class FileList {
  @Input() files: File[] = [];

  @Output() clear = new EventEmitter<void>();
  @Output() remove = new EventEmitter<File>();

  fileSizeMb(file: File) {
    return file.size / 1024 / 1024;
  }
}
