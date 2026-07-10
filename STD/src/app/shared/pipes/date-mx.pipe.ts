import { Pipe, PipeTransform } from '@angular/core';

@Pipe({ name: 'dateMx', standalone: true })
export class DateMxPipe implements PipeTransform {
  transform(value: Date | string | null | undefined, formato: 'corto' | 'largo' | 'cortoHora' = 'corto'): string {
    if (!value) return '';
    const fecha = value instanceof Date ? value : new Date(value);
    if (isNaN(fecha.getTime())) return '';

    const opciones: Intl.DateTimeFormatOptions =
      formato === 'largo' ? { day: 'numeric', month: 'long', year: 'numeric' } :
      formato === 'cortoHora' ? { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' } :
      { day: '2-digit', month: '2-digit', year: 'numeric' };

    return fecha.toLocaleDateString('es-MX', opciones);
  }
}
