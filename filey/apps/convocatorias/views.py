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

from apps.ferias.permisos import tiene_alcance_de_dueno, ve_como_admin

from . import senales
from .servicios import catalogo


def catalogo_de_la_feria(peticion):
    """Las convocatorias de esta feria, con lo que corresponda a quien mira.

    **No lleva decorador, y es deliberado.** Mirar qué hay convocado es
    lo que trae a la gente al sistema; exigir cuenta para eso rompe el
    embudo (CU-FER-006, A1). La sesión hará falta para registrarse, que
    es cuando hace falta una `Persona`.

    Es la misma pantalla para dos públicos: el participante ve un
    escaparate y el administrador un panel de control. Lo que decide
    cuál son ``administra`` y ``tiene_alcance_de_dueno`` —las mismas
    funciones que usan los decoradores de `apps/ferias/permisos.py`—,
    para que no haya dos respuestas distintas a "¿administra ésta?".
    Cuentan también al operador de la plataforma, que no tiene fila en
    ``AdminFeria`` y aun así opera cualquier feria (`ADR-0005`).

    Cuál se pinta lo decide además **por qué puerta entró**: la misma
    persona puede coordinar el showfloor y tener su propia editorial, y
    entrando por el acceso de participante viene a lo segundo.
    """
    # `ve_como_admin` y no `administra`: quien administra esta feria y
    # además participa en ella puede entrar por el acceso de participante,
    # y entonces esta pantalla es su escaparate, no su panel.
    es_administrador = ve_como_admin(peticion)
    feria = peticion.tenant

    # Abrir el catálogo es salir de lo que se estuviera haciendo. Esta app
    # no sabe qué significa eso para cada módulo —ni puede saberlo, ver
    # `senales.py`—: lo anuncia y cada vertical decide. Hoy solo `EVT`
    # escucha, para descartar los adjuntos a medio subir.
    senales.se_abrio_el_catalogo.send(
        sender=None, peticion=peticion, persona=getattr(peticion, "user", None)
    )

    return render(
        peticion,
        "convocatorias/catalogo.html",
        {
            "feria": feria,
            # Entradas y no convocatorias: la tarjeta necesita saber si
            # alguien sirve este tipo y si quien mira ya se inscribió, y
            # ninguna de las dos cosas está en `Convocatoria` (`ADR-0006`).
            "entradas": catalogo.entradas_visibles(
                es_administrador=es_administrador,
                persona=peticion.user,
                feria=feria,
            ),
            "es_dueno": tiene_alcance_de_dueno(peticion),
            # El chasis lo deduce solo dentro de una feria, pero la
            # pantalla también decide con esto qué texto enseña.
            "zona_admin": es_administrador,
        },
    )
