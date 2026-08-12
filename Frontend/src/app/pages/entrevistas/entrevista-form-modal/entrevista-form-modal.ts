import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { ReactiveFormsModule, UntypedFormControl, UntypedFormGroup, Validators } from '@angular/forms';
import { Button } from '../../../shared/components/button/button';
import { DataTable, DataTableColumn } from '../../../shared/components/data-table/data-table';
import { FormActions } from '../../../shared/components/form-actions/form-actions';
import { FormField } from '../../../shared/components/form-field/form-field';
import { FormSection } from '../../../shared/components/form-section/form-section';
import { IconButton } from '../../../shared/components/icon-button/icon-button';
import { Modal } from '../../../shared/components/modal/modal';
import { Stepper } from '../../../shared/components/stepper/stepper';
import { EntrevistaPayload, TipoEntrevista } from '../../../services/entrevistas.service';
import { CatalogosService, UsuarioCatalogoApi } from '../../../services/catalogos.service';
import { catchError, forkJoin, of, take, timeout } from 'rxjs';

interface IntegranteEntrevista {
  id: string;
  nombre: string;
  rol: string;
  fechaAgendamiento: string;
}

export interface EntrevistaCandidatoSeleccionado {
  id?: string;
  idSolicitud: string;
  nombre: string;
  cargo: string;
}

@Component({
  selector: 'app-entrevista-form-modal',
  imports: [CommonModule, ReactiveFormsModule, Button, DataTable, FormActions, FormField, FormSection, IconButton, Modal, Stepper],
  templateUrl: './entrevista-form-modal.html',
  styleUrl: './entrevista-form-modal.scss',
})
export class EntrevistaFormModal implements OnChanges, OnInit {
  @Input() initialData: Partial<EntrevistaPayload> | null = null;
  @Input() candidatos: EntrevistaCandidatoSeleccionado[] = [];

  @Output() cerrar = new EventEmitter<void>();
  @Output() candidatosChange = new EventEmitter<EntrevistaCandidatoSeleccionado[]>();
  @Output() guardar = new EventEmitter<EntrevistaPayload>();

  tipos: TipoEntrevista[] = ['Reclutamiento', 'Técnica', 'Operacional'];
  modalidades: EntrevistaPayload['modalidad'][] = ['Online', 'Presencial', 'Híbrida'];
  readonly duraciones = ['30 min', '45 min', '60 min', '90 min'];
  integrantesSeleccionados = new Set(['macarena-lopez', 'felipe-valdes']);
  tabFormulario = 'datos';

  pasosFormulario = [
    { clave: 'datos', numero: 1, titulo: 'Datos' },
    { clave: 'agenda', numero: 2, titulo: 'Agenda' },
    { clave: 'integrantes', numero: 3, titulo: 'Integrantes' },
    { clave: 'detalle', numero: 4, titulo: 'Detalle' },
  ];

  camposPorPaso: Record<string, string[]> = {
    datos: ['idSolicitud', 'candidato', 'cargo'],
    agenda: ['tipo', 'fecha', 'horaInicio', 'horaFin', 'modalidad'],
    integrantes: ['entrevistador'],
    detalle: ['asunto'],
  };

  columnasIntegrantes: DataTableColumn<IntegranteEntrevista>[] = [
    { key: 'nombre', label: 'Nombre', width: 180 },
    { key: 'rol', label: 'Rol', width: 150 },
    {
      key: 'fechaAgendamiento',
      label: 'Fecha agendamiento',
      width: 170,
      value: () => String(this.formulario.get('fecha')?.value || 'Sin fecha'),
    },
  ];

  integrantes: IntegranteEntrevista[] = [
    { id: 'macarena-lopez', nombre: 'Macarena Lopez', rol: 'Candidata', fechaAgendamiento: 'Sin fecha' },
    { id: 'valentina-rojas', nombre: 'Valentina Rojas', rol: 'Candidata', fechaAgendamiento: 'Sin fecha' },
    { id: 'felipe-valdes', nombre: 'Felipe Valdes', rol: 'Reclutador', fechaAgendamiento: 'Sin fecha' },
    { id: 'cathy', nombre: 'Cathy', rol: 'Area tecnica', fechaAgendamiento: 'Sin fecha' },
  ];

  formulario = new UntypedFormGroup({
    idSolicitud: new UntypedFormControl(null, Validators.required),
    candidato: new UntypedFormControl(null, Validators.required),
    tipo: new UntypedFormControl(null, Validators.required),
    asunto: new UntypedFormControl('', Validators.required),
    cargo: new UntypedFormControl('', Validators.required),
    fecha: new UntypedFormControl('', Validators.required),
    horaInicio: new UntypedFormControl('', Validators.required),
    horaFin: new UntypedFormControl('', Validators.required),
    duracion: new UntypedFormControl('45 min', Validators.required),
    modalidad: new UntypedFormControl('Online', Validators.required),
    entrevistador: new UntypedFormControl('', Validators.required),
    linkReunion: new UntypedFormControl(''),
    observacion: new UntypedFormControl(''),
  });

  constructor(private catalogosService: CatalogosService) {}

  ngOnInit() {
    this.cargarCatalogosEntrevista();
    this.aplicarDatosIniciales();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['initialData'] || changes['candidatos']) {
      this.aplicarDatosIniciales();
    }
  }

  get tituloModal() {
    return this.esAgendaMasiva ? 'Agendar entrevistas masivas' : 'Agendar nueva entrevista';
  }

  get subtituloModal() {
    return this.esAgendaMasiva
      ? 'Define una misma fecha y hora para los candidatos seleccionados.'
      : 'Completa los datos para crear la cita.';
  }

  get esAgendaMasiva() {
    return this.candidatos.length > 1;
  }

  get tieneCandidatosPreseleccionados() {
    return this.candidatos.length > 0;
  }

  get resumenCandidatos() {
    return this.esAgendaMasiva
      ? `${this.candidatos.length} candidatos seleccionados`
      : this.candidatos[0]?.nombre || String(this.control('candidato')?.value || 'Sin candidato');
  }

  get pasosCompletados() {
    return this.pasosFormulario
      .filter((paso) => this.pasoCompletado(paso.clave))
      .map((paso) => paso.clave);
  }

  enviar() {
    this.formulario.markAllAsTouched();

    if (this.formulario.invalid || !this.horarioValido()) {
      return;
    }

    this.guardar.emit(this.formulario.getRawValue() as EntrevistaPayload);
  }

  control(nombre: string) {
    return this.formulario.get(nombre);
  }

  horarioValido() {
    const inicio = String(this.formulario.get('horaInicio')?.value || '');
    const fin = String(this.formulario.get('horaFin')?.value || '');
    return !inicio || !fin || fin > inicio;
  }

  cambiarTabFormulario(tab: string) {
    const indiceDestino = this.pasosFormulario.findIndex((paso) => paso.clave === tab);

    if (indiceDestino > this.pasoActualIndice() && !this.validarPaso(this.tabFormulario)) {
      return;
    }

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
    if (!this.validarPaso(this.tabFormulario)) {
      return;
    }

    const indiceActual = this.pasoActualIndice();

    if (indiceActual < this.pasosFormulario.length - 1) {
      this.tabFormulario = this.pasosFormulario[indiceActual + 1].clave;
    }
  }

  esUltimoPaso() {
    return this.pasoActualIndice() === this.pasosFormulario.length - 1;
  }

  validarPaso(clave: string) {
    const controles = this.camposPorPaso[clave] ?? [];
    controles.forEach((nombre) => this.control(nombre)?.markAsTouched());

    const controlesValidos = controles.every((nombre) => this.control(nombre)?.valid);

    if (clave === 'agenda') {
      return controlesValidos && this.horarioValido();
    }

    return controlesValidos;
  }

  seleccionarTipo(tipo: TipoEntrevista) {
    this.formulario.get('tipo')?.setValue(tipo);
    this.formulario.get('tipo')?.markAsTouched();
  }

  cargarCatalogosEntrevista() {
    // Integración de catálogos para agenda de entrevistas:
    // - tipos-entrevista alimenta las opciones "Tipo de entrevista".
    // - modalidades alimenta el selector "Modalidad".
    // - usuarios alimenta la tabla de integrantes/entrevistadores.
    forkJoin({
      tipos: this.catalogosService.listarTiposEntrevista().pipe(timeout(4000), catchError(() => of([]))),
      modalidades: this.catalogosService.listarModalidades().pipe(timeout(4000), catchError(() => of([]))),
      usuarios: this.catalogosService.listarUsuarios().pipe(timeout(4000), catchError(() => of([]))),
    })
      .pipe(take(1))
      .subscribe(({ tipos, modalidades, usuarios }) => {
        const tiposCatalogo = tipos.map((tipo) => tipo.tpet_nombre).filter((nombre): nombre is string => Boolean(nombre));
        const modalidadesCatalogo = modalidades.map((modalidad) => modalidad.mdld_nombre).filter((nombre): nombre is string => Boolean(nombre));

        if (tiposCatalogo.length > 0) {
          this.tipos = tiposCatalogo;
        }

        if (modalidadesCatalogo.length > 0) {
          this.modalidades = modalidadesCatalogo;
          this.formulario.get('modalidad')?.setValue(modalidadesCatalogo[0]);
        }

        if (usuarios.length > 0) {
          this.integrantes = usuarios.map((usuario) => this.mapearUsuarioAIntegrante(usuario));
          this.integrantesSeleccionados = new Set(this.integrantes.slice(0, 2).map((integrante) => integrante.id));
        }
      });
  }

  agregarIntegrante() {
    const entrevistador = String(this.formulario.get('entrevistador')?.value ?? '').trim();

    if (!entrevistador || this.integrantes.some((integrante) => integrante.nombre === entrevistador)) {
      return;
    }

    const id = entrevistador.toLowerCase().replace(/\s+/g, '-');

    this.integrantes = [
      ...this.integrantes,
      {
        id,
        nombre: entrevistador,
        rol: 'Entrevistador',
        fechaAgendamiento: String(this.formulario.get('fecha')?.value || 'Sin fecha'),
      },
    ];
    this.integrantesSeleccionados = new Set([...this.integrantesSeleccionados, id]);
  }

  obtenerIdIntegrante(integrante: IntegranteEntrevista) {
    return integrante.id;
  }

  private mapearUsuarioAIntegrante(usuario: UsuarioCatalogoApi): IntegranteEntrevista {
    // Mapeo catálogo usuarios -> tabla "Integrantes": muestra nombre completo y rol del usuario.
    const nombre = [usuario.usr_nombres, usuario.usr_apellido_paterno, usuario.usr_apellido_materno]
      .filter(Boolean)
      .join(' ') || usuario.usr_email;

    return {
      id: String(usuario.usr_id),
      nombre,
      rol: usuario.rol?.rol_nombre ?? 'Usuario',
      fechaAgendamiento: 'Sin fecha',
    };
  }

  actualizarSeleccionIntegrantes(ids: Set<string>) {
    this.integrantesSeleccionados = ids;
  }

  eliminarCandidatoAgenda(candidato: EntrevistaCandidatoSeleccionado) {
    const candidatosActualizados = this.candidatos.filter(
      (item) => this.obtenerIdCandidatoAgenda(item) !== this.obtenerIdCandidatoAgenda(candidato),
    );

    if (candidatosActualizados.length === 0) {
      this.cerrar.emit();
      return;
    }

    this.candidatos = candidatosActualizados;
    this.candidatosChange.emit(candidatosActualizados);
    this.aplicarDatosIniciales();
  }

  private aplicarDatosIniciales() {
    if (this.initialData) {
      this.formulario.patchValue(this.initialData);
    }

    if (!this.tieneCandidatosPreseleccionados) {
      return;
    }

    const primerCandidato = this.candidatos[0];

    this.formulario.patchValue({
      idSolicitud: this.esAgendaMasiva ? 'Múltiples solicitudes' : primerCandidato.idSolicitud,
      candidato: this.esAgendaMasiva ? `${this.candidatos.length} candidatos seleccionados` : primerCandidato.nombre,
      cargo: this.esAgendaMasiva ? 'Múltiples cargos' : primerCandidato.cargo,
      asunto:
        this.formulario.get('asunto')?.value ||
        (this.esAgendaMasiva ? 'Agendamiento de entrevistas' : `Entrevista ${primerCandidato.cargo}`),
    });

    this.sincronizarIntegrantesPreseleccionados();
  }

  private sincronizarIntegrantesPreseleccionados() {
    const candidatosIntegrantes = this.candidatos.map((candidato) => ({
      id: this.crearId(candidato.nombre),
      nombre: candidato.nombre,
      rol: 'Candidato',
      fechaAgendamiento: String(this.formulario.get('fecha')?.value || 'Sin fecha'),
    }));

    const equipoInterno = this.integrantes.filter((integrante) => integrante.rol !== 'Candidata' && integrante.rol !== 'Candidato');

    this.integrantes = [...candidatosIntegrantes, ...equipoInterno];
    this.integrantesSeleccionados = new Set([
      ...candidatosIntegrantes.map((integrante) => integrante.id),
      ...equipoInterno.filter((integrante) => integrante.rol !== 'Area tecnica').map((integrante) => integrante.id),
    ]);
  }

  private crearId(valor: string) {
    return valor
      .trim()
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/\s+/g, '-');
  }

  private obtenerIdCandidatoAgenda(candidato: EntrevistaCandidatoSeleccionado) {
    return candidato.id || this.crearId(`${candidato.idSolicitud}-${candidato.nombre}`);
  }
}
