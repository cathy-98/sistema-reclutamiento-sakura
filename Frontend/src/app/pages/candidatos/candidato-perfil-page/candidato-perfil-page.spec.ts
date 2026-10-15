import { convertToParamMap } from '@angular/router';
import { CandidatoPerfilPage } from './candidato-perfil-page';

function crearComponente() {
  const route = {
    snapshot: {
      paramMap: convertToParamMap({ id: '21' }),
      queryParamMap: convertToParamMap({}),
    },
  };

  return new CandidatoPerfilPage(
    route as never,
    {} as never,
    {} as never,
    {} as never,
    {} as never,
    {} as never,
    {} as never,
    {} as never,
    {} as never,
    { detectChanges: () => undefined } as never,
  ) as unknown as {
    mapearEstudiosM3: (estudios: unknown[], catalogos: unknown) => Array<{ fecha: string }>;
    mapearCursosM3: (
      cursos: unknown[],
      catalogos: unknown,
    ) => Array<{
      nombre: string;
      institucion?: string;
      anio?: string;
      certificado: boolean;
      metadata: string[];
    }>;
    mapearExperienciasM3: (
      experiencias: unknown[],
      catalogos: unknown,
      habilidades: unknown[],
    ) => Array<{ fecha: string }>;
    tienePostulacionSeleccionada: boolean;
    tabs: Array<{ id: string }>;
    tabActiva: string;
    postulacionSeleccionadaId: string;
    mostrarModalEntrevista: boolean;
    abrirModalEntrevista: () => void;
    cambiarTab: (tab: string) => void;
    contextoPostulaciones: Map<string, unknown>;
  };
}

function catalogosVacios() {
  return {
    cargos: new Map(),
    empresas: new Map(),
    habilidades: new Map(),
    nivelesHabilidad: new Map(),
    instituciones: new Map(),
    carreras: new Map(),
    nivelesEducacionales: new Map(),
    comunas: new Map(),
  };
}

describe('CandidatoPerfilPage fechas de estudios', () => {
  it('muestra Fecha no disponible cuando inicio y fin son null', () => {
    const [estudio] = crearComponente().mapearEstudiosM3(
      [{ etcd_fecha_inicio: null, etcd_fecha_fin: null }],
      catalogosVacios(),
    );

    expect(estudio.fecha).toBe('Fecha no disponible');
  });

  it('muestra rango normal cuando inicio y fin existen', () => {
    const [estudio] = crearComponente().mapearEstudiosM3(
      [{ etcd_fecha_inicio: '2022-03-01', etcd_fecha_fin: '2024-12-31' }],
      catalogosVacios(),
    );

    expect(estudio.fecha).toBe('01-03-2022 - 31-12-2024');
  });

  it('muestra solo Desde cuando falta fecha fin y no comunica Actual', () => {
    const [estudio] = crearComponente().mapearEstudiosM3(
      [{ etcd_fecha_inicio: '2022-03-01', etcd_fecha_fin: null }],
      catalogosVacios(),
    );

    expect(estudio.fecha).toBe('Desde 01-03-2022');
    expect(estudio.fecha).not.toContain('Actual');
  });

  it('muestra Hasta cuando solo existe fecha fin', () => {
    const [estudio] = crearComponente().mapearEstudiosM3(
      [{ etcd_fecha_inicio: null, etcd_fecha_fin: '2024-12-31' }],
      catalogosVacios(),
    );

    expect(estudio.fecha).toBe('Hasta 31-12-2024');
  });
});

describe('CandidatoPerfilPage fechas de experiencias', () => {
  it('mantiene Actual para experiencia con fecha fin null', () => {
    const [experiencia] = crearComponente().mapearExperienciasM3(
      [{ expl_fecha_inicio: '2019-10-01', expl_fecha_fin: null }],
      catalogosVacios(),
      [],
    );

    expect(experiencia.fecha).toBe('01-10-2019 - Actual');
  });
});

describe('CandidatoPerfilPage cursos', () => {
  it('mapea nombre, institucion, anio y certificado desde perfil.cursos', () => {
    const catalogos = catalogosVacios();
    catalogos.instituciones.set(7, 'Academia Desafio Latam');

    const [curso] = crearComponente().mapearCursosM3(
      [
        {
          curs_nombre_curso: 'Curso de UX Research',
          curs_institucion_id: 7,
          curs_anio_curso: 2024,
          curs_es_certificado: true,
        },
      ],
      catalogos,
    );

    expect(curso).toEqual({
      nombre: 'Curso de UX Research',
      institucion: 'Academia Desafio Latam',
      anio: '2024',
      certificado: true,
      metadata: ['Academia Desafio Latam', '2024'],
    });
  });

  it('omite institucion no resuelta sin mostrar IDs internos', () => {
    const [curso] = crearComponente().mapearCursosM3(
      [
        {
          curs_nombre_curso: 'Diplomado Gestion de Proyectos',
          curs_institucion_id: 99,
          curs_es_certificado: false,
        },
      ],
      catalogosVacios(),
    );

    expect(curso.nombre).toBe('Diplomado Gestion de Proyectos');
    expect(curso.institucion).toBeUndefined();
    expect(curso.metadata).toEqual([]);
    expect(curso.certificado).toBe(false);
  });

  it('mantiene cursos sin metadatos opcionales disponibles', () => {
    const [curso] = crearComponente().mapearCursosM3(
      [{ curs_nombre_curso: 'Certificacion Scrum' }],
      catalogosVacios(),
    );

    expect(curso.nombre).toBe('Certificacion Scrum');
    expect(curso.metadata).toEqual([]);
    expect(curso.certificado).toBe(false);
  });
});

describe('CandidatoPerfilPage contexto de postulacion', () => {
  it('no trata un candidato general como postulacion seleccionada', () => {
    const componente = crearComponente();

    expect(componente.tienePostulacionSeleccionada).toBe(false);
    expect(componente.tabs.map((tab) => tab.id)).not.toContain('match');
    expect(componente.tabs.map((tab) => tab.id)).not.toContain('evaluaciones');

    componente.abrirModalEntrevista();
    expect(componente.mostrarModalEntrevista).toBe(false);

    componente.cambiarTab('match');
    expect(componente.tabActiva).toBe('experiencia');
  });

  it('habilita vistas y acciones de proceso cuando existe postulacion real', () => {
    const componente = crearComponente();
    componente.postulacionSeleccionadaId = 'SOL-1';
    componente.contextoPostulaciones.set('SOL-1', {
      postulacionId: 77,
      idSolicitud: 'SOL-1',
      cargo: 'UX Designer',
      estado: 'En entrevista',
      match: 86,
      renta: 1200000,
      fechaPostulacionTimestamp: 1,
    });

    expect(componente.tienePostulacionSeleccionada).toBe(true);
    expect(componente.tabs.map((tab) => tab.id)).toContain('match');
    expect(componente.tabs.map((tab) => tab.id)).toContain('evaluaciones');

    componente.abrirModalEntrevista();
    expect(componente.mostrarModalEntrevista).toBe(true);
  });
});
