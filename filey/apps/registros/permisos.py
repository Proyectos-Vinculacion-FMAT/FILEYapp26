"""
Control de acceso a las pantallas — el contrato con los demás módulos.

`registros` es la base de identidad del sistema: EVT, TAL, STD y VIS no
implementan su propia autenticación, **importan estos decoradores**. Es
la única forma en que un módulo de dominio depende de `registros`, y va
en una sola dirección (ver la regla de dependencias en CLAUDE.md).

Cómo se usa desde un módulo nuevo::

    from apps.registros.permisos import requiere_participante
    from apps.ferias.permisos import requiere_admin_feria, requiere_dueno_feria

    @requiere_participante
    def convocatoria(peticion): ...      # zona del participante

    @requiere_admin_feria                # dentro de /f/<slug>/
    def panel(peticion): ...

    @requiere_dueno_feria                # solo el dueño de la feria
    def abrir_convocatoria(peticion, convocatoria_id): ...

Reglas que imponen estos decoradores, iguales para todos los módulos:

- Sin sesión → se va a la pantalla de acceso que corresponde (la
  pública o la administrativa), no a un 403 sin salida.
- Con sesión pero sin el permiso → 403. Es un techo real, no una
  invitación a volver a intentarlo con otra cuenta.

> [!note] Aquí ya no hay permisos por módulo
> Hasta el 2026-08-25 existía ``requiere_modulo("EVT", nivel)``, que
> leía ``RolPermiso``. El acceso se otorga ahora **por feria** y sin
> niveles (ADR-0004), y quien decide es ``apps/ferias/permisos.py``:
> necesita saber **en qué feria** se está, y eso solo existe dentro de
> ``/f/<slug>/``.
"""

import functools

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from comun.urls import url_publica

from .services import sesion


def requiere_participante(vista):
    """Zona del participante: basta con tener sesión iniciada.

    Sirve **a los dos lados** de la frontera de `django-tenants`, y por
    eso el destino se resuelve con ``url_publica`` y no con un
    ``reverse`` normal: dentro de `/f/<slug>/` el urlconf activo es otro
    y el nombre ``registros:acceso`` no existe ahí. Fuera de una feria da
    exactamente la misma URL, así que no cambia nada para quien ya lo
    usaba. Es el mismo criterio que `apps/ferias/permisos.py`.
    """

    @functools.wraps(vista)
    def envoltura(peticion, *args, **kwargs):
        if not peticion.user.is_authenticated:
            return redirect(url_publica("registros:acceso"))
        return vista(peticion, *args, **kwargs)

    return envoltura


def requiere_admin(vista):
    """Zona administrativa **fuera** de una feria concreta.

    Sirve para lo que hay antes de elegir feria: la lista de "mis
    ferias" (CU-FER-002). Dentro de una feria no basta —administrar
    *alguna* no es administrar *ésta*— y ahí manda
    ``apps/ferias/permisos.py``.
    """

    @functools.wraps(vista)
    def envoltura(peticion, *args, **kwargs):
        if not peticion.user.is_authenticated:
            return redirect("registros:admin_acceso")
        if not peticion.user.es_administrativa:
            # Tiene sesión de participante e intenta entrar al panel:
            # no es un problema de identidad, es falta de permiso.
            raise PermissionDenied("Tu cuenta no administra ninguna feria.")
        # Entrar aquí **es** elegir administración: si venía mirando como
        # participante, la sesión vuelve a esa cara para que el chasis no
        # diga una cosa y la pantalla otra.
        sesion.asegurar_contexto_admin(peticion)
        return vista(peticion, *args, **kwargs)

    return envoltura
