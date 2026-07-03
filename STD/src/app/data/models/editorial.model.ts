export interface Domicilio {
  calle: string;
  numero: string;
  colonia: string;
  cp: string;
  municipio: string;
  estado: string;
  pais: string;
}

export interface Contacto {
  nombre: string;
  email: string;
}

export interface Editorial {
  id: string;
  cuentaId: string;
  nombre: string;
  domicilio: Domicilio;
  contactos: {
    directorGeneral: Contacto;
    directorComercial: Contacto;
    directorEditorial: Contacto;
    directorPromocion: Contacto;
  };
  responsableStand: string;
  giro: 'Editor' | 'Librero' | 'Distribuidor';
  telefonoOficina: string;
  telefonoCelular: string;
  correoElectronico: string;
  nombreAntepecho: string;
  numPersonasAtienden: number;
  totalSellos: number;
  cantidadLibrosAprox: number;
  cantidadTitulosAprox: number;
  materiales: string[];
  tematicas: string[];
  constanciaFiscalId?: string;
}
