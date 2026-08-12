"""
Filtros de presentación del nombre de una persona.

Están aquí —y no repetidos en cada plantilla— porque la barra superior
la comparten todas las pantallas del sistema, incluidas las que aún no
existen: cuando EVT o STD extiendan `layouts/panel.html`, el avatar y el
saludo salen ya resueltos.
"""

from django import template

register = template.Library()


@register.filter
def iniciales(nombre_completo: str) -> str:
    """Hasta dos iniciales para el avatar de la barra superior."""
    partes = [p for p in (nombre_completo or "").split() if p]
    return "".join(p[0].upper() for p in partes[:2])


@register.filter
def primer_nombre(nombre_completo: str) -> str:
    """Solo el primer nombre, para saludar sin recitar el nombre entero."""
    partes = (nombre_completo or "").split()
    return partes[0] if partes else ""
