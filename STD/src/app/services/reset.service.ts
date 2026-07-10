import { Injectable, inject } from '@angular/core';
import { AplicacionService } from './aplicacion.service';
import { ReservaService } from './reserva.service';
import { MovimientoService } from './movimiento.service';
import { CarritoService } from './carrito.service';
import { StandService } from './stand.service';
import { ParametrosService } from './parametros.service';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class ResetService {
  private readonly aplicacionService = inject(AplicacionService);
  private readonly reservaService = inject(ReservaService);
  private readonly movimientoService = inject(MovimientoService);
  private readonly carritoService = inject(CarritoService);
  private readonly standService = inject(StandService);
  private readonly parametrosService = inject(ParametrosService);
  private readonly authService = inject(AuthService);

  reiniciarDemo(): void {
    this.aplicacionService.resetear();
    this.reservaService.resetear();
    this.movimientoService.resetear();
    this.standService.resetear();
    this.parametrosService.resetear();
    this.carritoService.limpiar();
    this.authService.setRol('usuario');
    this.authService.setEditorialActual('ED-005');
  }

  reiniciarYRecargar(): void {
    this.reiniciarDemo();
    window.location.reload();
  }
}
