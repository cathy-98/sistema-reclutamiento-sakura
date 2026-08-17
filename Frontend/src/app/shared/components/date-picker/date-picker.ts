import { CommonModule } from '@angular/common';
import { Component, ElementRef, HostListener, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

interface DiaCalendario {
  fecha: string;
  dia: number;
  esMesActual: boolean;
  deshabilitado: boolean;
}

@Component({
  selector: 'app-date-picker',
  imports: [CommonModule],
  templateUrl: './date-picker.html',
  styleUrl: './date-picker.scss',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => DatePicker),
      multi: true,
    },
  ],
})
export class DatePicker implements ControlValueAccessor {
  @Input() placeholder = 'dd/mm/aaaa';
  @Input() min: string | null = null;

  value = '';
  disabled = false;
  abierto = false;
  mesVisible = this.inicioMes(new Date());

  readonly diasSemana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];
  readonly meses = [
    'enero',
    'febrero',
    'marzo',
    'abril',
    'mayo',
    'junio',
    'julio',
    'agosto',
    'septiembre',
    'octubre',
    'noviembre',
    'diciembre',
  ];

  private onChange: (value: string) => void = () => {};
  private onTouched: () => void = () => {};

  constructor(private elementRef: ElementRef<HTMLElement>) {}

  get valorVisible() {
    return this.formatearFecha(this.value);
  }

  get etiquetaMes() {
    return `${this.meses[this.mesVisible.getMonth()]} ${this.mesVisible.getFullYear()}`;
  }

  get diasCalendario(): DiaCalendario[] {
    const inicio = this.inicioGrilla(this.mesVisible);
    return Array.from({ length: 42 }, (_, indice) => {
      const fecha = new Date(inicio);
      fecha.setDate(inicio.getDate() + indice);
      const fechaIso = this.fechaIso(fecha);

      return {
        fecha: fechaIso,
        dia: fecha.getDate(),
        esMesActual: fecha.getMonth() === this.mesVisible.getMonth(),
        deshabilitado: Boolean(this.min && fechaIso < this.min),
      };
    });
  }

  @HostListener('document:click', ['$event'])
  cerrarSiClickExterno(event: MouseEvent) {
    if (!this.elementRef.nativeElement.contains(event.target as Node)) {
      this.abierto = false;
    }
  }

  writeValue(value: string | null): void {
    this.value = value ?? '';

    if (this.value) {
      this.mesVisible = this.inicioMes(this.fechaDesdeIso(this.value));
    }
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
    if (isDisabled) {
      this.abierto = false;
    }
  }

  alternar() {
    if (this.disabled) {
      return;
    }

    this.abierto = !this.abierto;
    if (this.abierto) {
      this.mesVisible = this.inicioMes(this.value ? this.fechaDesdeIso(this.value) : new Date());
    }
    this.onTouched();
  }

  cambiarMes(delta: number) {
    this.mesVisible = new Date(this.mesVisible.getFullYear(), this.mesVisible.getMonth() + delta, 1);
  }

  seleccionar(dia: DiaCalendario) {
    if (dia.deshabilitado || this.disabled) {
      return;
    }

    this.value = dia.fecha;
    this.abierto = false;
    this.onChange(this.value);
    this.onTouched();
  }

  limpiar(event: MouseEvent) {
    event.stopPropagation();
    this.value = '';
    this.abierto = false;
    this.onChange('');
    this.onTouched();
  }

  seleccionarHoy(event: MouseEvent) {
    event.stopPropagation();
    const hoy = this.fechaIso(new Date());

    if (this.min && hoy < this.min) {
      return;
    }

    this.value = hoy;
    this.mesVisible = this.inicioMes(new Date());
    this.abierto = false;
    this.onChange(this.value);
    this.onTouched();
  }

  private inicioMes(fecha: Date) {
    return new Date(fecha.getFullYear(), fecha.getMonth(), 1);
  }

  private inicioGrilla(fecha: Date) {
    const inicio = this.inicioMes(fecha);
    const diaSemanaLunesPrimero = (inicio.getDay() + 6) % 7;
    inicio.setDate(inicio.getDate() - diaSemanaLunesPrimero);
    return inicio;
  }

  private fechaDesdeIso(fecha: string) {
    const [year, month, day] = fecha.split('-').map(Number);
    return new Date(year, month - 1, day);
  }

  private fechaIso(fecha: Date) {
    return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(fecha.getDate()).padStart(2, '0')}`;
  }

  private formatearFecha(fecha: string) {
    if (!fecha) {
      return '';
    }

    const [year, month, day] = fecha.split('-');
    return year && month && day ? `${day}/${month}/${year}` : fecha;
  }
}
