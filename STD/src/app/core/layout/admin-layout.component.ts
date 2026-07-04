import { Component, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatSidenavModule, MatSidenav } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { map } from 'rxjs/operators';
import { NavbarComponent } from './navbar.component';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, MatSidenavModule, MatToolbarModule, MatListModule, MatIconModule, MatButtonModule, NavbarComponent],
  template: `
    <app-navbar></app-navbar>
    <mat-sidenav-container class="sidenav-container">
      <mat-sidenav #sidenav mode="side" opened class="sidenav">
        <mat-nav-list>
          <a mat-list-item routerLink="/admin/aplicaciones" routerLinkActive="active" (click)="cerrarSiMovil()">
            <mat-icon matListItemIcon>description</mat-icon>
            <span matListItemTitle>Aplicaciones</span>
          </a>
          <a mat-list-item routerLink="/admin/reservas" routerLinkActive="active" (click)="cerrarSiMovil()">
            <mat-icon matListItemIcon>event</mat-icon>
            <span matListItemTitle>Reservas</span>
          </a>
          <a mat-list-item routerLink="/admin/pagos-validar" routerLinkActive="active" (click)="cerrarSiMovil()">
            <mat-icon matListItemIcon>fact_check</mat-icon>
            <span matListItemTitle>Pagos por validar</span>
          </a>
          <a mat-list-item routerLink="/admin/expositores" routerLinkActive="active" (click)="cerrarSiMovil()">
            <mat-icon matListItemIcon>people</mat-icon>
            <span matListItemTitle>Expositores</span>
          </a>
          <a mat-list-item routerLink="/admin/mapa" routerLinkActive="active" (click)="cerrarSiMovil()">
            <mat-icon matListItemIcon>map</mat-icon>
            <span matListItemTitle>Mapa completo</span>
          </a>
          <a mat-list-item routerLink="/admin/configuracion" routerLinkActive="active" (click)="cerrarSiMovil()">
            <mat-icon matListItemIcon>settings</mat-icon>
            <span matListItemTitle>Configuración</span>
          </a>
        </mat-nav-list>
      </mat-sidenav>
      <mat-sidenav-content>
        <div class="content-toolbar">
          <button mat-icon-button (click)="sidenav.toggle()" class="menu-btn">
            <mat-icon>menu</mat-icon>
          </button>
        </div>
        <main class="content">
          <router-outlet></router-outlet>
        </main>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [`
    .sidenav-container {
      height: calc(100vh - 64px);
      background: #f5f5f5;
    }
    .sidenav {
      width: 240px;
      background: #fff;
      border-right: 1px solid #e5e7eb;
    }
    .sidenav .active {
      background: #e3f2fd;
      color: #1a237e;
    }
    .content-toolbar {
      background: #fff;
      border-bottom: 1px solid #e5e7eb;
      height: 48px;
      display: flex;
      align-items: center;
      padding: 0 16px;
    }
    .content {
      min-height: calc(100vh - 64px - 48px);
      background: #f5f5f5;
    }
  `]
})
export class AdminLayoutComponent {
  @ViewChild('sidenav') sidenav!: MatSidenav;
  private readonly breakpointObserver = inject(BreakpointObserver);
  esMovil = false;

  constructor() {
    this.breakpointObserver.observe([Breakpoints.Handset]).subscribe(result => {
      this.esMovil = result.matches;
    });
  }

  cerrarSiMovil(): void {
    if (this.esMovil && this.sidenav) {
      this.sidenav.close();
    }
  }
}
