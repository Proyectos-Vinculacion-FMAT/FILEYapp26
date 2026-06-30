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
      display: inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      line-height: 1.4;
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
      'pendiente': '#fff3cd',
      'pendiente_validacion': '#fff3cd',
      'aceptada': '#d4edda',
      'Confirmada': '#d4edda',
      'Pagada': '#cce5ff',
      'rechazada': '#f8d7da',
      'rechazado': '#f8d7da',
      'Cancelada': '#f8d7da',
      'cambios_solicitados': '#ffeaa7',
      'Por confirmar': '#fff3cd',
      'vencida': '#f8d7da',
      'Disponible': '#d4edda',
      'Reservado': '#fff3cd',
      'Ocupado': '#cce5ff',
      'validado': '#d4edda',
      'desconocido': '#e2e3e5'
    };
    return colors[this.estado()] || '#e2e3e5';
  });

  fg = computed(() => {
    const colors: Record<string, string> = {
      'pendiente': '#856404',
      'pendiente_validacion': '#856404',
      'aceptada': '#155724',
      'Confirmada': '#155724',
      'Pagada': '#004085',
      'rechazada': '#721c24',
      'rechazado': '#721c24',
      'Cancelada': '#721c24',
      'cambios_solicitados': '#7d6608',
      'Por confirmar': '#856404',
      'vencida': '#721c24',
      'Disponible': '#155724',
      'Reservado': '#856404',
      'Ocupado': '#004085',
      'validado': '#155724',
      'desconocido': '#383d41'
    };
    return colors[this.estado()] || '#383d41';
  });
}
