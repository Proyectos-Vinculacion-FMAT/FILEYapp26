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


def url_absoluta(ruta: str) -> str:
    """La misma ruta con el dominio delante, para meterla en un correo.

    Un `/f/2027/...` suelto no es una dirección dentro de un cliente de
    correo: no hay página desde la que resolverlo. `URL_BASE` es el
    ajuste que existe justo para esto.
    """
    return f"{settings.URL_BASE}{ruta}"


def url_de_esta_feria(nombre, *args, **kwargs) -> str:
    """La dirección completa de una pantalla **de la edición actual**.

    Tres piezas, y ninguna sola basta: el dominio (`URL_BASE`), el
    prefijo de la edición —que no vive en ninguna columna, porque la
    feria es el schema (`ADR-0003`)— y la ruta dentro del urlconf de
    feria.

    Es para los correos. Dentro de una plantilla servida basta
    ``{% url %}``, que ya sale prefijado.

    :raises RuntimeError: llamada desde `public`, donde no hay edición
        que prefijar y el enlace saldría mudo.
    """
    from apps.ferias.models import Feria

    feria = Feria.de_la_conexion()
    if feria is None:
        raise RuntimeError(
            f"«{nombre}» es una pantalla de una feria y no estamos en ninguna."
        )
    ruta = reverse(
        nombre, urlconf=settings.ROOT_URLCONF, args=args, kwargs=kwargs or None
    )
    return url_absoluta(f"{feria.url.rstrip('/')}{ruta}")
