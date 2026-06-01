import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

interface Solicitud {
  id: string;
  cliente: string;
  cargo: string;
  responsable: string;
  seleccion: string;
  inicioEmpleo: string;
  prioridad: 'Alta' | 'Media' | 'Baja';
  estado: 'En curso' | 'Pendiente' | 'Cerrada' | 'Cancelada';
}

@Component({
  selector: 'app-solicitudes-list',
  imports: [CommonModule, RouterLink],
  templateUrl: './solicitudes-list.html',
  styleUrl: './solicitudes-list.scss',
})
export class SolicitudesList {
  solicitudes: Solicitud[] = [
    {
      id: 'Req-021',
      cliente: 'Latam',
      cargo: 'Backend',
      responsable: 'Macarena Lopez',
      seleccion: '01/10/2025 - 31/10/2025',
      inicioEmpleo: '02/11/2025',
      prioridad: 'Alta',
      estado: 'En curso',
    },
    {
      id: 'Req-022',
      cliente: 'Banco de chile',
      cargo: 'QA',
      responsable: 'Macarena Lopez',
      seleccion: '01/10/2025 - 31/10/2025',
      inicioEmpleo: '02/11/2025',
      prioridad: 'Baja',
      estado: 'Pendiente',
    },
    {
      id: 'Req-023',
      cliente: 'Sports',
      cargo: 'Diseñador',
      responsable: 'Macarena Lopez',
      seleccion: '01/10/2025 - 01/11/2025',
      inicioEmpleo: '02/11/2025',
      prioridad: 'Media',
      estado: 'Cerrada',
    },
    {
      id: 'Req-024',
      cliente: 'Jumbo',
      cargo: 'QA',
      responsable: 'Macarena Lopez',
      seleccion: '01/10/2025 - 01/11/2025',
      inicioEmpleo: '02/11/2025',
      prioridad: 'Alta',
      estado: 'Cancelada',
    },
    {
      id: 'Req-025',
      cliente: 'Latam',
      cargo: 'Backend',
      responsable: 'Macarena Lopez',
      seleccion: '01/10/2025 - 01/11/2025',
      inicioEmpleo: '02/11/2025',
      prioridad: 'Baja',
      estado: 'Cerrada',
    },
    {
      id: 'Req-026',
      cliente: 'Sports',
      cargo: 'Frontend',
      responsable: 'Macarena Lopez',
      seleccion: '01/10/2025 - 31/10/2025',
      inicioEmpleo: '02/11/2025',
      prioridad: 'Media',
      estado: 'Cerrada',
    },
  ];

  trackSolicitud(_index: number, solicitud: Solicitud) {
    return solicitud.id;
  }

  estadoClase(estado: Solicitud['estado']) {
    return estado.toLowerCase().replace(' ', '-');
  }
}
