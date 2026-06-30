export interface Cuenta {
  id: string;
  correo: string;
  rol: 'usuario' | 'administrador';
  estado: 'activa' | 'inactiva';
  fechaRegistro: Date;
}
