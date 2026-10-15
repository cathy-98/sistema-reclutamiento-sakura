import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CandidateEducationSection } from './candidate-education-section';

describe('CandidateEducationSection', () => {
  let fixture: ComponentFixture<CandidateEducationSection>;
  let component: CandidateEducationSection;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CandidateEducationSection],
    }).compileComponents();

    fixture = TestBed.createComponent(CandidateEducationSection);
    component = fixture.componentInstance;
  });

  function textoRenderizado() {
    return (fixture.nativeElement as HTMLElement).textContent ?? '';
  }

  it('muestra estudios y cursos en subsecciones separadas cuando ambos existen', () => {
    component.estudios = [
      {
        titulo: 'Diseño y comunicacion digital',
        institucion: 'Instituto Profesional Los Leones',
        fecha: '01-03-2022 - 31-12-2024',
      },
    ];
    component.cursos = [
      {
        nombre: 'Curso de UX Research',
        institucion: 'Academia Desafio Latam',
        anio: '2024',
        certificado: true,
        metadata: ['Academia Desafio Latam', '2024'],
      },
    ];

    fixture.detectChanges();

    const texto = textoRenderizado();
    expect(texto).toContain('Formación académica');
    expect(texto).toContain('Cursos y certificaciones');
    expect(texto).toContain('Diseño y comunicacion digital');
    expect(texto).toContain('Curso de UX Research');
    expect(texto).toContain('Academia Desafio Latam · 2024');
    expect(texto).toContain('Certificado');
  });

  it('muestra solo la subseccion de estudios cuando no hay cursos', () => {
    component.estudios = [
      {
        titulo: 'Ingenieria Civil',
        institucion: 'Universidad de Chile',
        fecha: 'Fecha no disponible',
      },
    ];

    fixture.detectChanges();

    const texto = textoRenderizado();
    expect(texto).toContain('Formación académica');
    expect(texto).not.toContain('Cursos y certificaciones');
    expect(texto).not.toContain('No hay estudios ni cursos registrados.');
  });

  it('muestra solo la subseccion de cursos cuando no hay estudios', () => {
    component.cursos = [
      {
        nombre: 'Diplomado Gestion de Proyectos',
        certificado: false,
        metadata: [],
      },
    ];

    fixture.detectChanges();

    const texto = textoRenderizado();
    expect(texto).toContain('Cursos y certificaciones');
    expect(texto).toContain('Diplomado Gestion de Proyectos');
    expect(texto).not.toContain('Formación académica');
    expect(texto).not.toContain('No certificado');
  });

  it('muestra un unico estado vacio cuando no hay estudios ni cursos', () => {
    fixture.detectChanges();

    const texto = textoRenderizado();
    expect(texto).toContain('No hay estudios ni cursos registrados.');
    expect(texto).not.toContain('Formación académica');
    expect(texto).not.toContain('Cursos y certificaciones');
  });
});
