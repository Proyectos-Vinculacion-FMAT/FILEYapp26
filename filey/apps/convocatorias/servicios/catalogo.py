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

from dataclasses import dataclass

from django.db.models import Count, Q, QuerySet
from django.urls import NoReverseMatch, reverse

from apps.ferias.models import Feria

from .. import modulos
from ..models import Convocatoria, RegistroConvocatoria


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


@dataclass(frozen=True)
class EntradaCatalogo:
    """Una convocatoria con lo que hace falta para pintar su tarjeta.

    Existe porque la tarjeta necesita responder a tres preguntas que no
    están en `Convocatoria` y que no se pueden contestar desde la
    plantilla: si alguien sirve este tipo, si quien mira ya se inscribió
    y —solo a quien administra— cuántos registros lleva.

    Sigue exponiendo **nombres de dominio**: la plantilla decide qué
    clase CSS y qué texto corresponde a cada situación, que es el
    contrato vista ↔ plantilla del proyecto.
    """

    convocatoria: Convocatoria
    #: Cómo se llama el módulo que la sirve, o ``None`` si no hay
    #: ninguno. ``None`` es el estado normal de cinco de los seis tipos.
    etiqueta_modulo: str | None
    #: La URL del formulario del módulo, ya resuelta. ``None`` cuando no
    #: hay módulo **o** cuando lo hay pero sus rutas no están montadas.
    url_aplicar: str | None
    #: Si quien mira ya tiene registro en esta convocatoria.
    ya_registrada: bool
    #: Cuántos registros activos lleva. Solo se calcula para quien
    #: administra: al participante no le corresponde ese dato
    #: (`CU-FER-006`), y una convocatoria con pocos registros no tiene
    #: por qué anunciar que va vacía.
    registros_activos: int | None
    #: Si hoy admite que alguien se inscriba: hay módulo, está `abierta`
    #: y la edición no está archivada (`CU-FER-006` E1).
    admite_registro: bool


def _url_del_modulo(convocatoria: Convocatoria) -> tuple[str | None, str | None]:
    """La etiqueta y la URL del módulo que sirve esta convocatoria.

    El nombre de ruta se resuelve **aquí y no al inscribirse el módulo**
    porque durante ``AppConfig.ready()`` el urlconf todavía no está
    cargado.

    Un ``NoReverseMatch`` se traga a propósito: significa que el módulo
    se inscribió pero sus rutas no están montadas en este urlconf. El
    catálogo es una pantalla pública y no puede caerse por eso; degrada a
    "próximamente", que es exactamente lo que la situación es.
    """
    modulo = modulos.modulo_de(convocatoria.tipo)
    if modulo is None:
        return None, None
    try:
        return modulo.etiqueta, reverse(modulo.url_aplicar, args=[convocatoria.pk])
    except NoReverseMatch:
        return modulo.etiqueta, None


def entradas_visibles(
    *,
    es_administrador: bool,
    persona=None,
    feria=None,
) -> list[EntradaCatalogo]:
    """El catálogo listo para pintar (`CU-FER-006`).

    Envuelve a `convocatorias_visibles` —que sigue siendo quien decide
    **qué** se ve— y le añade por cada fila lo que la tarjeta necesita
    para saber **qué ofrece**.

    :param persona: quien mira. Admite anónimo: consultar el catálogo no
        pide sesión, y sin ella simplemente no hay registro que enseñar.
    :param feria: la edición en la que estamos, para E1. Si está
        archivada, ninguna convocatoria ofrece registro con independencia
        del estado en que quedaran.
    """
    convocatorias = convocatorias_visibles(es_administrador=es_administrador)

    if es_administrador:
        # Una sola consulta para todo el catálogo: contar por tarjeta
        # daría una consulta por convocatoria.
        convocatorias = convocatorias.annotate(
            _registros_activos=Count(
                "registros",
                filter=Q(registros__estado=RegistroConvocatoria.Estado.ACTIVO),
            )
        )

    edicion_operable = feria is None or feria.estado != Feria.Estado.ARCHIVADA

    # Las inscripciones de quien mira, de una vez. Preguntar por tarjeta
    # daría una consulta por convocatoria para responder algo que cabe en
    # un `IN`.
    ya_registradas: set[int] = set()
    if persona is not None and getattr(persona, "is_authenticated", False):
        ya_registradas = set(
            RegistroConvocatoria.objects.filter(persona=persona).values_list(
                "convocatoria_id", flat=True
            )
        )

    entradas = []
    for convocatoria in convocatorias:
        etiqueta, url = _url_del_modulo(convocatoria)
        entradas.append(
            EntradaCatalogo(
                convocatoria=convocatoria,
                etiqueta_modulo=etiqueta,
                url_aplicar=url,
                ya_registrada=convocatoria.pk in ya_registradas,
                registros_activos=(
                    getattr(convocatoria, "_registros_activos", 0)
                    if es_administrador
                    else None
                ),
                admite_registro=(
                    url is not None
                    and convocatoria.estado == Convocatoria.Estado.ABIERTA
                    and edicion_operable
                ),
            )
        )
    return entradas
