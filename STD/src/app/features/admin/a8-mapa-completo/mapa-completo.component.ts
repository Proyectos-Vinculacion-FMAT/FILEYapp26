import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { StandMapComponent } from '../../../shared/components/stand-map.component';
import { StandService } from '../../../services/stand.service';

@Component({
  selector: 'app-mapa-completo',
  standalone: true,
  imports: [
    CommonModule, RouterModule, StandMapComponent
  ],
  template: `
    <div class="page-container-fluid">
      <div class="header">
        <h1 class="page-title">Mapa completo del showfloor</h1>
        <p class="page-subtitle">Visualización con información de gestión: quién reservó cada stand y saldo pendiente.</p>
      </div>

      <div class="legend">
        <span class="legend-item"><span class="dot disponible"></span> Disponible</span>
        <span class="legend-item"><span class="dot reservado"></span> Reservado</span>
        <span class="legend-item"><span class="dot ocupado"></span> Ocupado</span>
        <span class="legend-item text-muted">Total stands: {{ totalStands }} · Disponibles: {{ disponibles }} · Reservados: {{ reservados }} · Ocupados: {{ ocupados }}</span>
      </div>

      <div class="map-area">
        <app-stand-map></app-stand-map>
      </div>
    </div>
  `,
  styles: [`
    .page-container-fluid { padding: 24px; max-width: 1600px; margin: 0 auto; }
    .header { margin-bottom: 16px; }
    .legend {
      display: flex;
      gap: 24px;
      align-items: center;
      background: #fff;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      flex-wrap: wrap;
    }
    .legend-item { display: flex; align-items: center; gap: 6px; font-size: 14px; }
    .dot { width: 14px; height: 14px; border-radius: 50%; display: inline-block; }
    .dot.disponible { background: #3a7d44; }
    .dot.reservado { background: #d9a441; }
    .dot.ocupado { background: #c0473b; }
    .map-area {
      background: #1a1a1a;
      border-radius: 8px;
      overflow: hidden;
      height: calc(100vh - 240px);
      min-height: 500px;
    }
  `]
})
export class MapaCompletoComponent {
  private readonly standService = inject(StandService);

  get totalStands(): number { return this.standService.stands.length; }
  get disponibles(): number { return this.standService.stands.filter(s => s.estado === 'Disponible').length; }
  get reservados(): number { return this.standService.stands.filter(s => s.estado === 'Reservado').length; }
  get ocupados(): number { return this.standService.stands.filter(s => s.estado === 'Ocupado').length; }
}
