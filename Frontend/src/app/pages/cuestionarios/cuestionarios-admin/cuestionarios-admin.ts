import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnDestroy, OnInit, inject } from '@angular/core';
import { FormArray, FormBuilder, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { catchError, finalize, forkJoin, map, of, Subscription, take, timeout } from 'rxjs';
import { CandidatosService, CandidatoApi, PostulacionCandidatoApi } from '../../../services/candidatos.service';
import {
  AsignacionCuestionarioApi,
  CuestionariosService,
  NivelCuestionario,
  PreguntaCuestionario,
  TecnologiaCuestionario,
} from '../../../services/cuestionarios.service';
import { SolicitudesService } from '../../../services/solicitudes.service';
import { Button } from '../../../shared/components/button/button';
import { Card } from '../../../shared/components/card/card';
import { DataTable, DataTableAction, DataTableActionEvent, DataTableColumn } from '../../../shared/components/data-table/data-table';
import { DatePicker } from '../../../shared/components/date-picker/date-picker';
import { AlertRegion } from '../../../shared/components/alert-region/alert-region';
import { FormField } from '../../../shared/components/form-field/form-field';
import { Modal } from '../../../shared/components/modal/modal';
import { PageHeader } from '../../../shared/components/page-header/page-header';
import { PageLayout } from '../../../shared/components/page-layout/page-layout';
import { TabItem, Tabs } from '../../../shared/components/tabs/tabs';
import { AlertaUi } from '../../../shared/models/alerta-ui.model';
import { obtenerMensajeError } from '../../../shared/utils/api-error';
import {
  CandidatoCuestionarioOption,
  CuestionarioEnvioModal,
  CuestionarioEnvioPayload,
  SolicitudCuestionarioOption,
} from '../cuestionario-envio-modal/cuestionario-envio-modal';

interface TecnologiaResumen {
  tecnologia: TecnologiaCuestionario;
  basico: number;
  junior: number;
  semiSenior: number;
  senior: number;
  cantidad: number;
  niveles: Array<{
    id: number;
    nombre: string;
    cantidad: number;
    duracion: string;
    porcentaje: number;
  }>;
  profundidad: string;
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
    DatePicker,
    Card,
    FormField,
    Modal,
    Button,
    AlertRegion,
    Tabs,
    CuestionarioEnvioModal,
  ],
  templateUrl: './cuestionarios-admin.html',
  styleUrl: './cuestionarios-admin.scss',
})
export class CuestionariosAdmin implements OnInit, OnDestroy {
  private readonly fb = inject(FormBuilder);
  private readonly cuestionariosService = inject(CuestionariosService);
  private readonly solicitudesService = inject(SolicitudesService);
  private readonly candidatosService = inject(CandidatosService);
  private readonly route = inject(ActivatedRoute);
  private readonly cdr = inject(ChangeDetectorRef);

  tecnologias: TecnologiaCuestionario[] = [];
  niveles: NivelCuestionario[] = [];
  preguntas: PreguntaCuestionario[] = [];
  resumenTecnologias: TecnologiaResumen[] = [];
  tecnologiaDetalle: TecnologiaCuestionario | null = null;
  busquedaTecnologia = '';
  busquedaTecnologiaArmar = '';
  busquedaPreguntas = '';
  preguntasSeleccionadas = new Set<string>();
  mostrarModalEnvio = false;
  alertaEnvio: AlertaUi | null = null;
  vistaActiva: 'armar' | 'crear' | 'asignaciones' = 'armar';
  nivelBancoActivo = 'todos';
  categoriaBancoActiva = 'todas';
  categoriaPreguntaActiva = 'todas';
  tabsBanco: TabItem[] = [];
  historialEnvios: EnvioCuestionarioHistorial[] = [];
  solicitudesEnvio: SolicitudCuestionarioOption[] = [];
  candidatosEnvio: CandidatoCuestionarioOption[] = [];
  asignaciones: AsignacionCuestionarioApi[] = [];
  resumenSeleccionPorTecnologia: Array<{ nombre: string; cantidad: number; duracion: string }> = [];
  asignacionReintento: AsignacionCuestionarioApi | null = null;
  reintentoFecha = '';
  reintentoHora = '18:00';
  guardandoReintento = false;
  paginaActual = 1;
  paginaBanco = 1;
  paginaAsignaciones = 1;
  registrosPorPagina = 10;
  registrosPorPaginaAsignaciones = 10;
  cargando = false;
  enviando = false;
  cargandoOpcionesEnvio = false;
  cargandoAsignaciones = false;
  errorAsignaciones = '';
  private tecnologiaSeleccionadaManualmente = false;
  private readonly subscriptions = new Subscription();

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
      label: 'Habilidad',
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

  readonly columnasPreguntasArmar: DataTableColumn<PreguntaCuestionario>[] = [
    { key: 'id', label: 'ID', width: 72, sticky: 'left' },
    {
      key: 'nivel',
      label: 'Nivel',
      width: 112,
      value: (pregunta) => this.obtenerNombreNivel(pregunta.nivelId),
    },
    { key: 'texto', label: 'Pregunta', width: 430, wrap: true },
    {
      key: 'duracion',
      label: 'Duracion',
      width: 92,
      value: (pregunta) => this.formatearDuracion(pregunta.duracionMinutos, pregunta.duracionSegundos),
    },
  ];

  readonly columnasTecnologiasPorNivel: DataTableColumn<TecnologiaResumen>[] = [
    {
      key: 'tecnologia',
      label: 'Habilidad',
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

  readonly columnasAsignaciones: DataTableColumn<AsignacionCuestionarioApi>[] = [
    { key: 'cdcu_id', label: 'ID', width: 90 },
    {
      key: 'cuestionario',
      label: 'Cuestionario',
      width: 240,
      wrap: true,
      value: (row) => row.cuestionario_nombre ?? `Cuestionario ${row.cdcu_cuestionario_id}`,
    },
    {
      key: 'candidato',
      label: 'Candidato',
      width: 220,
      wrap: true,
      value: (row) => row.candidato_email ?? `Candidato ${row.cdcu_candidato_id}`,
    },
    {
      key: 'estado',
      label: 'Estado',
      width: 145,
      type: 'badge',
      value: (row) => row.estado_nombre,
      className: (row) => this.claseEstadoAsignacion(row.estado_nombre),
    },
    {
      key: 'resultado',
      label: 'Resultado',
      width: 145,
      value: (row) => this.resultadoAsignacion(row),
    },
    {
      key: 'vencimiento',
      label: 'Vencimiento',
      width: 145,
      value: (row) => this.formatearFecha(row.cdcu_fecha_vencimiento),
    },
    {
      key: 'preguntas',
      label: 'Preguntas',
      width: 110,
      value: (row) => row.cantidad_preguntas,
    },
  ];

  readonly accionesAsignaciones: DataTableAction<AsignacionCuestionarioApi>[] = [
    {
      id: 'cancelar',
      label: 'Cancelar asignacion',
      icon: 'cancel',
      visible: (row) => !this.esAsignacionCancelada(row),
      disabled: (row) => !this.puedeCancelarAsignacion(row),
    },
    {
      id: 'editar',
      label: 'Editar asignacion',
      icon: 'edit',
      visible: (row) => !this.esAsignacionCancelada(row),
      disabled: (row) => !this.puedeEditarAsignacion(row),
    },
  ];

  ngOnInit() {
    this.sincronizarDuracionConNivel();
    this.subscriptions.add(
      this.route.data.subscribe((data) => {
        this.vistaActiva = data['vista'] === 'crear'
          ? 'crear'
          : data['vista'] === 'asignaciones'
            ? 'asignaciones'
            : 'armar';
        this.reiniciarEstadoEntrada();
        if (this.vistaActiva === 'asignaciones') {
          this.cargarAsignaciones();
        } else {
          this.cargarDatosCuestionarios();
        }
      }),
    );
  }

  ngOnDestroy() {
    this.subscriptions.unsubscribe();
  }

  get respuestas() {
    return this.formulario.get('respuestas') as FormArray;
  }

  get tecnologiaSeleccionada() {
    const tecnologiaId = Number(this.formulario.value.tecnologiaId);
    return this.tecnologias.find((tecnologia) => tecnologia.id === tecnologiaId) ?? this.tecnologias[0];
  }

  get tituloPagina() {
    if (this.vistaActiva === 'crear') {
      return 'Banco de preguntas';
    }

    if (this.vistaActiva === 'asignaciones') {
      return 'Asignaciones de cuestionarios';
    }

    return 'Armar y enviar cuestionario';
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
    if (this.vistaActiva === 'crear') {
      return 'Crear pregunta';
    }

    if (this.vistaActiva === 'asignaciones') {
      return 'Asignaciones de cuestionarios';
    }

    return 'Armar y enviar cuestionario';
  }

  get columnasBanco() {
    return this.nivelBancoActivo === 'todos' ? this.columnasTecnologias : this.columnasTecnologiasPorNivel;
  }

  get tituloBanco() {
    return this.nivelBancoActivo === 'todos' ? 'Listado de habilidades' : `Preguntas ${this.nombreNivelBancoActivo}`;
  }

  get nombreNivelBancoActivo() {
    return this.nivelBancoActivo !== 'todos' ? this.obtenerNombreNivel(Number(this.nivelBancoActivo)) : 'todos los niveles';
  }

  get subtituloBanco() {
    return `${this.tecnologiasFiltradas.length} habilidades encontradas.`;
  }

  get categoriasTecnologia() {
    const categorias = new Map<string, { id: string; nombre: string }>();

    this.tecnologias.forEach((tecnologia) => {
      const id = tecnologia.categoriaId != null
        ? String(tecnologia.categoriaId)
        : 'sin-categoria';
      categorias.set(id, {
        id,
        nombre: tecnologia.categoriaNombre,
      });
    });

    return Array.from(categorias.values()).sort((a, b) =>
      a.nombre.localeCompare(b.nombre, 'es-CL', { sensitivity: 'base' }),
    );
  }

  get categoriasFiltroBanco() {
    return [
      { id: 'todas', nombre: 'Todas' },
      ...this.categoriasTecnologia,
    ];
  }

  get tecnologiasFormularioPorCategoria() {
    return this.agruparTecnologiasPorCategoria(
      this.tecnologias.map((tecnologia) => this.resumenPorTecnologia(tecnologia)),
    );
  }

  get tecnologiasFormularioFiltradas() {
    const tecnologias = this.tecnologias.filter((tecnologia) => {
      const categoriaId = tecnologia.categoriaId != null
        ? String(tecnologia.categoriaId)
        : 'sin-categoria';

      return this.categoriaPreguntaActiva === 'todas' || this.categoriaPreguntaActiva === categoriaId;
    });

    return tecnologias.length ? tecnologias : this.tecnologias;
  }

  get tecnologiasFormularioFiltradasPorCategoria() {
    return this.agruparTecnologiasPorCategoria(
      this.tecnologiasFormularioFiltradas.map((tecnologia) => this.resumenPorTecnologia(tecnologia)),
    );
  }

  get tecnologiasFiltradasPorCategoria() {
    return this.agruparTecnologiasPorCategoria(this.tecnologiasFiltradasArmar);
  }

  get tecnologiasFiltradasArmar() {
    const busquedaNormalizada = this.normalizar(this.busquedaTecnologiaArmar);

    return this.resumenTecnologias.filter((row) => {
      const texto = `${row.tecnologia.categoriaNombre} ${row.tecnologia.nombre} ${row.basico} ${row.junior} ${row.semiSenior} ${row.senior} ${row.cantidad}`;
      return !busquedaNormalizada || this.normalizar(texto).includes(busquedaNormalizada);
    });
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
      const categoriaId =
        row.tecnologia.categoriaId != null
          ? String(row.tecnologia.categoriaId)
          : 'sin-categoria';
      const coincideCategoria =
        this.categoriaBancoActiva === 'todas' ||
        this.categoriaBancoActiva === categoriaId;
      const texto = `${row.tecnologia.categoriaNombre} ${row.tecnologia.nombre} ${row.basico} ${row.junior} ${row.semiSenior} ${row.senior} ${row.cantidad}`;
      const coincideBusqueda =
        !busquedaNormalizada ||
        this.normalizar(texto).includes(busquedaNormalizada);

      return coincideCategoria && coincideBusqueda;
    });
  }

  get tecnologiasBancoPaginadas() {
    const inicio = (this.paginaBanco - 1) * 10;
    return this.tecnologiasFiltradas.slice(inicio, inicio + 10);
  }

  get preguntasPaginadas() {
    const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
    return this.preguntasFiltradas.slice(inicio, inicio + this.registrosPorPagina);
  }

  get preguntasBancoDetalle() {
    const tecnologiaId = this.tecnologiaDetalle?.id;
    const nivelId = this.nivelBancoActivo === 'todos' ? null : Number(this.nivelBancoActivo);

    if (!tecnologiaId) {
      return [];
    }

    return this.preguntas.filter((pregunta) =>
      pregunta.tecnologiaId === tecnologiaId &&
      (!nivelId || pregunta.nivelId === nivelId),
    );
  }

  get preguntasBancoDetallePaginadas() {
    const inicio = (this.paginaActual - 1) * this.registrosPorPagina;
    return this.preguntasBancoDetalle.slice(inicio, inicio + this.registrosPorPagina);
  }

  get asignacionesPaginadas() {
    const inicio = (this.paginaAsignaciones - 1) * this.registrosPorPaginaAsignaciones;
    return this.asignaciones.slice(inicio, inicio + this.registrosPorPaginaAsignaciones);
  }

  get tituloDetalleBanco() {
    const tecnologia = this.tecnologiaDetalle?.nombre ?? 'Habilidad';

    return this.nivelBancoActivo === 'todos'
      ? `Preguntas creadas: ${tecnologia}`
      : `Preguntas ${this.nombreNivelBancoActivo}: ${tecnologia}`;
  }

  get subtituloDetalleBanco() {
    return `${this.preguntasBancoDetalle.length} preguntas encontradas.`;
  }

  get anchoDetalleBanco(): 'md' | 'lg' | 'xl' {
    return this.preguntasBancoDetalle.length === 0 ? 'md' : 'xl';
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
    return this.resumenTecnologiaDetalle?.niveles ?? [];
  }

  get resumenTecnologiaDetalle() {
    if (!this.tecnologiaDetalle) {
      return null;
    }

    return this.resumenTecnologias.find(
      (item) => item.tecnologia.id === this.tecnologiaDetalle?.id,
    ) ?? null;
  }

  get profundidadTecnologiaDetalle() {
    const resumen = this.resumenTecnologiaDetalle;

    if (!resumen || resumen.cantidad === 0) {
      return 'Sin preguntas creadas para esta habilidad.';
    }

    return resumen.profundidad;
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
      return 'Selecciona preguntas desde una o varias habilidades para armar el cuestionario.';
    }

    const tecnologias = new Set(this.preguntasParaEnviar.map((pregunta) => this.obtenerNombreTecnologia(pregunta.tecnologiaId)));
    const niveles = new Set(this.preguntasParaEnviar.map((pregunta) => this.obtenerNombreNivel(pregunta.nivelId)));
    return `${tecnologias.size} habilidad(es): ${Array.from(tecnologias).join(', ')}. ${niveles.size} nivel(es): ${Array.from(niveles).join(', ')}.`;
  }

  get fechaHoyInput() {
    return new Date().toISOString().slice(0, 10);
  }

  cargarDatosCuestionarios() {
    if (this.vistaActiva === 'armar') {
      this.prepararEntradaArmar();
    }

    this.cargando = true;
    this.refrescarVista();
    forkJoin({
      tecnologias: this.cuestionariosService.listarTecnologias(),
      niveles: this.cuestionariosService.listarNiveles(),
      preguntas: this.cuestionariosService.listar(),
    })
      .pipe(take(1))
      .subscribe({
        next: ({ tecnologias, niveles, preguntas }) => {
          this.tecnologias = tecnologias;
          this.niveles = niveles;
          this.preguntas = preguntas;
          this.tabsBanco = [{ id: 'todos', label: 'Todos' }, ...this.niveles.map((nivel) => ({ id: String(nivel.id), label: nivel.nombre }))];
          this.formulario.patchValue({
            tecnologiaId: this.tecnologias[0]?.id ?? 1,
            nivelId: this.niveles[0]?.id ?? 1,
            duracionMinutos: this.niveles[0]?.duracionMinutos ?? 45,
          });
          this.actualizarResumen();
          this.seleccionarTecnologiaInicial();
          this.actualizarResumenSeleccion();
          this.cargando = false;
          this.refrescarVista();
        },
        error: () => {
          this.tecnologias = [];
          this.niveles = [];
          this.preguntas = [];
          this.tabsBanco = [{ id: 'todos', label: 'Todos' }];
          this.actualizarResumen();
          this.seleccionarTecnologiaInicial();
          this.cargando = false;
          this.refrescarVista();
        },
      });
  }

  cargarOpcionesEnvio() {
    this.cargandoOpcionesEnvio = true;

    forkJoin({
      solicitudes: this.solicitudesService.listar().pipe(timeout(5000), catchError(() => of([]))),
      candidatos: this.candidatosService.listar().pipe(timeout(5000), catchError(() => of([]))),
    })
      .pipe(
        take(1),
        map(({ solicitudes, candidatos }) => ({
          solicitudes: solicitudes.map((solicitud) => ({
            id: Number(solicitud.id),
            codigo: solicitud.codigo,
            cargo: solicitud.cargo || solicitud.nombre || 'Solicitud sin cargo',
            cliente: solicitud.cliente || solicitud.empresaCliente || 'Cliente sin nombre',
            estado: solicitud.estado || 'Sin estado',
          })),
          candidatos,
        })),
      )
      .subscribe({
        next: ({ solicitudes, candidatos }) => {
          this.solicitudesEnvio = solicitudes;

          if (candidatos.length === 0) {
            this.candidatosEnvio = [];
            this.cargandoOpcionesEnvio = false;
            return;
          }

          forkJoin(
            candidatos.map((candidato) =>
              this.candidatosService.listarSolicitudes(String(candidato.cand_id)).pipe(
                timeout(4000),
                catchError(() => of([] as PostulacionCandidatoApi[])),
                map((postulaciones) => this.mapearCandidatoEnvio(candidato, postulaciones)),
              ),
            ),
          )
            .pipe(take(1))
            .subscribe({
              next: (candidatosPorSolicitud) => {
                this.candidatosEnvio = candidatosPorSolicitud.flat();
                this.cargandoOpcionesEnvio = false;
              },
              error: () => {
                this.candidatosEnvio = [];
                this.cargandoOpcionesEnvio = false;
              },
            });
        },
        error: () => {
          this.solicitudesEnvio = [];
          this.candidatosEnvio = [];
          this.cargandoOpcionesEnvio = false;
        },
      });
  }

  cargarAsignaciones() {
    this.cargandoAsignaciones = true;
    this.errorAsignaciones = '';
    this.refrescarVista();

    this.cuestionariosService
      .listarAsignaciones()
      .pipe(
        timeout(8000),
        take(1),
        finalize(() => {
          this.cargandoAsignaciones = false;
          this.refrescarVista();
        }),
      )
      .subscribe({
        next: (asignaciones) => {
          this.asignaciones = asignaciones;
          this.paginaAsignaciones = 1;
          this.refrescarVista();
        },
        error: (error) => {
          this.asignaciones = [];
          this.errorAsignaciones = obtenerMensajeError(error, 'No se pudieron cargar las asignaciones de cuestionarios.');
          this.refrescarVista();
        },
      });
  }

  cargarPreguntas() {
    this.cargando = true;
    this.refrescarVista();
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
          this.refrescarVista();
        },
        error: () => {
          this.actualizarResumen();
          this.seleccionarTecnologiaInicial();
          this.cargando = false;
          this.refrescarVista();
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
        this.alertaEnvio = {
          tipo: 'success',
          variante: 'soft',
          mensaje: 'Pregunta creada en el banco técnico.',
        };
      }, (error) => {
        this.alertaEnvio = {
          tipo: 'danger',
          variante: 'soft',
          mensaje: obtenerMensajeError(error, 'No se pudo crear la pregunta. Revisa los datos e intenta nuevamente.'),
        };
      });
  }

  cambiarVista(vista: 'armar' | 'crear' | 'asignaciones') {
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
    this.busquedaTecnologiaArmar = '';
    this.categoriaBancoActiva = 'todas';
    this.seleccionarTecnologiaInicial();
  }

  cambiarCategoriaPregunta() {
    const tecnologiaActualId = Number(this.formulario.value.tecnologiaId);
    const tecnologiaActualVisible = this.tecnologiasFormularioFiltradas.some(
      (tecnologia) => tecnologia.id === tecnologiaActualId,
    );

    if (!tecnologiaActualVisible) {
      this.formulario.patchValue({
        tecnologiaId: this.tecnologiasFormularioFiltradas[0]?.id ?? this.tecnologias[0]?.id ?? 1,
      });
    }
  }

  cambiarNivelBanco(nivel: string) {
    this.nivelBancoActivo = nivel;
    this.paginaBanco = 1;
  }

  cambiarCategoriaBanco() {
    this.paginaBanco = 1;
    this.tecnologiaDetalle = null;
  }

  cambiarPaginaBanco(pagina: number) {
    const totalPaginas = Math.max(1, Math.ceil(this.tecnologiasFiltradas.length / 10));
    this.paginaBanco = Math.min(Math.max(pagina, 1), totalPaginas);
  }

  cambiarPaginaAsignaciones(pagina: number) {
    const totalPaginas = Math.max(1, Math.ceil(this.asignaciones.length / this.registrosPorPaginaAsignaciones));
    this.paginaAsignaciones = Math.min(Math.max(pagina, 1), totalPaginas);
  }

  cambiarRegistrosPorPaginaAsignaciones(registros: number) {
    this.registrosPorPaginaAsignaciones = registros;
    this.paginaAsignaciones = 1;
  }

  cambiarPagina(pagina: number) {
    const totalPaginas = Math.max(1, Math.ceil(this.preguntasFiltradas.length / this.registrosPorPagina));
    this.paginaActual = Math.min(Math.max(pagina, 1), totalPaginas);
  }

  cambiarPaginaDetalleBanco(pagina: number) {
    const totalPaginas = Math.max(1, Math.ceil(this.preguntasBancoDetalle.length / this.registrosPorPagina));
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

    return row.niveles.find((nivel) => nivel.id === Number(this.nivelBancoActivo))?.cantidad ?? 0;
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
    this.tecnologiaSeleccionadaManualmente = true;
    this.tecnologiaDetalle = tecnologia;
    this.formulario.patchValue({ tecnologiaId: tecnologia.id });
    this.limpiarBusquedaPreguntas();
    this.alertaEnvio = null;
  }

  verPreguntasBanco(row: TecnologiaResumen) {
    this.tecnologiaDetalle = row.tecnologia;
    this.formulario.patchValue({ tecnologiaId: row.tecnologia.id });
    this.busquedaPreguntas = '';
    this.paginaActual = 1;
  }

  cerrarDetalleBanco() {
    this.tecnologiaDetalle = null;
    this.paginaActual = 1;
  }

  volverListadoTecnologias() {
    this.tecnologiaSeleccionadaManualmente = false;
    this.tecnologiaDetalle = null;
    this.limpiarBusquedaPreguntas();
    this.alertaEnvio = null;
  }

  abrirModalEnvio() {
    if (!this.puedeEnviarCuestionario) {
      return;
    }

    this.mostrarModalEnvio = true;
    this.cargarOpcionesEnvio();
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

    this.enviando = true;
    this.cuestionariosService
      .crearYAsignarCuestionario({
        solicitudId: payload.solicitudId,
        preguntaIds: this.preguntasParaEnviar.map((pregunta) => Number(pregunta.id)),
        candidatoIds: payload.candidatoIds,
        fechaVencimiento: payload.fechaVencimiento,
        descripcion: payload.mensaje || null,
      })
      .pipe(
        take(1),
        finalize(() => {
          this.enviando = false;
        }),
      )
      .subscribe({
        next: (resultado) => {
          this.historialEnvios = [
            {
              id: `CUEST-${resultado.cuestionario_id}`,
              solicitudId: String(resultado.solicitud_id),
              destinatarios: resultado.total_asignados,
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
            mensaje: `Cuestionario enviado a ${resultado.total_asignados} candidato(s). ${resultado.total_omitidos_ya_asignados} ya estaban asignado(s).`,
          };
          this.deseleccionarPreguntas();
          this.cerrarModalEnvio();
          this.cargarAsignaciones();
        },
        error: (error) => {
          this.alertaEnvio = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo enviar el cuestionario. Revisa la solicitud, candidatos y vencimiento.'),
          };
        },
      });
  }

  manejarAccionAsignacion(evento: DataTableActionEvent<AsignacionCuestionarioApi>) {
    if (evento.action === 'cancelar') {
      this.cancelarAsignacion(evento.row);
      return;
    }

    if (evento.action === 'editar') {
      this.editarAsignacion(evento.row);
    }
  }

  editarAsignacion(asignacion: AsignacionCuestionarioApi) {
    if (this.esErrorTecnico(asignacion)) {
      this.habilitarReintento(asignacion);
      return;
    }

    if (this.puedeMarcarErrorTecnico(asignacion)) {
      this.marcarErrorTecnico(asignacion);
    }
  }

  cancelarAsignacion(asignacion: AsignacionCuestionarioApi) {
    this.cuestionariosService
      .cancelarAsignacion(asignacion.cdcu_id)
      .pipe(take(1))
      .subscribe({
        next: () => {
          this.alertaEnvio = {
            tipo: 'success',
            variante: 'soft',
            mensaje: 'Asignacion cancelada correctamente.',
          };
          this.cargarAsignaciones();
        },
        error: (error) => {
          this.alertaEnvio = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo cancelar la asignacion.'),
          };
        },
      });
  }

  marcarErrorTecnico(asignacion: AsignacionCuestionarioApi) {
    this.cuestionariosService
      .marcarErrorTecnico(asignacion.cdcu_id)
      .pipe(take(1))
      .subscribe({
        next: () => {
          this.alertaEnvio = {
            tipo: 'success',
            variante: 'soft',
            mensaje: 'Asignacion marcada con error tecnico.',
          };
          this.cargarAsignaciones();
        },
        error: (error) => {
          this.alertaEnvio = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo marcar el error tecnico.'),
          };
        },
      });
  }

  habilitarReintento(asignacion: AsignacionCuestionarioApi) {
    this.asignacionReintento = asignacion;
    this.reintentoFecha = '';
    this.reintentoHora = '18:00';
  }

  cerrarModalReintento() {
    this.asignacionReintento = null;
    this.reintentoFecha = '';
    this.reintentoHora = '18:00';
  }

  confirmarReintento() {
    if (!this.asignacionReintento || !this.reintentoFecha || !this.reintentoHora) {
      this.alertaEnvio = {
        tipo: 'warning',
        variante: 'soft',
        mensaje: 'Selecciona nueva fecha y hora de vencimiento para habilitar el reintento.',
      };
      return;
    }

    const fechaVencimiento = `${this.reintentoFecha}T${this.reintentoHora}:00`;
    this.guardandoReintento = true;

    this.cuestionariosService
      .habilitarReintento(this.asignacionReintento.cdcu_id, fechaVencimiento)
      .pipe(
        take(1),
        finalize(() => {
          this.guardandoReintento = false;
        }),
      )
      .subscribe({
        next: () => {
          this.alertaEnvio = {
            tipo: 'success',
            variante: 'soft',
            mensaje: 'Reintento habilitado correctamente.',
          };
          this.cerrarModalReintento();
          this.cargarAsignaciones();
        },
        error: (error) => {
          this.alertaEnvio = {
            tipo: 'danger',
            variante: 'soft',
            mensaje: obtenerMensajeError(error, 'No se pudo habilitar el reintento.'),
          };
        },
      });
  }

  obtenerIdAsignacion(asignacion: AsignacionCuestionarioApi) {
    return String(asignacion.cdcu_id);
  }

  resultadoAsignacion(asignacion: AsignacionCuestionarioApi) {
    if (asignacion.cdcu_aprobado == null) {
      return asignacion.cdcu_porcentaje_obtenido == null ? 'Pendiente' : `${asignacion.cdcu_porcentaje_obtenido}%`;
    }

    return asignacion.cdcu_aprobado
      ? `Aprobado ${asignacion.cdcu_porcentaje_obtenido ?? ''}%`.trim()
      : `Reprobado ${asignacion.cdcu_porcentaje_obtenido ?? ''}%`.trim();
  }

  claseEstadoAsignacion(estado: string) {
    const estadoNormalizado = this.normalizar(estado);

    if (estadoNormalizado.includes('finalizado')) {
      return 'status-success';
    }

    if (estadoNormalizado.includes('error')) {
      return 'status-warning';
    }

    if (estadoNormalizado.includes('cancelado') || estadoNormalizado.includes('vencido')) {
      return 'status-danger';
    }

    return 'status-info';
  }

  puedeCancelarAsignacion(asignacion: AsignacionCuestionarioApi) {
    const estado = this.normalizar(asignacion.estado_nombre);
    return estado.includes('asignado') || estado.includes('progreso');
  }

  puedeMarcarErrorTecnico(asignacion: AsignacionCuestionarioApi) {
    const estado = this.normalizar(asignacion.estado_nombre);
    return estado.includes('asignado') || estado.includes('progreso');
  }

  puedeEditarAsignacion(asignacion: AsignacionCuestionarioApi) {
    return this.puedeMarcarErrorTecnico(asignacion) || this.esErrorTecnico(asignacion);
  }

  esAsignacionCancelada(asignacion: AsignacionCuestionarioApi) {
    return this.normalizar(asignacion.estado_nombre).includes('cancelado');
  }

  esErrorTecnico(asignacion: AsignacionCuestionarioApi) {
    return this.normalizar(asignacion.estado_nombre).includes('error');
  }

  formatearFecha(valor?: string | null) {
    if (!valor) {
      return 'Sin fecha';
    }

    const fecha = new Date(valor);

    if (Number.isNaN(fecha.getTime())) {
      return valor;
    }

    return new Intl.DateTimeFormat('es-CL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(fecha);
  }

  private mapearCandidatoEnvio(candidato: CandidatoApi, postulaciones: PostulacionCandidatoApi[]) {
    const nombre = [
      candidato.cand_nombres,
      candidato.cand_apellido_paterno,
      candidato.cand_apellido_materno,
    ]
      .filter(Boolean)
      .join(' ') || candidato.cand_email || `Candidato ${candidato.cand_id}`;

    const email = candidato.cand_email ?? 'Sin correo';

    return postulaciones.map((postulacion) => ({
      id: candidato.cand_id,
      nombre,
      correo: email,
      solicitudId: postulacion.slcd_solicitud_id,
      estado: this.estadoPostulacion(postulacion.slcd_estado_solicitud_candidato_id),
    }));
  }

  private estadoPostulacion(estadoId?: number | null) {
    const estados = new Map([
      [1, 'En revision'],
      [2, 'En entrevista'],
      [3, 'Inhabilitado'],
      [4, 'Seleccionado'],
      [5, 'Descartado'],
      [6, 'Contratado'],
    ]);

    return estadoId ? estados.get(estadoId) ?? `Estado ${estadoId}` : 'Sin estado';
  }

  private sincronizarDuracionConNivel() {
    const nivelControl = this.formulario.get('nivelId');
    if (!nivelControl) {
      return;
    }

    this.subscriptions.add(
      nivelControl.valueChanges.subscribe((nivelId) => {
        const nivel = this.niveles.find((item) => item.id === Number(nivelId));
        if (nivel) {
          this.formulario.patchValue(
            { duracionMinutos: nivel.duracionMinutos, duracionSegundos: 0 },
            { emitEvent: false },
          );
        }
      }),
    );
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

    this.resumenTecnologias = this.tecnologias.map((tecnologia) => {
      const preguntasTecnologia = this.preguntas.filter((pregunta) => pregunta.tecnologiaId === tecnologia.id);
      const cantidad = preguntasTecnologia.length;
      const niveles = this.niveles.map((nivel) => {
        const preguntasNivel = preguntasTecnologia.filter((pregunta) => pregunta.nivelId === nivel.id);
        const totalSegundos = preguntasNivel.reduce(
          (total, pregunta) => total + pregunta.duracionMinutos * 60 + pregunta.duracionSegundos,
          0,
        );

        return {
          id: nivel.id,
          nombre: nivel.nombre,
          cantidad: preguntasNivel.length,
          duracion: this.formatearSegundos(totalSegundos),
          porcentaje: cantidad > 0 ? Math.round((preguntasNivel.length / cantidad) * 100) : 0,
        };
      });
      const nivelesConPreguntas = niveles.filter((nivel) => nivel.cantidad > 0);

      return {
        tecnologia,
        basico: this.contarPreguntas(tecnologia.id, basicoId),
        junior: this.contarPreguntas(tecnologia.id, juniorId),
        semiSenior: this.contarPreguntas(tecnologia.id, semiSeniorId),
        senior: this.contarPreguntas(tecnologia.id, seniorId),
        cantidad,
        niveles,
        profundidad: nivelesConPreguntas.length
          ? nivelesConPreguntas.map((nivel) => `${nivel.nombre}: ${nivel.cantidad}`).join(' / ')
          : 'Sin preguntas',
      };
    });
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
    if (this.vistaActiva === 'crear' || this.tecnologiaSeleccionadaManualmente || this.tecnologias.length === 0) {
      return;
    }

    const tecnologiaConPreguntas = this.resumenTecnologias.find((item) => item.cantidad > 0);
    const tecnologiaActual = this.tecnologiaDetalle
      ? this.resumenTecnologias.find((item) => item.tecnologia.id === this.tecnologiaDetalle?.id)
      : null;
    const debeReemplazarSeleccion =
      !tecnologiaActual ||
      (tecnologiaActual.cantidad === 0 && Boolean(tecnologiaConPreguntas));

    if (debeReemplazarSeleccion) {
      this.tecnologiaDetalle = tecnologiaConPreguntas?.tecnologia ?? this.tecnologias[0];
      this.formulario.patchValue({ tecnologiaId: this.tecnologiaDetalle.id });
    }
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

  private reiniciarEstadoEntrada() {
    this.busquedaTecnologia = '';
    this.busquedaTecnologiaArmar = '';
    this.busquedaPreguntas = '';
    this.nivelBancoActivo = 'todos';
    this.categoriaBancoActiva = 'todas';
    this.categoriaPreguntaActiva = 'todas';
    this.paginaActual = 1;
    this.paginaBanco = 1;
    this.paginaAsignaciones = 1;
    this.tecnologiaDetalle = null;
    this.tecnologiaSeleccionadaManualmente = false;

    if (this.vistaActiva === 'armar') {
      this.preguntasSeleccionadas = new Set();
      this.actualizarResumenSeleccion();
    }
  }

  private prepararEntradaArmar() {
    this.busquedaTecnologia = '';
    this.busquedaTecnologiaArmar = '';
    this.busquedaPreguntas = '';
    this.categoriaBancoActiva = 'todas';
    this.paginaActual = 1;
    this.paginaBanco = 1;
    this.paginaAsignaciones = 1;
    this.tecnologiaSeleccionadaManualmente = false;
  }

  private refrescarVista() {
    this.cdr.detectChanges();
  }

  private agruparTecnologiasPorCategoria(rows: TecnologiaResumen[]) {
    const grupos = new Map<string, { nombre: string; items: TecnologiaResumen[] }>();

    rows.forEach((row) => {
      const key = row.tecnologia.categoriaId != null
        ? String(row.tecnologia.categoriaId)
        : 'sin-categoria';
      const grupo = grupos.get(key) ?? {
        nombre: row.tecnologia.categoriaNombre,
        items: [],
      };

      grupo.items.push(row);
      grupos.set(key, grupo);
    });

    return Array.from(grupos.values())
      .map((grupo) => ({
        ...grupo,
        items: grupo.items.sort((a, b) =>
          a.tecnologia.nombre.localeCompare(b.tecnologia.nombre, 'es-CL', { sensitivity: 'base' }),
        ),
      }))
      .sort((a, b) =>
        a.nombre.localeCompare(b.nombre, 'es-CL', { sensitivity: 'base' }),
      );
  }

  private resumenPorTecnologia(tecnologia: TecnologiaCuestionario): TecnologiaResumen {
    return this.resumenTecnologias.find((row) => row.tecnologia.id === tecnologia.id) ?? {
      tecnologia,
      basico: 0,
      junior: 0,
      semiSenior: 0,
      senior: 0,
      cantidad: 0,
      niveles: [],
      profundidad: 'Sin preguntas',
    };
  }
}
