import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { AuthService, RolUsuario } from '../../services/auth.service';
import { map, take } from 'rxjs/operators';

export function roleGuard(rolRequerido: RolUsuario): CanActivateFn {
  return (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);
    if (authService.rol === rolRequerido) return true;
    router.navigate(['/']);
    return false;
  };
}
