import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MovimientoService } from '../../../services/movimiento.service';
import { ReservaService } from '../../../services/reserva.service';
import { EditorialService } from '../../../services/editorial.service';
import { CurrencyMxPipe } from '../../../shared/pipes/currency-mx.pipe';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';
import { Movimiento } from '../../../data/models';
import { EmptyStateComponent } from '../../../shared/components/empty-state.component';
import { ValidarMovimientoDialogComponent } from '../a4-detalle-reserva/detalle-reserva.component';

@Component({
  selector: 'app-pagos-validar',
  standalone: true,
  imports: [
    CommonModule, RouterModule, MatCardModule, MatTableModule, MatButtonModule, MatIconModule,
    MatDialogModule, MatSnackBarModule, CurrencyMxPipe, DateMxPipe, EmptyStateComponent
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title">Pagos por validar</h1>
      <p class="page-subtitle">Cola de movimientos pendientes de validación. Los pagos validados aquí afectan el saldo de la reserva.</p>

      <mat-card>
        <mat-card-content>
          <ng-container *ngIf="pendientes().length > 0; else vacio">
            <table mat-table [dataSource]="pendientes()" class="full-width">
              <ng-container matColumnDef="fecha">
                <th mat-header-cell *matHeaderCellDef>Fecha</th>
                <td mat-cell *matCellDef="let m">{{ m.fechaRegistro | dateMx:'cortoHora' }}</td>
              </ng-container>
              <ng-container matColumnDef="editorial">
                <th mat-header-cell *matHeaderCellDef>Editorial</th>
                <td mat-cell *matCellDef="let m">{{ nombreEditorial(m.reservaId) }}</td>
              </ng-container>
              <ng-container matColumnDef="reserva">
                <th mat-header-cell *matHeaderCellDef>Reserva</th>
                <td mat-cell *matCellDef="let m">
                  <a [routerLink]="['/admin/reservas', m.reservaId]">{{ m.reservaId }}</a>
                </td>
              </ng-container>
              <ng-container matColumnDef="monto">
                <th mat-header-cell *matHeaderCellDef>Monto</th>
                <td mat-cell *matCellDef="let m">{{ m.monto | currencyMx }}</td>
              </ng-container>
              <ng-container matColumnDef="metodo">
                <th mat-header-cell *matHeaderCellDef>Método</th>
                <td mat-cell *matCellDef="let m">{{ m.metodo }}</td>
              </ng-container>
              <ng-container matColumnDef="comprobante">
                <th mat-header-cell *matHeaderCellDef>Comprobante</th>
                <td mat-cell *matCellDef="let m">
                  <button mat-button (click)="verComprobante(m)" *ngIf="m.comprobanteNombre">
                    <mat-icon>description</mat-icon> Ver
                  </button>
                </td>
              </ng-container>
              <ng-container matColumnDef="accion">
                <th mat-header-cell *matHeaderCellDef></th>
                <td mat-cell *matCellDef="let m">
                  <button mat-raised-button color="primary" (click)="validar(m)">
                    <mat-icon>fact_check</mat-icon> Validar
                  </button>
                </td>
              </ng-container>
              <tr mat-header-row *matHeaderRowDef="columnas"></tr>
              <tr mat-row *matRowDef="let row; columns: columnas;"></tr>
            </table>
          </ng-container>
          <ng-template #vacio>
            <app-empty-state
              icono="check_circle"
              titulo="No hay pagos pendientes"
              mensaje="Todos los pagos han sido validados.">
            </app-empty-state>
          </ng-template>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [``]
})
export class PagosValidarComponent implements OnInit {
  private readonly movimientoService = inject(MovimientoService);
  private readonly reservaService = inject(ReservaService);
  private readonly editorialService = inject(EditorialService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  readonly pendientes = signal<Movimiento[]>([]);
  columnas = ['fecha', 'editorial', 'reserva', 'monto', 'metodo', 'comprobante', 'accion'];

  ngOnInit(): void {
    this.movimientoService.movimientos$.subscribe(() => this.cargar());
    this.cargar();
  }

  cargar(): void {
    this.pendientes.set(this.movimientoService.getPendientesValidacion());
  }

  nombreEditorial(reservaId: string): string {
    const r = this.reservaService.getById(reservaId);
    return this.editorialService.getById(r?.editorialId || '')?.nombre || 'Desconocida';
  }

  verComprobante(m: Movimiento): void {
    this.snackBar.open(`Viendo ${m.comprobanteNombre} (simulado)`, 'OK', { duration: 2000 });
  }

  validar(m: Movimiento): void {
    const ref = this.dialog.open(ValidarMovimientoDialogComponent);
    ref.componentInstance.movimiento = m;
    ref.afterClosed().subscribe(result => {
      if (!result) return;
      if (result.accion === 'validar') {
        this.movimientoService.validar(m.id);
        this.snackBar.open('Movimiento validado. El saldo ha sido actualizado.', 'OK', { duration: 3000 });
      } else if (result.accion === 'rechazar') {
        this.movimientoService.rechazar(m.id, result.motivo);
        this.snackBar.open('Movimiento rechazado.', 'OK', { duration: 3000 });
      }
    });
  }
}
