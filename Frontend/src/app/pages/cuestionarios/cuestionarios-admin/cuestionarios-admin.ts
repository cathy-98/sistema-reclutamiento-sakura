import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormArray, FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { forkJoin, take } from 'rxjs';
import {
  CuestionariosService,
  NivelCuestionario,
  PreguntaCuestionario,
  TecnologiaCuestionario,
} from '../../../services/cuestionarios.service';
import { Button } from '../../../shared/components/button/button';
import { Card } from '../../../shared/components/card/card';
import { DataTable, DataTableColumn } from '../../../shared/components/data-table/data-table';
import { AlertRegion } from '../../../shared/components/alert-region/alert-region';
import { FormField } from '../../../shared/components/form-field/form-field';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { TabItem, Tabs } from '../../../shared/components/tabs/tabs';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { CuestionarioEnvioModal, CuestionarioEnvioPayload } from '../cuestionario-envio-modal/cuestionario-envio-modal';

interface TecnologiaResumen {
  tecnologia: TecnologiaCuestionario;
  basico: number;
  junior: number;
  semiSenior: number;
  senior: number;
  cantidad: number;
}

interface EnvioCuestionarioHistorial {
  id: string;
  solicitudId: string;
  destinatarios: number;
  preguntas: number;
  duracion: string;
  resumen: string;
  fecha: string;
}

@Component({
  selector: 'app-cuestionarios-admin',
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    PageLayout,
    PageHeader,
    DataTable,
    Card,
    FormField,
    Button,
    AlertRegion,
    Tabs,
    CuestionarioEnvioModal,
  ],
  templateUrl: './cuestionarios-admin.html',
  styleUrl: './cuestionarios-admin.scss',
})
export class CuestionariosAdmin implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly cuestionariosService = inject(CuestionariosService);
  private readonly route = inject(ActivatedRoute);

  tecnologias: TecnologiaCuestionario[] = [];
  niveles: NivelCuestionario[] = [];
  preguntas: PreguntaCuestionario[] = [];
  resumenTecnologias: TecnologiaResumen[] = [];
  tecnologiaDetalle: TecnologiaCuestionario | null = null;
  busquedaTecnologia = '';
  busquedaPreguntas = '';
  preguntasSeleccionadas = new Set<string>();
  mostrarModalEnvio = false;
  alertaEnvio: AlertaUi | null = null;
  vistaActiva: 'armar' | 'crear' = 'armar';
  nivelBancoActivo = 'todos';
  tabsBanco: TabItem[] = [];
  historialEnvios: EnvioCuestionarioHistorial[] = [];
  resumenSeleccionPorTecnologia: Array<{ nombre: string; cantidad: number; duracion: string }> = [];
  paginaActual = 1;
  registrosPorPagina = 10;
  cargando = false;

  readonly opcionesRespuestaCorrecta = [0, 1, 2].map((indice) => ({
    indice,
    label: `Respuesta ${indice + 1}`,
  }));

  readonly formulario = this.fb.group({
    texto: ['', [Validators.required, Validators.minLength(5)]],
    tecnologiaId: [1, Validators.required],
    nivelId: [1, Validators.required],
    respuestas: this.fb.array([
      this.fb.control('', Validators.required),
      this.fb.control('', Validators.required),
      this.fb.control('', Validators.required),
    ]),
    respuestaCorrecta: [0, Validators.required],
    duracionMinutos: [45, [Validators.required, Validators.min(0)]],
    duracionSegundos: [0, [Validators.required, Validators.min(0), Validators.max(59)]],
  });

  readonly columnasPreguntas: DataTableColumn<PreguntaCuestionario>[] = [
    { key: 'id', label: 'ID pregunta', width: 105, sticky: 'left' },
    { key: 'fechaCreacion', label: 'Fecha creacion', width: 145 },
    {
      key: 'nivel',
      label: 'Nivel',
      width: 120,
      value: (pregunta) => this.obtenerNombreNivel(pregunta.nivelId),
    },
    { key: 'texto', label: 'Pregunta', width: 360, wrap: true },
    {
      key: 'duracion',
      label: 'Duracion',
      width: 120,
      value: (pregunta) => this.formatearDuracion(pregunta.duracionMinutos, pregunta.duracionSegundos),
    },
  ];

  readonly columnasTecnologias: DataTableColumn<TecnologiaResumen>[] = [
    {
      key: 'tecnologia',
      label: 'Tecnologia',
      width: 220,
      wrap: true,
      value: (row) => row.tecnologia.nombre,
    },
    { key: 'basico', label: 'Basico', width: 140 },
    { key: 'junior', label: 'Junior', width: 140 },
    { key: 'semiSenior', label: 'Semi Senior', width: 140 },
    { key: 'senior', label: 'Senior', width: 140 },
    { key: 'cantidad', label: 'Total', width: 140 },
  ];

  readonly columnasTecnologiasPorNivel: DataTableColumn<TecnologiaResumen>[] = [
    {
      key: 'tecnologia',
      label: 'Tecnologia',
      width: 280,
      wrap: true,
      value: (row) => row.tecnologia.nombre,
    },
    {
      key: 'cantidad',
      label: 'Cantidad',
      width: 180,
      value: (row) => this.cantidadBancoPorNivel(row),
    },
  ];

  ngOnInit() {
    this.vistaActiva = this.route.snapshot.data['vista'] === 'crear' ? 'crear' : 'armar';
    this.cargarCatalogosCuestionarios();
    this.cargarPreguntas();
    this.sincronizarDuracionConNivel();
  }

  get respuestas() {
    return this.formulario.get('respuestas') as FormArray;
  }

  get tecnologiaSeleccionada() {
    const tecnologiaId = Number(this.formulario.value.tecnologiaId);
    return this.tecnologias.find((tecnologia) => tecnologia.id === tecnologiaId) ?? this.tecnologias[0];
  }

  get tituloPagina() {
    return this.vistaActiva === 'crear' ? 'Banco de preguntas' : 'Armar y enviar test';
  }

  get subtituloPagina() {
    return 'Gestión de cuestionarios';
  }

  get respuestaCorrectaTexto() {
    return `Respuesta ${Number(this.formulario.value.respuestaCorrecta) + 1}`;
  }

  get nivelFormularioNombre() {
    return this.obtenerNombreNivel(Number(this.formulario.value.nivelId));
  }

  get duracionFormulario() {
    return this.formatearDuracion(this.obtenerDuracionNivelActual(), 0);
  }

  get tituloVistaActiva() {
    return this.vistaActiva === 'crear' ? 'Crear pregunta' : 'Armar y enviar test';
  }

  get columnasBanco() {
    return this.nivelBancoActivo === 'todos' ? this.columnasTecnologias : this.columnasTecnologiasPorNivel;
  }

  get tituloBanco() {
    return this.nivelBancoActivo === 'todos' ? 'Listado de tecnologias' : `Preguntas ${this.nombreNivelBancoActivo}`;
  }

  get nombreNivelBancoActivo() {
    return this.nivelBancoActivo !== 'todos' ? this.obtenerNombreNivel(Number(this.nivelBancoActivo)) : 'todos los niveles';
  }

  get subtituloBanco() {
    return `${this.tecnologiasFiltradas.length} tecnologias encontradas.`;
  }

  get preguntasSeleccionadasDetalle() {
    return this.preguntasParaEnviar.map((pregunta) => ({
      ...pregunta,
      tecnologia: this.obtenerNombreTecnologia(pregunta.tecnologiaId),
      nivel: this.obtenerNombreNivel(pregunta.nivelId),
      duracion: this.formatearDuracion(pregunta.duracionMinutos, pregunta.duracionSegundos),
    }));
  }

  get preguntasFiltradas() {
    const tecnologiaId = this.tecnologiaDetalle?.id;
    const busquedaNormalizada = this.normalizar(this.busquedaPreguntas);

    return this.preguntas.filter((pregunta) => {
      const coincideTecnologia = !tecnologiaId || pregunta.tecnologiaId === tecnologiaId;
      const coincideBusqueda = !busquedaNormalizada || this.normalizar(`${pregunta.id} ${pregunta.texto}`).includes(busquedaNormalizada);
      return coincideTecnologia && coincideBusqueda;
    });
  }

  get tecnologiasFiltradas() {
    const busquedaNormalizada = this.normalizar(this.busquedaTecnologia);

    return this.resumenTecnologias.filter((row) => {
      const texto = `${row.tecnologia.nombre} ${row.basico} ${row.junior} ${row.semiSenior} ${row.senior} ${row.cantidad}`;
      return !busquedaNormalizada || this.normalizar(texto).includes(busquedaNormalizada);
    });
  }

  get preguntasPaginadas() {
    const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
    return this.preguntasFiltradas.slice(inicio, inicio + this.registrosPorPagina);
  }

  get totalPreguntasDetalle() {
    return this.preguntasFiltradas.length;
  }

  get duracionTotalDetalle() {
    const totalSegundos = this.preguntasFiltradas.reduce(
      (total, pregunta) => total + pregunta.duracionMinutos * 60 + pregunta.duracionSegundos,
      0,
    );

    return this.formatearSegundos(totalSegundos);
  }

  get resumenNivelesDetalle() {
    return this.niveles.map((nivel) => ({
      nombre: nivel.nombre,
      cantidad: this.preguntasFiltradas.filter((pregunta) => pregunta.nivelId === nivel.id).length,
    }));
  }

  get preguntasParaEnviar() {
    return this.preguntas.filter((pregunta) => this.preguntasSeleccionadas.has(pregunta.id));
  }

  get cantidadPreguntasParaEnviar() {
    return this.preguntasParaEnviar.length;
  }

  get duracionParaEnviar() {
    const totalSegundos = this.preguntasParaEnviar.reduce(
      (total, pregunta) => total + pregunta.duracionMinutos * 60 + pregunta.duracionSegundos,
      0,
    );

    return this.formatearSegundos(totalSegundos);
  }

  get puedeEnviarCuestionario() {
    return this.cantidadPreguntasParaEnviar > 0;
  }

  get totalPreguntasBanco() {
    return this.preguntas.length;
  }

  get tecnologiasEnTest() {
    return new Set(this.preguntasParaEnviar.map((pregunta) => pregunta.tecnologiaId)).size;
  }

  get preguntasRecientes() {
    return [...this.preguntas].slice(0, 6);
  }

  get ultimosEnvios() {
    return this.historialEnvios.slice(0, 4);
  }

  get resumenTestSeleccionado() {
    if (this.preguntasParaEnviar.length === 0) {
      return 'Selecciona preguntas desde una o varias tecnologias para armar el test.';
    }

    const tecnologias = new Set(this.preguntasParaEnviar.map((pregunta) => this.obtenerNombreTecnologia(pregunta.tecnologiaId)));
    const niveles = new Set(this.preguntasParaEnviar.map((pregunta) => this.obtenerNombreNivel(pregunta.nivelId)));
    return `${tecnologias.size} tecnologia(s): ${Array.from(tecnologias).join(', ')}. ${niveles.size} nivel(es): ${Array.from(niveles).join(', ')}.`;
  }

  cargarPreguntas() {
    this.cargando = true;
    this.cuestionariosService
      .listar()
      .pipe(take(1))
      .subscribe({
        next: (preguntas) => {
          this.preguntas = preguntas;
          this.actualizarResumen();
          this.seleccionarTecnologiaInicial();
          this.actualizarResumenSeleccion();
          this.cargando = false;
        },
        error: () => {
          this.actualizarResumen();
          this.seleccionarTecnologiaInicial();
          this.cargando = false;
        },
      });
  }

  cargarCatalogosCuestionarios() {
    // Integración de catálogos para cuestionarios:
    // - habilidades alimenta el listado de tecnologías.
    // - niveles-habilidad alimenta los niveles y duración sugerida.
    forkJoin({
      tecnologias: this.cuestionariosService.listarTecnologias(),
      niveles: this.cuestionariosService.listarNiveles(),
    })
      .pipe(take(1))
      .subscribe(({ tecnologias, niveles }) => {
        this.tecnologias = tecnologias;
        this.niveles = niveles;
        this.tabsBanco = [{ id: 'todos', label: 'Todos' }, ...this.niveles.map((nivel) => ({ id: String(nivel.id), label: nivel.nombre }))];
        this.formulario.patchValue({
          tecnologiaId: this.tecnologias[0]?.id ?? 1,
          nivelId: this.niveles[0]?.id ?? 1,
          duracionMinutos: this.niveles[0]?.duracionMinutos ?? 45,
        });
        this.actualizarResumen();
        this.seleccionarTecnologiaInicial();
      });
  }

  agregarPregunta() {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    const valor = this.formulario.getRawValue();
    const duracionMinutos = this.obtenerDuracionNivelActual();
    this.cuestionariosService
      .crear({
        texto: valor.texto ?? '',
        tecnologiaId: Number(valor.tecnologiaId),
        nivelId: Number(valor.nivelId),
        respuestas: valor.respuestas.map((respuesta) => respuesta ?? ''),
        respuestaCorrecta: Number(valor.respuestaCorrecta),
        // La duracion no se captura manualmente: viene precargada desde nvhb_duracion del nivel.
        duracionMinutos,
        duracionSegundos: 0,
      })
      .pipe(take(1))
      .subscribe(() => {
        this.formulario.patchValue({
          texto: '',
          respuestas: ['', '', ''],
          respuestaCorrecta: 0,
        });
        this.formulario.markAsPristine();
        this.formulario.markAsUntouched();
        this.cargarPreguntas();
      });
  }

  cambiarVista(vista: 'armar' | 'crear') {
    this.vistaActiva = vista;
  }

  buscar() {
    this.paginaActual = 1;
  }

  limpiarBusquedaPreguntas() {
    this.busquedaPreguntas = '';
    this.paginaActual = 1;
  }

  limpiarBusquedaTecnologia() {
    this.busquedaTecnologia = '';
  }

  cambiarNivelBanco(nivel: string) {
    this.nivelBancoActivo = nivel;
  }

  cambiarPagina(pagina: number) {
    const totalPaginas = Math.max(1, Math.ceil(this.preguntasFiltradas.length / this.registrosPorPagina));
    this.paginaActual = Math.min(Math.max(pagina, 1), totalPaginas);
  }

  cambiarRegistrosPorPagina(registros: number) {
    this.registrosPorPagina = registros;
    this.paginaActual = 1;
  }

  actualizarPreguntasSeleccionadas(ids: Set<string>) {
    this.preguntasSeleccionadas = ids;
    this.actualizarResumenSeleccion();
  }

  obtenerIdPregunta(pregunta: PreguntaCuestionario) {
    return pregunta.id;
  }

  obtenerIdTecnologiaResumen(row: TecnologiaResumen) {
    return String(row.tecnologia.id);
  }

  cantidadBancoPorNivel(row: TecnologiaResumen) {
    if (this.nivelBancoActivo === 'todos') {
      return row.cantidad;
    }

    const nivel = this.obtenerNombreNivel(Number(this.nivelBancoActivo)).toLowerCase();
    if (nivel === 'basico') {
      return row.basico;
    }
    if (nivel === 'junior') {
      return row.junior;
    }
    if (nivel === 'semi senior') {
      return row.semiSenior;
    }
    return row.senior;
  }

  obtenerNombreNivel(nivelId: number) {
    return this.niveles.find((nivel) => nivel.id === nivelId)?.nombre ?? 'Sin nivel';
  }

  obtenerNombreTecnologia(tecnologiaId: number) {
    return this.tecnologias.find((tecnologia) => tecnologia.id === tecnologiaId)?.nombre ?? 'Sin tecnologia';
  }

  formatearDuracion(minutos: number, segundos: number) {
    return this.formatearSegundos(minutos * 60 + segundos);
  }

  verDetalleTecnologia(tecnologia: TecnologiaCuestionario) {
    this.tecnologiaDetalle = tecnologia;
    this.formulario.patchValue({ tecnologiaId: tecnologia.id });
    this.limpiarBusquedaPreguntas();
    this.alertaEnvio = null;
  }

  volverListadoTecnologias() {
    this.tecnologiaDetalle = null;
    this.limpiarBusquedaPreguntas();
    this.alertaEnvio = null;
  }

  abrirModalEnvio() {
    if (!this.puedeEnviarCuestionario) {
      return;
    }

    this.mostrarModalEnvio = true;
  }

  cerrarModalEnvio() {
    this.mostrarModalEnvio = false;
  }

  deseleccionarPreguntas() {
    this.preguntasSeleccionadas = new Set();
    this.actualizarResumenSeleccion();
  }

  quitarPreguntaSeleccionada(id: string) {
    const seleccion = new Set(this.preguntasSeleccionadas);
    seleccion.delete(id);
    this.preguntasSeleccionadas = seleccion;
    this.actualizarResumenSeleccion();
  }

  enviarCuestionario(payload: CuestionarioEnvioPayload) {
    if (!this.puedeEnviarCuestionario) {
      return;
    }

    this.historialEnvios = [
      {
        id: `ENV-${String(this.historialEnvios.length + 1).padStart(3, '0')}`,
        solicitudId: payload.solicitudId,
        destinatarios: payload.destinatarios.length,
        preguntas: this.cantidadPreguntasParaEnviar,
        duracion: this.duracionParaEnviar,
        resumen: this.resumenTestSeleccionado,
        fecha: new Intl.DateTimeFormat('es-CL').format(new Date()),
      },
      ...this.historialEnvios,
    ];
    this.alertaEnvio = {
      tipo: 'success',
      variante: 'soft',
      mensaje: `Test ${payload.solicitudId} enviado a ${payload.destinatarios.length} destinatario(s) con ${this.cantidadPreguntasParaEnviar} pregunta(s).`,
    };
    this.cerrarModalEnvio();
  }

  private sincronizarDuracionConNivel() {
    this.formulario.get('nivelId')?.valueChanges.subscribe((nivelId) => {
      const nivel = this.niveles.find((item) => item.id === Number(nivelId));
      if (nivel) {
        this.formulario.patchValue(
          { duracionMinutos: nivel.duracionMinutos, duracionSegundos: 0 },
          { emitEvent: false },
        );
      }
    });
  }

  private obtenerDuracionNivelActual() {
    const nivelId = Number(this.formulario.value.nivelId);
    return this.niveles.find((nivel) => nivel.id === nivelId)?.duracionMinutos ?? 45;
  }

  private actualizarResumen() {
    const obtenerNivelId = (nombre: string) => this.niveles.find((nivel) => nivel.nombre === nombre)?.id;
    const basicoId = obtenerNivelId('Basico');
    const juniorId = obtenerNivelId('Junior');
    const semiSeniorId = obtenerNivelId('Semi Senior');
    const seniorId = obtenerNivelId('Senior');

    this.resumenTecnologias = this.tecnologias.map((tecnologia) => ({
      tecnologia,
      basico: this.contarPreguntas(tecnologia.id, basicoId),
      junior: this.contarPreguntas(tecnologia.id, juniorId),
      semiSenior: this.contarPreguntas(tecnologia.id, semiSeniorId),
      senior: this.contarPreguntas(tecnologia.id, seniorId),
      cantidad: this.preguntas.filter((pregunta) => pregunta.tecnologiaId === tecnologia.id).length,
    }));
  }

  private actualizarResumenSeleccion() {
    const resumen = this.preguntasParaEnviar.reduce((mapa, pregunta) => {
      const tecnologia = this.obtenerNombreTecnologia(pregunta.tecnologiaId);
      const actual = mapa.get(tecnologia) ?? { nombre: tecnologia, cantidad: 0, segundos: 0 };
      actual.cantidad += 1;
      actual.segundos += pregunta.duracionMinutos * 60 + pregunta.duracionSegundos;
      mapa.set(tecnologia, actual);
      return mapa;
    }, new Map<string, { nombre: string; cantidad: number; segundos: number }>());

    this.resumenSeleccionPorTecnologia = Array.from(resumen.values()).map((item) => ({
      nombre: item.nombre,
      cantidad: item.cantidad,
      duracion: this.formatearSegundos(item.segundos),
    }));
  }

  private seleccionarTecnologiaInicial() {
    if (this.tecnologiaDetalle || this.tecnologias.length === 0) {
      return;
    }

    const tecnologiaConPreguntas = this.resumenTecnologias.find((item) => item.cantidad > 0);
    this.tecnologiaDetalle = tecnologiaConPreguntas?.tecnologia ?? this.tecnologias[0];
  }

  private contarPreguntas(tecnologiaId: number, nivelId?: number) {
    return this.preguntas.filter((pregunta) => pregunta.tecnologiaId === tecnologiaId && pregunta.nivelId === nivelId).length;
  }

  private formatearSegundos(totalSegundos: number) {
    const minutos = Math.floor(totalSegundos / 60);
    const segundos = totalSegundos % 60;

    if (minutos === 0) {
      return `${segundos} seg`;
    }

    if (segundos === 0) {
      return `${minutos} min`;
    }

    return `${minutos} min ${segundos} seg`;
  }

  private normalizar(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
  }
}
