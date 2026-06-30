import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'currencyMx', standalone: true })
export class CurrencyMxPipe implements PipeTransform {
  transform(value: number | null | undefined, prefix: string = '$'): string {
    if (value === null || value === undefined || isNaN(value)) return `${prefix}0.00`;
    return `${prefix}${value.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
}
