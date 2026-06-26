export interface DatosBancarios {
  banco: string;
  titular: string;
  cuenta: string;
  clabe: string;
  sucursal: string;
  referencia: string;
}

export interface ParametrosSistema {
  id: string;
  costoM2: number;
  porcentajeAnticipo: number;
  plazoReservaDias: number;
  descuentoProntoPago: number;
  fechaLimiteProntoPago: Date;
  datosBancarios: DatosBancarios;
  instruccionesPago: string;
}
