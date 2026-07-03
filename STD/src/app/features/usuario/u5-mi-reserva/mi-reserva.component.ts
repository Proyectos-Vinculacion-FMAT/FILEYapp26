import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ReservaService } from '../../../services/reserva.service';
import { MovimientoService } from '../../../services/movimiento.service';
import { ParametrosService } from '../../../services/parametros.service';
import { AuthService } from '../../../services/auth.service';
import { StatusBadgeComponent } from '../../../shared/components/status-badge.component';
import { CurrencyMxPipe } from '../../../shared/pipes/currency-mx.pipe';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';
import { EmptyStateComponent } from '../../../shared/components/empty-state.component';
import { Movimiento, Reserva } from '../../../data/models';

@Component({
  selector: 'app-mi-reserva',
  standalone: true,
  imports: [
    CommonModule, RouterModule, ReactiveFormsModule, FormsModule,
    MatCardModule, MatButtonModule, MatIconModule, MatProgressBarModule, MatDividerModule,
    MatTabsModule, MatTableModule, MatFormFieldModule, MatInputModule, MatSelectModule,
    MatSnackBarModule, StatusBadgeComponent, CurrencyMxPipe, DateMxPipe, EmptyStateComponent
  ],
  template: `
    <div class="page-container">
      <h1 class="page-title">Mi reserva</h1>
      <p class="page-subtitle">Estado de tu reserva, stands seleccionados y gestión de pagos.</p>

      <ng-container *ngIf="reserva(); else sinReserva">
        <div *ngIf="estaVencida()" class="warning-banner">
          <mat-icon>warning</mat-icon>
          <div>
            <strong>Su reserva puede ser cancelada.</strong><br>
            El plazo de 30 días para cubrir el anticipo del 50% ha vencido.
            Aún no ha cubierto el monto mínimo. Por favor regularice su situación registrando
            un pago en la pestaña "Pagos", o contacte a la organización.
          </div>
        </div>

        <mat-card>
          <mat-card-content>
            <div class="reserva-header">
              <div>
                <div class="reserva-id">Reserva {{ reserva()!.id }}</div>
                <div class="text-muted">Creada: {{ reserva()!.fechaCreacion | dateMx:'largo' }}</div>
              </div>
              <app-status-badge [estado]="reserva()!.estado"></app-status-badge>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-tab-group class="mt-2">
          <mat-tab label="Resumen">
            <div class="grid-layout">
              <mat-card>
                <mat-card-header>
                  <mat-card-title>Desglose financiero</mat-card-title>
                </mat-card-header>
                <mat-card-content>
                  <div class="summary-row">
                    <span class="summary-label">Total sin descuento</span>
                    <span class="summary-value">{{ reserva()!.montoOriginal | currencyMx }}</span>
                  </div>
                  <div class="summary-row" *ngFor="let d of reserva()!.descuentos">
                    <span class="summary-label">
                      Descuento {{ d.tipo === 'pronto_pago' ? 'pronto pago' : 'especial' }}
                      ({{ d.porcentaje }}%)
                    </span>
                    <span class="summary-value discount">- {{ d.montoDescontado | currencyMx }}</span>
                  </div>
                  <div class="summary-row">
                    <span class="summary-label">Total con descuento</span>
                    <span class="summary-value">{{ reserva()!.montoTotal | currencyMx }}</span>
                  </div>
                  <div class="summary-row">
                    <span class="summary-label">Anticipo requerido ({{ porcentajeAnticipo }}%)</span>
                    <span class="summary-value warn">{{ reserva()!.anticipoRequerido | currencyMx }}</span>
                  </div>
                  <div class="summary-row">
                    <span class="summary-label">Monto abonado</span>
                    <span class="summary-value">{{ reserva()!.montoAbonado | currencyMx }}</span>
                  </div>
                  <div class="summary-row total">
                    <span>Saldo pendiente</span>
                    <span>{{ reserva()!.montoPendiente | currencyMx }}</span>
                  </div>

                  <div class="progress-section mt-3">
                    <div class="progress-label">
                      <span>Progreso de pago</span>
                      <span>{{ porcentajePagado() }}%</span>
                    </div>
                    <mat-progress-bar
                      mode="determinate"
                      [value]="porcentajePagado()"
                      [color]="porcentajePagado() >= 100 ? 'primary' : 'accent'">
                    </mat-progress-bar>
                    <div class="progress-marks">
                      <span class="mark" [class.reached]="porcentajePagado() >= 50">50% Confirmada</span>
                      <span class="mark" [class.reached]="porcentajePagado() >= 100">100% Pagada</span>
                    </div>
                  </div>

                  <mat-divider class="my-3"></mat-divider>

                  <h3>Fechas clave</h3>
                  <div class="fechas-grid">
                    <div class="fecha-item">
                      <mat-icon>schedule</mat-icon>
                      <div>
                        <div class="fecha-label">Vencimiento del anticipo</div>
                        <div class="fecha-value" [class.warn]="estaVencida()">
                          {{ reserva()!.fechaVencimientoAnticipo | dateMx:'largo' }}
                        </div>
                      </div>
                    </div>
                    <div class="fecha-item" *ngIf="reserva()!.fechaCortePagoTotal">
                      <mat-icon>event</mat-icon>
                      <div>
                        <div class="fecha-label">Fecha de corte (pago total)</div>
                        <div class="fecha-value">{{ reserva()!.fechaCortePagoTotal | dateMx:'largo' }}</div>
                      </div>
                    </div>
                  </div>
                </mat-card-content>
              </mat-card>

              <mat-card>
                <mat-card-header>
                  <mat-card-title>Stands reservados</mat-card-title>
                </mat-card-header>
                <mat-card-content>
                  <div *ngFor="let s of reserva()!.stands" class="stand-item">
                    <div class="clave">{{ s.clave }}</div>
                    <div class="info">
                      <div>{{ s.zona }}</div>
                      <div class="text-muted small">{{ s.metrosCuadradosSnapshot }} m²</div>
                    </div>
                    <div class="precio">{{ s.precioSnapshot | currencyMx }}</div>
                  </div>
                </mat-card-content>
              </mat-card>
            </div>
          </mat-tab>

          <mat-tab label="Pagos">
            <div class="pagos-content">
              <div class="info-banner">
                <mat-icon>info</mat-icon>
                <div>
                  <strong>Importante:</strong> No se aceptan pagos en efectivo.
                  Los métodos aceptados son transferencia bancaria, depósito bancario o cheque.
                </div>
              </div>

              <h3>Datos bancarios</h3>
              <div class="datos-bancarios">
                <div class="dato">
                  <span class="lbl">Titular</span>
                  <span class="val">{{ datos.titular }}</span>
                </div>
                <div class="dato">
                  <span class="lbl">Banco</span>
                  <span class="val">{{ datos.banco }}</span>
                </div>
                <div class="dato">
                  <span class="lbl">Número de cuenta</span>
                  <span class="val">{{ datos.cuenta }}</span>
                </div>
                <div class="dato">
                  <span class="lbl">CLABE</span>
                  <span class="val">{{ datos.clabe }}</span>
                </div>
                <div class="dato">
                  <span class="lbl">Sucursal</span>
                  <span class="val">{{ datos.sucursal }}</span>
                </div>
                <div class="dato">
                  <span class="lbl">Concepto / Referencia</span>
                  <span class="val">{{ datos.referencia }}</span>
                </div>
              </div>

              <p class="mt-2 text-muted"><small>{{ params.instruccionesPago }}</small></p>

              <mat-divider class="my-3"></mat-divider>

              <h3>Registrar nuevo abono</h3>
              <form [formGroup]="formPago" (ngSubmit)="registrarPago()" class="form-pago">
                <div class="grid-2">
                  <mat-form-field appearance="outline">
                    <mat-label>Monto del abono</mat-label>
                    <span matTextPrefix>$&nbsp;</span>
                    <input matInput type="number" formControlName="monto" min="0.01">
                    <mat-error *ngIf="formPago.get('monto')?.hasError('required')">El monto es requerido</mat-error>
                    <mat-error *ngIf="formPago.get('monto')?.hasError('excede')">El monto excede el saldo pendiente</mat-error>
                  </mat-form-field>

                  <mat-form-field appearance="outline">
                    <mat-label>Método de pago</mat-label>
                    <mat-select formControlName="metodo">
                      <mat-option value="transferencia">Transferencia bancaria</mat-option>
                      <mat-option value="deposito">Depósito bancario</mat-option>
                      <mat-option value="cheque">Cheque</mat-option>
                    </mat-select>
                  </mat-form-field>
                </div>

                <div class="comprobante-upload">
                  <label class="lbl">Comprobante de pago *</label>
                  <button mat-stroked-button type="button" (click)="simularComprobante()">
                    <mat-icon>upload</mat-icon>
                    {{ nombreComprobante() || 'Adjuntar comprobante' }}
                  </button>
                  <p class="text-muted mt-1" *ngIf="!nombreComprobante()">
                    <small>* Prototipo: la carga de archivo es simulada. En el sistema real se requiere comprobante obligatorio.</small>
                  </p>
                </div>

                <div class="action-bar">
                  <button mat-raised-button color="primary" type="submit"
                    [disabled]="formPago.invalid || !nombreComprobante()">
                    <mat-icon>send</mat-icon> Registrar pago
                  </button>
                </div>
              </form>

              <mat-divider class="my-3"></mat-divider>

              <h3>Historial de pagos</h3>
              <ng-container *ngIf="movimientos().length > 0; else sinMovs">
                <table mat-table [dataSource]="movimientos()" class="full-width">
                  <ng-container matColumnDef="fecha">
                    <th mat-header-cell *matHeaderCellDef>Fecha</th>
                    <td mat-cell *matCellDef="let mov">{{ mov.fechaRegistro | dateMx:'corto' }}</td>
                  </ng-container>
                  <ng-container matColumnDef="monto">
                    <th mat-header-cell *matHeaderCellDef>Monto</th>
                    <td mat-cell *matCellDef="let mov">{{ mov.monto | currencyMx }}</td>
                  </ng-container>
                  <ng-container matColumnDef="metodo">
                    <th mat-header-cell *matHeaderCellDef>Método</th>
                    <td mat-cell *matCellDef="let mov">{{ mov.metodo }}</td>
                  </ng-container>
                  <ng-container matColumnDef="origen">
                    <th mat-header-cell *matHeaderCellDef>Origen</th>
                    <td mat-cell *matCellDef="let mov">{{ mov.origen === 'usuario' ? 'Usuario' : 'Administrador' }}</td>
                  </ng-container>
                  <ng-container matColumnDef="estado">
                    <th mat-header-cell *matHeaderCellDef>Estado</th>
                    <td mat-cell *matCellDef="let mov"><app-status-badge [estado]="mov.estado"></app-status-badge></td>
                  </ng-container>
                  <ng-container matColumnDef="comprobante">
                    <th mat-header-cell *matHeaderCellDef>Comprobante</th>
                    <td mat-cell *matCellDef="let mov">
                      <button mat-button (click)="verComprobante(mov)" *ngIf="mov.comprobanteNombre">
                        <mat-icon>description</mat-icon> Ver
                      </button>
                    </td>
                  </ng-container>
                  <ng-container matColumnDef="motivo">
                    <th mat-header-cell *matHeaderCellDef></th>
                    <td mat-cell *matCellDef="let mov">
                      <span class="text-muted small" *ngIf="mov.motivoRechazo">
                        {{ mov.motivoRechazo }}
                      </span>
                    </td>
                  </ng-container>
                  <tr mat-header-row *matHeaderRowDef="columnasMov"></tr>
                  <tr mat-row *matRowDef="let row; columns: columnasMov;"></tr>
                </table>
              </ng-container>
              <ng-template #sinMovs>
                <app-empty-state
                  icono="receipt_long"
                  titulo="Aún no se han registrado pagos"
                  mensaje="Cuando registres un pago, aparecerá aquí.">
                </app-empty-state>
              </ng-template>
            </div>
          </mat-tab>
        </mat-tab-group>
      </ng-container>

      <ng-template #sinReserva>
        <mat-card>
          <mat-card-content class="text-center p-4">
            <mat-icon class="big-icon">event_busy</mat-icon>
            <h2>No tienes una reserva activa</h2>
            <p class="text-muted">Selecciona stands en el mapa del showfloor para iniciar tu reserva.</p>
            <a mat-raised-button color="primary" routerLink="/usuario/seleccion">
              <mat-icon>map</mat-icon> Ir a selección de stands
            </a>
          </mat-card-content>
        </mat-card>
      </ng-template>
    </div>
  `,
  styles: [`
    .mt-2 { margin-top: 16px; }
    .my-3 { margin: 16px 0; }
    .reserva-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }
    .reserva-id { font-size: 18px; font-weight: 600; color: var(--filey-primary); }
    .text-muted { color: var(--filey-text-muted); }
    .small { font-size: 12px; }
    .grid-layout {
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 24px;
      margin-top: 16px;
    }
    .progress-section { background: var(--filey-bg-soft); padding: 16px; border-radius: 8px; }
    .progress-label { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; color: var(--filey-text-muted); }
    .progress-marks { display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; }
    .mark { color: #9ca3af; }
    .mark.reached { color: var(--filey-success); font-weight: 600; }
    .fechas-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .fecha-item { display: flex; gap: 12px; align-items: flex-start; padding: 12px; background: var(--filey-bg-soft); border-radius: 4px; }
    .fecha-item mat-icon { color: var(--filey-primary); }
    .fecha-label { font-size: 12px; color: var(--filey-text-muted); text-transform: uppercase; }
    .fecha-value { font-weight: 600; color: var(--filey-primary); }
    .fecha-value.warn { color: var(--filey-secondary); }
    .stand-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-bottom: 1px solid var(--filey-border); }
    .stand-item:last-child { border-bottom: none; }
    .stand-item .clave { font-size: 20px; font-weight: 700; color: var(--filey-primary); min-width: 50px; }
    .stand-item .info { flex: 1; }
    .stand-item .precio { font-weight: 600; color: var(--filey-secondary); }
    .discount { color: var(--filey-success); }
    .big-icon { font-size: 64px; width: 64px; height: 64px; color: var(--filey-text-muted); }
    .text-center { text-align: center; }
    .p-4 { padding: 32px; }

    .pagos-content { padding-top: 16px; }
    .datos-bancarios {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 12px;
      background: var(--filey-bg-soft);
      padding: 16px;
      border-radius: 8px;
      margin-top: 8px;
    }
    .dato { display: flex; flex-direction: column; padding: 8px 0; }
    .dato .lbl { font-size: 12px; color: var(--filey-text-muted); text-transform: uppercase; }
    .dato .val { font-weight: 600; color: var(--filey-primary); font-size: 15px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .form-pago { max-width: 700px; }
    .comprobante-upload { margin: 16px 0; }
    .comprobante-upload .lbl { display: block; font-weight: 600; margin-bottom: 8px; color: var(--filey-primary); }

    @media (max-width: 1024px) {
      .grid-layout { grid-template-columns: 1fr; }
      .grid-2 { grid-template-columns: 1fr; }
      .fechas-grid { grid-template-columns: 1fr; }
    }
  `]
})
export class MiReservaComponent implements OnInit {
  private readonly reservaService = inject(ReservaService);
  private readonly movimientoService = inject(MovimientoService);
  private readonly parametrosService = inject(ParametrosService);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly snackBar = inject(MatSnackBar);
  private readonly fb = inject(FormBuilder);

  readonly reserva = signal<Reserva | null>(null);
  readonly movimientos = signal<Movimiento[]>([]);
  readonly nombreComprobante = signal<string | null>(null);

  readonly params = this.parametrosService.parametros;
  readonly datos = this.params.datosBancarios;
  readonly porcentajeAnticipo = 50;
  columnasMov = ['fecha', 'monto', 'metodo', 'origen', 'estado', 'comprobante', 'motivo'];

  formPago!: FormGroup;

  ngOnInit(): void {
    this.reservaService.reservas$.subscribe(() => {
      this.reserva.set(this.reservaService.getReservaActual() || null);
      this.cargarMovimientos();
    });
    this.movimientoService.movimientos$.subscribe(() => this.cargarMovimientos());
    this.reserva.set(this.reservaService.getReservaActual() || null);
    this.cargarMovimientos();

    this.formPago = this.fb.group({
      monto: [null, [Validators.required, Validators.min(0.01)]],
      metodo: ['transferencia', Validators.required]
    });

    const r = this.reserva();
    if (r) {
      this.formPago.get('monto')?.setValidators([
        Validators.required,
        Validators.min(0.01),
        (control) => control.value > r.montoPendiente ? { excede: true } : null
      ]);
      this.formPago.get('monto')?.updateValueAndValidity();
    }
  }

  cargarMovimientos(): void {
    const r = this.reserva();
    if (r) {
      this.movimientos.set(this.movimientoService.getByReserva(r.id));
    }
  }

  totalDescuentos(): number {
    return this.reserva()?.descuentos.reduce((s, d) => s + d.montoDescontado, 0) || 0;
  }

  porcentajePagado(): number {
    const r = this.reserva();
    if (!r || r.montoTotal === 0) return 0;
    return Math.min(100, Math.round((r.montoAbonado / r.montoTotal) * 100));
  }

  estaVencida(): boolean {
    const r = this.reserva();
    if (!r) return false;
    return r.estado === 'Por confirmar' &&
      r.fechaVencimientoAnticipo < new Date() &&
      r.montoAbonado < r.anticipoRequerido;
  }

  simularComprobante(): void {
    const nombre = `comprobante_${Date.now()}.pdf`;
    this.nombreComprobante.set(nombre);
    this.snackBar.open('Comprobante simulado adjunto', 'OK', { duration: 2000 });
  }

  registrarPago(): void {
    const r = this.reserva();
    if (!r || !this.formPago.valid || !this.nombreComprobante()) {
      this.snackBar.open('Complete todos los campos', 'OK', { duration: 3000 });
      return;
    }
    const { monto, metodo } = this.formPago.value;
    this.movimientoService.registrarPagoUsuario(r.id, monto, metodo, this.nombreComprobante()!);
    this.snackBar.open('Pago registrado. Está en revisión por el administrador.', 'OK', { duration: 4000 });
    this.formPago.reset({ metodo: 'transferencia' });
    this.nombreComprobante.set(null);
  }

  verComprobante(mov: Movimiento): void {
    this.snackBar.open(`Viendo ${mov.comprobanteNombre} (simulado)`, 'OK', { duration: 2000 });
  }
}
