"""
Enlazar de una plantilla hacia fuera de la feria.

Es la versión para plantillas de ``comun/urls.py::url_publica``, y hace
falta por lo mismo: dentro de ``/f/<slug>/`` el urlconf activo es el de
la feria, así que ``{% url 'registros:salir' %}`` **revienta con
NoReverseMatch** — ese nombre vive en el urlconf público.

No es un caso raro ni de una pantalla suelta: la barra superior tiene un
botón de cerrar sesión, y la barra sale en todas.
"""

from django import template

from comun.urls import url_publica as _url_publica

register = template.Library()


@register.simple_tag(name="url_publica")
def url_publica(nombre, *args, **kwargs):
    """`{% url_publica 'registros:salir' %}` → `/salir/`.

    Nunca `/f/2027/salir/`: la cuenta es única en todo el sistema, así
    que su acceso y su cierre de sesión no llevan prefijo de edición.
    """
    return _url_publica(nombre, *args, **kwargs)
