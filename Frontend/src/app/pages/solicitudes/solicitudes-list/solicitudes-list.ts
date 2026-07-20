import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface HabilidadSolicitud {
  id_habilidad: number | null;
  id_nivel_habilidad: number | null;
  anios_experiencia: number;
  es_excluyente: boolean;
}

@Component({
  selector: 'app-solicitudes-list',
  imports: [CommonModule, FormsModule],
  templateUrl: './solicitudes-list.html',
  styleUrl: './solicitudes-list.scss',
})
export class SolicitudesList {
  cargando = false;
  error = '';
  mostrarFormulario = false;
  tabFormulario = 'general';
  pasosFormulario = [
    { clave: 'general', numero: 1, titulo: 'Información general' },
    { clave: 'condiciones', numero: 2, titulo: 'Condiciones' },
    { clave: 'cronograma', numero: 3, titulo: 'Cronograma' },
    { clave: 'descripcion', numero: 4, titulo: 'Descripción' },
    { clave: 'habilidades', numero: 5, titulo: 'Habilidades' },
  ];

  nuevaHabilidad = {
    id_habilidad: null as number | null,
    id_nivel_habilidad: null as number | null,
    anios_experiencia: 0,
    es_excluyente: false,
  };

  catalogoActivo = '';
  nuevoValorCatalogo = '';

  cargosCatalogo = [
    { id: 1, nombre: 'Desarrollador Python' },
    { id: 2, nombre: 'Desarrollador Angular' },
    { id: 3, nombre: 'Analista QA' },
  ];

  areasCatalogo = [
    { id: 1, nombre: 'Tecnología' },
    { id: 2, nombre: 'Operaciones' },
    { id: 3, nombre: 'Recursos Humanos' },
  ];

  clientesCatalogo = [
    { id: 1, nombre: 'Banco Elitsoft' },
  ];

  habilidadesCatalogo = [
    { id: 1, nombre: 'Python' },
    { id: 2, nombre: 'SQL' },
    { id: 3, nombre: 'Angular' },
    { id: 4, nombre: 'Git' },
  ];

  nivelesHabilidadCatalogo = [
    { id: 1, nombre: 'Trainee' },
    { id: 2, nombre: 'Junior' },
    { id: 3, nombre: 'Semi Senior' },
    { id: 4, nombre: 'Senior' },
  ];

  cambiarTabFormulario(tab: string) {
    this.tabFormulario = tab;
  }

  pasoActualIndice() {
    return this.pasosFormulario.findIndex((paso) => paso.clave === this.tabFormulario);
  }

  pasoCompletado(clave: string) {
    const indicePaso = this.pasosFormulario.findIndex((paso) => paso.clave === clave);
    return indicePaso < this.pasoActualIndice();
  }

  volverPaso() {
    const indiceActual = this.pasoActualIndice();

    if (indiceActual > 0) {
      this.tabFormulario = this.pasosFormulario[indiceActual - 1].clave;
    }
  }

  siguientePaso() {
    const indiceActual = this.pasoActualIndice();

    if (indiceActual < this.pasosFormulario.length - 1) {
      this.tabFormulario = this.pasosFormulario[indiceActual + 1].clave;
    }
  }

  esUltimoPaso() {
    return this.pasoActualIndice() === this.pasosFormulario.length - 1;
  }

  guardarSolicitud() {
    console.log('Guardar solicitud', this.formularioSolicitud);
  }

  manejarSeleccionCatalogo(catalogo: string, valor: string | number | null) {
    if (valor !== 'crear') {
      return;
    }

    this.catalogoActivo = catalogo;
    this.nuevoValorCatalogo = '';

    if (catalogo === 'cargo') {
      this.formularioSolicitud.id_cargo = null;
    }

    if (catalogo === 'area') {
      this.formularioSolicitud.id_area = null;
    }

    if (catalogo === 'cliente') {
      this.formularioSolicitud.id_cliente = null;
    }

    if (catalogo === 'habilidad') {
      this.nuevaHabilidad.id_habilidad = null;
    }
  }

  guardarNuevoCatalogo() {
    const nombre = this.nuevoValorCatalogo.trim();

    if (!nombre) {
      return;
    }

    if (this.catalogoActivo === 'cargo') {
      const nuevoId = this.siguienteId(this.cargosCatalogo);
      this.cargosCatalogo.push({ id: nuevoId, nombre });
      this.formularioSolicitud.id_cargo = nuevoId;
    }

    if (this.catalogoActivo === 'area') {
      const nuevoId = this.siguienteId(this.areasCatalogo);
      this.areasCatalogo.push({ id: nuevoId, nombre });
      this.formularioSolicitud.id_area = nuevoId;
    }

    if (this.catalogoActivo === 'cliente') {
      const nuevoId = this.siguienteId(this.clientesCatalogo);
      this.clientesCatalogo.push({ id: nuevoId, nombre });
      this.formularioSolicitud.id_cliente = nuevoId;
    }

    if (this.catalogoActivo === 'habilidad') {
      const nuevoId = this.siguienteId(this.habilidadesCatalogo);
      this.habilidadesCatalogo.push({ id: nuevoId, nombre });
      this.nuevaHabilidad.id_habilidad = nuevoId;
    }

    this.cancelarNuevoCatalogo();
  }

  cancelarNuevoCatalogo() {
    this.catalogoActivo = '';
    this.nuevoValorCatalogo = '';
  }

  siguienteId(catalogo: { id: number; nombre: string }[]) {
    return Math.max(...catalogo.map((item) => item.id), 0) + 1;
  }

  agregarHabilidad() {
    if (!this.nuevaHabilidad.id_habilidad || !this.nuevaHabilidad.id_nivel_habilidad) {
      return;
    }

    this.formularioSolicitud.habilidades.push({
      id_habilidad: this.nuevaHabilidad.id_habilidad,
      id_nivel_habilidad: this.nuevaHabilidad.id_nivel_habilidad,
      anios_experiencia: Number(this.nuevaHabilidad.anios_experiencia) || 0,
      es_excluyente: this.nuevaHabilidad.es_excluyente,
    });

    this.nuevaHabilidad = {
      id_habilidad: null,
      id_nivel_habilidad: null,
      anios_experiencia: 0,
      es_excluyente: false,
    };
  }

  eliminarHabilidad(indice: number) {
    this.formularioSolicitud.habilidades.splice(indice, 1);
  }

  obtenerNombreHabilidad(id: number | null) {
    return this.habilidadesCatalogo.find((habilidad) => habilidad.id === id)?.nombre ?? 'Habilidad';
  }

  obtenerNombreNivel(id: number | null) {
    return this.nivelesHabilidadCatalogo.find((nivel) => nivel.id === id)?.nombre ?? 'Nivel';
  }

  estadoClase(estado: string) {
    return estado.toLowerCase().replace(/\s+/g, '-');
  }

  prioridadClase(prioridad: string) {
    return prioridad.toLowerCase();
  }

  habilidadExcluyenteClase(esExcluyente: boolean) {
    return esExcluyente ? 'excluyente' : 'no-excluyente';
  }

  formularioSolicitud = {
    titulo: '',
    descripcion: '',
    id_cargo: null as number | null,
    id_prioridad: null as number | null,
    cantidad_vacantes: 1,
    id_cliente: null as number | null,
    id_usuario_solicitante: null as number | null,
    id_usuario_responsable: null as number | null,
    id_modalidad: null as number | null,
    salario_minimo: null as number | null,
    salario_maximo: null as number | null,
    fecha_inicio_busqueda: '',
    fecha_cierre_busqueda: '',
    fecha_inicio_cliente: '',
    id_estado_solicitud: null as number | null,
    id_area: null as number | null,
    hora_inicio_jornada: '',
    hora_fin_jornada: '',
    habilidades: [] as HabilidadSolicitud[],
  };

  solicitudes = [
    {
      id: 'Req-001',
      nombre: 'Desarrollador Python Senior',
      cliente: 'Banco Elitsoft',
      cargo: 'Desarrollador Python',
      vacantes: 2,
      responsable: 'Cathy',
      seleccion: '01/06/2026 - 30/06/2026',
      inicioEmpleo: '15/07/2026',
      prioridad: 'Alta',
      estado: 'Pendiente',
      observacion: 'Perfil crítico para continuidad del equipo backend.',
    },

    {
      id: 'Req-002',
      nombre: 'Desarrollador Python Junior',
      cliente: 'Banco Elitsoft',
      cargo: 'Desarrollador Python',
      vacantes: 2,
      responsable: 'Cathy',
      seleccion: '01/06/2026 - 30/06/2026',
      inicioEmpleo: '15/07/2026',
      prioridad: 'Media',
      estado: 'En curso',
      observacion: 'Requiere disponibilidad para onboarding durante julio.',
    },
    {
      id: 'Req-003',
      nombre: 'Analista QA',
      cliente: 'Cliente interno',
      cargo: 'Analista QA',
      vacantes: 1,
      responsable: 'Felipe',
      seleccion: '10/07/2026 - 30/07/2026',
      inicioEmpleo: '05/08/2026',
      prioridad: 'Baja',
      estado: 'Cerrada',
      observacion: 'Solicitud cubierta con candidato interno.',
    },
  ];

  abrirFormulario() {
    this.mostrarFormulario = true;
  }

  cerrarFormulario() {
    this.mostrarFormulario = false;
  }
}

