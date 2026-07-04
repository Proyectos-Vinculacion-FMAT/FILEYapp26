import { Documento } from './documento.model';
import { SelloEditorial } from './sello.model';

export type EstadoAplicacion = 'pendiente' | 'aceptada' | 'rechazada' | 'cambios_solicitados';

export interface Aplicacion {
  id: string;
  editorialId: string;
  eventoId: string;
  estado: EstadoAplicacion;
  fechaEnvio: Date;
  fechaRevision?: Date;
  revisadoPor?: string;
  motivoPeticion?: string;
  sellos: SelloEditorial[];
  documentos: Documento[];
}
