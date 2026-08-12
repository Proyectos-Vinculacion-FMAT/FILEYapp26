"""
Control de acceso a las pantallas — el contrato con los demás módulos.

`registros` es la base de identidad del sistema: EVT, TAL, STD y VIS no
implementan su propia autenticación, **importan estos decoradores**. Es
la única forma en que un módulo de dominio depende de `registros`, y va
en una sola dirección (ver la regla de dependencias en CLAUDE.md).

Cómo se usa desde un módulo nuevo::

    from apps.registros.models import NivelPermiso
    from apps.registros.permisos import requiere_modulo, requiere_participante

    @requiere_participante
    def convocatoria(peticion): ...          # zona del participante

    @requiere_modulo("EVT")                  # basta con poder leer
    def panel(peticion): ...

    @requiere_modulo("EVT", NivelPermiso.EDICION)
    def dictaminar(peticion, propuesta_id): ...

Reglas que imponen estos decoradores, iguales para todos los módulos:

- Sin sesión → se va a la pantalla de acceso que corresponde (la
  pública o la administrativa), no a un 403 sin salida.
- Con sesión pero sin el permiso → 403. Es un techo real, no una
  invitación a volver a intentarlo con otra cuenta.
- Quien tiene el rol ``*`` administra todos los módulos, y ``edicion``
  cubre lo que solo pide ``lectura`` (ver ``Persona.puede_administrar``).
"""

import functools

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import NivelPermiso


def requiere_participante(vista):
    """Zona del participante: basta con tener sesión iniciada."""

    @functools.wraps(vista)
    def envoltura(peticion, *args, **kwargs):
        if not peticion.user.is_authenticated:
            return redirect("registros:acceso")
        return vista(peticion, *args, **kwargs)

    return envoltura


def requiere_admin(vista):
    """Panel administrativo: sesión con al menos un permiso de módulo."""

    @functools.wraps(vista)
    def envoltura(peticion, *args, **kwargs):
        if not peticion.user.is_authenticated:
            return redirect("registros:admin_acceso")
        if not peticion.user.es_administrativa:
            # Tiene sesión de participante e intenta entrar al panel:
            # no es un problema de identidad, es falta de permiso.
            raise PermissionDenied(
                "Tu cuenta no tiene permisos administrativos."
            )
        return vista(peticion, *args, **kwargs)

    return envoltura


def requiere_modulo(modulo, nivel=NivelPermiso.LECTURA):
    """Panel de un módulo concreto (EVT, TAL, STD, VIS).

    ``modulo`` es la clave de ``Modulo`` ("EVT", "TAL", …) y ``nivel``
    el mínimo exigido para esa pantalla.
    """

    def decorador(vista):
        @functools.wraps(vista)
        @requiere_admin
        def envoltura(peticion, *args, **kwargs):
            if not peticion.user.puede_administrar(modulo, nivel):
                raise PermissionDenied(
                    f"Tu cuenta no tiene permiso de {NivelPermiso(nivel).label} "
                    f"sobre el módulo {modulo}."
                )
            return vista(peticion, *args, **kwargs)

        return envoltura

    return decorador
