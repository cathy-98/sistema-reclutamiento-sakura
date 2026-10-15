import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { CatalogosService } from '../../../../../services/catalogos.service';
import { CandidatoPerfil } from '../../candidato-perfil.models';
import { CandidateProfileHeader } from './candidate-profile-header';

function candidatoBase(): CandidatoPerfil {
  return {
    idSolicitud: '',
    match: null,
    nombre: 'Catherine Rebolledo',
    correo: 'cathyrebopas@gmail.com',
    telefono: '+56957034447',
    cargo: 'Sin solicitud asociada',
    estado: 'Sin postulación',
    disponibilidad: 'Inmediata',
    renta: null,
    rut: 'Sin RUT',
    fechaNacimiento: 'Sin fecha',
    fechaRegistro: 'Sin fecha',
    tituloProfesional: 'UX/UI Designer',
    estadoUsuario: 'Activo',
    resumenProfesional: 'Diseñadora UX/UI',
    urlPerfil: '',
    enlaces: [],
    idiomas: [],
    comuna: 'Santiago',
    direccion: 'Sin dirección',
  };
}

describe('CandidateProfileHeader contexto de postulacion', () => {
  let fixture: ComponentFixture<CandidateProfileHeader>;
  let component: CandidateProfileHeader;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CandidateProfileHeader],
      providers: [
        {
          provide: CatalogosService,
          useValue: {
            listarDisponibilidadesSeguro: () => of([]),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CandidateProfileHeader);
    component = fixture.componentInstance;
    component.candidato = candidatoBase();
  });

  function textoRenderizado() {
    return (fixture.nativeElement as HTMLElement).textContent ?? '';
  }

  it('oculta controles de postulacion para candidato general y mantiene disponibilidad', () => {
    component.hasSelectedPostulation = false;

    fixture.detectChanges();

    const texto = textoRenderizado();
    expect(texto).toContain('Catherine Rebolledo');
    expect(texto).toContain('Diseñadora UX/UI');
    expect(texto).toContain('Disponibilidad');
    expect(texto).toContain('Inmediata');
    expect(texto).not.toContain('Postulado a');
    expect(texto).not.toContain('Sin solicitud');
    expect(texto).not.toContain('Estado postulación');
    expect(texto).not.toContain('Guardar estado');
    expect(texto).not.toContain('Agendar entrevista');
    expect(texto).not.toContain('Match');
    expect(texto).not.toContain('Renta esperada');
  });

  it('mantiene datos y acciones de proceso cuando existe postulacion seleccionada', () => {
    component.hasSelectedPostulation = true;
    component.canSavePostulationState = true;
    component.matchText = '86%';
    component.candidato = {
      ...candidatoBase(),
      idSolicitud: 'SOL-1',
      cargo: 'UX Designer',
      estado: 'En entrevista',
      match: 86,
      renta: 1200000,
    };

    fixture.detectChanges();

    const texto = textoRenderizado();
    expect(texto).toContain('Postulado a');
    expect(texto).toContain('UX Designer');
    expect(texto).toContain('SOL-1');
    expect(texto).toContain('Estado postulación');
    expect(texto).toContain('Guardar estado');
    expect(texto).toContain('Agendar entrevista');
    expect(texto).toContain('Match');
    expect(texto).toContain('86%');
    expect(texto).toContain('Renta esperada');
  });
});
