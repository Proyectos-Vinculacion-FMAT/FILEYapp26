"""
Enviar una propuesta de actividad (`CU-EVT-002`).

El registro en la convocatoria **nace aquí, dentro de la misma
transacción que la propuesta**, y no al pulsar el botón del catálogo. Si
naciera con el clic, cada visita curiosa dejaría una inscripción vacía y
los conteos de la convocatoria contarían gente que nunca propuso
(`ADR-0006`). Es el mismo trato que ya tiene `STD`.

.. note:: En `EVT` se proponen varias actividades

   A diferencia de `STD`, aquí **no hay una regla de una sola solicitud
   viva**: el paso 14 del CU ofrece explícitamente "Crear una nueva
   solicitud". De un mismo registro cuelgan todas las propuestas de esa
   persona a esa convocatoria.
"""

import logging

from django.db import transaction

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import registros

from ..models import MODELO_POR_TIPO, Documento, Solicitud
from . import avisos

logger = logging.getLogger(__name__)


class EnvioRechazado(Exception):
    """La propuesta no se puede enviar ahora mismo."""


def admite_propuestas(convocatoria: Convocatoria) -> bool:
    """Si esta convocatoria acepta envíos en este momento.

    Lo decide `estado` y no las fechas: adelantar la fecha de cierre no
    cierra una convocatoria (`CU-FER-008`). La pantalla lo usa para no
    ofrecer un formulario que el envío va a rechazar; quien lo hace
    cumplir de verdad es `crear`, porque entre pintar y enviar puede
    pasar cualquier cosa (`E1` del CU).
    """
    return convocatoria.estado == Convocatoria.Estado.ABIERTA


@transaction.atomic
def crear(
    *,
    convocatoria: Convocatoria,
    persona,
    comunes: dict,
    nombre_tipo: str,
    detalle: dict,
    documentos=(),
) -> Solicitud:
    """Da de alta la propuesta entera: solicitud, actividad y adjuntos.

    Todo o nada. Si algo falla —la convocatoria cerró entre que se pintó
    el formulario y se pulsó enviar, un archivo no pasa la lista blanca—
    no queda ni la solicitud ni el registro, que es lo que exige `E1`:
    «no se crea ningún registro».

    :param comunes: los campos de `Solicitud`, ya validados por el
        formulario. Este servicio no valida forma —eso es del
        formulario—; valida **reglas**.
    :param nombre_tipo: el valor de `CatalogoActividades.Nombre`. Decide
        a qué tabla hija va `detalle`.
    :param detalle: los campos propios del tipo.
    :param documentos: iterable de ``(tipo_documento, archivo)``. Hoy
        solo los llenan los dos tipos de publicación.
    """
    if nombre_tipo not in MODELO_POR_TIPO:
        # No es entrada de usuario: el formulario ya lo acotó al
        # catálogo. Si llega aquí, quien llama se equivocó.
        raise EnvioRechazado(f"«{nombre_tipo}» no es un tipo de actividad.")

    # `FER` es quien decide si se admiten inscripciones —y de paso
    # comprueba la invariante que el esquema no puede: que esta propuesta
    # no cuelgue de una convocatoria de stands (`ADR-0006`)—.
    try:
        registro, _ = registros.obtener_o_crear_registro(
            convocatoria=convocatoria,
            persona=persona,
            tipo_esperado=TipoConvocatoria.EVT,
        )
    except registros.RegistroRechazado as motivo:
        # Se traduce a la excepción de este módulo para que la vista no
        # tenga que conocer las de `FER`, pero el texto es el de `FER`:
        # es quien sabe por qué dijo que no.
        raise EnvioRechazado(str(motivo)) from motivo

    # Nace en `pendiente` por el valor por omisión de la columna: el
    # dictamen son campos de esta misma fila y no una tabla aparte, así
    # que no hay nada más que crear. La pregunta de si debería estar
    # desacoplado sigue abierta en `ADR-0011`.
    solicitud = Solicitud.objects.create(registro=registro, **comunes)

    Modelo = MODELO_POR_TIPO[nombre_tipo]
    actividad = Modelo.objects.create(
        solicitud=solicitud,
        tipo_id=_id_del_tipo(nombre_tipo),
        **detalle,
    )

    for tipo_documento, archivo in documentos:
        if not archivo:
            continue
        Documento.objects.create(
            actividad=actividad,
            tipo_documento=tipo_documento,
            archivo=archivo,
            nombre_original=getattr(archivo, "name", "")[:255],
            subido_por=persona,
        )

    logger.info(
        "Propuesta %s enviada a la convocatoria %s", solicitud.pk, convocatoria.pk
    )

    # Paso 13 del CU. Va en `on_commit` por dos motivos: no se avisa de
    # algo que todavía puede deshacerse, y un buzón que rebota no puede
    # tirar una propuesta que ya tiene folio.
    transaction.on_commit(lambda: avisos.avisar_recepcion(solicitud))
    return solicitud


def _id_del_tipo(nombre: str) -> int:
    """El id del tipo, que siembra la migración `0002`.

    Se busca por nombre y no se recibe el objeto para que quien llama
    —una vista, un comando— no tenga que ir a buscarlo antes.
    """
    from ..models import CatalogoActividades

    return CatalogoActividades.objects.values_list("pk", flat=True).get(nombre=nombre)
