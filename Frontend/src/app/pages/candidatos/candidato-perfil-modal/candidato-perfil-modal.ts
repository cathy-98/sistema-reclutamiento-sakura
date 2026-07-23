import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { IconButton } from '../../../shared/components/icon-button/icon-button';
import { MatchScore } from '../../../shared/components/match-score/match-score';
import { Modal } from '../../../shared/components/modal/modal';
import { StatusBadge } from '../../../shared/components/status-badge/status-badge';
import { CandidatoProfileTab, CandidatoProfileTabs } from '../candidato-profile-tabs/candidato-profile-tabs';
import { CandidatoSummaryCard } from '../candidato-summary-card/candidato-summary-card';

export interface CandidatoPerfilResumen {
  idSolicitud: string;
  match: number;
  nombre: string;
  correo: string;
  telefono: string;
  cargo: string;
  estado: string;
  disponibilidad: string;
  renta: number;
}

type PerfilTab =
  | 'datos'
  | 'experiencia'
  | 'estudios'
  | 'historial'
  | 'proceso'
  | 'match'
  | 'documentos';

@Component({
  selector: 'app-candidato-perfil-modal',
  imports: [
    CommonModule,
    FormsModule,
    Button,
    CandidatoProfileTabs,
    CandidatoSummaryCard,
    IconButton,
    MatchScore,
    Modal,
    StatusBadge,
  ],
  templateUrl: './candidato-perfil-modal.html',
  styleUrl: './candidato-perfil-modal.scss',
})
export class CandidatoPerfilModal {
  @Input() candidato: CandidatoPerfilResumen | null = null;
  @Output() cerrar = new EventEmitter<void>();

  tabActiva: PerfilTab = 'datos';
  busquedaPostulaciones = '';
  filtroEstado = 'Todos';
  nota = '';

  readonly tabs: CandidatoProfileTab[] = [
    { id: 'datos', label: 'Datos personales', icon: 'user' },
    { id: 'experiencia', label: 'Experiencia laboral', icon: 'briefcase' },
    { id: 'estudios', label: 'Estudios y cursos', icon: 'graduation' },
    { id: 'historial', label: 'Historial de postulaciones', icon: 'list' },
    { id: 'proceso', label: 'Proceso de selección', icon: 'puzzle' },
    { id: 'match', label: 'Análisis de match', icon: 'users' },
    { id: 'documentos', label: 'Documentos y notas', icon: 'file' },
  ];

  readonly postulaciones = [
    ['REQ-021', 'Tech Solutions SpA', 'Senior React Developer', '24 oct 2024', 'En proceso'],
    ['REQ-015', 'Fintek Chile', 'Frontend Developer', '02 oct 2024', 'En proceso'],
    ['REQ-008', 'DataMind', 'Full Stack Developer', '15 sep 2024', 'No seleccionado'],
    ['REQ-004', 'Global Soft', 'React Developer', '28 ago 2024', 'No seleccionado'],
    ['REQ-001', 'Innovar Tech', 'Desarrollador JavaScript', '10 ago 2024', 'No seleccionado'],
  ];

  readonly experiencias = [
    {
      empresa: 'MercadoLibre',
      cargo: 'Desarrollador Frontend Senior',
      fecha: 'ene 2022 - may 2024 (2 años 4 meses)',
      modalidad: 'Remoto',
      logros: [
        'Desarrolló e implementó interfaces escalables con React y TypeScript.',
        'Mejoró el rendimiento de la web reduciendo el tiempo de carga en 35%.',
        'Colaboró con equipos multidisciplinarios en nuevas funcionalidades.',
      ],
      tags: ['React', 'TypeScript', 'Next.js', 'Tailwind CSS', 'AWS'],
    },
    {
      empresa: 'Cornershop',
      cargo: 'Desarrollador Full Stack',
      fecha: 'jun 2020 - dic 2021 (1 año 7 meses)',
      modalidad: 'Híbrido',
      logros: [
        'Desarrolló APIs REST con Node.js y Express para aplicaciones internas.',
        'Implementó funcionalidades del frontend con React y Redux.',
        'Participó en la migración de servicios a AWS.',
      ],
      tags: ['React', 'Node.js', 'Express', 'Redux', 'AWS'],
    },
    {
      empresa: 'Bci',
      cargo: 'Desarrollador de Software',
      fecha: 'ene 2019 - may 2020 (1 año 5 meses)',
      modalidad: 'Presencial',
      logros: [
        'Desarrolló módulos para banca digital utilizando React y JavaScript.',
        'Realizó integraciones con servicios internos y de terceros.',
        'Colaboró en pruebas, QA y despliegues productivos.',
      ],
      tags: ['React', 'JavaScript', 'Bootstrap', 'Git', 'Jenkins'],
    },
  ];

  readonly habilidadesMatch = [
    ['React', 'Avanzado', 'Avanzado', '4.5', 'Cumple', 'success'],
    ['TypeScript', 'Avanzado', 'Avanzado', '4', 'Cumple', 'success'],
    ['Node.js', 'Intermedio', 'Avanzado', '3.5', 'Cumple', 'success'],
    ['AWS', 'Intermedio', 'Intermedio', '2.5', 'Cumple parcialmente', 'warning'],
    ['Docker', 'Intermedio', 'Básico', '1.5', 'No cumple', 'danger'],
    ['Testing', 'Intermedio', 'Intermedio', '2.5', 'Cumple', 'success'],
  ];

  readonly etapas = [
    ['Postulación', 'Completado'],
    ['Filtro CV', 'Completado'],
    ['Entrevista RRHH', 'Completado'],
    ['Entrevista técnica', 'Actual'],
    ['Prueba técnica', 'Pendiente'],
    ['Oferta', 'Pendiente'],
  ];

  readonly documentos = [
    ['CV_Juan_Perez_Gonzalez.pdf', 'Currículum', 'Req-021', '24 oct 2024, 10:15', 'pdf'],
    ['Carta_de_presentacion.docx', 'Carta de presentación', 'Req-021', '24 oct 2024, 10:16', 'doc'],
    ['Certificado_Titulo_Ingenieria.pdf', 'Certificado', 'No aplica', '24 oct 2024, 10:17', 'pdf'],
    ['Portafolio_Proyectos.xlsx', 'Portafolio', 'Req-021', '24 oct 2024, 10:18', 'xls'],
    ['Certificacion_English_B2.pdf', 'Certificación', 'No aplica', '24 oct 2024, 10:19', 'pdf'],
  ];

  get nombre() {
    return this.candidato?.nombre || 'Juan Perez Gonzalez';
  }

  get cargo() {
    return this.candidato?.cargo || 'Senior React Developer';
  }

  get iniciales() {
    return this.nombre
      .split(' ')
      .slice(0, 2)
      .map((parte) => parte[0])
      .join('')
      .toUpperCase();
  }

  get rentaFormateada() {
    return `$${Number(this.candidato?.renta || 2800000).toLocaleString('es-CL')} CLP líquidos`;
  }

  get postulacionesFiltradas() {
    const texto = this.busquedaPostulaciones.trim().toLowerCase();
    return this.postulaciones.filter((postulacion) => {
      const coincideTexto = postulacion.join(' ').toLowerCase().includes(texto);
      const coincideEstado = this.filtroEstado === 'Todos' || postulacion[4] === this.filtroEstado;
      return coincideTexto && coincideEstado;
    });
  }

  cambiarTab(tab: string) {
    this.tabActiva = tab as PerfilTab;
  }

  statusClass(estado: string) {
    return estado === 'En proceso' ? 'en-revision' : 'cerrada';
  }
}
