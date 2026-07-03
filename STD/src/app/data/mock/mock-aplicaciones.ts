import { Aplicacion, SelloEditorial, Documento } from '../models';

const sellosED001: SelloEditorial[] = [
  { id: 'SL-001', editorialId: 'ED-001', nombre: 'Porrúa', cartaRepresentacionId: undefined },
  { id: 'SL-002', editorialId: 'ED-001', nombre: 'Nostra Ediciones', cartaRepresentacionId: 'DOC-CR-001' },
  { id: 'SL-003', editorialId: 'ED-001', nombre: 'Ediciones B', cartaRepresentacionId: 'DOC-CR-002' }
];

const sellosED002: SelloEditorial[] = [
  { id: 'SL-004', editorialId: 'ED-002', nombre: 'Gandhi' }
];

const sellosED003: SelloEditorial[] = [
  { id: 'SL-005', editorialId: 'ED-003', nombre: 'La Nave' },
  { id: 'SL-006', editorialId: 'ED-003', nombre: 'Pequeño Navegante', cartaRepresentacionId: 'DOC-CR-003' }
];

const sellosED004: SelloEditorial[] = [
  { id: 'SL-007', editorialId: 'ED-004', nombre: 'Península' },
  { id: 'SL-008', editorialId: 'ED-004', nombre: 'Sur Académico', cartaRepresentacionId: 'DOC-CR-004' },
  { id: 'SL-009', editorialId: 'ED-004', nombre: 'Lectores del Mayab' },
  { id: 'SL-010', editorialId: 'ED-004', nombre: 'Letras del Sur' }
];

const docsED001: Documento[] = [
  { id: 'DOC-001', tipo: 'constancia_fiscal', nombreArchivo: 'CSF_Porrúa.pdf', url: '#', fechaCarga: new Date('2026-04-10') },
  { id: 'DOC-CR-001', tipo: 'carta_representacion', nombreArchivo: 'Carta_Nostra.pdf', url: '#', fechaCarga: new Date('2026-04-10') },
  { id: 'DOC-CR-002', tipo: 'carta_representacion', nombreArchivo: 'Carta_EdicionesB.pdf', url: '#', fechaCarga: new Date('2026-04-10') },
  { id: 'DOC-LT-001', tipo: 'lista_titulos', nombreArchivo: 'Catalogo_Porrúa.pdf', url: '#', fechaCarga: new Date('2026-04-10') }
];

const docsED002: Documento[] = [
  { id: 'DOC-002', tipo: 'constancia_fiscal', nombreArchivo: 'CSF_Gandhi.pdf', url: '#', fechaCarga: new Date('2026-04-12') },
  { id: 'DOC-LT-002', tipo: 'lista_titulos', nombreArchivo: 'Catalogo_Gandhi.pdf', url: '#', fechaCarga: new Date('2026-04-12') }
];

const docsED003: Documento[] = [
  { id: 'DOC-003', tipo: 'constancia_fiscal', nombreArchivo: 'CSF_LaNave.pdf', url: '#', fechaCarga: new Date('2026-05-01') },
  { id: 'DOC-CR-003', tipo: 'carta_representacion', nombreArchivo: 'Carta_PequeñoNavegante.pdf', url: '#', fechaCarga: new Date('2026-05-01') },
  { id: 'DOC-LT-003', tipo: 'lista_titulos', nombreArchivo: 'Catalogo_LaNave.pdf', url: '#', fechaCarga: new Date('2026-05-01') }
];

const docsED004: Documento[] = [
  { id: 'DOC-CR-004', tipo: 'carta_representacion', nombreArchivo: 'Carta_SurAcademico.pdf', url: '#', fechaCarga: new Date('2026-05-15') }
];

export const MOCK_APLICACIONES: Aplicacion[] = [
  {
    id: 'AP-001',
    editorialId: 'ED-001',
    eventoId: 'EVT-001',
    estado: 'aceptada',
    fechaEnvio: new Date('2026-04-10'),
    fechaRevision: new Date('2026-04-15'),
    revisadoPor: 'Administrador',
    sellos: sellosED001,
    documentos: docsED001
  },
  {
    id: 'AP-002',
    editorialId: 'ED-002',
    eventoId: 'EVT-001',
    estado: 'pendiente',
    fechaEnvio: new Date('2026-04-12'),
    sellos: sellosED002,
    documentos: docsED002
  },
  {
    id: 'AP-003',
    editorialId: 'ED-003',
    eventoId: 'EVT-001',
    estado: 'cambios_solicitados',
    fechaEnvio: new Date('2026-05-01'),
    fechaRevision: new Date('2026-05-05'),
    revisadoPor: 'Administrador',
    motivoPeticion: 'Falta presentar la carta de representación del sello "Pequeño Navegante" firmada por el representante legal. Por favor adjuntar el documento en formato PDF.',
    sellos: sellosED003,
    documentos: docsED003
  },
  {
    id: 'AP-004',
    editorialId: 'ED-004',
    eventoId: 'EVT-001',
    estado: 'rechazada',
    fechaEnvio: new Date('2026-04-20'),
    fechaRevision: new Date('2026-04-25'),
    revisadoPor: 'Administrador',
    motivoPeticion: 'No se cumple con el giro comercial requerido para FILEY 2026.',
    sellos: sellosED004,
    documentos: docsED004
  },
  {
    id: 'AP-005',
    editorialId: 'ED-002',
    eventoId: 'EVT-001',
    estado: 'pendiente',
    fechaEnvio: new Date('2026-05-20'),
    sellos: sellosED002,
    documentos: docsED002
  }
];
