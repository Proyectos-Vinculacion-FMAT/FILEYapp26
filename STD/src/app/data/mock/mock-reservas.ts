import { Reserva } from '../models';

const fechaVencida = new Date();
fechaVencida.setDate(fechaVencida.getDate() - 10);

const fechaFutura = new Date();
fechaFutura.setDate(fechaFutura.getDate() + 20);

const fechaCorte = new Date();
fechaCorte.setDate(fechaCorte.getDate() + 60);

export const MOCK_RESERVAS: Reserva[] = [
  {
    id: 'RES-001',
    editorialId: 'ED-001',
    eventoId: 'EVT-001',
    estado: 'Por confirmar',
    fechaCreacion: fechaVencida,
    fechaVencimientoAnticipo: fechaVencida,
    fechaCortePagoTotal: fechaCorte,
    montoTotal: 40500,
    montoAbonado: 5000,
    montoPendiente: 35500,
    anticipoRequerido: 20250,
    montoOriginal: 45000,
    stands: [
      { standId: 'S-A3', clave: 'A3', metrosCuadradosSnapshot: 6, precioSnapshot: 15000, zona: 'Pabellón Internacional' },
      { standId: 'S-B2', clave: 'B2', metrosCuadradosSnapshot: 9, precioSnapshot: 22500, zona: 'Pabellón Nacional' },
      { standId: 'S-C2', clave: 'C2', metrosCuadradosSnapshot: 12, precioSnapshot: 30000, zona: 'Pabellón Académico' }
    ],
    descuentos: [
      { id: 'DSC-001', tipo: 'pronto_pago', porcentaje: 10, montoDescontado: 4500, aplicadoPor: 'Sistema', fecha: fechaVencida }
    ]
  },
  {
    id: 'RES-002',
    editorialId: 'ED-002',
    eventoId: 'EVT-001',
    estado: 'Confirmada',
    fechaCreacion: fechaFutura,
    fechaVencimientoAnticipo: fechaFutura,
    fechaCortePagoTotal: fechaCorte,
    montoTotal: 30000,
    montoAbonado: 15000,
    montoPendiente: 15000,
    anticipoRequerido: 15000,
    montoOriginal: 30000,
    stands: [
      { standId: 'S-D3', clave: 'D3', metrosCuadradosSnapshot: 6, precioSnapshot: 15000, zona: 'Pabellón Independiente' },
      { standId: 'S-B2', clave: 'B2', metrosCuadradosSnapshot: 9, precioSnapshot: 22500, zona: 'Pabellón Nacional' }
    ],
    descuentos: []
  },
  {
    id: 'RES-003',
    editorialId: 'ED-003',
    eventoId: 'EVT-001',
    estado: 'Pagada',
    fechaCreacion: new Date('2026-03-01'),
    fechaVencimientoAnticipo: new Date('2026-03-31'),
    fechaCortePagoTotal: new Date('2026-08-31'),
    montoTotal: 22500,
    montoAbonado: 22500,
    montoPendiente: 0,
    anticipoRequerido: 11250,
    montoOriginal: 25000,
    stands: [
      { standId: 'S-C3', clave: 'C3', metrosCuadradosSnapshot: 12, precioSnapshot: 30000, zona: 'Pabellón Académico' }
    ],
    descuentos: [
      { id: 'DSC-002', tipo: 'pronto_pago', porcentaje: 10, montoDescontado: 2500, aplicadoPor: 'Sistema', fecha: new Date('2026-03-15') }
    ]
  }
];
