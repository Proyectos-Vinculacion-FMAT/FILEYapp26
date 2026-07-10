import { Injectable, inject, signal } from '@angular/core';
import { BehaviorSubject, Observable, map } from 'rxjs';
import {
  Reserva,
  ReservaStand,
  DescuentoAplicado,
  EstadoReserva
} from '../data/models';
import { MOCK_RESERVAS } from '../data/mock';
import { ParametrosService } from './parametros.service';
import { StandService } from './stand.service';
import { CarritoService, ItemCarrito } from './carrito.service';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class ReservaService {
  private readonly parametrosService = inject(ParametrosService);
  private readonly standService = inject(StandService);
  private readonly carritoService = inject(CarritoService);
  private readonly authService = inject(AuthService);

  private readonly reservasSubject = new BehaviorSubject<Reserva[]>(MOCK_RESERVAS);
  readonly reservas$ = this.reservasSubject.asObservable();

  resetear(): void {
    this.reservasSubject.next([...MOCK_RESERVAS]);
  }

  get reservas(): Reserva[] {
    return this.reservasSubject.value;
  }

  getById(id: string): Reserva | undefined {
    return this.reservas.find(r => r.id === id);
  }

  getReservaActual(): Reserva | undefined {
    const editorialId = this.authService.editorialActual;
    return this.reservas.find(r => r.editorialId === editorialId);
  }

  getReservaActual$(): Observable<Reserva | undefined> {
    return this.reservas$.pipe(
      map(list => list.find(r => r.editorialId === this.authService.editorialActual))
    );
  }

  getByEditorial(editorialId: string): Reserva | undefined {
    return this.reservas.find(r => r.editorialId === editorialId);
  }

  getVencidas(): Reserva[] {
    const hoy = new Date();
    return this.reservas.filter(r =>
      r.estado === 'Por confirmar' &&
      r.fechaVencimientoAnticipo < hoy &&
      r.montoAbonado < r.anticipoRequerido
    );
  }

  filtrar(filtros: {
    estado?: EstadoReserva;
    busqueda?: string;
    editorialId?: string;
    soloVencidas?: boolean;
  }): Reserva[] {
    let list = this.reservasSubject.value;
    if (filtros.estado) {
      list = list.filter(r => r.estado === filtros.estado);
    }
    if (filtros.editorialId) {
      list = list.filter(r => r.editorialId === filtros.editorialId);
    }
    if (filtros.soloVencidas) {
      const hoy = new Date();
      list = list.filter(r =>
        r.estado === 'Por confirmar' &&
        r.fechaVencimientoAnticipo < hoy &&
        r.montoAbonado < r.anticipoRequerido
      );
    }
    if (filtros.busqueda && filtros.busqueda.trim().length > 0) {
      const term = filtros.busqueda.toLowerCase();
      list = list.filter(r => {
        const ed = this.editorialesCache.find(e => e.id === r.editorialId);
        return ed?.nombre.toLowerCase().includes(term) || r.id.toLowerCase().includes(term);
      });
    }
    return list;
  }

  private readonly editorialesCache: { id: string; nombre: string }[] = [];

  setEditorialesCache(list: { id: string; nombre: string }[]): void {
    this.editorialesCache.splice(0, this.editorialesCache.length, ...list);
  }

  crearDesdeCarrito(editorialId: string, eventoId: string): { ok: boolean; reserva?: Reserva; errores?: string[] } {
    const validacion = this.carritoService.validarDisponibilidad();
    if (!validacion.ok) {
      return { ok: false, errores: validacion.noDisponibles.map(c => `El stand ${c} ya no está disponible`) };
    }

    const items = this.carritoService.items();
    if (items.length === 0) {
      return { ok: false, errores: ['El carrito está vacío'] };
    }

    const params = this.parametrosService.parametros;
    const hoy = new Date();
    const fechaVencimiento = new Date(hoy);
    fechaVencimiento.setDate(fechaVencimiento.getDate() + params.plazoReservaDias);

    const fechaCorte = new Date(params.fechaLimiteProntoPago);
    fechaCorte.setDate(fechaCorte.getDate() + 30);

    const montoOriginal = items.reduce((sum, i) => sum + i.precioUnitario, 0);

    let montoTotal = montoOriginal;
    const descuentos: DescuentoAplicado[] = [];
    if (hoy <= params.fechaLimiteProntoPago) {
      const montoDescuento = montoOriginal * (params.descuentoProntoPago / 100);
      montoTotal = montoOriginal - montoDescuento;
      descuentos.push({
        id: `DSC-${Date.now()}`,
        tipo: 'pronto_pago',
        porcentaje: params.descuentoProntoPago,
        montoDescontado: montoDescuento,
        aplicadoPor: 'Sistema',
        fecha: hoy
      });
    }

    const anticipoRequerido = montoTotal * (params.porcentajeAnticipo / 100);
    const montoPendiente = montoTotal;

    const stands: ReservaStand[] = items.map(i => ({
      standId: i.stand.id,
      clave: i.stand.clave,
      metrosCuadradosSnapshot: i.stand.metrosCuadrados,
      precioSnapshot: i.precioUnitario,
      zona: i.stand.zona
    }));

    const reserva: Reserva = {
      id: `RES-${Date.now()}`,
      editorialId,
      eventoId,
      estado: 'Por confirmar',
      fechaCreacion: hoy,
      fechaVencimientoAnticipo: fechaVencimiento,
      fechaCortePagoTotal: fechaCorte,
      montoTotal,
      montoAbonado: 0,
      montoPendiente,
      anticipoRequerido,
      stands,
      descuentos,
      montoOriginal
    };

    this.reservasSubject.next([...this.reservasSubject.value, reserva]);
    this.standService.marcarReservado(stands.map(s => s.standId));
    this.carritoService.limpiar();

    return { ok: true, reserva };
  }

  prorrogar(reservaId: string, nuevaFecha: Date): void {
    this.actualizarReserva(reservaId, { fechaVencimientoAnticipo: nuevaFecha });
  }

  cancelar(reservaId: string): void {
    const reserva = this.getById(reservaId);
    if (!reserva) return;
    this.actualizarReserva(reservaId, { estado: 'Cancelada' });
    this.standService.liberar(reserva.stands.map(s => s.standId));
  }

  modificarFechaCorte(reservaId: string, nuevaFecha: Date): void {
    this.actualizarReserva(reservaId, { fechaCortePagoTotal: nuevaFecha });
  }

  aplicarDescuentoEspecial(reservaId: string, porcentaje: number, motivo: string, adminId: string): void {
    const reserva = this.getById(reservaId);
    if (!reserva) return;
    if (reserva.descuentos.some(d => d.tipo === 'especial')) return;

    const yaTieneProntoPago = reserva.descuentos.some(d => d.tipo === 'pronto_pago');
    const baseParaDescuento = reserva.montoTotal;
    const montoDescuento = baseParaDescuento * (porcentaje / 100);
    const nuevoMontoTotal = baseParaDescuento - montoDescuento;

    const nuevoDescuento: DescuentoAplicado = {
      id: `DSC-${Date.now()}`,
      tipo: 'especial',
      porcentaje,
      motivo,
      montoDescontado: montoDescuento,
      aplicadoPor: adminId,
      fecha: new Date()
    };

    const nuevoAnticipo = nuevoMontoTotal * (this.parametrosService.parametros.porcentajeAnticipo / 100);
    const nuevoPendiente = nuevoMontoTotal - reserva.montoAbonado;

    this.actualizarReserva(reservaId, {
      descuentos: [...reserva.descuentos, nuevoDescuento],
      montoTotal: nuevoMontoTotal,
      anticipoRequerido: nuevoAnticipo,
      montoPendiente: nuevoPendiente
    });

    this.evaluarUmbrales(reservaId);
  }

  actualizarMontosReserva(reservaId: string): void {
    const reserva = this.getById(reservaId);
    if (!reserva) return;
    const montoPendiente = Math.max(0, reserva.montoTotal - reserva.montoAbonado);
    this.actualizarReserva(reservaId, { montoPendiente });
    this.evaluarUmbrales(reservaId);
  }

  sumarAbonoDirecto(reservaId: string, monto: number): void {
    const reserva = this.getById(reservaId);
    if (!reserva) return;
    const nuevoAbonado = reserva.montoAbonado + monto;
    this.actualizarReserva(reservaId, { montoAbonado: nuevoAbonado });
    this.actualizarMontosReserva(reservaId);
  }

  private actualizarReserva(reservaId: string, cambios: Partial<Reserva>): void {
    const list = this.reservasSubject.value.map(r => r.id === reservaId ? { ...r, ...cambios } : r);
    this.reservasSubject.next(list);
  }

  private evaluarUmbrales(reservaId: string): void {
    const reserva = this.getById(reservaId);
    if (!reserva) return;
    if (reserva.estado === 'Cancelada' || reserva.estado === 'Pagada') return;

    if (reserva.montoAbonado >= reserva.montoTotal && reserva.montoTotal > 0) {
      this.actualizarReserva(reservaId, { estado: 'Pagada', montoPendiente: 0 });
      this.standService.marcarOcupado(reserva.stands.map(s => s.standId));
    } else if (reserva.montoAbonado >= reserva.anticipoRequerido) {
      this.actualizarReserva(reservaId, { estado: 'Confirmada' });
    }
  }
}
