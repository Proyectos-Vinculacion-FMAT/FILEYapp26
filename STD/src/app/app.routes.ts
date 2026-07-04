import { Routes } from '@angular/router';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/usuario/aplicacion', pathMatch: 'full' },

  {
    path: 'usuario',
    canActivate: [roleGuard('usuario')],
    loadComponent: () => import('./core/layout/user-layout.component').then(m => m.UserLayoutComponent),
    children: [
      { path: '', redirectTo: 'aplicacion', pathMatch: 'full' },
      {
        path: 'aplicacion',
        loadComponent: () => import('./features/usuario/u1-aplicacion/aplicacion.component').then(m => m.AplicacionComponent)
      },
      {
        path: 'seleccion',
        loadComponent: () => import('./features/usuario/seleccion/seleccion.component').then(m => m.SeleccionComponent)
      },
      {
        path: 'confirmar',
        loadComponent: () => import('./features/usuario/u4-confirmar-reserva/confirmar-reserva.component').then(m => m.ConfirmarReservaComponent)
      },
      {
        path: 'mi-reserva',
        loadComponent: () => import('./features/usuario/u5-mi-reserva/mi-reserva.component').then(m => m.MiReservaComponent)
      }
    ]
  },

  {
    path: 'admin',
    canActivate: [roleGuard('administrador')],
    loadComponent: () => import('./core/layout/admin-layout.component').then(m => m.AdminLayoutComponent),
    children: [
      { path: '', redirectTo: 'aplicaciones', pathMatch: 'full' },
      {
        path: 'aplicaciones',
        loadComponent: () => import('./features/admin/a1-aplicaciones/aplicaciones.component').then(m => m.AplicacionesComponent)
      },
      {
        path: 'aplicaciones/:id',
        loadComponent: () => import('./features/admin/a2-detalle-aplicacion/detalle-aplicacion.component').then(m => m.DetalleAplicacionComponent)
      },
      {
        path: 'reservas',
        loadComponent: () => import('./features/admin/a3-reservas/reservas.component').then(m => m.ReservasComponent)
      },
      {
        path: 'reservas/:id',
        loadComponent: () => import('./features/admin/a4-detalle-reserva/detalle-reserva.component').then(m => m.DetalleReservaComponent)
      },
      {
        path: 'pagos-validar',
        loadComponent: () => import('./features/admin/a5-pagos-validar/pagos-validar.component').then(m => m.PagosValidarComponent)
      },
      {
        path: 'expositores',
        loadComponent: () => import('./features/admin/a6-expositores/expositores.component').then(m => m.ExpositoresComponent)
      },
      {
        path: 'expositores/:id',
        loadComponent: () => import('./features/admin/a7-detalle-expositor/detalle-expositor.component').then(m => m.DetalleExpositorComponent)
      },
      {
        path: 'mapa',
        loadComponent: () => import('./features/admin/a8-mapa-completo/mapa-completo.component').then(m => m.MapaCompletoComponent)
      },
      {
        path: 'mapa/editar/:standId',
        loadComponent: () => import('./features/admin/a9-editar-espacio/editar-espacio.component').then(m => m.EditarEspacioComponent)
      },
      {
        path: 'configuracion',
        loadComponent: () => import('./features/admin/a10-configuracion/configuracion.component').then(m => m.ConfiguracionComponent)
      }
    ]
  }
];
