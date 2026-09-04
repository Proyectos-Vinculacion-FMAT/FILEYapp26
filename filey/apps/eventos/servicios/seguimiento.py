"""
Consultar las propuestas propias (`CU-EVT-003`).

La otra mitad de `solicitudes.py`: ahí se envía, aquí se mira lo enviado.
Están separadas porque no comparten nada salvo la tabla — una escribe
dentro de una transacción y avisa por correo, la otra solo lee— y porque
así cada caso de uso tiene un archivo donde buscarlo.

.. warning:: Quién pregunta es parte de la consulta, no un filtro que se
   aplica después

   Las dos funciones reciben a la persona y la meten en el ``filter``.
   No hay ninguna que devuelva "la propuesta con este id" a secas y deje
   la comprobación de dueño para quien llame: lo que no se pide no llega
   a la respuesta, y una propuesta ajena que llega a la vista ya es una
   fuga esperando a que alguien olvide un ``if``.
"""

from django.db.models import Prefetch, QuerySet

from apps.convocatorias.models import Convocatoria

from ..models import Documento, Solicitud

#: Lo que hay que traer para pintar una fila del listado sin una consulta
#: por columna: el tipo de actividad y el prefijo con el que se compone el
#: folio —que cuelga de la convocatoria y no de aquí—. El estado es una
#: columna de la propia fila, así que no hace falta traerlo.
_DE_LA_FILA = (
    "actividad",
    "actividad__tipo",
    "registro__convocatoria__configuracion_eventos",
)


def _mias(convocatoria: Convocatoria, persona) -> QuerySet[Solicitud]:
    """Las de esa persona en esa convocatoria. Sin sesión, ninguna."""
    if persona is None or not getattr(persona, "is_authenticated", False):
        return Solicitud.objects.none()
    return Solicitud.objects.filter(
        registro__convocatoria=convocatoria, registro__persona=persona
    )


def propuestas_de(convocatoria: Convocatoria, persona) -> QuerySet[Solicitud]:
    """El listado del paso 2, de la más nueva a la más vieja.

    El orden lo pone ``Solicitud.Meta.ordering`` y no se repite aquí: es
    el mismo que quiere el acuse de `CU-EVT-002`, que también llama a
    esta función.
    """
    return _mias(convocatoria, persona).select_related(*_DE_LA_FILA)


def propuesta_de(convocatoria: Convocatoria, persona, solicitud_id: int):
    """Una propuesta con todo lo que hace falta para el paso 4, o ``None``.

    ``None`` y no una excepción: quien llama es una vista, y las dos
    razones por las que puede no haber nada —no existe, o es de otra
    persona— terminan en el mismo 404. Distinguirlas en la respuesta
    diría a un curioso que ese folio existe.

    Trae los documentos en la misma consulta porque el detalle los
    enseña siempre, y en una presentación de libro son dos.
    """
    return (
        _mias(convocatoria, persona)
        .select_related(*_DE_LA_FILA)
        .prefetch_related(
            Prefetch(
                "actividad__documentos",
                queryset=Documento.objects.order_by("tipo_documento"),
            )
        )
        .filter(pk=solicitud_id)
        .first()
    )
