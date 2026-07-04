import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ParametrosSistema } from '../data/models';
import { MOCK_PARAMETROS } from '../data/mock';

@Injectable({ providedIn: 'root' })
export class ParametrosService {
  private readonly parametrosSubject = new BehaviorSubject<ParametrosSistema>(MOCK_PARAMETROS);
  readonly parametros$ = this.parametrosSubject.asObservable();

  resetear(): void {
    this.parametrosSubject.next({ ...MOCK_PARAMETROS });
  }

  get parametros(): ParametrosSistema {
    return this.parametrosSubject.value;
  }

  actualizar(p: Partial<ParametrosSistema>): void {
    this.parametrosSubject.next({ ...this.parametrosSubject.value, ...p });
  }
}
