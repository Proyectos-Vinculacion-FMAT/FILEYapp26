"""
Vistas del Core Ferias que viven **fuera** de una feria.

Las dos son la misma pregunta hecha por dos públicos: *¿a qué edición
entro?*. El participante elige entre las ferias abiertas (CU-FER-010) y
el administrador entre las que administra (CU-FER-002).

Corren sobre el schema `public` a propósito: son lo que se ve **antes**
de haber elegido feria, así que no pueden colgar de `/f/<slug>/`. Son
también las únicas consultas del sistema que cruzan ediciones, y pueden
hacerlo porque `Feria` y `AdminFeria` son globales (`ADR-0003`).

Lo que pasa **dentro** de una feria no está aquí: el catálogo de
convocatorias lo sirve `apps/convocatorias`.
"""

from django.shortcuts import redirect, render

from apps.registros.permisos import requiere_admin, requiere_participante

from .servicios import seleccion


@requiere_participante
def elegir_feria(peticion):
    """En qué edición quiero participar (`CU-FER-010`).

    Con **una sola** feria abierta la pantalla no se enseña: se entra
    directo. Preguntar entre una opción no es elegir, es un clic de
    peaje —y hoy, con una sola edición viva, es el caso normal—.

    El salto vive aquí y no en el destino del acceso para que llegar a
    esta dirección a mano se comporte igual que acabar de identificarse.
    La puerta de vuelta, cuando aparece la segunda feria, la pone la
    barra superior (`templatetags/chasis.py`).
    """
    ferias = seleccion.ferias_para_participante()

    if len(ferias) == 1:
        return redirect(ferias[0].url)

    return render(peticion, "ferias/elegir_feria.html", {"ferias": ferias})


@requiere_admin
def mis_ferias(peticion):
    """Las ferias que administro, para entrar a una (`CU-FER-002`).

    Sustituye a la pantalla de selección de módulo de CU-REG-006. El
    cambio no es cosmético: antes se elegía **módulo** sobre un sistema
    de una sola feria; ahora se elige **feria**, y el módulo se elige ya
    dentro de ella.

    Mismo salto que en el lado del participante, y por el mismo motivo.
    Lo que no se comparte es el filtro: aquí **no** se descartan las
    ferias inactivas —montar una edición en preparación o consultar una
    archivada son cosas que un administrador hace—; ver
    ``servicios/seleccion.py``.
    """
    accesos = seleccion.ferias_administradas(peticion.user)

    if len(accesos) == 1:
        return redirect(accesos[0].feria.url)

    return render(
        peticion,
        "ferias/mis_ferias.html",
        {
            "accesos": accesos,
            # `zona_admin` le dice al chasis compartido que pinte la
            # variante administrativa. Fuera de una feria hace falta
            # decírselo: no hay `tenant` contra el que comprobarlo.
            "zona_admin": True,
        },
    )
