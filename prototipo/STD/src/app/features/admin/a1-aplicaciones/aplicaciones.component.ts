import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AplicacionService } from '../../../services/aplicacion.service';
import { EditorialService } from '../../../services/editorial.service';
import { StatusBadgeComponent } from '../../../shared/components/status-badge.component';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';
import { EstadoAplicacion, Aplicacion } from '../../../data/models';
import { EmptyStateComponent } from '../../../shared/components/empty-state.component';

@Component({
  selector: 'app-aplicaciones',
  standalone: true,
  imports: [
    CommonModule, FormsModule, RouterModule, MatCardModule, MatTableModule, MatChipsModule,
    MatIconModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatTooltipModule,
    StatusBadgeComponent, DateMxPipe, EmptyStateComponent
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title">Aplicaciones</h1>
      <p class="page-subtitle">Solicitudes recibidas de las editoriales que desean participar.</p>

      <div class="filters">
        <mat-chip-listbox (change)="aplicarFiltroEstado($event)" [value]="filtroEstado()">
          <mat-chip-option value="todas" selected>Todas</mat-chip-option>
          <mat-chip-option value="pendiente">Pendientes</mat-chip-option>
          <mat-chip-option value="aceptada">Aceptadas</mat-chip-option>
          <mat-chip-option value="rechazada">Rechazadas</mat-chip-option>
          <mat-chip-option value="cambios_solicitados">Cambios solicitados</mat-chip-option>
        </mat-chip-listbox>
        <mat-form-field appearance="outline" class="search">
          <mat-label>Buscar por editorial</mat-label>
          <input matInput [(ngModel)]="busqueda" (input)="aplicarFiltro()" placeholder="Nombre...">
          <mat-icon matSuffix>search</mat-icon>
        </mat-form-field>
      </div>

      <mat-card>
        <mat-card-content>
          <ng-container *ngIf="aplicacionesFiltradas().length > 0; else vacio">
            <table mat-table [dataSource]="aplicacionesFiltradas()" class="full-width">
              <ng-container matColumnDef="id">
                <th mat-header-cell *matHeaderCellDef>Folio</th>
                <td mat-cell *matCellDef="let app">{{ app.id }}</td>
              </ng-container>
              <ng-container matColumnDef="editorial">
                <th mat-header-cell *matHeaderCellDef>Editorial</th>
                <td mat-cell *matCellDef="let app">
                  <strong>{{ nombreEditorial(app.editorialId) }}</strong>
                </td>
              </ng-container>
              <ng-container matColumnDef="estado">
                <th mat-header-cell *matHeaderCellDef>Estado</th>
                <td mat-cell *matCellDef="let app"><app-status-badge [estado]="app.estado"></app-status-badge></td>
              </ng-container>
              <ng-container matColumnDef="fecha">
                <th mat-header-cell *matHeaderCellDef>Enviada</th>
                <td mat-cell *matCellDef="let app">{{ app.fechaEnvio | dateMx }}</td>
              </ng-container>
              <ng-container matColumnDef="accion">
                <th mat-header-cell *matHeaderCellDef></th>
                <td mat-cell *matCellDef="let app">
                  <a mat-button color="primary" [routerLink]="['/admin/aplicaciones', app.id]">
                    Ver detalle <mat-icon>arrow_forward</mat-icon>
                  </a>
                </td>
              </ng-container>
              <tr mat-header-row *matHeaderRowDef="columnas"></tr>
              <tr mat-row *matRowDef="let row; columns: columnas;"></tr>
            </table>
          </ng-container>
          <ng-template #vacio>
            <app-empty-state
              icono="inbox"
              titulo="Sin aplicaciones"
              mensaje="No hay aplicaciones que coincidan con los filtros.">
            </app-empty-state>
          </ng-template>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .filters { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 16px; }
    .search { flex: 1; min-width: 250px; }
  `]
})
export class AplicacionesComponent implements OnInit {
  private readonly aplicacionService = inject(AplicacionService);
  private readonly editorialService = inject(EditorialService);

  readonly aplicaciones = this.aplicacionService.aplicaciones$;
  readonly aplicacionesFiltradas = signal<Aplicacion[]>([]);
  readonly filtroEstado = signal<EstadoAplicacion | 'todas'>('todas');
  busqueda = '';

  columnas = ['id', 'editorial', 'estado', 'fecha', 'accion'];

  ngOnInit(): void {
    this.aplicaciones.subscribe(list => {
      this.aplicarFiltroLista(list);
    });
  }

  aplicarFiltro(): void {
    this.aplicarFiltroLista(this.aplicacionService.aplicaciones);
  }

  aplicarFiltroEstado(event: any): void {
    this.filtroEstado.set(event.value);
    this.aplicarFiltroLista(this.aplicacionService.aplicaciones);
  }

  private aplicarFiltroLista(list: Aplicacion[]): void {
    let result = list;
    if (this.filtroEstado() !== 'todas') {
      result = result.filter(a => a.estado === this.filtroEstado());
    }
    if (this.busqueda.trim()) {
      const term = this.busqueda.toLowerCase();
      result = result.filter(a => {
        const ed = this.editorialService.getById(a.editorialId);
        return ed?.nombre.toLowerCase().includes(term);
      });
    }
    this.aplicacionesFiltradas.set(result);
  }

  nombreEditorial(id: string): string {
    return this.editorialService.getById(id)?.nombre || 'Desconocida';
  }
}
