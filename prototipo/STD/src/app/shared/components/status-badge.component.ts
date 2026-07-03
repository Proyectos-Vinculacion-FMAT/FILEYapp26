import { Component, input, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

type Estado =
  | 'pendiente' | 'aceptada' | 'rechazada' | 'cambios_solicitados'
  | 'Por confirmar' | 'Confirmada' | 'Pagada' | 'Cancelada'
  | 'Disponible' | 'Reservado' | 'Ocupado'
  | 'pendiente_validacion' | 'validado' | 'rechazado'
  | 'vencida' | 'desconocido';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="badge" [style.background]="bg()" [style.color]="fg()">
      <ng-content>{{ label() }}</ng-content>
    </span>
  `,
  styles: [`
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 11px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      line-height: 1.4;
    }
    .badge::before {
      content: "";
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: currentColor;
    }
  `]
})
export class StatusBadgeComponent {
  estado = input.required<Estado>();

  label = computed(() => {
    const map: Record<string, string> = {
      'pendiente': 'Pendiente',
      'aceptada': 'Aceptada',
      'rechazada': 'Rechazada',
      'cambios_solicitados': 'Cambios solicitados',
      'Por confirmar': 'Por confirmar',
      'Confirmada': 'Confirmada',
      'Pagada': 'Pagada',
      'Cancelada': 'Cancelada',
      'Disponible': 'Disponible',
      'Reservado': 'Reservado',
      'Ocupado': 'Ocupado',
      'pendiente_validacion': 'Pendiente',
      'validado': 'Validado',
      'rechazado': 'Rechazado',
      'vencida': 'Vencida',
      'desconocido': 'Desconocido'
    };
    return map[this.estado()] || this.estado();
  });

  bg = computed(() => {
    const colors: Record<string, string> = {
      'pendiente': '#fdf6e3',
      'pendiente_validacion': '#fdf6e3',
      'aceptada': '#e7f6ee',
      'Confirmada': '#e7f6ee',
      'Pagada': '#e6f0fa',
      'rechazada': '#fbeae8',
      'rechazado': '#fbeae8',
      'Cancelada': '#fbeae8',
      'cambios_solicitados': '#fdf6e3',
      'Por confirmar': '#fdf6e3',
      'vencida': '#fbeae8',
      'Disponible': '#e7f6ee',
      'Reservado': '#fdf6e3',
      'Ocupado': '#e6f0fa',
      'validado': '#e7f6ee',
      'desconocido': '#eef1f6'
    };
    return colors[this.estado()] || '#eef1f6';
  });

  fg = computed(() => {
    const colors: Record<string, string> = {
      'pendiente': '#b8860b',
      'pendiente_validacion': '#b8860b',
      'aceptada': '#1d8a4e',
      'Confirmada': '#1d8a4e',
      'Pagada': '#003b7a',
      'rechazada': '#c0392b',
      'rechazado': '#c0392b',
      'Cancelada': '#c0392b',
      'cambios_solicitados': '#b8860b',
      'Por confirmar': '#b8860b',
      'vencida': '#c0392b',
      'Disponible': '#1d8a4e',
      'Reservado': '#b8860b',
      'Ocupado': '#003b7a',
      'validado': '#1d8a4e',
      'desconocido': '#6b7686'
    };
    return colors[this.estado()] || '#6b7686';
  });
}
