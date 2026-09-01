import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Button } from '../button/button';
import { IconButton } from '../icon-button/icon-button';

export interface FileListStatus {
  state: 'pending' | 'processing' | 'success' | 'error';
  label: string;
  message?: string;
}

@Component({
  selector: 'app-file-list',
  imports: [CommonModule, Button, IconButton],
  templateUrl: './file-list.html',
  styleUrl: './file-list.scss',
})
export class FileList {
  @Input() files: File[] = [];
  @Input() statuses: Record<string, FileListStatus> = {};

  @Output() clear = new EventEmitter<void>();
  @Output() remove = new EventEmitter<File>();

  readonly listId = `file-list-${Math.random().toString(36).slice(2)}`;

  get titleId() {
    return `${this.listId}-title`;
  }

  get descriptionId() {
    return `${this.listId}-description`;
  }

  get totalSizeMb() {
    return this.files.reduce((total, file) => total + this.fileSizeMb(file), 0);
  }

  fileSizeMb(file: File) {
    return file.size / 1024 / 1024;
  }

  trackFile(_index: number, file: File) {
    return `${file.name}-${file.size}-${file.lastModified}`;
  }

  fileStatus(file: File) {
    return this.statuses[this.trackFile(0, file)] ?? null;
  }

  get hasStatuses() {
    return Object.keys(this.statuses).length > 0;
  }
}
