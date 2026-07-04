import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDividerModule } from '@angular/material/divider';
import { StandMapComponent } from '../../../shared/components/stand-map.component';
import { StandService } from '../../../services/stand.service';
import { CarritoService } from '../../../services/carrito.service';
import { ParametrosService } from '../../../services/parametros.service';
import { FaseService } from '../../../services/fase.service';
import { Stand } from '../../../data/models';
import { CurrencyMxPipe } from '../../../shared/pipes/currency-mx.pipe';
import { EmptyStateComponent } from '../../../shared/components/empty-state.component';

@Component({
  selector: 'app-seleccion',
  standalone: true,
  imports: [
    CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule,
    MatTooltipModule, MatSnackBarModule, MatDividerModule,
    StandMapComponent, CurrencyMxPipe, EmptyStateComponent
  ],
  template: `
    <div class="page-container-fluid">
      <div class="header">
        <div>
          <h1 class="page-title">Selección de stands</h1>
          <p class="page-subtitle">
            Haz click en cualquier stand disponible del mapa para ver su detalle y agregarlo a tu selección.
            El mapa y la gestión del carrito se sincronizan automáticamente.
          </p>
        </div>
      </div>

      <div *ngIf="!puedeAvanzar()" class="warning-banner">
        <mat-icon>info</mat-icon>
        <div>
          Para seleccionar stands primero debes tener tu aplicación aceptada.
          <a routerLink="/usuario/aplicacion" class="ms-2">Ir a mi aplicación →</a>
        </div>
      </div>

      <div class="legend">
        <span class="legend-item"><span class="dot disponible"></span> Disponible</span>
        <span class="legend-item"><span class="dot no-disponible"></span> No disponible</span>
        <span class="legend-item text-muted">Costo por m²: {{ costoM2 | currencyMx }}</span>
      </div>

      <div class="layout" *ngIf="puedeAvanzar(); else locked">
        <div class="map-area">
          <app-stand-map
            [ocultarNoDisponibles]="true"
            (standAddedToCart)="onAddToCart($event.standId)">
          </app-stand-map>
        </div>

        <aside class="cart-panel">
          <div class="cart-header">
            <h3>
              <mat-icon>shopping_cart</mat-icon>
              Tu selección
              <span class="badge-count" *ngIf="items().length > 0">{{ items().length }}</span>
            </h3>
            <button mat-button color="warn"
              *ngIf="items().length > 0"
              (click)="limpiarCarrito()">
              <mat-icon>delete_sweep</mat-icon> Vaciar
            </button>
          </div>

          <mat-divider></mat-divider>

          <div class="cart-body" *ngIf="items().length > 0; else emptyCart">
            <div *ngFor="let item of items()" class="cart-item">
              <div class="cart-item-clave">{{ item.stand.clave }}</div>
              <div class="cart-item-info">
                <div class="cart-item-zona">{{ item.stand.zona }}</div>
                <div class="cart-item-meta text-muted">{{ item.stand.metrosCuadrados }} m²</div>
              </div>
              <div class="cart-item-precio">{{ item.precioUnitario | currencyMx }}</div>
              <button mat-icon-button color="warn"
                (click)="quitarDelCarrito(item.stand.id)"
                matTooltip="Quitar del carrito">
                <mat-icon>close</mat-icon>
              </button>
            </div>
          </div>

          <ng-template #emptyCart>
            <div class="cart-empty">
              <mat-icon>shopping_bag</mat-icon>
              <p>Tu selección está vacía.</p>
              <small>Haz click en un stand del mapa para agregarlo.</small>
            </div>
          </ng-template>

          <div class="cart-footer" *ngIf="items().length > 0">
            <mat-divider></mat-divider>
            <div class="summary-row">
              <span class="summary-label">Total de stands</span>
              <span class="summary-value">{{ items().length }}</span>
            </div>
            <div class="summary-row">
              <span class="summary-label">Superficie</span>
              <span class="summary-value">{{ metrosCuadrados() }} m²</span>
            </div>
            <div class="summary-row total">
              <span>Subtotal</span>
              <span>{{ subtotal() | currencyMx }}</span>
            </div>
            <button mat-raised-button color="primary"
              class="full-width mt-2"
              (click)="irAConfirmar()">
              Continuar a confirmar
              <mat-icon>arrow_forward</mat-icon>
            </button>
            <p class="cart-help">
              El descuento por pronto pago y el anticipo se calculan en el siguiente paso.
            </p>
          </div>
        </aside>
      </div>

      <ng-template #locked>
        <app-empty-state
          icono="lock"
          titulo="Acceso bloqueado"
          mensaje="No es posible seleccionar stands en este momento.">
        </app-empty-state>
      </ng-template>
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
    .dot.no-disponible { background: #c0473b; }
    .layout {
      display: grid;
      grid-template-columns: 1fr 380px;
      gap: 16px;
      height: calc(100vh - 320px);
      min-height: 500px;
    }
    .map-area {
      background: #1a1a1a;
      border-radius: 8px;
      overflow: hidden;
      min-height: 500px;
    }
    .cart-panel {
      background: #fff;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .cart-header {
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .cart-header h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      color: var(--filey-primary);
      font-size: 18px;
    }
    .badge-count {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 24px;
      height: 24px;
      padding: 0 8px;
      border-radius: 12px;
      background: var(--filey-secondary);
      color: #fff;
      font-size: 13px;
      font-weight: 700;
    }
    .cart-body {
      flex: 1;
      overflow-y: auto;
      padding: 8px 16px;
    }
    .cart-item {
      display: grid;
      grid-template-columns: 50px 1fr auto auto;
      align-items: center;
      gap: 8px;
      padding: 12px 0;
      border-bottom: 1px solid var(--filey-border);
    }
    .cart-item:last-child { border-bottom: none; }
    .cart-item-clave {
      font-weight: 700;
      color: var(--filey-primary);
      font-size: 16px;
    }
    .cart-item-info { min-width: 0; }
    .cart-item-zona {
      font-weight: 500;
      font-size: 13px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .cart-item-meta { font-size: 11px; }
    .cart-item-precio {
      font-weight: 600;
      color: var(--filey-secondary);
      font-size: 14px;
    }
    .cart-empty {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      text-align: center;
      color: var(--filey-text-muted);
    }
    .cart-empty mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      margin-bottom: 12px;
      opacity: 0.5;
    }
    .cart-empty p { margin: 4px 0; font-weight: 500; color: var(--filey-text); }
    .cart-empty small { font-size: 12px; }
    .cart-footer {
      padding: 16px;
      background: var(--filey-bg-soft);
    }
    .cart-help {
      font-size: 11px;
      color: var(--filey-text-muted);
      margin: 8px 0 0;
      text-align: center;
    }
    .full-width { width: 100%; }
    .ms-2 { margin-left: 8px; }
    @media (max-width: 1024px) {
      .layout { grid-template-columns: 1fr; height: auto; }
      .cart-panel { max-height: 400px; }
    }
  `]
})
export class SeleccionComponent implements OnInit {
  private readonly standService: StandService = inject(StandService);
  private readonly carritoService: CarritoService = inject(CarritoService);
  private readonly parametrosService: ParametrosService = inject(ParametrosService);
  private readonly faseService: FaseService = inject(FaseService);
  private readonly router: Router = inject(Router);
  private readonly snackBar: MatSnackBar = inject(MatSnackBar);

  readonly items = this.carritoService.items;
  readonly subtotal = this.carritoService.subtotal;
  readonly metrosCuadrados = this.carritoService.metrosCuadrados;
  readonly costoM2 = this.parametrosService.parametros.costoM2;

  readonly puedeAvanzar = computed(() => this.faseService.puedeAvanzarASeleccion());

  ngOnInit(): void {
    if (!this.puedeAvanzar()) {
      this.router.navigate(['/usuario/aplicacion']);
    }
  }

  onAddToCart(standId: string): void {
    const stand = this.standService.getById(standId);
    if (!stand) return;
    const result = this.carritoService.agregar(stand);
    if (result.ok) {
      this.snackBar.open(`Stand ${stand.clave} agregado a tu selección`, 'OK', { duration: 2500 });
    } else {
      this.snackBar.open(result.mensaje || 'No se pudo agregar', 'OK', { duration: 2500 });
    }
  }

  quitarDelCarrito(standId: string): void {
    this.carritoService.quitar(standId);
  }

  limpiarCarrito(): void {
    this.carritoService.limpiar();
  }

  irAConfirmar(): void {
    if (this.items().length === 0) return;
    this.router.navigate(['/usuario/confirmar']);
  }
}
