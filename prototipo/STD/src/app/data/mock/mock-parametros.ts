import { ParametrosSistema } from '../models';

export const MOCK_PARAMETROS: ParametrosSistema = {
  id: 'PAR-001',
  costoM2: 2500,
  porcentajeAnticipo: 50,
  plazoReservaDias: 30,
  descuentoProntoPago: 10,
  fechaLimiteProntoPago: new Date('2026-07-15'),
  datosBancarios: {
    banco: 'BBVA Bancomer',
    titular: 'Patronato de la UADY',
    cuenta: '0123 4567 8901 2345 67',
    clabe: '012 345 678 901 234 567',
    sucursal: 'Sucursal 1234 Mérida Centro',
    referencia: 'Nombre de la Editorial'
  },
  instruccionesPago: 'Realizar transferencia bancaria o depósito con cheque a la cuenta indicada. No se aceptan pagos en efectivo. Enviar comprobante al sistema para validación. El concepto de pago debe incluir el nombre de la editorial.'
};
