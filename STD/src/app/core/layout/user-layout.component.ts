import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { filter } from 'rxjs/operators';
import { NavbarComponent } from './navbar.component';
import { FaseService } from '../../services/fase.service';

@Component({
  selector: 'app-user-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, NavbarComponent],
  template: `
    <app-navbar></app-navbar>

    <main class="content">
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    .content {
      min-height: calc(100vh - 64px);
      background: var(--filey-bg-soft);
    }
  `]
})
export class UserLayoutComponent implements OnInit {
  private readonly router = inject(Router);
  private readonly faseService = inject(FaseService);

  ngOnInit(): void {
    this.router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe(e => this.verificarRedireccion(e.urlAfterRedirects));

    setTimeout(() => {
      this.verificarRedireccion(this.router.url);
    }, 50);
  }

  private verificarRedireccion(url: string): void {
    setTimeout(() => {
      const actual = this.faseService.faseActual();
      const faseToPath: Record<string, string> = {
        'aplicacion': '/usuario/aplicacion',
        'seleccion': '/usuario/seleccion',
        'confirmar': '/usuario/confirmar',
        'reserva': '/usuario/mi-reserva'
      };
      const rutaEsperada = faseToPath[actual];
      if (!rutaEsperada) return;
      if (this.router.url.startsWith(rutaEsperada)) return;
      if (url.startsWith('/usuario/')) {
        this.router.navigate([rutaEsperada], { replaceUrl: true });
      }
    }, 0);
  }
}
