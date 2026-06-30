import { Movimiento } from '../models';

export const MOCK_MOVIMIENTOS: Movimiento[] = [
  {
    id: 'MOV-001',
    reservaId: 'RES-001',
    monto: 5000,
    metodo: 'transferencia',
    origen: 'usuario',
    estado: 'pendiente_validacion',
    comprobanteId: 'DOC-COMP-001',
    comprobanteNombre: 'comprobante_transferencia_001.pdf',
    registradoPor: 'ED-001',
    fechaRegistro: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
  },
  {
    id: 'MOV-002',
    reservaId: 'RES-002',
    monto: 15000,
    metodo: 'transferencia',
    origen: 'usuario',
    estado: 'validado',
    comprobanteId: 'DOC-COMP-002',
    comprobanteNombre: 'comprobante_gandhi_001.pdf',
    registradoPor: 'ED-002',
    fechaRegistro: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    validadoPor: 'Administrador',
    fechaValidacion: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000)
  },
  {
    id: 'MOV-003',
    reservaId: 'RES-003',
    monto: 11250,
    metodo: 'deposito',
    origen: 'usuario',
    estado: 'validado',
    comprobanteId: 'DOC-COMP-003',
    comprobanteNombre: 'deposito_lanave.pdf',
    registradoPor: 'ED-003',
    fechaRegistro: new Date('2026-03-10'),
    validadoPor: 'Administrador',
    fechaValidacion: new Date('2026-03-12')
  },
  {
    id: 'MOV-004',
    reservaId: 'RES-003',
    monto: 11250,
    metodo: 'transferencia',
    origen: 'usuario',
    estado: 'validado',
    comprobanteId: 'DOC-COMP-004',
    comprobanteNombre: 'transferencia_lanave_final.pdf',
    registradoPor: 'ED-003',
    fechaRegistro: new Date('2026-03-20'),
    validadoPor: 'Administrador',
    fechaValidacion: new Date('2026-03-21')
  },
  {
    id: 'MOV-005',
    reservaId: 'RES-001',
    monto: 3000,
    metodo: 'transferencia',
    origen: 'usuario',
    estado: 'rechazado',
    comprobanteId: 'DOC-COMP-005',
    comprobanteNombre: 'transferencia_rechazada.pdf',
    registradoPor: 'ED-001',
    fechaRegistro: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    validadoPor: 'Administrador',
    fechaValidacion: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000),
    motivoRechazo: 'El comprobante no es legible. Favor de reenviar una imagen más clara.'
  },
  {
    id: 'MOV-006',
    reservaId: 'RES-001',
    monto: 2000,
    metodo: 'cheque',
    origen: 'admin_manual',
    estado: 'validado',
    comprobanteId: 'DOC-COMP-006',
    comprobanteNombre: 'cheque_porrua.pdf',
    registradoPor: 'Administrador',
    fechaRegistro: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    validadoPor: 'Administrador',
    fechaValidacion: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
  }
];
