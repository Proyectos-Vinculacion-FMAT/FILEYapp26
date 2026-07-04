import { Injectable, inject, computed, signal } from '@angular/core';
import { Stand } from '../data/models';
import { StandService } from './stand.service';
import { ParametrosService } from './parametros.service';

export interface ItemCarrito {
  stand: Stand;
  precioUnitario: number;
}

@Injectable({ providedIn: 'root' })
export class CarritoService {
  private readonly standService = inject(StandService);
  private readonly parametrosService = inject(ParametrosService);

  private readonly itemsSignal = signal<ItemCarrito[]>([]);
  readonly items = this.itemsSignal.asReadonly();
  readonly cantidad = computed(() => this.itemsSignal().length);

  readonly subtotal = computed(() =>
    this.itemsSignal().reduce((sum, item) => sum + item.precioUnitario, 0)
  );

  readonly metrosCuadrados = computed(() =>
    this.itemsSignal().reduce((sum, item) => sum + item.stand.metrosCuadrados, 0)
  );

  agregar(stand: Stand): { ok: boolean; mensaje?: string } {
    if (stand.estado !== 'Disponible') {
      return { ok: false, mensaje: 'El stand ya no está disponible' };
    }
    if (this.itemsSignal().some(i => i.stand.id === stand.id)) {
      return { ok: false, mensaje: 'El stand ya está en tu carrito' };
    }
    const precio = this.standService.precioStand(stand, this.parametrosService.parametros.costoM2);
    this.itemsSignal.update(list => [...list, { stand, precioUnitario: precio }]);
    return { ok: true };
  }

  quitar(standId: string): void {
    this.itemsSignal.update(list => list.filter(i => i.stand.id !== standId));
  }

  limpiar(): void {
    this.itemsSignal.set([]);
  }

  contiene(standId: string): boolean {
    return this.itemsSignal().some(i => i.stand.id === standId);
  }

  validarDisponibilidad(): { ok: boolean; noDisponibles: string[] } {
    const noDisponibles: string[] = [];
    for (const item of this.itemsSignal()) {
      const stand = this.standService.getById(item.stand.id);
      if (!stand || stand.estado !== 'Disponible') {
        noDisponibles.push(item.stand.clave);
      }
    }
    return { ok: noDisponibles.length === 0, noDisponibles };
  }
}
