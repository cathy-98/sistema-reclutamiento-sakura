import { CommonModule } from '@angular/common';
import { Component, ElementRef, HostListener, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

export interface CompactSelectOption {
  id: number;
  nombre: string;
}

@Component({
  selector: 'app-compact-select',
  imports: [CommonModule],
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

  value: number | null = null;
  disabled = false;
  abierto = false;

  private onChange: (value: number | null) => void = () => {};
  private onTouched: () => void = () => {};

  constructor(private elementRef: ElementRef<HTMLElement>) {}

  get selectedLabel() {
    return this.options.find((option) => option.id === this.value)?.nombre ?? this.placeholder;
  }

  // Cierra el panel al hacer click fuera; evita que la lista quede flotando sobre el modal.
  @HostListener('document:click', ['$event'])
  cerrarSiClickExterno(event: MouseEvent) {
    if (!this.elementRef.nativeElement.contains(event.target as Node)) {
      this.abierto = false;
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
    this.onTouched();
  }

  seleccionar(value: number | null) {
    this.value = value;
    this.abierto = false;
    this.onChange(value);
    this.onTouched();
  }
}
