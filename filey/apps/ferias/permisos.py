"""
Permisos **dentro** de una feria (`ADR-0004`).

Aquí vive la comprobación que el middleware no puede hacer.
`TenantSubfolderMiddleware` va primero en la pila —tiene que fijar el
`search_path` antes de que nada toque la base— y eso es **antes** de
`AuthenticationMiddleware`, así que cuando corre todavía no hay
`request.user`. ADR-0003 describía el middleware como el sitio de esta
comprobación; en la práctica es este archivo.

Que estén separados no es solo una limitación técnica: hay pantallas de
feria que **son públicas**. El catálogo de convocatorias se consulta sin
cuenta a propósito (CU-FER-006, A1) — pedir sesión para mirar qué hay
convocado rompe el embudo—, así que resolver la feria y exigir permiso
tienen que ser dos decisiones distintas.

Dos niveles, y solo dos:

- ``requiere_admin_feria`` — administra **esta** feria. Da acceso a
  todo su contenido.
- ``requiere_dueno_feria`` — además es su dueño. Reservado a dar de
  alta y retirar administradores (CU-FER-003, CU-FER-004) y a
  administrar las convocatorias (CU-FER-005, 007, 008, 009).

No hay nivel de solo lectura: ADR-0004 lo elimina a sabiendas.
"""

import functools

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from comun.urls import url_publica

from .models import AdminFeria


def acceso_a(peticion):
    """La fila `AdminFeria` de quien pide sobre la feria de la URL, o None.

    La feria sale de ``peticion.tenant``, que puso el middleware al
    resolver el prefijo. No se recibe por parámetro ni se re-resuelve el
    slug: si esas dos fuentes divergieran, el permiso se comprobaría
    contra una feria y los datos saldrían de otra.

    Es pública —y no privada, como fue hasta el 2026-08-26— porque la
    usan también las pantallas que **no** exigen permiso pero enseñan
    cosas distintas según quién mire: el catálogo de convocatorias, que
    es público y sin embargo le muestra los borradores a quien
    administra la feria (CU-FER-006). Que haya una sola respuesta a
    "¿administra ésta?" es lo que impide que la pantalla y el decorador
    discrepen.

    Por eso también tolera a quien no ha iniciado sesión: esas pantallas
    la llaman antes de saber si hay alguien detrás.
    """
    feria = getattr(peticion, "tenant", None)
    if feria is None or feria.es_la_de_sistema:
        return None
    usuario = getattr(peticion, "user", None)
    if usuario is None or not usuario.is_authenticated:
        return None
    return AdminFeria.objects.filter(feria=feria, persona=usuario).first()


def requiere_admin_feria(vista):
    """Panel de una feria: hay que administrar **ésta**."""

    @functools.wraps(vista)
    def envoltura(peticion, *args, **kwargs):
        if not peticion.user.is_authenticated:
            return redirect(url_publica("registros:admin_acceso"))
        if acceso_a(peticion) is None:
            # Administrar otra feria no da acceso a ésta. Se dice sin
            # rodeos: quien llega aquí ya demostró su identidad, así que
            # el mensaje no revela nada que no sepa.
            raise PermissionDenied("Tu cuenta no administra esta feria.")
        return vista(peticion, *args, **kwargs)

    return envoltura


def requiere_dueno_feria(vista):
    """Solo el dueño de la feria (enmienda del 2026-08-25 a ADR-0004)."""

    @functools.wraps(vista)
    def envoltura(peticion, *args, **kwargs):
        if not peticion.user.is_authenticated:
            return redirect(url_publica("registros:admin_acceso"))
        acceso = acceso_a(peticion)
        if acceso is None:
            raise PermissionDenied("Tu cuenta no administra esta feria.")
        if not acceso.es_dueno:
            raise PermissionDenied(
                "Solo quien es dueño de esta feria puede hacer esto."
            )
        return vista(peticion, *args, **kwargs)

    return envoltura
