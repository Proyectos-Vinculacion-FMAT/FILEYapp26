import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { MatDialog, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AplicacionService } from '../../../services/aplicacion.service';
import { EditorialService } from '../../../services/editorial.service';
import { StatusBadgeComponent } from '../../../shared/components/status-badge.component';
import { DateMxPipe } from '../../../shared/pipes/date-mx.pipe';
import { Aplicacion } from '../../../data/models';

@Component({
  selector: 'app-cambios-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatIconModule],
  template: `
    <h2 mat-dialog-title>Solicitar cambios</h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>Motivo de la solicitud de cambios *</mat-label>
        <textarea matInput [(ngModel)]="motivo" rows="4" required></textarea>
      </mat-form-field>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="primary" (click)="confirmar()" [disabled]="!motivo.trim()">
        <mat-icon>send</mat-icon> Solicitar cambios
      </button>
    </mat-dialog-actions>
  `,
  styles: [`.full-width { width: 100%; min-width: 400px; }`]
})
export class CambiosDialogComponent {
  motivo = '';
  private readonly ref = inject(MatDialogRef<CambiosDialogComponent>);
  cancelar(): void { this.ref.close(); }
  confirmar(): void { this.ref.close(this.motivo); }
}

@Component({
  selector: 'app-detalle-aplicacion',
  standalone: true,
  imports: [
    CommonModule, RouterModule, MatCardModule, MatButtonModule, MatIconModule, MatDividerModule,
    MatDialogModule, MatSnackBarModule, StatusBadgeComponent, DateMxPipe
  ],
  template: `
    <div class="page-container" *ngIf="aplicacion(); else noExiste">
      <a mat-button routerLink="/admin/aplicaciones" class="back-link">
        <mat-icon>arrow_back</mat-icon> Aplicaciones
      </a>

      <div class="header-row">
        <div>
          <h1 class="page-title">Aplicación {{ aplicacion()!.id }}</h1>
          <p class="page-subtitle">{{ nombreEditorial() }} · Enviada: {{ aplicacion()!.fechaEnvio | dateMx:'largo' }}</p>
        </div>
        <app-status-badge [estado]="aplicacion()!.estado"></app-status-badge>
      </div>

      <div *ngIf="aplicacion()!.estado === 'pendiente'" class="info-banner">
        <mat-icon>hourglass_empty</mat-icon>
        <div>Aplicación pendiente de revisión. Puede aceptar, rechazar o solicitar cambios.</div>
      </div>

      <div *ngIf="aplicacion()!.estado === 'cambios_solicitados'" class="warning-banner">
        <mat-icon>edit</mat-icon>
        <div>
          <strong>Cambios solicitados al usuario.</strong>
          <div *ngIf="aplicacion()!.motivoPeticion" class="mt-1">Motivo: {{ aplicacion()!.motivoPeticion }}</div>
        </div>
      </div>

      <div *ngIf="aplicacion()!.estado === 'rechazada'" class="danger-banner">
        <mat-icon>cancel</mat-icon>
        <div>
          <strong>Aplicación rechazada.</strong>
          <div *ngIf="aplicacion()!.motivoPeticion" class="mt-1">Motivo: {{ aplicacion()!.motivoPeticion }}</div>
        </div>
      </div>

      <div *ngIf="aplicacion()!.estado === 'aceptada'" class="success-banner">
        <mat-icon>check_circle</mat-icon>
        <div><strong>Aplicación aceptada.</strong> La editorial está habilitada para reservar stands.</div>
      </div>

      <div class="grid-2">
        <mat-card>
          <mat-card-header>
            <mat-card-title>Datos de la editorial</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div *ngIf="editorial()">
              <h3>{{ editorial()!.nombre }}</h3>
              <p class="text-muted">
                {{ editorial()!.domicilio.calle }} {{ editorial()!.domicilio.numero }},
                {{ editorial()!.domicilio.colonia }}, {{ editorial()!.domicilio.municipio }},
                {{ editorial()!.domicilio.estado }}
              </p>
              <p><strong>Giro:</strong> {{ editorial()!.giro }}</p>
              <p><strong>Responsable del stand:</strong> {{ editorial()!.responsableStand }}</p>
              <p><strong>Antepecho:</strong> {{ editorial()!.nombreAntepecho }}</p>

              <mat-divider class="my-3"></mat-divider>

              <h4>Contactos</h4>
              <div class="contactos">
                <div class="contacto">
                  <strong>Director general</strong>
                  <div>{{ editorial()!.contactos.directorGeneral.nombre }}</div>
                  <div class="text-muted small">{{ editorial()!.contactos.directorGeneral.email }}</div>
                </div>
                <div class="contacto">
                  <strong>Director comercial</strong>
                  <div>{{ editorial()!.contactos.directorComercial.nombre }}</div>
                  <div class="text-muted small">{{ editorial()!.contactos.directorComercial.email }}</div>
                </div>
                <div class="contacto">
                  <strong>Director editorial</strong>
                  <div>{{ editorial()!.contactos.directorEditorial.nombre }}</div>
                  <div class="text-muted small">{{ editorial()!.contactos.directorEditorial.email }}</div>
                </div>
                <div class="contacto">
                  <strong>Director promoción</strong>
                  <div>{{ editorial()!.contactos.directorPromocion.nombre }}</div>
                  <div class="text-muted small">{{ editorial()!.contactos.directorPromocion.email }}</div>
                </div>
              </div>

              <mat-divider class="my-3"></mat-divider>

              <h4>Materiales y temáticas</h4>
              <p><strong>Materiales:</strong> {{ editorial()!.materiales.join(', ') }}</p>
              <p><strong>Temáticas:</strong> {{ editorial()!.tematicas.join(', ') }}</p>

              <p class="mt-2">
                <strong>Personas que atenderán:</strong> {{ editorial()!.numPersonasAtienden }}<br>
                <strong>Total de sellos:</strong> {{ editorial()!.totalSellos }}<br>
                <strong>Libros aprox.:</strong> {{ editorial()!.cantidadLibrosAprox }}<br>
                <strong>Títulos aprox.:</strong> {{ editorial()!.cantidadTitulosAprox }}
              </p>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card>
          <mat-card-header>
            <mat-card-title>Sellos editoriales</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div *ngFor="let sello of aplicacion()!.sellos" class="sello-item">
              <mat-icon>book</mat-icon>
              <div class="flex-grow">
                <strong>{{ sello.nombre }}</strong>
                <div class="text-muted small" *ngIf="sello.cartaRepresentacionId">
                  <mat-icon class="inline-icon">check_circle</mat-icon> Carta de representación adjunta
                </div>
                <div class="text-muted small" *ngIf="!sello.cartaRepresentacionId">
                  <mat-icon class="inline-icon">remove</mat-icon> Sin carta de representación
                </div>
              </div>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="full-span">
          <mat-card-header>
            <mat-card-title>Documentos</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="docs">
              <div *ngFor="let doc of aplicacion()!.documentos" class="doc-item">
                <mat-icon>description</mat-icon>
                <div class="flex-grow">
                  <div class="doc-name">{{ doc.nombreArchivo }}</div>
                  <div class="doc-type text-muted small">{{ doc.tipo }}</div>
                </div>
                <button mat-button (click)="descargarDoc(doc)">
                  <mat-icon>download</mat-icon> Descargar
                </button>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <mat-card class="mt-3" *ngIf="aplicacion()!.estado === 'pendiente'">
        <mat-card-content>
          <h3>Acciones</h3>
          <div class="action-bar">
            <button mat-raised-button color="primary" (click)="aceptar()">
              <mat-icon>check</mat-icon> Aceptar
            </button>
            <button mat-raised-button color="warn" (click)="rechazar()">
              <mat-icon>close</mat-icon> Rechazar
            </button>
            <button mat-raised-button (click)="solicitarCambios()">
              <mat-icon>edit</mat-icon> Solicitar cambios
            </button>
          </div>
        </mat-card-content>
      </mat-card>
    </div>

    <ng-template #noExiste>
      <div class="page-container">
        <h1 class="page-title">Aplicación no encontrada</h1>
        <button mat-button routerLink="/admin/aplicaciones">
          <mat-icon>arrow_back</mat-icon> Volver al listado
        </button>
      </div>
    </ng-template>
  `,
  styles: [`
    .back-link { margin-bottom: 16px; }
    .header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .grid-2 {
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 24px;
    }
    .full-span { grid-column: 1 / -1; }
    .contactos { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .contacto { background: var(--filey-bg-soft); padding: 12px; border-radius: 4px; }
    .small { font-size: 12px; }
    .inline-icon { font-size: 14px; width: 14px; height: 14px; vertical-align: middle; }
    .sello-item {
      display: flex; align-items: center; gap: 12px; padding: 10px;
      background: var(--filey-bg-soft); border-radius: 4px; margin-bottom: 8px;
    }
    .docs { display: flex; flex-direction: column; gap: 8px; }
    .doc-item {
      display: flex; align-items: center; gap: 12px; padding: 12px;
      border: 1px solid var(--filey-border); border-radius: 4px;
    }
    .doc-name { font-weight: 500; }
    .doc-type { text-transform: uppercase; }
    .my-3 { margin: 16px 0; }
    .mt-2 { margin-top: 16px; }
    .mt-3 { margin-top: 24px; }
  `]
})
export class DetalleAplicacionComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly aplicacionService = inject(AplicacionService);
  private readonly editorialService = inject(EditorialService);
  private readonly dialog = inject(MatDialog);
  private readonly snackBar = inject(MatSnackBar);

  readonly aplicacion = signal<Aplicacion | null>(null);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) this.aplicacion.set(this.aplicacionService.getById(id) || null);
  }

  nombreEditorial(): string {
    return this.editorialService.getById(this.aplicacion()?.editorialId || '')?.nombre || 'Desconocida';
  }

  editorial() {
    return this.editorialService.getById(this.aplicacion()?.editorialId || '');
  }

  aceptar(): void {
    const app = this.aplicacion();
    if (app) {
      this.aplicacionService.aceptar(app.id);
      this.aplicacion.set(this.aplicacionService.getById(app.id) || null);
      this.snackBar.open('Aplicación aceptada. Se ha notificado al usuario (simulado).', 'OK', { duration: 3000 });
    }
  }

  rechazar(): void {
    const app = this.aplicacion();
    if (app) {
      this.aplicacionService.rechazar(app.id);
      this.aplicacion.set(this.aplicacionService.getById(app.id) || null);
      this.snackBar.open('Aplicación rechazada. Se ha notificado al usuario (simulado).', 'OK', { duration: 3000 });
    }
  }

  solicitarCambios(): void {
    const ref = this.dialog.open(CambiosDialogComponent);
    ref.afterClosed().subscribe(motivo => {
      if (motivo) {
        const app = this.aplicacion();
        if (app) {
          this.aplicacionService.solicitarCambios(app.id, motivo);
          this.aplicacion.set(this.aplicacionService.getById(app.id) || null);
          this.snackBar.open('Cambios solicitados. Se ha notificado al usuario (simulado).', 'OK', { duration: 3000 });
        }
      }
    });
  }

  descargarDoc(doc: any): void {
    this.snackBar.open(`Descargando ${doc.nombreArchivo} (simulado)`, 'OK', { duration: 2000 });
  }
}
