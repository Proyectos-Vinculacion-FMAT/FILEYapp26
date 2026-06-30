import { Injectable, signal, computed } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type RolUsuario = 'usuario' | 'administrador';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly rolSubject = new BehaviorSubject<RolUsuario>('usuario');
  readonly rol$ = this.rolSubject.asObservable();

  private readonly editorialActualSubject = new BehaviorSubject<string>('ED-005');
  readonly editorialActual$ = this.editorialActualSubject.asObservable();

  get rol(): RolUsuario {
    return this.rolSubject.value;
  }

  get editorialActual(): string {
    return this.editorialActualSubject.value;
  }

  switchRole(): void {
    const next: RolUsuario = this.rolSubject.value === 'usuario' ? 'administrador' : 'usuario';
    this.rolSubject.next(next);
  }

  setRol(rol: RolUsuario): void {
    this.rolSubject.next(rol);
  }

  setEditorialActual(id: string): void {
    this.editorialActualSubject.next(id);
  }
}
