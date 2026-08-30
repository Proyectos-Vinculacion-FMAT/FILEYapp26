"""
La barra de pasos del expositor.

Es chasis, como `{% topbar %}` y `{% barra_lateral %}`: la pantalla no
enumera los pasos ni resuelve sus enlaces, solo dice en cuál está. Que
los cinco salgan de un sitio es lo que impide que la solicitud diga que
hay cuatro y el carrito que hay seis.

Los pasos los define `views.PASOS`, que es también de donde sale el
ruteo (`views.paso_actual`). Dos listas se habrían separado al primer
paso nuevo, y la barra acabaría marcando un paso distinto del que se
está viendo.
"""

from django import template
from django.urls import NoReverseMatch, reverse

from ..views import PASOS

register = template.Library()


@register.inclusion_tag("stands/parciales/pasos.html", takes_context=True)
def barra_de_pasos(context, paso: str):
    """Los cinco pasos, con el actual marcado y los ya hechos enlazados.

    :param paso: la clave del paso que se está viendo (`PASOS`).

    **Solo se enlaza hacia atrás.** Un enlace a un paso que todavía no
    toca sería una puerta que se abre a un 404 —o peor, a un mapa que no
    se puede usar todavía—; hacia atrás sí, porque volver a leer la
    solicitud enviada es legítimo en cualquier momento.
    """
    convocatoria = context.get("convocatoria")
    claves = [clave for clave, _, _ in PASOS]
    actual = claves.index(paso) if paso in claves else 0

    entradas = []
    for indice, (clave, etiqueta, ruta) in enumerate(PASOS):
        url = None
        if ruta and indice <= actual and convocatoria is not None:
            try:
                url = reverse(ruta, args=[convocatoria.pk])
            except NoReverseMatch:
                url = None
        entradas.append(
            {
                "numero": indice + 1,
                "etiqueta": etiqueta,
                "url": url if indice != actual else None,
                "hecho": indice < actual,
                "actual": indice == actual,
            }
        )
    return {"pasos": entradas}
