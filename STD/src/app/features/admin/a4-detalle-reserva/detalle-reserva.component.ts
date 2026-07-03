import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDialog, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ReservaService } from '../../../services/reserva.service';
import { MovimientoService } from '../../../services/movimiento.service';
import { EditorialService } from '../../../services/editorial.service';
import { StatusBadgeComponent } from '../../../shared/components/status-badge.component';
import { CurrencyMxPipe } from '../../../shared/pipes/currency-mx.pipe';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';
import { MetodoPago, Movimiento, Reserva } from '../../../data/models';

// Diálogo: Resolver reserva vencida
@Component({
  selector: 'app-resolver-vencida-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, MatDialogModule, MatButtonModule, MatFormFieldModule,
    MatInputModule, MatDatepickerModule, MatNativeDateModule, MatIconModule],
  template: `
    <h2 mat-dialog-title>Resolver reserva vencida</h2>
    <mat-dialog-content>
      <p>Seleccione la acción a tomar para esta reserva vencida:</p>
      <div class="opciones">
        <button mat-stroked-button [class.selected]="opcion() === 'prorrogar'" (click)="opcion.set('prorrogar')">
          <mat-icon>schedule</mat-icon> Prorrogar plazo
        </button>
        <button mat-stroked-button color="warn" [class.selected]="opcion() === 'cancelar'" (click)="opcion.set('cancelar')">
          <mat-icon>cancel</mat-icon> Cancelar reserva
        </button>
      </div>

      <div *ngIf="opcion() === 'prorrogar'" class="mt-3">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Nueva fecha de vencimiento del anticipo</mat-label>
          <input matInput [matDatepicker]="picker" [(ngModel)]="nuevaFecha">
          <mat-datepicker-toggle matIconSuffix [for]="picker"></mat-datepicker-toggle>
          <mat-datepicker #picker></mat-datepicker>
        </mat-form-field>
      </div>

      <div *ngIf="opcion() === 'cancelar'" class="mt-3">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Motivo (opcional)</mat-label>
          <textarea matInput [(ngModel)]="motivo" rows="3"></textarea>
        </mat-form-field>
        <p class="warning-banner">Esta acción es irreversible. Los stands serán liberados al mercado.</p>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary"
        (click)="confirmar()"
        [disabled]="opcion() === 'prorrogar' && !nuevaFecha">
        <mat-icon>check</mat-icon>
        {{ opcion() === 'prorrogar' ? 'Prorrogar' : 'Cancelar reserva' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .opciones { display: flex; gap: 12px; margin-top: 12px; }
    .opciones .selected { background: var(--filey-primary); color: #fff; border-color: var(--filey-primary); }
    .full-width { width: 100%; min-width: 400px; }
    .mt-3 { margin-top: 16px; }
  `]
})
export class ResolverVencidaDialogComponent {
  readonly opcion = signal<'prorrogar' | 'cancelar'>('prorrogar');
  nuevaFecha: Date | null = null;
  motivo = '';
  private readonly ref = inject(MatDialogRef<ResolverVencidaDialogComponent>);
  cancelar(): void { this.ref.close(); }
  confirmar(): void {
    this.ref.close({
      opcion: this.opcion(),
      nuevaFecha: this.nuevaFecha,
      motivo: this.motivo
    });
  }
}

// Diálogo: Registrar abono manual
@Component({
  selector: 'app-abono-manual-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MatDialogModule, MatButtonModule,
    MatFormFieldModule, MatInputModule, MatSelectModule, MatIconModule],
  template: `
    <h2 mat-dialog-title>Registrar abono manual</h2>
    <mat-dialog-content>
      <p class="text-muted">Como administrador, este abono se registrará directamente como validado.</p>
      <form [formGroup]="form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Monto</mat-label>
          <span matTextPrefix>$&nbsp;</span>
          <input matInput type="number" formControlName="monto" min="0.01">
        </mat-form-field>
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Método</mat-label>
          <mat-select formControlName="metodo">
            <mat-option value="transferencia">Transferencia</mat-option>
            <mat-option value="deposito">Depósito</mat-option>
            <mat-option value="cheque">Cheque</mat-option>
          </mat-select>
        </mat-form-field>
        <div class="full-width">
          <label class="lbl">Documento de respaldo *</label>
          <button mat-stroked-button type="button" (click)="adjuntarDoc()">
            <mat-icon>upload</mat-icon>
            {{ docNombre || 'Adjuntar documento (obligatorio)' }}
          </button>
          <p class="text-muted small mt-1" *ngIf="!docNombre">
            <small>* Todo abono manual requiere un documento adjunto.</small>
          </p>
        </div>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="confirmar()"
        [disabled]="form.invalid || !docNombre">
        <mat-icon>save</mat-icon> Registrar
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width { width: 100%; min-width: 400px; display: block; }
    .lbl { display: block; font-weight: 600; margin: 16px 0 8px; color: var(--filey-primary); }
    .small { font-size: 12px; }
    .mt-1 { margin-top: 8px; }
  `]
})
export class AbonoManualDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly ref = inject(MatDialogRef<AbonoManualDialogComponent>);
  form = this.fb.group({
    monto: [null, [Validators.required, Validators.min(0.01)]],
    metodo: ['transferencia', Validators.required]
  });
  docNombre: string | null = null;
  cancelar(): void { this.ref.close(); }
  adjuntarDoc(): void { this.docNombre = `doc_abono_${Date.now()}.pdf`; }
  confirmar(): void {
    if (this.form.valid && this.docNombre) {
      this.ref.close({ ...this.form.value, docNombre: this.docNombre });
    }
  }
}

// Diálogo: Aplicar descuento especial
@Component({
  selector: 'app-descuento-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MatDialogModule, MatButtonModule,
    MatFormFieldModule, MatInputModule, MatIconModule],
  template: `
    <h2 mat-dialog-title>Aplicar descuento especial</h2>
    <mat-dialog-content>
      <p class="text-muted">Este descuento es independiente del pronto pago y se aplica directamente al total.</p>
      <form [formGroup]="form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Porcentaje de descuento</mat-label>
          <input matInput type="number" formControlName="porcentaje" min="0.01" max="100">
          <span matTextSuffix>%</span>
        </mat-form-field>
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Motivo *</mat-label>
          <textarea matInput formControlName="motivo" rows="3" required></textarea>
        </mat-form-field>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="confirmar()" [disabled]="form.invalid">
        <mat-icon>local_offer</mat-icon> Aplicar
      </button>
    </mat-dialog-actions>
  `,
  styles: [`.full-width { width: 100%; min-width: 400px; display: block; }`]
})
export class DescuentoDialogComponent {
  private readonly fb = inject(FormBuilder);
  private readonly ref = inject(MatDialogRef<DescuentoDialogComponent>);
  form = this.fb.group({
    porcentaje: [null, [Validators.required, Validators.min(0.01), Validators.max(100)]],
    motivo: ['', Validators.required]
  });
  cancelar(): void { this.ref.close(); }
  confirmar(): void {
    if (this.form.valid) this.ref.close(this.form.value);
  }
}

// Diálogo: Validar/Rechazar movimiento
@Component({
  selector: 'app-validar-movimiento-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, MatDialogModule, MatButtonModule, MatFormFieldModule,
    MatInputModule, MatIconModule, CurrencyMxPipe, DateMxPipe],
  template: `
    <h2 mat-dialog-title>Detalle del movimiento</h2>
    <mat-dialog-content>
      <div *ngIf="movimiento">
        <p><strong>Monto:</strong> {{ movimiento.monto | currencyMx }}</p>
        <p><strong>Método:</strong> {{ movimiento.metodo }}</p>
        <p><strong>Fecha de registro:</strong> {{ movimiento.fechaRegistro | dateMx:'largo' }}</p>
        <p><strong>Origen:</strong> {{ movimiento.origen === 'usuario' ? 'Usuario' : 'Administrador' }}</p>
        <p *ngIf="movimiento.comprobanteNombre">
          <strong>Comprobante:</strong>
          <button mat-button (click)="verComprobante()">
            <mat-icon>description</mat-icon> {{ movimiento.comprobanteNombre }}
          </button>
        </p>

        <div *ngIf="modoRechazo()" class="mt-3">
          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Motivo de rechazo *</mat-label>
            <textarea matInput [(ngModel)]="motivoRechazo" rows="3" required></textarea>
          </mat-form-field>
        </div>
      </div>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cerrar</button>
      <ng-container *ngIf="!modoRechazo()">
        <button mat-raised-button color="warn" (click)="mostrarRechazo()">
          <mat-icon>close</mat-icon> Rechazar
        </button>
        <button mat-raised-button color="primary" (click)="validar()">
          <mat-icon>check</mat-icon> Validar abono
        </button>
      </ng-container>
      <ng-container *ngIf="modoRechazo()">
        <button mat-button (click)="cancelarRechazo()">Volver</button>
        <button mat-raised-button color="warn" (click)="rechazar()" [disabled]="!motivoRechazo.trim()">
          Confirmar rechazo
        </button>
      </ng-container>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width { width: 100%; min-width: 400px; }
    .mt-3 { margin-top: 16px; }
  `]
})
export class ValidarMovimientoDialogComponent {
  movimiento!: Movimiento;
  modoRechazo = signal(false);
  motivoRechazo = '';
  private readonly ref = inject(MatDialogRef<ValidarMovimientoDialogComponent>);
  private readonly snackBar = inject(MatSnackBar);

  cancelar(): void { this.ref.close(); }
  mostrarRechazo(): void { this.modoRechazo.set(true); }
  cancelarRechazo(): void { this.modoRechazo.set(false); }
  verComprobante(): void { this.snackBar.open('Viendo comprobante (simulado)', 'OK', { duration: 2000 }); }
  validar(): void { this.ref.close({ accion: 'validar' }); }
  rechazar(): void { this.ref.close({ accion: 'rechazar', motivo: this.motivoRechazo }); }
}

// Componente principal
@Component({
  selector: 'app-detalle-reserva',
  standalone: true,
  imports: [
    CommonModule, RouterModule, FormsModule, ReactiveFormsModule, MatCardModule, MatTableModule,
    MatButtonModule, MatIconModule, MatTabsModule, MatDividerModule, MatExpansionModule,
    MatDialogModule, MatSnackBarModule, MatTooltipModule, MatFormFieldModule, MatInputModule,
    MatDatepickerModule, MatNativeDateModule,
    StatusBadgeComponent, CurrencyMxPipe, DateMxPipe
  ],
  template: `
    <div class="page-container" *ngIf="reserva(); else noExiste">
      <a mat-button routerLink="/admin/reservas" class="back-link">
        <mat-icon>arrow_back</mat-icon> Reservas
      </a>

      <div class="header-row">
        <div>
          <h1 class="page-title">Reserva {{ reserva()!.id }}</h1>
          <p class="page-subtitle">{{ nombreEditorial() }} · Creada: {{ reserva()!.fechaCreacion | dateMx:'largo' }}</p>
        </div>
        <app-status-badge [estado]="reserva()!.estado"></app-status-badge>
      </div>

      <div *ngIf="esVencida()" class="warning-banner">
        <mat-icon>warning</mat-icon>
        <div>
          <strong>Reserva vencida.</strong> No se ha cubierto el anticipo del 50% en el plazo de 30 días.
          Resuelva la situación prorrogando o cancelando.
          <button mat-raised-button color="primary" (click)="resolverVencida()" class="ml-2">
            <mat-icon>build</mat-icon> Resolver reserva vencida
          </button>
        </div>
      </div>

      <div class="grid-layout">
        <mat-card>
          <mat-card-header>
            <mat-card-title>Información general</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div *ngIf="editorial()">
              <h3>{{ editorial()!.nombre }}</h3>
              <p class="text-muted">{{ editorial()!.giro }} · {{ editorial()!.responsableStand }}</p>
              <p>
                <mat-icon class="icon-sm">phone</mat-icon> {{ editorial()!.telefonoOficina }} ·
                <mat-icon class="icon-sm">email</mat-icon> {{ editorial()!.correoElectronico }}
              </p>
            </div>

            <mat-divider class="my-3"></mat-divider>

            <h4>Fechas</h4>
            <div class="fechas">
              <div>
                <span class="lbl">Creación</span>
                <span>{{ reserva()!.fechaCreacion | dateMx:'largo' }}</span>
              </div>
              <div>
                <span class="lbl">Vencimiento del anticipo</span>
                <span [class.warn-text]="esVencida()">{{ reserva()!.fechaVencimientoAnticipo | dateMx:'largo' }}</span>
              </div>
              <div *ngIf="reserva()!.fechaCortePagoTotal">
                <span class="lbl">Fecha de corte (pago total)</span>
                <span>{{ reserva()!.fechaCortePagoTotal | dateMx:'largo' }}</span>
              </div>
            </div>
          </mat-card-content>
        </mat-card>

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
              <span class="summary-label">Anticipo requerido (50%)</span>
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
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header>
            <mat-card-title>Stands reservados</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <table>
              <thead>
                <tr>
                  <th>Stand</th>
                  <th>Zona</th>
                  <th>Superficie</th>
                  <th class="num">Precio</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let s of reserva()!.stands">
                  <td><strong>{{ s.clave }}</strong></td>
                  <td>{{ s.zona }}</td>
                  <td>{{ s.metrosCuadradosSnapshot }} m²</td>
                  <td class="num">{{ s.precioSnapshot | currencyMx }}</td>
                </tr>
              </tbody>
            </table>
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header>
            <mat-card-title>Historial de movimientos</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <table *ngIf="movimientos().length > 0; else sinMovs" class="full-width">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Monto</th>
                  <th>Método</th>
                  <th>Origen</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let m of movimientos()">
                  <td>{{ m.fechaRegistro | dateMx }}</td>
                  <td>{{ m.monto | currencyMx }}</td>
                  <td>{{ m.metodo }}</td>
                  <td>{{ m.origen === 'usuario' ? 'Usuario' : 'Admin' }}</td>
                  <td><app-status-badge [estado]="m.estado"></app-status-badge></td>
                  <td>
                    <button mat-button *ngIf="m.estado === 'pendiente_validacion'" (click)="validarMovimiento(m)">
                      <mat-icon>fact_check</mat-icon> Revisar
                    </button>
                    <span *ngIf="m.motivoRechazo" class="text-muted small" [matTooltip]="m.motivoRechazo">
                      <mat-icon class="icon-sm">info</mat-icon>
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <ng-template #sinMovs>
              <p class="text-muted">No hay movimientos registrados.</p>
            </ng-template>
          </mat-card-content>
        </mat-card>
      </div>

      <mat-card class="mt-3">
        <mat-card-header>
          <mat-card-title>Acciones de administración</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="action-bar">
            <button mat-raised-button color="primary" (click)="abonoManual()">
              <mat-icon>add</mat-icon> Registrar abono manual
            </button>
            <button mat-raised-button (click)="aplicarDescuento()">
              <mat-icon>local_offer</mat-icon> Aplicar descuento especial
            </button>
            <button mat-raised-button (click)="modificarFechaCorte()">
              <mat-icon>event</mat-icon> Modificar fecha de corte
            </button>
            <button mat-raised-button color="warn" (click)="resolverVencida()" *ngIf="esVencida()">
              <mat-icon>build</mat-icon> Resolver reserva vencida
            </button>
          </div>
        </mat-card-content>
      </mat-card>
    </div>

    <ng-template #noExiste>
      <div class="page-container">
        <h1 class="page-title">Reserva no encontrada</h1>
        <button mat-button routerLink="/admin/reservas">
          <mat-icon>arrow_back</mat-icon> Volver al listado
        </button>
      </div>
    </ng-template>
  `,
  styles: [`
    .back-link { margin-bottom: 16px; }
    .header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .grid-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }
    .icon-sm { font-size: 16px; width: 16px; height: 16px; vertical-align: middle; }
    .fechas { display: flex; flex-direction: column; gap: 8px; }
    .fechas > div { display: flex; flex-direction: column; padding: 8px 0; }
    .lbl { font-size: 12px; color: var(--filey-text-muted); text-transform: uppercase; }
    .warn-text { color: var(--filey-secondary); font-weight: 600; }
    .my-3 { margin: 16px 0; }
    .mt-3 { margin-top: 24px; }
    .ml-2 { margin-left: 16px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid var(--filey-border); }
    th { color: var(--filey-primary); font-weight: 600; font-size: 13px; text-transform: uppercase; }
    .num { text-align: right; }
    .small { font-size: 12px; }
  `]
})
export class DetalleReservaComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly reservaService = inject(ReservaService);
  private readonly movimientoService = inject(MovimientoService);
  private readonly editorialService = inject(EditorialService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  readonly reserva = signal<Reserva | null>(null);
  readonly movimientos = signal<Movimiento[]>([]);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.reserva.set(this.reservaService.getById(id) || null);
      this.cargarMovimientos();
    }
    this.reservaService.reservas$.subscribe(() => {
      const r = this.reserva();
      if (r) this.reserva.set(this.reservaService.getById(r.id) || null);
    });
    this.movimientoService.movimientos$.subscribe(() => this.cargarMovimientos());
  }

  cargarMovimientos(): void {
    const r = this.reserva();
    if (r) this.movimientos.set(this.movimientoService.getByReserva(r.id));
  }

  nombreEditorial(): string {
    return this.editorialService.getById(this.reserva()?.editorialId || '')?.nombre || 'Desconocida';
  }

  editorial() {
    return this.editorialService.getById(this.reserva()?.editorialId || '');
  }

  esVencida(): boolean {
    const r = this.reserva();
    if (!r) return false;
    return r.estado === 'Por confirmar' && r.fechaVencimientoAnticipo < new Date() && r.montoAbonado < r.anticipoRequerido;
  }

  validarMovimiento(m: Movimiento): void {
    const ref = this.dialog.open(ValidarMovimientoDialogComponent, { data: m });
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

  abonoManual(): void {
    const r = this.reserva();
    if (!r) return;
    const ref = this.dialog.open(AbonoManualDialogComponent);
    ref.afterClosed().subscribe(data => {
      if (data) {
        this.movimientoService.registrarAbonoManual(r.id, data.monto, data.metodo, data.docNombre);
        this.snackBar.open('Abono manual registrado. Saldo actualizado.', 'OK', { duration: 3000 });
      }
    });
  }

  aplicarDescuento(): void {
    const r = this.reserva();
    if (!r) return;
    if (r.descuentos.some(d => d.tipo === 'especial')) {
      this.snackBar.open('Ya se aplicó un descuento especial a esta reserva.', 'OK', { duration: 3000 });
      return;
    }
    const ref = this.dialog.open(DescuentoDialogComponent);
    ref.afterClosed().subscribe(data => {
      if (data) {
        this.reservaService.aplicarDescuentoEspecial(r.id, data.porcentaje, data.motivo, 'Administrador');
        this.snackBar.open(`Descuento del ${data.porcentaje}% aplicado.`, 'OK', { duration: 3000 });
      }
    });
  }

  modificarFechaCorte(): void {
    const r = this.reserva();
    if (!r) return;
    const nuevaFecha = prompt('Ingrese la nueva fecha de corte (YYYY-MM-DD):',
      r.fechaCortePagoTotal?.toISOString().split('T')[0] || '');
    if (nuevaFecha) {
      const fecha = new Date(nuevaFecha);
      if (!isNaN(fecha.getTime())) {
        this.reservaService.modificarFechaCorte(r.id, fecha);
        this.snackBar.open('Fecha de corte actualizada.', 'OK', { duration: 3000 });
      }
    }
  }

  resolverVencida(): void {
    const r = this.reserva();
    if (!r) return;
    const ref = this.dialog.open(ResolverVencidaDialogComponent);
    ref.afterClosed().subscribe(result => {
      if (!result) return;
      if (result.opcion === 'prorrogar' && result.nuevaFecha) {
        this.reservaService.prorrogar(r.id, result.nuevaFecha);
        this.snackBar.open('Reserva prorrogada. El contador de vencimiento se ha actualizado.', 'OK', { duration: 3000 });
      } else if (result.opcion === 'cancelar') {
        this.reservaService.cancelar(r.id);
        this.snackBar.open('Reserva cancelada. Los stands han sido liberados.', 'OK', { duration: 3000 });
        setTimeout(() => this.router.navigate(['/admin/reservas']), 1500);
      }
    });
  }

  private readonly router = inject(Router);
}
