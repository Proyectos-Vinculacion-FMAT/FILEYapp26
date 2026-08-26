"""
Qué ferias le corresponde ver a cada quien.

Son las dos únicas consultas del sistema que **cruzan ediciones**, y
pueden hacerlo porque `Feria` y `AdminFeria` viven en `public`
(`ADR-0003`). Todo lo demás pregunta dentro de una feria y no puede
alcanzar a otra.

Están en un servicio y no en la vista porque la regla de qué ferias son
visibles es de negocio: se tiene que poder responder desde un comando de
`manage.py` sin pasar por HTTP. El salto de la pantalla cuando solo hay
una feria sí es de la vista — eso es traducción a HTTP, no negocio.
"""

from django.db.models import QuerySet

from ..models import AdminFeria, Feria


def ferias_para_participante() -> QuerySet[Feria]:
    """Las ediciones en las que un participante puede participar hoy.

    Solo las ``activa``. Una feria ``en_preparacion`` todavía no tiene
    revisadas sus convocatorias —es el mismo motivo por el que una
    convocatoria en ``borrador`` no se enseña (CU-FER-006)— y una
    ``archivada`` ya no admite a nadie.

    .. warning:: Una feria nace ``en_preparacion``

       Ni ``alta_feria`` ni el alta desde ``/django-admin/`` la activan,
       así que una edición recién creada **no le aparece al
       participante** hasta que alguien la pase a ``activa``. Es
       deliberado, pero es un paso operativo que hay que recordar.

    Se consulta ``reales`` y no ``objects``: con ``objects`` sale la fila
    de sistema, que no es una feria (ver ``Feria``).
    """
    return Feria.reales.filter(estado=Feria.Estado.ACTIVA)


def ferias_administradas(persona) -> QuerySet[AdminFeria]:
    """Los accesos de esta persona, uno por feria que administra.

    Devuelve ``AdminFeria`` y no ``Feria`` a propósito: la pantalla
    necesita saber, además de qué feria es, **si es su dueña** — que es
    lo que decide si puede dar de alta administradores y administrar
    convocatorias (`ADR-0004` y su enmienda del 2026-08-25).

    **No se filtra por estado**, al revés que la lista del participante.
    Quien administra una edición tiene motivos para entrar a una que
    está en preparación (montarla) o archivada (consultarla): lo que
    cambia entonces es lo que puede hacer dentro, no si la ve.
    """
    return (
        AdminFeria.objects.filter(persona=persona)
        .select_related("feria")
        .exclude(feria__schema_name="public")
        .order_by("-feria__creada_en")
    )
