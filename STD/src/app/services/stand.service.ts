import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Stand } from '../data/models';
import { MOCK_STANDS } from '../data/mock';

@Injectable({ providedIn: 'root' })
export class StandService {
  private readonly standsSubject = new BehaviorSubject<Stand[]>(MOCK_STANDS);
  readonly stands$ = this.standsSubject.asObservable();

  resetear(): void {
    this.standsSubject.next([...MOCK_STANDS]);
  }

  get stands(): Stand[] {
    return this.standsSubject.value;
  }

  getById(id: string): Stand | undefined {
    return this.stands.find(s => s.id === id);
  }

  getByClave(clave: string): Stand | undefined {
    return this.stands.find(s => s.clave === clave);
  }

  getDisponibles(): Stand[] {
    return this.stands.filter(s => s.estado === 'Disponible');
  }

  getReservados(): Stand[] {
    return this.stands.filter(s => s.estado === 'Reservado' || s.estado === 'Ocupado');
  }

  marcarReservado(standIds: string[]): void {
    const list = this.standsSubject.value.map(s =>
      standIds.includes(s.id) ? { ...s, estado: 'Reservado' as const } : s
    );
    this.standsSubject.next(list);
  }

  marcarOcupado(standIds: string[]): void {
    const list = this.standsSubject.value.map(s =>
      standIds.includes(s.id) ? { ...s, estado: 'Ocupado' as const } : s
    );
    this.standsSubject.next(list);
  }

  liberar(standIds: string[]): void {
    const list = this.standsSubject.value.map(s =>
      standIds.includes(s.id) ? { ...s, estado: 'Disponible' as const } : s
    );
    this.standsSubject.next(list);
  }

  actualizar(stand: Stand): void {
    const list = this.standsSubject.value.map(s => s.id === stand.id ? stand : s);
    this.standsSubject.next(list);
  }

  precioStand(stand: Stand, costoM2: number): number {
    if (stand.precio !== undefined) return stand.precio;
    return stand.metrosCuadrados * costoM2;
  }
}
