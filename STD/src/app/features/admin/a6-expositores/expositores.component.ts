import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { AplicacionService } from '../../../services/aplicacion.service';
import { EditorialService } from '../../../services/editorial.service';
import { Editorial } from '../../../data/models';
import { EmptyStateComponent } from '../../../shared/components/empty-state.component';

@Component({
  selector: 'app-expositores',
  standalone: true,
  imports: [
    CommonModule, FormsModule, RouterModule, MatCardModule, MatTableModule, MatButtonModule,
    MatIconModule, MatFormFieldModule, MatInputModule, EmptyStateComponent
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title">Expositores</h1>
      <p class="page-subtitle">Editoriales con aplicación aceptada y habilitadas para reservar stands.</p>

      <mat-form-field appearance="outline" class="search">
        <mat-label>Buscar</mat-label>
        <input matInput [(ngModel)]="busqueda" (input)="aplicarFiltro()" placeholder="Nombre, RFC o email">
        <mat-icon matSuffix>search</mat-icon>
      </mat-form-field>

      <mat-card>
        <mat-card-content>
          <ng-container *ngIf="expositores().length > 0; else vacio">
            <table mat-table [dataSource]="expositores()" class="full-width">
              <ng-container matColumnDef="nombre">
                <th mat-header-cell *matHeaderCellDef>Nombre</th>
                <td mat-cell *matCellDef="let ed">
                  <strong>{{ ed.nombre }}</strong>
                  <div class="text-muted small">{{ ed.nombreAntepecho }}</div>
                </td>
              </ng-container>
              <ng-container matColumnDef="giro">
                <th mat-header-cell *matHeaderCellDef>Giro</th>
                <td mat-cell *matCellDef="let ed">{{ ed.giro }}</td>
              </ng-container>
              <ng-container matColumnDef="sellos">
                <th mat-header-cell *matHeaderCellDef>Sellos</th>
                <td mat-cell *matCellDef="let ed">{{ ed.totalSellos }}</td>
              </ng-container>
              <ng-container matColumnDef="contacto">
                <th mat-header-cell *matHeaderCellDef>Contacto</th>
                <td mat-cell *matCellDef="let ed">
                  {{ ed.responsableStand }}<br>
                  <span class="text-muted small">{{ ed.correoElectronico }}</span>
                </td>
              </ng-container>
              <ng-container matColumnDef="telefono">
                <th mat-header-cell *matHeaderCellDef>Teléfono</th>
                <td mat-cell *matCellDef="let ed">{{ ed.telefonoOficina }}</td>
              </ng-container>
              <ng-container matColumnDef="accion">
                <th mat-header-cell *matHeaderCellDef></th>
                <td mat-cell *matCellDef="let ed">
                  <a mat-button color="primary" [routerLink]="['/admin/expositores', ed.id]">
                    Ver perfil <mat-icon>arrow_forward</mat-icon>
                  </a>
                </td>
              </ng-container>
              <tr mat-header-row *matHeaderRowDef="columnas"></tr>
              <tr mat-row *matRowDef="let row; columns: columnas;"></tr>
            </table>
          </ng-container>
          <ng-template #vacio>
            <app-empty-state
              icono="people"
              titulo="Sin expositores aceptados"
              mensaje="Aún no hay editoriales con aplicación aceptada. Revise la bandeja de aplicaciones.">
            </app-empty-state>
          </ng-template>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .search { width: 100%; max-width: 400px; margin-bottom: 16px; }
    .small { font-size: 12px; }
  `]
})
export class ExpositoresComponent implements OnInit {
  private readonly aplicacionService = inject(AplicacionService);
  private readonly editorialService = inject(EditorialService);

  readonly expositores = signal<Editorial[]>([]);
  busqueda = '';
  columnas = ['nombre', 'giro', 'sellos', 'contacto', 'telefono', 'accion'];

  ngOnInit(): void {
    this.cargar();
  }

  aplicarFiltro(): void { this.cargar(); }

  private cargar(): void {
    const aceptadas = this.aplicacionService.aplicaciones
      .filter(a => a.estado === 'aceptada')
      .map(a => a.editorialId);
    let list = this.editorialService.editoriales.filter(e => aceptadas.includes(e.id));
    if (this.busqueda.trim()) {
      const term = this.busqueda.toLowerCase();
      list = list.filter(e =>
        e.nombre.toLowerCase().includes(term) ||
        e.correoElectronico.toLowerCase().includes(term)
      );
    }
    this.expositores.set(list);
  }
}
