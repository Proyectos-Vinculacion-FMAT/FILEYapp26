import { Editorial } from '../models';

export const MOCK_EDITORIALES: Editorial[] = [
  {
    id: 'ED-001',
    cuentaId: 'CT-001',
    nombre: 'Editorial Porrúa Yucatán',
    domicilio: {
      calle: 'Av. Reforma',
      numero: '123',
      colonia: 'Centro',
      cp: '97000',
      municipio: 'Mérida',
      estado: 'Yucatán',
      pais: 'México'
    },
    contactos: {
      directorGeneral: { nombre: 'Juan Pérez Martín', email: 'juan.perez@porrua.com' },
      directorComercial: { nombre: 'María López García', email: 'maria.lopez@porrua.com' },
      directorEditorial: { nombre: 'Carlos Rodríguez', email: 'carlos.rodriguez@porrua.com' },
      directorPromocion: { nombre: 'Ana Martínez', email: 'ana.martinez@porrua.com' }
    },
    responsableStand: 'Roberto Sánchez',
    giro: 'Editor',
    telefonoOficina: '999 123 4567',
    telefonoCelular: '999 987 6543',
    correoElectronico: 'contacto@porrua.com',
    nombreAntepecho: 'PORRÚA',
    numPersonasAtienden: 4,
    totalSellos: 3,
    cantidadLibrosAprox: 800,
    cantidadTitulosAprox: 250,
    materiales: ['Libro', 'Revista'],
    tematicas: ['Literatura', 'Infantil', 'Académica'],
    constanciaFiscalId: 'DOC-001'
  },
  {
    id: 'ED-002',
    cuentaId: 'CT-002',
    nombre: 'Librerías Gandhi del Sureste',
    domicilio: {
      calle: 'Calle 60',
      numero: '456',
      colonia: 'Itzimná',
      cp: '97100',
      municipio: 'Mérida',
      estado: 'Yucatán',
      pais: 'México'
    },
    contactos: {
      directorGeneral: { nombre: 'Luis Hernández Solís', email: 'luis.hernandez@gandhi.com' },
      directorComercial: { nombre: 'Patricia Núñez', email: 'patricia.nunez@gandhi.com' },
      directorEditorial: { nombre: 'Fernando Torres', email: 'fernando.torres@gandhi.com' },
      directorPromocion: { nombre: 'Sandra Ruiz', email: 'sandra.ruiz@gandhi.com' }
    },
    responsableStand: 'Patricia Núñez',
    giro: 'Librero',
    telefonoOficina: '999 222 3344',
    telefonoCelular: '999 555 6677',
    correoElectronico: 'sureste@gandhi.com',
    nombreAntepecho: 'GANDHI',
    numPersonasAtienden: 3,
    totalSellos: 1,
    cantidadLibrosAprox: 1500,
    cantidadTitulosAprox: 500,
    materiales: ['Libro', 'Audiolibro', 'Libros electrónicos'],
    tematicas: ['Literatura', 'Ciencias', 'Historia', 'Arte'],
    constanciaFiscalId: 'DOC-002'
  },
  {
    id: 'ED-003',
    cuentaId: 'CT-003',
    nombre: 'Ediciones La Nave',
    domicilio: {
      calle: 'Calle 41',
      numero: '789',
      colonia: 'Santa María',
      cp: '97203',
      municipio: 'Mérida',
      estado: 'Yucatán',
      pais: 'México'
    },
    contactos: {
      directorGeneral: { nombre: 'Diego Vargas Cano', email: 'diego.vargas@lanave.mx' },
      directorComercial: { nombre: 'Lucía Mendoza', email: 'lucia.mendoza@lanave.mx' },
      directorEditorial: { nombre: 'Andrés Castro', email: 'andres.castro@lanave.mx' },
      directorPromocion: { nombre: 'Camila Ortiz', email: 'camila.ortiz@lanave.mx' }
    },
    responsableStand: 'Lucía Mendoza',
    giro: 'Editor',
    telefonoOficina: '999 333 4455',
    telefonoCelular: '999 666 7788',
    correoElectronico: 'contacto@lanave.mx',
    nombreAntepecho: 'LA NAVE',
    numPersonasAtienden: 2,
    totalSellos: 2,
    cantidadLibrosAprox: 400,
    cantidadTitulosAprox: 120,
    materiales: ['Libro', 'Material didáctico'],
    tematicas: ['Infantil', 'Juvenil'],
    constanciaFiscalId: 'DOC-003'
  },
  {
    id: 'ED-004',
    cuentaId: 'CT-004',
    nombre: 'Distribuidora Península',
    domicilio: {
      calle: 'Av. Itzáes',
      numero: '321',
      colonia: 'Garcia Ginerés',
      cp: '97070',
      municipio: 'Mérida',
      estado: 'Yucatán',
      pais: 'México'
    },
    contactos: {
      directorGeneral: { nombre: 'Manuel Quiñones', email: 'manuel@peninsula.mx' },
      directorComercial: { nombre: 'Gabriela Pacheco', email: 'gabriela@peninsula.mx' },
      directorEditorial: { nombre: 'Ricardo Ek', email: 'ricardo@peninsula.mx' },
      directorPromocion: { nombre: 'Verónica Balam', email: 'veronica@peninsula.mx' }
    },
    responsableStand: 'Gabriela Pacheco',
    giro: 'Distribuidor',
    telefonoOficina: '999 444 5566',
    telefonoCelular: '999 777 8899',
    correoElectronico: 'contacto@peninsula.mx',
    nombreAntepecho: 'PENÍNSULA',
    numPersonasAtienden: 5,
    totalSellos: 4,
    cantidadLibrosAprox: 2200,
    cantidadTitulosAprox: 750,
    materiales: ['Libro', 'Revista', 'Libros electrónicos'],
    tematicas: ['Administración', 'Ciencias', 'Académica', 'Historia', 'Arte']
  },
  {
    id: 'ED-005',
    cuentaId: 'CT-005',
    nombre: 'Editorial Sureste Nueva',
    domicilio: {
      calle: 'Av. Reforma',
      numero: '555',
      colonia: 'Centro',
      cp: '97000',
      municipio: 'Mérida',
      estado: 'Yucatán',
      pais: 'México'
    },
    contactos: {
      directorGeneral: { nombre: 'María Solís Patrón', email: 'maria@suroeste.mx' },
      directorComercial: { nombre: 'Jorge Cabrera Cano', email: 'jorge@suroeste.mx' },
      directorEditorial: { nombre: 'Lucía Pérez Pech', email: 'lucia@suroeste.mx' },
      directorPromocion: { nombre: 'Roberto Ancona Mex', email: 'roberto@suroeste.mx' }
    },
    responsableStand: 'Lucía Pérez Pech',
    giro: 'Editor',
    telefonoOficina: '999 555 1212',
    telefonoCelular: '999 333 1212',
    correoElectronico: 'contacto@sureste.mx',
    nombreAntepecho: 'SURESTE',
    numPersonasAtienden: 3,
    totalSellos: 1,
    cantidadLibrosAprox: 350,
    cantidadTitulosAprox: 80,
    materiales: ['Libro'],
    tematicas: ['Literatura', 'Historia regional']
  }
];
