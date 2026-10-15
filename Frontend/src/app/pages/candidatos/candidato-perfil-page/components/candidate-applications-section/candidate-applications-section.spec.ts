import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CandidatoPerfil } from '../../candidato-perfil.models';
import { CandidateApplicationsSection } from './candidate-applications-section';

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

describe('CandidateApplicationsSection empty state', () => {
  let fixture: ComponentFixture<CandidateApplicationsSection>;
  let component: CandidateApplicationsSection;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CandidateApplicationsSection],
    }).compileComponents();

    fixture = TestBed.createComponent(CandidateApplicationsSection);
    component = fixture.componentInstance;
    component.candidato = candidatoBase();
  });

  function textoRenderizado() {
    return (fixture.nativeElement as HTMLElement).textContent ?? '';
  }

  it('muestra un unico estado vacio cuando no hay postulaciones', () => {
    component.postulaciones = [];

    fixture.detectChanges();

    const texto = textoRenderizado();
    expect(texto).toContain('Sin postulaciones registradas.');
    expect(texto).not.toContain('Proceso seleccionado');
    expect(texto).not.toContain('Proceso de selección');
    expect(texto).not.toContain('Sin solicitud');
  });

  it('renderiza resumen de proceso cuando existe postulacion', () => {
    component.postulaciones = [
      ['SOL-1', 'Cliente Demo', 'UX Designer', '01-10-2026', 'En entrevista'],
    ];
    component.postulacionSeleccionadaId = 'SOL-1';

    fixture.detectChanges();

    const texto = textoRenderizado();
    expect(texto).toContain('SOL-1');
    expect(texto).toContain('UX Designer');
    expect(texto).toContain('Proceso seleccionado');
    expect(texto).toContain('Proceso de selección: SOL-1');
    expect(texto).not.toContain('Sin postulaciones registradas.');
  });
});
