export type EstadoStand = 'Disponible' | 'Reservado' | 'Ocupado';

export interface Stand {
  id: string;
  eventoId: string;
  clave: string;
  posX: number;
  posY: number;
  ancho: number;
  largo: number;
  metrosCuadrados: number;
  estado: EstadoStand;
  incluye: string;
  precio?: number;
  zona?: string;
}
