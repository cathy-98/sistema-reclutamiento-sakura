import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Button } from '../button/button';
import { FileList } from '../file-list/file-list';

@Component({
  selector: 'app-file-dropzone',
  imports: [CommonModule, Button, FileList],
  templateUrl: './file-dropzone.html',
  styleUrl: './file-dropzone.scss',
})
export class FileDropzone {
  @Input() title = 'Arrastra archivos aquí';
  @Input() description = 'También puedes seleccionarlos desde tu equipo.';
  @Input() buttonText = 'Seleccionar archivos';
  @Input() allowedExtensions = ['pdf', 'doc', 'docx'];
  @Input() multiple = true;
  @Input() maxFileSizeMb = 10;

  @Output() filesChange = new EventEmitter<File[]>();

  dragging = false;
  files: File[] = [];
  error = '';

  get accept() {
    return this.allowedExtensions.map((extension) => `.${extension}`).join(',');
  }

  get allowedText() {
    return this.allowedExtensions.map((extension) => extension.toUpperCase()).join(', ');
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.dragging = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.dragging = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragging = false;
    this.addFiles(Array.from(event.dataTransfer?.files ?? []));
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    this.addFiles(Array.from(input.files ?? []));
    input.value = '';
  }

  removeFile(fileToRemove: File) {
    this.files = this.files.filter((file) => file !== fileToRemove);
    this.filesChange.emit(this.files);
  }

  clearFiles() {
    this.files = [];
    this.error = '';
    this.filesChange.emit(this.files);
  }

  private addFiles(selectedFiles: File[]) {
    this.error = '';

    if (selectedFiles.length === 0) {
      return;
    }

    const invalidByExtension = selectedFiles.filter((file) => !this.hasAllowedExtension(file));

    if (invalidByExtension.length > 0) {
      this.error = `Solo se permiten archivos ${this.allowedText}.`;
      return;
    }

    const maxSize = this.maxFileSizeMb * 1024 * 1024;
    const invalidBySize = selectedFiles.filter((file) => file.size > maxSize);

    if (invalidBySize.length > 0) {
      this.error = `Cada archivo debe pesar máximo ${this.maxFileSizeMb} MB.`;
      return;
    }

    this.files = this.multiple ? this.mergeFiles(selectedFiles) : [selectedFiles[0]];
    this.filesChange.emit(this.files);
  }

  private mergeFiles(selectedFiles: File[]) {
    const currentKeys = new Set(this.files.map((file) => this.fileKey(file)));
    const newFiles = selectedFiles.filter((file) => !currentKeys.has(this.fileKey(file)));
    return [...this.files, ...newFiles];
  }

  private hasAllowedExtension(file: File) {
    const extension = file.name.split('.').pop()?.toLowerCase();
    return extension ? this.allowedExtensions.includes(extension) : false;
  }

  private fileKey(file: File) {
    return `${file.name}-${file.size}-${file.lastModified}`;
  }
}
