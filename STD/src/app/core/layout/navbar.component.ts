import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDialog, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { EditorialService } from '../../services/editorial.service';
import { ResetService } from '../../services/reset.service';
import { AplicacionService } from '../../services/aplicacion.service';
import { FaseService } from '../../services/fase.service';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Editorial } from '../../data/models';

@Component({
  selector: 'app-reset-confirm-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatIconModule],
  template: `
    <h2 mat-dialog-title>
      <mat-icon class="warn-icon">restart_alt</mat-icon>
      ¿Reiniciar el demo?
    </h2>
    <mat-dialog-content>
      <p>Esto restablecerá todo el estado del prototipo a sus valores iniciales:</p>
      <ul>
        <li>Aplicaciones, reservas, pagos y movimientos vuelven a los datos mock</li>
        <li>El carrito de selección se vacía</li>
        <li>El rol vuelve a "Usuario" (Editorial Sureste Nueva)</li>
      </ul>
      <p class="text-muted">Esta acción es útil entre demos para empezar desde cero.</p>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="cancelar()">Cancelar</button>
      <button mat-raised-button color="warn" (click)="confirmar()">
        <mat-icon>refresh</mat-icon> Sí, reiniciar
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .warn-icon { color: var(--filey-secondary); vertical-align: middle; margin-right: 8px; }
    ul { padding-left: 20px; color: var(--filey-text-muted); }
    li { margin-bottom: 4px; }
    .text-muted { color: var(--filey-text-muted); }
  `]
})
export class ResetConfirmDialogComponent {
  private readonly ref = inject(MatDialogRef<ResetConfirmDialogComponent>);
  cancelar() { this.ref.close(false); }
  confirmar() { this.ref.close(true); }
}

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule, RouterModule, FormsModule, MatToolbarModule, MatButtonModule, MatIconModule,
    MatMenuModule, MatBadgeModule, MatTooltipModule, MatSelectModule, MatFormFieldModule
  ],
  template: `
    <mat-toolbar color="primary" class="navbar">
      <span class="logo" (click)="irAInicio()">
        <mat-icon>menu_book</mat-icon>
        <span class="logo-text">FILEY</span>
      </span>

      <span class="spacer"></span>

      <ng-container *ngIf="rolActual === 'usuario'">
        <div class="editorial-selector">
          <mat-icon class="editorial-icon">account_circle</mat-icon>
          <mat-form-field appearance="outline" class="editorial-field" subscriptSizing="dynamic">
            <mat-select [value]="editorialActualId()" (selectionChange)="cambiarEditorial($event.value)">
              <mat-option *ngFor="let ed of todasEditoriales" [value]="ed.id">
                {{ ed.nombre }}
              </mat-option>
            </mat-select>
          </mat-form-field>
        </div>
      </ng-container>

      <button mat-button
        (click)="reiniciarDemo()"
        class="reset-btn"
        matTooltip="Reiniciar el estado del prototipo a los valores iniciales">
        <mat-icon>restart_alt</mat-icon>
        <span class="reset-label">Reiniciar</span>
      </button>

      <button mat-button [matMenuTriggerFor]="menuRol" class="role-btn">
        <mat-icon>{{ rolActual === 'usuario' ? 'person' : 'admin_panel_settings' }}</mat-icon>
        <span class="role-label">{{ rolActual === 'usuario' ? 'Usuario' : 'Administrador' }}</span>
        <mat-icon>arrow_drop_down</mat-icon>
      </button>
      <mat-menu #menuRol="matMenu">
        <button mat-menu-item (click)="cambiarRol('usuario')" [disabled]="rolActual === 'usuario'">
          <mat-icon>person</mat-icon>
          <span>Usuario</span>
        </button>
        <button mat-menu-item (click)="cambiarRol('administrador')" [disabled]="rolActual === 'administrador'">
          <mat-icon>admin_panel_settings</mat-icon>
          <span>Administrador</span>
        </button>
      </mat-menu>
    </mat-toolbar>
  `,
  styles: [`
    .navbar {
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      position: sticky;
      top: 0;
      z-index: 1000;
      gap: 8px;
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      font-weight: 500;
      font-size: 18px;
    }
    .logo-text { letter-spacing: 1px; }
    .editorial-selector {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-right: 4px;
    }
    .editorial-icon { color: rgba(255,255,255,0.8); }
    .editorial-field {
      width: 200px;
    }
    .editorial-field ::ng-deep .mat-mdc-form-field-subscript-wrapper {
      display: none;
    }
    .editorial-field ::ng-deep .mat-mdc-text-field-wrapper {
      background: rgba(255,255,255,0.15);
      border-radius: 4px;
    }
    .editorial-field ::ng-deep .mdc-text-field--outlined .mdc-notched-outline > * {
      border-color: rgba(255,255,255,0.4);
    }
    .editorial-field ::ng-deep .mat-mdc-select-value,
    .editorial-field ::ng-deep .mat-mdc-select-arrow {
      color: #fff !important;
    }
    .role-btn {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .role-label { margin: 0 4px; }
    .reset-btn {
      margin-right: 4px;
      border: 1px solid rgba(255,255,255,0.3);
    }
    @media (max-width: 900px) {
      .editorial-field { width: 140px; }
      .reset-label, .role-label { display: none; }
    }
    @media (max-width: 600px) {
      .editorial-selector { display: none; }
    }
  `]
})
export class NavbarComponent {
  private readonly authService = inject(AuthService);
  private readonly editorialService = inject(EditorialService);
  private readonly resetService = inject(ResetService);
  private readonly aplicacionService = inject(AplicacionService);
  private readonly faseService = inject(FaseService);
  private readonly router = inject(Router);
  private readonly dialog = inject(MatDialog);

  readonly rolActual = this.authService.rol;
  readonly editorialActualId = signal<string>(this.authService.editorialActual);

  readonly todasEditoriales: Editorial[] = this.editorialService.editoriales;

  constructor() {
    this.authService.editorialActual$.subscribe(id => this.editorialActualId.set(id));
  }

  cambiarEditorial(id: string): void {
    if (id === this.authService.editorialActual) return;
    this.authService.setEditorialActual(id);
    this.faseService.refrescar();
    if (this.rolActual === 'usuario') {
      const fase = this.faseService.faseActual();
      const faseToPath: Record<string, string> = {
        'aplicacion': '/usuario/aplicacion',
        'seleccion': '/usuario/seleccion',
        'confirmar': '/usuario/confirmar',
        'reserva': '/usuario/mi-reserva'
      };
      const rutaEsperada = faseToPath[fase];
      if (rutaEsperada && this.router.url !== rutaEsperada) {
        this.router.navigate([rutaEsperada], { replaceUrl: true });
      } else {
        this.router.navigate(['/usuario/aplicacion']);
      }
    }
  }

  irAInicio(): void {
    if (this.rolActual === 'usuario') {
      this.router.navigate(['/usuario/aplicacion']);
    } else {
      this.router.navigate(['/admin/aplicaciones']);
    }
  }

  cambiarRol(rol: 'usuario' | 'administrador'): void {
    this.authService.setRol(rol);
    if (rol === 'usuario') {
      this.router.navigate(['/usuario/aplicacion']);
    } else {
      this.router.navigate(['/admin/aplicaciones']);
    }
  }

  reiniciarDemo(): void {
    const ref = this.dialog.open(ResetConfirmDialogComponent);
    ref.afterClosed().subscribe(confirmado => {
      if (confirmado) {
        this.resetService.reiniciarYRecargar();
      }
    });
  }
}
