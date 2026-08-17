import { CommonModule } from '@angular/common';
import { Component, ElementRef, EventEmitter, HostListener, Input, Output, forwardRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

export interface CompactSelectOption {
  id: number;
  nombre: string;
}

@Component({
  selector: 'app-compact-select',
  imports: [CommonModule, FormsModule],
  templateUrl: './compact-select.html',
  styleUrl: './compact-select.scss',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => CompactSelect),
      multi: true,
    },
  ],
})
export class CompactSelect implements ControlValueAccessor {
  @Input() options: CompactSelectOption[] = [];
  @Input() placeholder = 'Selecciona una opción';
  @Input() actionLabel = '';
  @Input() actionDisabled = false;
  @Input() searchable = false;
  @Input() searchPlaceholder = 'Buscar...';
  @Output() actionSelected = new EventEmitter<void>();
  @Output() valueChange = new EventEmitter<number | null>();

  value: number | null = null;
  disabled = false;
  abierto = false;
  searchTerm = '';

  private onChange: (value: number | null) => void = () => {};
  private onTouched: () => void = () => {};

  constructor(private elementRef: ElementRef<HTMLElement>) {}

  get selectedLabel() {
    return this.options.find((option) => option.id === this.value)?.nombre ?? this.placeholder;
  }

  get filteredOptions() {
    const term = this.normalizar(this.searchTerm);
    if (!term) {
      return this.options;
    }

    return this.options.filter((option) => this.normalizar(option.nombre).includes(term));
  }

  // Cierra el panel al hacer click fuera; evita que la lista quede flotando sobre el modal.
  @HostListener('document:click', ['$event'])
  cerrarSiClickExterno(event: MouseEvent) {
    if (!this.elementRef.nativeElement.contains(event.target as Node)) {
      this.abierto = false;
      this.searchTerm = '';
    }
  }

  writeValue(value: number | null): void {
    this.value = value;
  }

  registerOnChange(fn: (value: number | null) => void): void {
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
    if (!this.abierto) {
      this.searchTerm = '';
    }
    this.onTouched();
  }

  seleccionar(value: number | null) {
    this.value = value;
    this.abierto = false;
    this.searchTerm = '';
    this.onChange(value);
    this.valueChange.emit(value);
    this.onTouched();
  }

  ejecutarAccion(event: MouseEvent) {
    event.stopPropagation();
    if (this.actionDisabled) {
      return;
    }

    this.abierto = false;
    this.searchTerm = '';
    this.actionSelected.emit();
    this.onTouched();
  }

  private normalizar(value: string) {
    return value.trim().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }
}
