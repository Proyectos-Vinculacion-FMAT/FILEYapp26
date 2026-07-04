import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="empty">
      <mat-icon class="icon">{{ icono() }}</mat-icon>
      <h3>{{ titulo() }}</h3>
      <p class="text-muted">{{ mensaje() }}</p>
      <ng-content></ng-content>
    </div>
  `,
  styles: [`
    .empty {
      text-align: center;
      padding: 48px 24px;
      background: #f9fafb;
      border: 1px dashed #d1d5db;
      border-radius: 8px;
    }
    .icon {
      font-size: 56px;
      width: 56px;
      height: 56px;
      color: #9ca3af;
    }
    h3 { margin: 16px 0 8px; color: #1f2937; font-weight: 500; }
    p { margin-bottom: 16px; }
  `]
})
export class EmptyStateComponent {
  icono = input<string>('inbox');
  titulo = input<string>('Sin datos');
  mensaje = input<string>('No hay información para mostrar.');
}
