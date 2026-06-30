import { Injectable, inject, signal, computed } from '@angular/core';
import { AuthService } from './auth.service';
import { AplicacionService } from './aplicacion.service';
import { ReservaService } from './reserva.service';
import { CarritoService } from './carrito.service';
import { Aplicacion, Reserva } from '../data/models';

export type FaseActual = 'aplicacion' | 'seleccion' | 'confirmar' | 'reserva';

@Injectable({ providedIn: 'root' })
export class FaseService {
  private readonly authService = inject(AuthService);
  private readonly aplicacionService = inject(AplicacionService);
  private readonly reservaService = inject(ReservaService);
  private readonly carritoService = inject(CarritoService);

  private readonly revisionTrigger = signal(0);

  readonly faseActual = computed<FaseActual>(() => {
    this.revisionTrigger();
    const editorialId = this.authService.editorialActual;

    const aplicacion = this.aplicacionService.getByEditorial(editorialId);
    const reserva = this.reservaService.getByEditorial(editorialId);

    if (reserva && reserva.estado !== 'Cancelada') {
      return 'reserva';
    }
    if (this.carritoService.cantidad() > 0) {
      return 'confirmar';
    }
    if (aplicacion && aplicacion.estado === 'aceptada') {
      return 'seleccion';
    }
    return 'aplicacion';
  });

  readonly aplicacion = computed<Aplicacion | undefined>(() => {
    this.revisionTrigger();
    return this.aplicacionService.getByEditorial(this.authService.editorialActual);
  });

  readonly reserva = computed<Reserva | undefined>(() => {
    this.revisionTrigger();
    return this.reservaService.getByEditorial(this.authService.editorialActual);
  });

  readonly tieneReservaActiva = computed(() => {
    const r = this.reserva();
    return !!r && r.estado !== 'Cancelada';
  });

  readonly puedeAvanzarASeleccion = computed(() => {
    return this.aplicacion()?.estado === 'aceptada' && !this.tieneReservaActiva();
  });

  readonly puedeAvanzarAConfirmar = computed(() => {
    return this.puedeAvanzarASeleccion() && this.carritoService.cantidad() > 0;
  });

  readonly puedeAccederAMiReserva = computed(() => {
    return this.tieneReservaActiva();
  });

  refrescar(): void {
    this.revisionTrigger.update(v => v + 1);
  }
}
