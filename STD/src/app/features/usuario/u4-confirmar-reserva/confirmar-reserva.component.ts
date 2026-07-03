import { Component, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { CarritoService } from '../../../services/carrito.service';
import { ReservaService } from '../../../services/reserva.service';
import { ParametrosService } from '../../../services/parametros.service';
import { AuthService } from '../../../services/auth.service';
import { CurrencyMxPipe } from '../../../shared/pipes/currency-mx.pipe';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';
import { MOCK_EVENTO } from '../../../data/mock';

@Component({
  selector: 'app-confirmar-reserva',
  standalone: true,
  imports: [
    CommonModule, MatCardModule, MatButtonModule, MatIconModule, MatDividerModule,
    MatSnackBarModule, CurrencyMxPipe, DateMxPipe
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title">Confirmar reserva</h1>
      <p class="page-subtitle">Revisa el resumen y confirma tu reserva para {{ evento.nombre }} {{ evento.edicion }}</p>

      <div class="grid-2">
        <mat-card>
          <mat-card-header>
            <mat-card-title>Stands seleccionados</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <table class="full-width">
              <thead>
                <tr>
                  <th>Stand</th>
                  <th>Zona</th>
                  <th>Superficie</th>
                  <th class="num">Precio</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let item of items()">
                  <td><strong>{{ item.stand.clave }}</strong></td>
                  <td>{{ item.stand.zona }}</td>
                  <td>{{ item.stand.metrosCuadrados }} m²</td>
                  <td class="num">{{ item.precioUnitario | currencyMx }}</td>
                </tr>
              </tbody>
            </table>

            <div class="mt-3">
              <div class="summary-row">
                <span class="summary-label">Subtotal</span>
                <span class="summary-value">{{ subtotal() | currencyMx }}</span>
              </div>
              <div class="summary-row" *ngIf="aplicaProntoPago()">
                <span class="summary-label">
                  Descuento pronto pago ({{ params.descuentoProntoPago }}%)
                </span>
                <span class="summary-value discount">- {{ montoDescuento() | currencyMx }}</span>
              </div>
              <div class="summary-row total">
                <span>Total con descuento</span>
                <span>{{ totalConDescuento() | currencyMx }}</span>
              </div>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header>
            <mat-card-title>Información de pago</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="summary-row">
              <span class="summary-label">Anticipo requerido ({{ params.porcentajeAnticipo }}%)</span>
              <span class="summary-value warn">{{ anticipo() | currencyMx }}</span>
            </div>
            <div class="summary-row">
              <span class="summary-label">Saldo restante</span>
              <span class="summary-value">{{ saldoRestante() | currencyMx }}</span>
            </div>

            <mat-divider class="my-3"></mat-divider>

            <div class="info-banner">
              <mat-icon>schedule</mat-icon>
              <div>
                <strong>Plazo para cubrir el anticipo</strong><br>
                {{ fechaVencimiento() | dateMx:'largo' }}<br>
                <small>({{ params.plazoReservaDias }} días a partir de la confirmación)</small>
              </div>
            </div>

            <div class="info-banner" *ngIf="aplicaProntoPago()">
              <mat-icon>local_offer</mat-icon>
              <div>
                <strong>Descuento por pronto pago</strong><br>
                Aplicas un {{ params.descuentoProntoPago }}% de descuento.
                Después del {{ params.fechaLimiteProntoPago | dateMx:'largo' }} el total
                vuelve a ser {{ subtotal() | currencyMx }}.
              </div>
            </div>

            <div class="action-bar">
              <button mat-stroked-button (click)="cancelar()">
                <mat-icon>close</mat-icon> Cancelar
              </button>
              <button mat-raised-button color="primary" (click)="confirmar()">
                <mat-icon>check</mat-icon> Confirmar reserva
              </button>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .grid-2 {
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 24px;
    }
    table { border-collapse: collapse; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid var(--filey-border); }
    th { color: var(--filey-primary); font-weight: 600; font-size: 13px; text-transform: uppercase; }
    .num { text-align: right; }
    .my-3 { margin: 16px 0; }
    @media (max-width: 1024px) {
      .grid-2 { grid-template-columns: 1fr; }
    }
  `]
})
export class ConfirmarReservaComponent {
  private readonly carritoService = inject(CarritoService);
  private readonly reservaService = inject(ReservaService);
  private readonly parametrosService = inject(ParametrosService);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);

  readonly evento = MOCK_EVENTO;
  readonly items = this.carritoService.items;
  readonly subtotal = this.carritoService.subtotal;
  readonly params = this.parametrosService.parametros;

  readonly montoDescuento = computed(() => this.subtotal() * (this.params.descuentoProntoPago / 100));
  readonly totalConDescuento = computed(() => this.subtotal() - this.montoDescuento());
  readonly anticipo = computed(() => this.totalConDescuento() * (this.params.porcentajeAnticipo / 100));
  readonly saldoRestante = computed(() => this.totalConDescuento() - this.anticipo());

  aplicaProntoPago(): boolean {
    return new Date() <= this.params.fechaLimiteProntoPago;
  }

  fechaVencimiento(): Date {
    const f = new Date();
    f.setDate(f.getDate() + this.params.plazoReservaDias);
    return f;
  }

  confirmar(): void {
    const result = this.reservaService.crearDesdeCarrito(this.authService.editorialActual, this.evento.id);
    if (!result.ok) {
      this.snackBar.open(`Error: ${result.errores?.join(', ')}`, 'OK', { duration: 4000 });
      return;
    }
    this.snackBar.open('¡Reserva confirmada con éxito!', 'OK', { duration: 3000 });
    this.router.navigate(['/usuario/mi-reserva']);
  }

  cancelar(): void {
    this.router.navigate(['/usuario/seleccion']);
  }
}
