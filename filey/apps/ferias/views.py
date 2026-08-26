"""
Vistas del Core Ferias.

Por ahora solo la portada de una feria, que es la ruta mínima que hace
falta para que `/f/<slug>/` exista y para poder comprobar de punta a
punta que el aislamiento por schema funciona. Las pantallas de verdad
(catálogo, alta de convocatorias, panel) llegan con CU-FER-002 y
CU-FER-005…009.
"""

from django.shortcuts import render

from apps.convocatorias.models import Convocatoria
from apps.registros.permisos import requiere_admin

from .models import AdminFeria


def portada(peticion):
    """Portada pública de una feria.

    No pide sesión: mirar qué hay convocado es lo que trae a la gente al
    sistema, y exigir cuenta para eso rompe el embudo (CU-FER-006, A1).
    Registrarse a una convocatoria sí la pedirá.

    Nótese que la consulta **no filtra por feria**. No es un descuido: la
    feria es el schema en el que el middleware dejó apuntando la
    conexión, así que esta misma línea devuelve cosas distintas según se
    llegue por `/f/2027/` o por `/f/2028/` (ADR-0003).
    """
    convocatorias = Convocatoria.objects.exclude(
        estado=Convocatoria.Estado.BORRADOR
    )
    return render(
        peticion,
        "ferias/portada.html",
        {"feria": peticion.tenant, "convocatorias": convocatorias},
    )


@requiere_admin
def mis_ferias(peticion):
    """Las ferias que administro, para entrar a una (`CU-FER-002`).

    Sustituye a la pantalla de selección de módulo de CU-REG-006. El
    cambio no es cosmético: antes se elegía **módulo** sobre un sistema
    de una sola feria; ahora se elige **feria**, y el módulo se elige ya
    dentro de ella.

    Vive fuera de `/f/<slug>/` a propósito: es la pantalla que se ve
    justo cuando todavía no se ha elegido feria, así que corre sobre el
    schema `public` y es la única consulta del sistema que cruza
    ediciones legítimamente — puede hacerlo porque `AdminFeria` es
    global (ADR-0003).
    """
    accesos = (
        AdminFeria.objects.filter(persona=peticion.user)
        .select_related("feria")
        .exclude(feria__schema_name="public")
        .order_by("-feria__creada_en")
    )
    return render(
        peticion,
        "ferias/mis_ferias.html",
        {
            "accesos": accesos,
            # `zona_admin` le dice al layout compartido que pinte la
            # variante administrativa (ver layouts/panel.html).
            "zona_admin": True,
        },
    )
