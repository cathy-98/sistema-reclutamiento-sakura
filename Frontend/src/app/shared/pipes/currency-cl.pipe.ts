import { Injectable, Pipe, PipeTransform } from '@angular/core';

@Injectable({ providedIn: 'root' })
@Pipe({
  name: 'currencyCl',
})
export class CurrencyClPipe implements PipeTransform {
  transform(value: number | string | null | undefined) {
    const numericValue = Number(value);

    if (!Number.isFinite(numericValue)) {
      return '';
    }

    return numericValue.toLocaleString('es-CL');
  }
}
