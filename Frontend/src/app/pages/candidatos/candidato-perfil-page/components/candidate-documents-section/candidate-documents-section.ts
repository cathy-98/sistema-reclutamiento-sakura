import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FileDropzone } from '../../../../../shared/components/file-dropzone/file-dropzone';
import { DocumentoPerfil } from '../../candidato-perfil.models';

@Component({
  selector: 'app-candidate-documents-section',
  imports: [CommonModule, FileDropzone],
  templateUrl: './candidate-documents-section.html',
  styleUrl: './candidate-documents-section.scss',
})
export class CandidateDocumentsSection {
  @Input() documentos: DocumentoPerfil[] = [];
  @Output() filesChange = new EventEmitter<File[]>();
}
