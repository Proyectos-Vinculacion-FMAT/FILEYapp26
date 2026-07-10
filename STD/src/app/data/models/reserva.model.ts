export type EstadoReserva = 'Por confirmar' | 'Confirmada' | 'Pagada' | 'Cancelada';

export interface ReservaStand {
  standId: string;
  clave: string;
  metrosCuadradosSnapshot: number;
  precioSnapshot: number;
  zona?: string;
}

export interface DescuentoAplicado {
  id: string;
  tipo: 'pronto_pago' | 'especial';
  porcentaje: number;
  motivo?: string;
  montoDescontado: number;
  aplicadoPor: string;
  fecha: Date;
}

export interface Reserva {
  id: string;
  editorialId: string;
  eventoId: string;
  estado: EstadoReserva;
  fechaCreacion: Date;
  fechaVencimientoAnticipo: Date;
  fechaCortePagoTotal?: Date;
  montoTotal: number;
  montoAbonado: number;
  montoPendiente: number;
  anticipoRequerido: number;
  stands: ReservaStand[];
  descuentos: DescuentoAplicado[];
  montoOriginal: number;
}
