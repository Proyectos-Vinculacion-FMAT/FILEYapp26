import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { StandService } from '../../../services/stand.service';
import { Stand } from '../../../data/models';
import { CurrencyMxPipe } from '../../../shared/pipes/currency-mx.pipe';

@Component({
  selector: 'app-editar-espacio',
  standalone: true,
  imports: [
    CommonModule, RouterModule, FormsModule, ReactiveFormsModule, MatCardModule,
    MatFormFieldModule, MatInputModule, MatButtonModule, MatIconModule, MatDividerModule,
    MatSnackBarModule, CurrencyMxPipe
  ],
  template: `
    <div class="page-container" *ngIf="stand(); else noExiste">
      <a mat-button routerLink="/admin/mapa" class="back-link">
        <mat-icon>arrow_back</mat-icon> Mapa completo
      </a>

      <h1 class="page-title">Editar espacio: {{ stand()!.clave }}</h1>
      <p class="page-subtitle">Modifica las características físicas del stand. Estos cambios no afectan reservas existentes.</p>

      <div *ngIf="estaReservado()" class="warning-banner">
        <mat-icon>info</mat-icon>
        <div>
          <strong>Este stand ya está reservado.</strong><br>
          Los cambios en dimensiones o precio solo afectarán nuevas reservas.
          Las reservas existentes conservan el precio y m² capturados en el momento de su creación (snapshot).
        </div>
      </div>

      <mat-card class="mt-2">
        <mat-card-content>
          <form [formGroup]="form" (ngSubmit)="guardar()">
            <div class="grid-2">
              <mat-form-field appearance="outline">
                <mat-label>Clave del stand</mat-label>
                <input matInput formControlName="clave">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Zona</mat-label>
                <input matInput formControlName="zona">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Ancho (m)</mat-label>
                <input matInput type="number" formControlName="ancho" min="0.1">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Largo (m)</mat-label>
                <input matInput type="number" formControlName="largo" min="0.1">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Precio manual (opcional)</mat-label>
                <span matTextPrefix>$&nbsp;</span>
                <input matInput type="number" formControlName="precio">
                <mat-hint>Si se deja vacío, se calcula con m² × costo por m²</mat-hint>
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Posición X (col)</mat-label>
                <input matInput type="number" formControlName="posX">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Posición Y (row)</mat-label>
                <input matInput type="number" formControlName="posY">
              </mat-form-field>
            </div>

            <mat-divider class="my-3"></mat-divider>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Qué incluye</mat-label>
              <textarea matInput formControlName="incluye" rows="3"></textarea>
            </mat-form-field>

            <div class="preview">
              <h3>Vista previa</h3>
              <div class="summary-row">
                <span class="summary-label">Superficie calculada</span>
                <span class="summary-value">{{ metrosCuadrados() }} m²</span>
              </div>
              <div class="summary-row">
                <span class="summary-label">Precio final</span>
                <span class="summary-value">{{ precioFinal() | currencyMx }}</span>
              </div>
            </div>

            <div class="action-bar">
              <button mat-stroked-button type="button" routerLink="/admin/mapa">Cancelar</button>
              <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid">
                <mat-icon>save</mat-icon> Guardar cambios
              </button>
            </div>
          </form>
        </mat-card-content>
      </mat-card>
    </div>

    <ng-template #noExiste>
      <div class="page-container">
        <h1 class="page-title">Stand no encontrado</h1>
        <button mat-button routerLink="/admin/mapa">
          <mat-icon>arrow_back</mat-icon> Volver al mapa
        </button>
      </div>
    </ng-template>
  `,
  styles: [`
    .back-link { margin-bottom: 16px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .preview {
      background: var(--filey-bg-soft);
      padding: 16px;
      border-radius: 8px;
      margin: 24px 0;
    }
    .my-3 { margin: 16px 0; }
    .mt-2 { margin-top: 16px; }
    .full-width { width: 100%; }
  `]
})
export class EditarEspacioComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);
  private readonly standService = inject(StandService);
  private readonly snackBar = inject(MatSnackBar);

  readonly stand = signal<Stand | null>(null);
  form!: FormGroup;
  private costoM2 = 2500;

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('standId');
    if (id) {
      const s = this.standService.getById(id);
      if (s) {
        this.stand.set(s);
        this.form = this.fb.group({
          clave: [s.clave, Validators.required],
          zona: [s.zona || ''],
          ancho: [s.ancho, [Validators.required, Validators.min(0.1)]],
          largo: [s.largo, [Validators.required, Validators.min(0.1)]],
          precio: [s.precio || null],
          posX: [s.posX, Validators.required],
          posY: [s.posY, Validators.required],
          incluye: [s.incluye, Validators.required]
        });
      }
    }
  }

  estaReservado(): boolean {
    const s = this.stand();
    return s ? s.estado === 'Reservado' || s.estado === 'Ocupado' : false;
  }

  metrosCuadrados(): number {
    const v = this.form?.value;
    if (!v) return 0;
    return Math.round((v.ancho * v.largo) * 100) / 100;
  }

  precioFinal(): number {
    if (!this.form) return 0;
    if (this.form.value.precio) return this.form.value.precio;
    return this.metrosCuadrados() * this.costoM2;
  }

  guardar(): void {
    if (this.form.invalid) return;
    const s = this.stand();
    if (!s) return;
    const v = this.form.value;
    const actualizado: Stand = {
      ...s,
      clave: v.clave,
      zona: v.zona,
      ancho: v.ancho,
      largo: v.largo,
      metrosCuadrados: this.metrosCuadrados(),
      precio: v.precio || undefined,
      posX: v.posX,
      posY: v.posY,
      incluye: v.incluye
    };
    this.standService.actualizar(actualizado);
    this.snackBar.open('Cambios guardados. Se ha registrado en la bitácora (simulado).', 'OK', { duration: 3000 });
    this.router.navigate(['/admin/mapa']);
  }
}
