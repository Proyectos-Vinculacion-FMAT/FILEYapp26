"""
El catálogo de convocatorias de una feria (`CU-FER-006`).

Es la portada de `/f/<slug>/` y la pantalla a la que lleva elegir feria.
Sustituye a la lista inventada que hasta el 2026-08-26 vivía en
`apps/registros/catalogo.py` y alimentaba `/convocatorias`: cuatro
tarjetas escritas a mano, con sus fechas, que no consultaban nada.

Está en `apps/convocatorias` y no en `apps/ferias` porque es contenido
de una edición. Tenerla en `ferias` obligaba a que la app global de
`FER` importara la app por feria, que es la dependencia al revés.
"""

from django.shortcuts import render

from apps.ferias.permisos import acceso_a

from .servicios import catalogo


def catalogo_de_la_feria(peticion):
    """Las convocatorias de esta feria, con lo que corresponda a quien mira.

    **No lleva decorador, y es deliberado.** Mirar qué hay convocado es
    lo que trae a la gente al sistema; exigir cuenta para eso rompe el
    embudo (CU-FER-006, A1). La sesión hará falta para registrarse, que
    es cuando hace falta una `Persona`.

    Es la misma pantalla para dos públicos: el participante ve un
    escaparate y el administrador un panel de control. Lo que decide
    cuál es ``acceso_a`` —la misma función que usan los decoradores de
    `apps/ferias/permisos.py`—, para que no haya dos respuestas
    distintas a "¿administra ésta?".
    """
    acceso = acceso_a(peticion)
    es_administrador = acceso is not None

    return render(
        peticion,
        "convocatorias/catalogo.html",
        {
            "feria": peticion.tenant,
            "convocatorias": catalogo.convocatorias_visibles(
                es_administrador=es_administrador
            ),
            "es_dueno": acceso is not None and acceso.es_dueno,
            # El chasis lo deduce solo dentro de una feria, pero la
            # pantalla también decide con esto qué texto enseña.
            "zona_admin": es_administrador,
        },
    )
