"""
Qué convocatorias de esta feria ve quien está mirando (`CU-FER-006`).

El caso de uso lo pide por escrito y conviene repetirlo aquí: **el filtro
va en la consulta, no en la plantilla**. Una convocatoria en borrador no
tiene revisada su configuración —puede no tener precio, ni cupos, ni
fechas de dictamen—, así que no debe llegar siquiera a la respuesta del
participante. Ocultarla con un ``{% if %}`` la dejaría en el HTML.

.. note:: Ninguna consulta de aquí filtra por feria, y no falta nada

   La feria es el schema en el que el middleware dejó la conexión
   (`ADR-0003`). Estas mismas líneas devuelven cosas distintas según se
   llegue por ``/f/2027/`` o por ``/f/2028/``.
"""

from django.db.models import QuerySet

from ..models import Convocatoria


def convocatorias_visibles(*, es_administrador: bool) -> QuerySet[Convocatoria]:
    """El catálogo de esta feria, recortado según quién pregunta.

    Al administrador se le da **todo**, borradores incluidos: es el
    catálogo que opera. A cualquier otro —participante con sesión o
    visitante anónimo— se le dan las abiertas y las cerradas.

    Las cerradas se quedan a propósito (CU-FER-006, A4): que se vea que
    existieron y cuándo cerraron dice bastante más que una pantalla
    vacía que parece una feria sin nada.
    """
    convocatorias = Convocatoria.objects.all()
    if es_administrador:
        return convocatorias
    return convocatorias.exclude(estado=Convocatoria.Estado.BORRADOR)
