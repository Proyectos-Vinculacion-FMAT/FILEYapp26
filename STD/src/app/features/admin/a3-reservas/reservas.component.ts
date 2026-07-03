import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { ReservaService } from '../../../services/reserva.service';
import { EditorialService } from '../../../services/editorial.service';
import { StatusBadgeComponent } from '../../../shared/components/status-badge.component';
import { CurrencyMxPipe } from '../../../shared/pipes/currency-mx.pipe';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';
import { EstadoReserva, Reserva } from '../../../data/models';
import { EmptyStateComponent } from '../../../shared/components/empty-state.component';

@Component({
  selector: 'app-reservas',
  standalone: true,
  imports: [
    CommonModule, FormsModule, RouterModule, MatCardModule, MatTableModule, MatChipsModule,
    MatIconModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatSelectModule,
    StatusBadgeComponent, CurrencyMxPipe, DateMxPipe, EmptyStateComponent
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title">Reservas</h1>
      <p class="page-subtitle">Listado de todas las reservas del evento.</p>

      <div class="filters">
        <mat-chip-listbox (change)="aplicarFiltroEstado($event)" [value]="filtroEstado()">
          <mat-chip-option value="todas" selected>Todas</mat-chip-option>
          <mat-chip-option value="vencidas" class="vencida-chip">Vencidas</mat-chip-option>
          <mat-chip-option value="Por confirmar">Por confirmar</mat-chip-option>
          <mat-chip-option value="Confirmada">Confirmadas</mat-chip-option>
          <mat-chip-option value="Pagada">Pagadas</mat-chip-option>
          <mat-chip-option value="Cancelada">Canceladas</mat-chip-option>
        </mat-chip-listbox>
        <mat-form-field appearance="outline" class="search">
          <mat-label>Buscar</mat-label>
          <input matInput [(ngModel)]="busqueda" (input)="aplicarFiltro()" placeholder="ID o nombre de editorial">
          <mat-icon matSuffix>search</mat-icon>
        </mat-form-field>
      </div>

      <mat-card>
        <mat-card-content>
          <ng-container *ngIf="reservasFiltradas().length > 0; else vacio">
            <table mat-table [dataSource]="reservasFiltradas()" class="full-width">
              <ng-container matColumnDef="id">
                <th mat-header-cell *matHeaderCellDef>Folio</th>
                <td mat-cell *matCellDef="let r">{{ r.id }}</td>
              </ng-container>
              <ng-container matColumnDef="editorial">
                <th mat-header-cell *matHeaderCellDef>Editorial</th>
                <td mat-cell *matCellDef="let r">{{ nombreEditorial(r.editorialId) }}</td>
              </ng-container>
              <ng-container matColumnDef="estado">
                <th mat-header-cell *matHeaderCellDef>Estado</th>
                <td mat-cell *matCellDef="let r"><app-status-badge [estado]="r.estado"></app-status-badge></td>
              </ng-container>
              <ng-container matColumnDef="stands">
                <th mat-header-cell *matHeaderCellDef>Stands</th>
                <td mat-cell *matCellDef="let r">{{ r.stands.length }}</td>
              </ng-container>
              <ng-container matColumnDef="total">
                <th mat-header-cell *matHeaderCellDef>Total</th>
                <td mat-cell *matCellDef="let r">{{ r.montoTotal | currencyMx }}</td>
              </ng-container>
              <ng-container matColumnDef="abonado">
                <th mat-header-cell *matHeaderCellDef>Abonado</th>
                <td mat-cell *matCellDef="let r">{{ r.montoAbonado | currencyMx }}</td>
              </ng-container>
              <ng-container matColumnDef="pendiente">
                <th mat-header-cell *matHeaderCellDef>Pendiente</th>
                <td mat-cell *matCellDef="let r">{{ r.montoPendiente | currencyMx }}</td>
              </ng-container>
              <ng-container matColumnDef="vencimiento">
                <th mat-header-cell *matHeaderCellDef>Vence</th>
                <td mat-cell *matCellDef="let r" [class.warn-text]="esVencida(r)">
                  {{ r.fechaVencimientoAnticipo | dateMx }}
                </td>
              </ng-container>
              <ng-container matColumnDef="accion">
                <th mat-header-cell *matHeaderCellDef></th>
                <td mat-cell *matCellDef="let r">
                  <a mat-button color="primary" [routerLink]="['/admin/reservas', r.id]">
                    Ver detalle <mat-icon>arrow_forward</mat-icon>
                  </a>
                </td>
              </ng-container>
              <tr mat-header-row *matHeaderRowDef="columnas"></tr>
              <tr mat-row *matRowDef="let row; columns: columnas;" [class.status-vencida-row]="esVencida(row)"></tr>
            </table>
          </ng-container>
          <ng-template #vacio>
            <app-empty-state
              icono="event"
              titulo="Sin reservas"
              mensaje="No hay reservas que coincidan con los filtros.">
            </app-empty-state>
          </ng-template>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .filters { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 16px; }
    .search { flex: 1; min-width: 250px; }
    .vencida-chip { background: #fff5f5 !important; color: #c0473b !important; }
    .warn-text { color: var(--filey-secondary); font-weight: 600; }
  `]
})
export class ReservasComponent implements OnInit {
  private readonly reservaService = inject(ReservaService);
  private readonly editorialService = inject(EditorialService);

  readonly reservasFiltradas = signal<Reserva[]>([]);
  readonly filtroEstado = signal<string>('todas');
  busqueda = '';
  columnas = ['id', 'editorial', 'estado', 'stands', 'total', 'abonado', 'pendiente', 'vencimiento', 'accion'];

  ngOnInit(): void {
    this.reservaService.reservas$.subscribe(() => this.aplicarFiltroLista());
    this.aplicarFiltroLista();
  }

  aplicarFiltro(): void { this.aplicarFiltroLista(); }

  aplicarFiltroEstado(event: any): void {
    this.filtroEstado.set(event.value);
    this.aplicarFiltroLista();
  }

  private aplicarFiltroLista(): void {
    let list = this.reservaService.reservas;
    if (this.filtroEstado() === 'vencidas') {
      list = this.reservaService.getVencidas();
    } else if (this.filtroEstado() !== 'todas') {
      list = list.filter(r => r.estado === this.filtroEstado());
    }
    if (this.busqueda.trim()) {
      const term = this.busqueda.toLowerCase();
      list = list.filter(r => {
        const ed = this.editorialService.getById(r.editorialId);
        return r.id.toLowerCase().includes(term) || (ed?.nombre.toLowerCase().includes(term) ?? false);
      });
    }
    this.reservasFiltradas.set(list);
  }

  nombreEditorial(id: string): string {
    return this.editorialService.getById(id)?.nombre || 'Desconocida';
  }

  esVencida(r: Reserva): boolean {
    return r.estado === 'Por confirmar' && r.fechaVencimientoAnticipo < new Date() && r.montoAbonado < r.anticipoRequerido;
  }
}
