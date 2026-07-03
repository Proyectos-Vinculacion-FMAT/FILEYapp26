import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { ParametrosService } from '../../../services/parametros.service';

@Component({
  selector: 'app-configuracion',
  standalone: true,
  imports: [
    CommonModule, FormsModule, ReactiveFormsModule, MatCardModule, MatFormFieldModule,
    MatInputModule, MatButtonModule, MatIconModule, MatDividerModule, MatSnackBarModule,
    MatDatepickerModule, MatNativeDateModule
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title">Configuración del sistema</h1>
      <p class="page-subtitle">Parámetros globales. Los cambios no afectan reservas existentes (usan snapshots).</p>

      <form [formGroup]="form" (ngSubmit)="guardar()">
        <div class="grid-2">
          <mat-card>
            <mat-card-header>
              <mat-card-title>Costos y porcentajes</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Costo por m²</mat-label>
                <span matTextPrefix>$&nbsp;</span>
                <input matInput type="number" formControlName="costoM2" min="0">
                <mat-hint>Precio base por metro cuadrado</mat-hint>
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Porcentaje de anticipo</mat-label>
                <input matInput type="number" formControlName="porcentajeAnticipo" min="0" max="100">
                <span matTextSuffix>%</span>
                <mat-hint>% del total que se requiere para confirmar la reserva</mat-hint>
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Plazo de reserva (días)</mat-label>
                <input matInput type="number" formControlName="plazoReservaDias" min="1">
                <mat-hint>Días de vigencia antes de requerir el anticipo</mat-hint>
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Descuento por pronto pago</mat-label>
                <input matInput type="number" formControlName="descuentoProntoPago" min="0" max="100">
                <span matTextSuffix>%</span>
              </mat-form-field>

              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Fecha límite de pronto pago</mat-label>
                <input matInput [matDatepicker]="picker" formControlName="fechaLimiteProntoPago">
                <mat-datepicker-toggle matIconSuffix [for]="picker"></mat-datepicker-toggle>
                <mat-datepicker #picker></mat-datepicker>
              </mat-form-field>
            </mat-card-content>
          </mat-card>

          <mat-card>
            <mat-card-header>
              <mat-card-title>Datos bancarios</mat-card-title>
            </mat-card-header>
            <mat-card-content>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Titular</mat-label>
                <input matInput formControlName="titular">
              </mat-form-field>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Banco</mat-label>
                <input matInput formControlName="banco">
              </mat-form-field>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Número de cuenta</mat-label>
                <input matInput formControlName="cuenta">
              </mat-form-field>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>CLABE</mat-label>
                <input matInput formControlName="clabe">
              </mat-form-field>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Sucursal</mat-label>
                <input matInput formControlName="sucursal">
              </mat-form-field>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Referencia / Concepto</mat-label>
                <input matInput formControlName="referencia">
              </mat-form-field>
            </mat-card-content>
          </mat-card>
        </div>

        <mat-card class="mt-3">
          <mat-card-header>
            <mat-card-title>Instrucciones de pago</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Texto de instrucciones</mat-label>
              <textarea matInput formControlName="instruccionesPago" rows="4"></textarea>
            </mat-form-field>
          </mat-card-content>
        </mat-card>

        <div class="action-bar mt-3">
          <button mat-stroked-button type="button" (click)="restablecer()">Restablecer</button>
          <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid">
            <mat-icon>save</mat-icon> Guardar configuración
          </button>
        </div>
      </form>
    </div>
  `,
  styles: [`
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    .full-width { width: 100%; }
    .mt-3 { margin-top: 24px; }
    @media (max-width: 1024px) { .grid-2 { grid-template-columns: 1fr; } }
  `]
})
export class ConfiguracionComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly parametrosService = inject(ParametrosService);
  private readonly snackBar = inject(MatSnackBar);

  form!: FormGroup;

  ngOnInit(): void {
    const p = this.parametrosService.parametros;
    this.form = this.fb.group({
      costoM2: [p.costoM2, [Validators.required, Validators.min(0)]],
      porcentajeAnticipo: [p.porcentajeAnticipo, [Validators.required, Validators.min(0), Validators.max(100)]],
      plazoReservaDias: [p.plazoReservaDias, [Validators.required, Validators.min(1)]],
      descuentoProntoPago: [p.descuentoProntoPago, [Validators.required, Validators.min(0), Validators.max(100)]],
      fechaLimiteProntoPago: [p.fechaLimiteProntoPago, Validators.required],
      titular: [p.datosBancarios.titular, Validators.required],
      banco: [p.datosBancarios.banco, Validators.required],
      cuenta: [p.datosBancarios.cuenta, Validators.required],
      clabe: [p.datosBancarios.clabe, Validators.required],
      sucursal: [p.datosBancarios.sucursal, Validators.required],
      referencia: [p.datosBancarios.referencia, Validators.required],
      instruccionesPago: [p.instruccionesPago, Validators.required]
    });
  }

  guardar(): void {
    if (this.form.invalid) {
      this.snackBar.open('Verifique los campos requeridos', 'OK', { duration: 3000 });
      return;
    }
    const v = this.form.value;
    this.parametrosService.actualizar({
      costoM2: v.costoM2,
      porcentajeAnticipo: v.porcentajeAnticipo,
      plazoReservaDias: v.plazoReservaDias,
      descuentoProntoPago: v.descuentoProntoPago,
      fechaLimiteProntoPago: v.fechaLimiteProntoPago,
      datosBancarios: {
        titular: v.titular,
        banco: v.banco,
        cuenta: v.cuenta,
        clabe: v.clabe,
        sucursal: v.sucursal,
        referencia: v.referencia
      },
      instruccionesPago: v.instruccionesPago
    });
    this.snackBar.open('Configuración actualizada. Los cambios se aplicarán a nuevas operaciones.', 'OK', { duration: 3000 });
  }

  restablecer(): void {
    this.ngOnInit();
    this.snackBar.open('Formulario restablecido', 'OK', { duration: 1500 });
  }
}
