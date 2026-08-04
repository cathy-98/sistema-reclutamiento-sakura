import { Injectable } from '@angular/core';
import { BehaviorSubject, delay, map, of } from 'rxjs';

export interface TecnologiaCuestionario {
  id: number;
  nombre: string;
}

export interface NivelCuestionario {
  id: number;
  nombre: string;
  duracionMinutos: number;
}

export interface PreguntaCuestionario {
  id: string;
  texto: string;
  tecnologiaId: number;
  nivelId: number;
  fechaCreacion: string;
  respuestas: string[];
  respuestaCorrecta: number;
  duracionMinutos: number;
  duracionSegundos: number;
}

export interface PreguntaCuestionarioCreate {
  texto: string;
  tecnologiaId: number;
  nivelId: number;
  respuestas: string[];
  respuestaCorrecta: number;
  duracionMinutos: number;
  duracionSegundos: number;
}

@Injectable({
  providedIn: 'root',
})
export class CuestionariosService {
  readonly tecnologias: TecnologiaCuestionario[] = [
    { id: 1, nombre: 'JAVA' },
    { id: 2, nombre: 'Python' },
    { id: 3, nombre: 'CSS' },
    { id: 4, nombre: 'Angular' },
    { id: 5, nombre: 'Javascript' },
  ];

  readonly niveles: NivelCuestionario[] = [
    { id: 1, nombre: 'Trainee', duracionMinutos: 45 },
    { id: 2, nombre: 'Junior', duracionMinutos: 50 },
    { id: 3, nombre: 'Senior', duracionMinutos: 60 },
  ];

  private readonly preguntas = new BehaviorSubject<PreguntaCuestionario[]>([
    {
      id: '5',
      texto: 'Que es la JVM?',
      tecnologiaId: 1,
      nivelId: 1,
      fechaCreacion: '19/05/2026',
      respuestas: ['Maquina virtual de Java', 'Libreria de frontend', 'Motor de base de datos'],
      respuestaCorrecta: 0,
      duracionMinutos: 45,
      duracionSegundos: 0,
    },
    {
      id: '6',
      texto: 'Por que Java es multihilo?',
      tecnologiaId: 1,
      nivelId: 1,
      fechaCreacion: '17/05/2026',
      respuestas: ['Porque permite ejecutar multiples hilos', 'Porque solo usa un proceso', 'Porque no compila'],
      respuestaCorrecta: 0,
      duracionMinutos: 45,
      duracionSegundos: 30,
    },
    {
      id: '7',
      texto: 'Explica el polimorfismo en Java',
      tecnologiaId: 1,
      nivelId: 2,
      fechaCreacion: '15/05/2026',
      respuestas: ['Sobrescritura y sobrecarga', 'Un tipo de servidor', 'Una etiqueta HTML'],
      respuestaCorrecta: 0,
      duracionMinutos: 50,
      duracionSegundos: 0,
    },
    {
      id: '8',
      texto: 'Para que sirve un elif?',
      tecnologiaId: 2,
      nivelId: 1,
      fechaCreacion: '12/05/2026',
      respuestas: ['Evaluar otra condicion', 'Declarar una clase', 'Crear un paquete'],
      respuestaCorrecta: 0,
      duracionMinutos: 45,
      duracionSegundos: 15,
    },
    {
      id: '9',
      texto: 'En donde interviene CSS?',
      tecnologiaId: 3,
      nivelId: 1,
      fechaCreacion: '10/05/2026',
      respuestas: ['En estilos visuales', 'En consultas SQL', 'En compilacion Java'],
      respuestaCorrecta: 0,
      duracionMinutos: 45,
      duracionSegundos: 0,
    },
  ]);

  listar() {
    return this.preguntas.asObservable().pipe(delay(120));
  }

  crear(payload: PreguntaCuestionarioCreate) {
    const siguienteId = String(Math.max(0, ...this.preguntas.value.map((pregunta) => Number(pregunta.id))) + 1);
    const nuevaPregunta: PreguntaCuestionario = {
      ...payload,
      id: siguienteId,
      fechaCreacion: new Intl.DateTimeFormat('es-CL').format(new Date()),
    };

    this.preguntas.next([nuevaPregunta, ...this.preguntas.value]);
    return of(nuevaPregunta).pipe(delay(120));
  }

  contarPorTecnologia() {
    return this.listar().pipe(
      map((preguntas) =>
        this.tecnologias.map((tecnologia) => ({
          tecnologia,
          cantidad: preguntas.filter((pregunta) => pregunta.tecnologiaId === tecnologia.id).length,
        })),
      ),
    );
  }
}
