import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Button } from '../button/button';
import { IconButton } from '../icon-button/icon-button';

@Component({
  selector: 'app-file-list',
  imports: [CommonModule, Button, IconButton],
  templateUrl: './file-list.html',
  styleUrl: './file-list.scss',
})
export class FileList {
  @Input() files: File[] = [];

  @Output() clear = new EventEmitter<void>();
  @Output() remove = new EventEmitter<File>();

  get totalSizeMb() {
    return this.files.reduce((total, file) => total + this.fileSizeMb(file), 0);
  }

  fileSizeMb(file: File) {
    return file.size / 1024 / 1024;
  }

  trackFile(_index: number, file: File) {
    return `${file.name}-${file.size}-${file.lastModified}`;
  }
}
