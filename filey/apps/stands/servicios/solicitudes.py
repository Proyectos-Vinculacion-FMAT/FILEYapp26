"""
Enviar y reenviar la solicitud de expositor (`CU-STD-001`, `CU-STD-002`).

Es la primera vertical que estrena el enganche de `ADR-0006`, y por eso
el orden de este módulo importa más de lo que parece: **el registro en la
convocatoria nace aquí, dentro de la misma transacción que la
solicitud**, y no al pulsar el botón del catálogo. Si naciera con el
clic, cada visita curiosa dejaría una inscripción vacía y los conteos de
la convocatoria contarían gente que nunca aplicó.
"""

import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import registros

from ..models import Editorial, Solicitud

logger = logging.getLogger(__name__)


class EnvioRechazado(Exception):
    """La solicitud no se puede enviar o reenviar ahora mismo."""


def solicitud_viva(convocatoria: Convocatoria, persona) -> Solicitud | None:
    """La solicitud de esa persona que sigue en juego, si la hay.

    "Viva" es `pendiente` o `cambios_solicitados` (`RN-22`). Una
    rechazada no bloquea: se puede volver a aplicar con la misma
    editorial.
    """
    if persona is None or not getattr(persona, "is_authenticated", False):
        return None
    return (
        Solicitud.objects.filter(
            registro__convocatoria=convocatoria,
            registro__persona=persona,
            estado__in=Solicitud.VIVOS,
        )
        .select_related("editorial")
        .first()
    )


def ultima_solicitud(convocatoria: Convocatoria, persona) -> Solicitud | None:
    """La más reciente, viva o no. Es lo que rutea `CU-STD-003`.

    Distinta de `solicitud_viva` a propósito: tras un rechazo no hay
    ninguna viva, pero la pantalla tiene que poder decir *por qué* y
    ofrecer volver a aplicar.
    """
    if persona is None or not getattr(persona, "is_authenticated", False):
        return None
    return (
        Solicitud.objects.filter(
            registro__convocatoria=convocatoria, registro__persona=persona
        )
        .select_related("editorial")
        .first()  # `ordering` del modelo: la más reciente primero.
    )


def _fotografia(editorial: Editorial) -> tuple[dict, list]:
    """Copia de los datos de la editorial, tal como se envían (`RN-22`).

    Corregir la ficha después no reescribe lo que el administrador
    dictaminó. Se guardan los campos, no el objeto: si mañana `Editorial`
    gana una columna, las fotografías viejas siguen diciendo lo que se
    envió en su día, que es exactamente lo que se quiere de una
    fotografía.
    """
    campos = [
        "nombre",
        "domicilio_calle",
        "domicilio_numero",
        "domicilio_colonia",
        "cp",
        "municipio",
        "estado",
        "pais",
        "director_general_nombre",
        "director_general_email",
        "director_comercial_nombre",
        "director_comercial_email",
        "director_editorial_nombre",
        "director_editorial_email",
        "director_promocion_nombre",
        "director_promocion_email",
        "responsable_stand",
        "giro",
        "telefono_oficina",
        "telefono_celular",
        "correo_electronico",
        "nombre_antepecho",
        "num_personas_atienden",
        "total_sellos",
        "cantidad_libros_aprox",
        "cantidad_titulos_aprox",
        "materiales",
        "tematicas",
    ]
    datos = {campo: getattr(editorial, campo) for campo in campos}
    sellos = list(editorial.sellos.values_list("nombre", flat=True))
    return datos, sellos


def _convocatoria_que_admite(convocatoria: Convocatoria) -> None:
    """Que sea de stands y esté abierta.

    Lo segundo lo vuelve a comprobar `FER` al crear el registro; se
    adelanta aquí para que el error salga antes de tocar nada y con las
    palabras de este dominio.
    """
    if convocatoria.tipo != TipoConvocatoria.STD:
        raise EnvioRechazado(
            f"«{convocatoria.nombre}» no es una convocatoria de stands."
        )
    if convocatoria.estado != Convocatoria.Estado.ABIERTA:
        raise EnvioRechazado(
            f"«{convocatoria.nombre}» no está abierta: no admite solicitudes."
        )


@transaction.atomic
def enviar_solicitud(
    *, convocatoria: Convocatoria, persona, editorial: Editorial
) -> Solicitud:
    """Aplica a ser expositor (`CU-STD-001`, pasos 5-7).

    Crea el registro en la convocatoria si no existe, y cuelga de él la
    solicitud con su fotografía. Las dos cosas en la misma transacción:
    un registro sin solicitud sería una inscripción fantasma en los
    conteos de `FER`.

    E2: si la persona ya tiene una solicitud viva, no se crea otra. Si
    tiene cambios pedidos, se reedita la misma (`CU-STD-002`); si fue
    rechazada, **no bloquea** — se aplica de nuevo con la misma
    editorial (`RN-22`).
    """
    _convocatoria_que_admite(convocatoria)

    viva = solicitud_viva(convocatoria, persona)
    if viva is not None:
        raise EnvioRechazado(
            "Ya tienes una solicitud en esta convocatoria "
            f"({viva.get_estado_display().lower()}). "
            "No se puede enviar otra mientras siga en juego."
        )

    # El registro se pide a `FER` declarando el tipo que esperamos. Es la
    # única comprobación que existe de que este expediente no cuelgue de
    # una convocatoria de eventos: la base no puede sostenerla porque el
    # `tipo` vive un salto más allá (`ADR-0006`).
    registro, _ = registros.obtener_o_crear_registro(
        convocatoria=convocatoria,
        persona=persona,
        tipo_esperado=TipoConvocatoria.STD,
    )

    datos, sellos = _fotografia(editorial)
    solicitud = Solicitud(
        registro=registro,
        editorial=editorial,
        datos_editorial=datos,
        sellos=sellos,
        estado=Solicitud.Estado.PENDIENTE,
    )
    solicitud.save()

    logger.info(
        "Solicitud de stands enviada: editorial «%s» a «%s»",
        editorial.nombre,
        convocatoria.nombre,
    )
    return solicitud


@transaction.atomic
def reenviar_solicitud(solicitud: Solicitud) -> Solicitud:
    """Corrige y reenvía tras una petición de cambios (`CU-STD-002`).

    **Es la misma solicitud, no una nueva** — esa es la diferencia con
    `CU-STD-001`. Vuelve a `pendiente` con fotografía nueva, y conserva
    `motivo_peticion` como antecedente de lo que se pidió (paso 6).
    """
    if solicitud.estado != Solicitud.Estado.CAMBIOS_SOLICITADOS:
        raise EnvioRechazado(
            "Solo se reenvía una solicitud a la que se le pidieron cambios. "
            f"Ésta está {solicitud.get_estado_display().lower()}."
        )

    _convocatoria_que_admite(solicitud.registro.convocatoria)

    datos, sellos = _fotografia(solicitud.editorial)
    solicitud.datos_editorial = datos
    solicitud.sellos = sellos
    solicitud.estado = Solicitud.Estado.PENDIENTE
    solicitud.fecha_envio = timezone.now()
    # El dictamen anterior deja de aplicar: la solicitud vuelve a la cola
    # y quien la revise ahora puede ser otra persona.
    solicitud.fecha_revision = None
    solicitud.revisado_por = None
    solicitud.save(
        update_fields=[
            "datos_editorial",
            "sellos",
            "estado",
            "fecha_envio",
            "fecha_revision",
            "revisado_por",
        ]
    )

    logger.info(
        "Solicitud de stands reenviada: editorial «%s»", solicitud.editorial.nombre
    )
    return solicitud


def guardar_editorial(editorial: Editorial, *, sellos: list[str]) -> Editorial:
    """Guarda la ficha y sus sellos, sustituyendo los que hubiera.

    Se sustituyen en vez de reconciliarse porque un sello no tiene nada
    colgando: es un nombre. Reconciliar por nombre daría el mismo
    resultado con más código.

    ``total_sellos`` se deriva de la lista en vez de creerle al
    formulario: son dos formas de decir lo mismo, y la que se puede
    contar gana.
    """
    editorial.total_sellos = len(sellos)
    editorial.full_clean(exclude=["persona"])
    with transaction.atomic():
        editorial.save()
        editorial.sellos.all().delete()
        for nombre in dict.fromkeys(n.strip() for n in sellos if n.strip()):
            editorial.sellos.create(nombre=nombre)
    return editorial


__all__ = [
    "EnvioRechazado",
    "ValidationError",
    "enviar_solicitud",
    "guardar_editorial",
    "reenviar_solicitud",
    "solicitud_viva",
    "ultima_solicitud",
]
