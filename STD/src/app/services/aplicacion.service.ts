import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, map } from 'rxjs';
import { Aplicacion, EstadoAplicacion, SelloEditorial, Documento } from '../data/models';
import { MOCK_APLICACIONES } from '../data/mock';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class AplicacionService {
  private readonly authService = inject(AuthService);
  private readonly aplicacionesSubject = new BehaviorSubject<Aplicacion[]>(MOCK_APLICACIONES);

  readonly aplicaciones$ = this.aplicacionesSubject.asObservable();

  resetear(): void {
    this.aplicacionesSubject.next([...MOCK_APLICACIONES]);
  }

  get aplicaciones(): Aplicacion[] {
    return this.aplicacionesSubject.value;
  }

  getAplicacionActual() {
    const editorialId = this.authService.editorialActual;
    return this.aplicaciones.find(a => a.editorialId === editorialId);
  }

  getAplicacionesByEditorial$(editorialId: string) {
    return this.aplicaciones$.pipe(
      map(list => list.find(a => a.editorialId === editorialId))
    );
  }

  getById(id: string): Aplicacion | undefined {
    return this.aplicaciones.find(a => a.id === id);
  }

  getByEditorial(editorialId: string): Aplicacion | undefined {
    return this.aplicaciones.find(a => a.editorialId === editorialId);
  }

  filtrar(estado?: EstadoAplicacion, busqueda?: string): Aplicacion[] {
    let list = this.aplicacionesSubject.value;
    if (estado) {
      list = list.filter(a => a.estado === estado);
    }
    if (busqueda && busqueda.trim().length > 0) {
      const term = busqueda.toLowerCase();
      list = list.filter(a => {
        const editorial = this.editorialesCache.find(e => e.id === a.editorialId);
        return editorial?.nombre.toLowerCase().includes(term);
      });
    }
    return list;
  }

  private readonly editorialesCache: { id: string; nombre: string }[] = [];

  setEditorialesCache(list: { id: string; nombre: string }[]): void {
    this.editorialesCache.splice(0, this.editorialesCache.length, ...list);
  }

  crear(editorialId: string, eventoId: string, sellos: SelloEditorial[], documentos: Documento[]): Aplicacion {
    const id = `AP-${Date.now()}`;
    const nueva: Aplicacion = {
      id,
      editorialId,
      eventoId,
      estado: 'pendiente',
      fechaEnvio: new Date(),
      sellos,
      documentos
    };
    this.aplicacionesSubject.next([...this.aplicacionesSubject.value, nueva]);
    return nueva;
  }

  actualizar(id: string, cambios: Partial<Aplicacion>): void {
    const list = this.aplicacionesSubject.value.map(a => a.id === id ? { ...a, ...cambios } : a);
    this.aplicacionesSubject.next(list);
  }

  reenviar(id: string, sellos: SelloEditorial[], documentos: Documento[]): Aplicacion | undefined {
    const actual = this.getById(id);
    if (!actual) return undefined;
    const actualizada: Aplicacion = {
      ...actual,
      estado: 'pendiente',
      fechaEnvio: new Date(),
      sellos,
      documentos,
      motivoPeticion: undefined
    };
    this.aplicacionesSubject.next(
      this.aplicacionesSubject.value.map(a => a.id === id ? actualizada : a)
    );
    return actualizada;
  }

  aceptar(id: string): void {
    this.actualizar(id, {
      estado: 'aceptada',
      fechaRevision: new Date(),
      revisadoPor: 'Administrador'
    });
  }

  rechazar(id: string, motivo?: string): void {
    this.actualizar(id, {
      estado: 'rechazada',
      fechaRevision: new Date(),
      revisadoPor: 'Administrador',
      motivoPeticion: motivo
    });
  }

  solicitarCambios(id: string, motivo: string): void {
    this.actualizar(id, {
      estado: 'cambios_solicitados',
      fechaRevision: new Date(),
      revisadoPor: 'Administrador',
      motivoPeticion: motivo
    });
  }
}
