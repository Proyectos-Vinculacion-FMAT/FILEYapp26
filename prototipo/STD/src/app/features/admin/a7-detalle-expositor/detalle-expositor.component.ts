import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { EditorialService } from '../../../services/editorial.service';
import { ReservaService } from '../../../services/reserva.service';
import { AplicacionService } from '../../../services/aplicacion.service';
import { StatusBadgeComponent } from '../../../shared/components/status-badge.component';
import { CurrencyMxPipe } from '../../../shared/pipes/currency-mx.pipe';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';
import { Aplicacion, Editorial, Reserva } from '../../../data/models';

@Component({
  selector: 'app-detalle-expositor',
  standalone: true,
  imports: [
    CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule, MatDividerModule,
    StatusBadgeComponent, CurrencyMxPipe, DateMxPipe
  ],
  template: `
    <div class="page-container" *ngIf="editorial(); else noExiste">
      <a mat-button routerLink="/admin/expositores" class="back-link">
        <mat-icon>arrow_back</mat-icon> Expositores
      </a>

      <div class="header-row">
        <div>
          <h1 class="page-title">{{ editorial()!.nombre }}</h1>
          <p class="page-subtitle">{{ editorial()!.giro }} · {{ editorial()!.nombreAntepecho }}</p>
        </div>
        <app-status-badge *ngIf="aplicacion()" [estado]="aplicacion()!.estado"></app-status-badge>
      </div>

      <div class="grid-layout">
        <mat-card>
          <mat-card-header>
            <mat-card-title>Datos fiscales</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <p><strong>Nombre:</strong> {{ editorial()!.nombre }}</p>
            <p><strong>Giro:</strong> {{ editorial()!.giro }}</p>
            <p *ngIf="aplicacion() && aplicacion()!.documentos.length > 0">
              <strong>Constancia de Situación Fiscal:</strong>
              <button mat-button (click)="descargarCSF()">
                <mat-icon>download</mat-icon> Descargar
              </button>
            </p>
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header>
            <mat-card-title>Contacto</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <p><strong>Responsable del stand:</strong> {{ editorial()!.responsableStand }}</p>
            <p><strong>Email:</strong> {{ editorial()!.correoElectronico }}</p>
            <p><strong>Teléfonos:</strong> {{ editorial()!.telefonoOficina }} / {{ editorial()!.telefonoCelular }}</p>
            <mat-divider class="my-3"></mat-divider>
            <h4>Directores</h4>
            <div class="directores">
              <div class="director">
                <strong>General</strong>
                <div>{{ editorial()!.contactos.directorGeneral.nombre }}</div>
                <div class="text-muted small">{{ editorial()!.contactos.directorGeneral.email }}</div>
              </div>
              <div class="director">
                <strong>Comercial</strong>
                <div>{{ editorial()!.contactos.directorComercial.nombre }}</div>
                <div class="text-muted small">{{ editorial()!.contactos.directorComercial.email }}</div>
              </div>
              <div class="director">
                <strong>Editorial</strong>
                <div>{{ editorial()!.contactos.directorEditorial.nombre }}</div>
                <div class="text-muted small">{{ editorial()!.contactos.directorEditorial.email }}</div>
              </div>
              <div class="director">
                <strong>Promoción</strong>
                <div>{{ editorial()!.contactos.directorPromocion.nombre }}</div>
                <div class="text-muted small">{{ editorial()!.contactos.directorPromocion.email }}</div>
              </div>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header>
            <mat-card-title>Domicilio</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <p>
              {{ editorial()!.domicilio.calle }} {{ editorial()!.domicilio.numero }}<br>
              {{ editorial()!.domicilio.colonia }}<br>
              CP {{ editorial()!.domicilio.cp }}, {{ editorial()!.domicilio.municipio }}<br>
              {{ editorial()!.domicilio.estado }}, {{ editorial()!.domicilio.pais }}
            </p>
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header>
            <mat-card-title>Datos editoriales</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <p><strong>Total de sellos:</strong> {{ editorial()!.totalSellos }}</p>
            <p><strong>Cantidad de libros (aprox.):</strong> {{ editorial()!.cantidadLibrosAprox }}</p>
            <p><strong>Cantidad de títulos (aprox.):</strong> {{ editorial()!.cantidadTitulosAprox }}</p>
            <p><strong>Personas que atienden:</strong> {{ editorial()!.numPersonasAtienden }}</p>
            <p><strong>Materiales:</strong> {{ editorial()!.materiales.join(', ') }}</p>
            <p><strong>Temáticas:</strong> {{ editorial()!.tematicas.join(', ') }}</p>
          </mat-card-content>
        </mat-card>

        <mat-card *ngIf="aplicacion() && aplicacion()!.sellos.length > 0">
          <mat-card-header>
            <mat-card-title>Sellos editoriales</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div *ngFor="let sello of aplicacion()!.sellos" class="sello">
              <mat-icon>book</mat-icon>
              <strong>{{ sello.nombre }}</strong>
              <span class="badge-carta" *ngIf="sello.cartaRepresentacionId">Carta adjunta</span>
              <span class="badge-sin-carta" *ngIf="!sello.cartaRepresentacionId">Sin carta</span>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card *ngIf="reserva()">
          <mat-card-header>
            <mat-card-title>Reserva activa</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="reserva-info">
              <div>
                <strong>{{ reserva()!.id }}</strong>
                <app-status-badge [estado]="reserva()!.estado"></app-status-badge>
              </div>
              <div class="text-muted small">Creada: {{ reserva()!.fechaCreacion | dateMx:'largo' }}</div>
              <div class="reserva-stats">
                <div>
                  <span class="lbl">Stands</span>
                  <span class="val">{{ reserva()!.stands.length }}</span>
                </div>
                <div>
                  <span class="lbl">Total</span>
                  <span class="val">{{ reserva()!.montoTotal | currencyMx }}</span>
                </div>
                <div>
                  <span class="lbl">Abonado</span>
                  <span class="val">{{ reserva()!.montoAbonado | currencyMx }}</span>
                </div>
                <div>
                  <span class="lbl">Pendiente</span>
                  <span class="val warn">{{ reserva()!.montoPendiente | currencyMx }}</span>
                </div>
              </div>
            </div>
            <a mat-raised-button color="primary" [routerLink]="['/admin/reservas', reserva()!.id]" class="mt-2">
              Ver detalle de reserva <mat-icon>arrow_forward</mat-icon>
            </a>
          </mat-card-content>
        </mat-card>
      </div>
    </div>

    <ng-template #noExiste>
      <div class="page-container">
        <h1 class="page-title">Expositor no encontrado</h1>
        <button mat-button routerLink="/admin/expositores">
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
    .directores { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px; }
    .director { background: var(--filey-bg-soft); padding: 12px; border-radius: 4px; }
    .small { font-size: 12px; }
    .sello {
      display: flex; align-items: center; gap: 8px; padding: 8px 0;
      border-bottom: 1px solid var(--filey-border);
    }
    .sello:last-child { border-bottom: none; }
    .badge-carta { background: #d4edda; color: #155724; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; }
    .badge-sin-carta { background: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 8px; }
    .reserva-info { display: flex; flex-direction: column; gap: 8px; }
    .reserva-info > div:first-child { display: flex; align-items: center; gap: 12px; }
    .reserva-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px; }
    .reserva-stats > div { background: var(--filey-bg-soft); padding: 8px 12px; border-radius: 4px; }
    .lbl { display: block; font-size: 11px; color: var(--filey-text-muted); text-transform: uppercase; }
    .val { font-weight: 600; color: var(--filey-primary); }
    .val.warn { color: var(--filey-secondary); }
    .my-3 { margin: 16px 0; }
    .mt-2 { margin-top: 16px; }
  `]
})
export class DetalleExpositorComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly editorialService = inject(EditorialService);
  private readonly reservaService = inject(ReservaService);
  private readonly aplicacionService = inject(AplicacionService);

  readonly editorial = signal<Editorial | null>(null);
  readonly reserva = signal<Reserva | null>(null);
  readonly aplicacion = signal<Aplicacion | null>(null);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.editorial.set(this.editorialService.getById(id) || null);
      this.reserva.set(this.reservaService.getByEditorial(id) || null);
      this.aplicacion.set(this.aplicacionService.getByEditorial(id) || null);
    }
  }

  descargarCSF(): void {
    // simulado
  }
}
