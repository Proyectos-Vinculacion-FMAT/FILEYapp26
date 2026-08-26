"""
Enlazar de dentro de una feria hacia fuera.

Con ADR-0003 el sistema tiene **dos** urlconfs: el de dentro de una
feria (`ROOT_URLCONF`, que `django-tenants` prefija con `/f/<slug>/`) y
el de fuera (`PUBLIC_SCHEMA_URLCONF`). Durante una petición bajo
`/f/2027/…` el urlconf activo es el primero, así que un
`reverse("registros:acceso")` normal **falla**: ese nombre no existe
ahí.

No es un caso raro. La identidad es global —la cuenta no pertenece a
ninguna feria—, así que el acceso, el alta de cuenta y el cierre de
sesión viven fuera, y cualquier pantalla de feria que enlace al login
tiene que salir del prefijo.
"""

from django.conf import settings
from django.urls import reverse


def url_publica(nombre, *args, **kwargs) -> str:
    """`reverse()` contra el urlconf de fuera de toda feria.

    Devuelve `/acceso/`, nunca `/f/2027/acceso/`: si la URL del login
    llevara el prefijo de una feria, habría una dirección de acceso
    distinta por edición para una cuenta que es única en todo el
    sistema.
    """
    return reverse(
        nombre, urlconf=settings.PUBLIC_SCHEMA_URLCONF, args=args, kwargs=kwargs or None
    )
