import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, map } from 'rxjs';
import { Editorial } from '../data/models';
import { MOCK_EDITORIALES } from '../data/mock';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class EditorialService {
  private readonly authService = inject(AuthService);
  private readonly editorialesSubject = new BehaviorSubject<Editorial[]>(MOCK_EDITORIALES);
  readonly editoriales$ = this.editorialesSubject.asObservable();

  get editoriales(): Editorial[] {
    return this.editorialesSubject.value;
  }

  getById(id: string): Editorial | undefined {
    return this.editoriales.find(e => e.id === id);
  }

  getEditorialActual(): Observable<Editorial | undefined> {
    return this.authService.editorialActual$.pipe(
      map(id => this.getById(id))
    );
  }

  actualizar(editorial: Editorial): void {
    const list = this.editorialesSubject.value.map(e => e.id === editorial.id ? editorial : e);
    this.editorialesSubject.next(list);
  }

  crear(editorial: Editorial): void {
    this.editorialesSubject.next([...this.editorialesSubject.value, editorial]);
  }
}
