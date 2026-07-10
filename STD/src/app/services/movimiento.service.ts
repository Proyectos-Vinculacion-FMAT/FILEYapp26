import { Injectable, inject, Injector } from '@angular/core';
import { BehaviorSubject, Observable, map } from 'rxjs';
import { Movimiento, MetodoPago } from '../data/models';
import { MOCK_MOVIMIENTOS } from '../data/mock';
import { ReservaService } from './reserva.service';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class MovimientoService {
  private readonly injector = inject(Injector);
  private readonly authService = inject(AuthService);
  private _reservaService?: ReservaService;

  private get reservaService(): ReservaService {
    if (!this._reservaService) {
      this._reservaService = this.injector.get(ReservaService);
    }
    return this._reservaService;
  }

  private readonly movimientosSubject = new BehaviorSubject<Movimiento[]>(MOCK_MOVIMIENTOS);
  readonly movimientos$ = this.movimientosSubject.asObservable();

  resetear(): void {
    this.movimientosSubject.next([...MOCK_MOVIMIENTOS]);
  }

  get movimientos(): Movimiento[] {
    return this.movimientosSubject.value;
  }

  getByReserva(reservaId: string): Movimiento[] {
    return this.movimientos.filter(m => m.reservaId === reservaId);
  }

  getByReserva$(reservaId: string): Observable<Movimiento[]> {
    return this.movimientos$.pipe(
      map(list => list.filter(m => m.reservaId === reservaId)
        .sort((a, b) => b.fechaRegistro.getTime() - a.fechaRegistro.getTime()))
    );
  }

  getPendientesValidacion(): Movimiento[] {
    return this.movimientos.filter(m => m.estado === 'pendiente_validacion');
  }

  getPendientesValidacion$(): Observable<Movimiento[]> {
    return this.movimientos$.pipe(
      map(list => list.filter(m => m.estado === 'pendiente_validacion')
        .sort((a, b) => b.fechaRegistro.getTime() - a.fechaRegistro.getTime()))
    );
  }

  registrarPagoUsuario(reservaId: string, monto: number, metodo: MetodoPago, comprobanteNombre: string): Movimiento {
    const mov: Movimiento = {
      id: `MOV-${Date.now()}`,
      reservaId,
      monto,
      metodo,
      origen: 'usuario',
      estado: 'pendiente_validacion',
      comprobanteNombre,
      registradoPor: this.authService.editorialActual,
      fechaRegistro: new Date()
    };
    this.movimientosSubject.next([...this.movimientosSubject.value, mov]);
    return mov;
  }

  registrarAbonoManual(reservaId: string, monto: number, metodo: MetodoPago, comprobanteNombre: string): Movimiento {
    const mov: Movimiento = {
      id: `MOV-${Date.now()}`,
      reservaId,
      monto,
      metodo,
      origen: 'admin_manual',
      estado: 'validado',
      comprobanteNombre,
      registradoPor: 'Administrador',
      fechaRegistro: new Date(),
      validadoPor: 'Administrador',
      fechaValidacion: new Date()
    };
    this.movimientosSubject.next([...this.movimientosSubject.value, mov]);
    this.reservaService.sumarAbonoDirecto(reservaId, monto);
    return mov;
  }

  validar(movimientoId: string): void {
    this.actualizar(movimientoId, {
      estado: 'validado',
      validadoPor: 'Administrador',
      fechaValidacion: new Date()
    });
    const mov = this.movimientos.find(m => m.id === movimientoId);
    if (mov) {
      this.reservaService.sumarAbonoDirecto(mov.reservaId, mov.monto);
    }
  }

  rechazar(movimientoId: string, motivo: string): void {
    this.actualizar(movimientoId, {
      estado: 'rechazado',
      validadoPor: 'Administrador',
      fechaValidacion: new Date(),
      motivoRechazo: motivo
    });
  }

  private actualizar(id: string, cambios: Partial<Movimiento>): void {
    const list = this.movimientosSubject.value.map(m => m.id === id ? { ...m, ...cambios } : m);
    this.movimientosSubject.next(list);
  }
}
