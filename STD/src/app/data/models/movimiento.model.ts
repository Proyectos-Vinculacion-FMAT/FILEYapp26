export type MetodoPago = 'transferencia' | 'deposito' | 'cheque';
export type OrigenMovimiento = 'usuario' | 'admin_manual';
export type EstadoMovimiento = 'pendiente_validacion' | 'validado' | 'rechazado';

export interface Movimiento {
  id: string;
  reservaId: string;
  monto: number;
  metodo: MetodoPago;
  origen: OrigenMovimiento;
  estado: EstadoMovimiento;
  comprobanteId?: string;
  comprobanteNombre?: string;
  registradoPor: string;
  fechaRegistro: Date;
  validadoPor?: string;
  fechaValidacion?: Date;
  motivoRechazo?: string;
}
