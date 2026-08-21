"""
Plomería de HTMX.

Son cuatro funciones para no repetir cabeceras a mano en cada vista.
Todas las pantallas del monolito siguen la misma regla: **funcionan sin
JavaScript**. HTMX solo mejora la experiencia (no recargar la página,
mostrar el error donde ocurrió), así que cada vista responde de dos
formas y estas ayudas son el interruptor entre ambas.
"""

import json

from django.http import HttpResponse
from django.shortcuts import redirect


def es_htmx(peticion) -> bool:
    """True si la petición la hizo HTMX y no una navegación normal."""
    return peticion.headers.get("HX-Request") == "true"


def redirigir(peticion, destino, *args, **kwargs):
    """Navega a otra página, venga la petición de HTMX o del navegador.

    HTMX no sigue un 302: reemplazaría el fragmento con la página
    entera. Se le indica el destino con ``HX-Redirect`` y él navega.
    """
    respuesta = redirect(destino, *args, **kwargs)
    if es_htmx(peticion):
        redireccion = HttpResponse(status=204)
        redireccion["HX-Redirect"] = respuesta["Location"]
        return redireccion
    return respuesta


def disparar(respuesta: HttpResponse, evento: str, detalle=None) -> HttpResponse:
    """Adjunta un evento del navegador a la respuesta (``HX-Trigger``).

    Es el canal para avisarle a Alpine de algo que solo el servidor
    sabe —"el código estuvo mal", "hay un cool-down nuevo"— sin tener
    que volver a renderizar el componente y perder su estado.
    """
    previos = json.loads(respuesta.get("HX-Trigger") or "{}")
    previos[evento] = detalle if detalle is not None else {}
    respuesta["HX-Trigger"] = json.dumps(previos)
    return respuesta


def reintentar_en(respuesta: HttpResponse, segundos: int) -> HttpResponse:
    """Cabecera estándar para las esperas (cool-down, lockout, 429)."""
    respuesta["Retry-After"] = str(segundos)
    return respuesta
