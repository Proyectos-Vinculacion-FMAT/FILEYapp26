"""
Resolver una solicitud (`CU-STD-006`, `CU-STD-007`).

Las tres acciones del administrador —aceptar, rechazar, pedir cambios—
tienen la misma forma: comprobar que la solicitud sigue pendiente,
escribir el dictamen, y avisar. Están juntas porque comparten esa forma y
sobre todo la comprobación, que es la que evita el fallo silencioso de
dos administradores resolviendo la misma solicitud.
"""

import logging

from django.db import transaction
from django.utils import timezone

from ..models import BitacoraSTD, Notificacion, Solicitud
from . import avisos, bitacora

logger = logging.getLogger(__name__)


class DictamenRechazado(Exception):
    """La solicitud no se puede resolver: ya lo está."""


def _resolver(
    solicitud: Solicitud, *, estado: str, revisor, motivo: str = ""
) -> Solicitud:
    """El tronco común de las tres acciones.

    El bloqueo de fila (``select_for_update``) es lo que hace real la E1
    de `CU-STD-006` y la E2 de `CU-STD-007`. Sin él, dos administradores
    que abran la misma solicitud y pulsen a la vez pasan los dos la
    comprobación: el segundo pisa el dictamen del primero, se manda un
    correo contradictorio, y nada lo señala.
    """
    with transaction.atomic():
        actual = Solicitud.objects.select_for_update().get(pk=solicitud.pk)
        if not actual.se_puede_dictaminar:
            raise DictamenRechazado(
                "Esta solicitud ya está "
                f"{actual.get_estado_display().lower()}: no se puede volver a "
                "resolver."
            )

        actual.estado = estado
        actual.fecha_revision = timezone.now()
        actual.revisado_por = revisor
        actual.motivo_peticion = motivo
        actual.save(
            update_fields=["estado", "fecha_revision", "revisado_por", "motivo_peticion"]
        )
        # Dentro de la transacción, como todo lo que anota la bitácora.
        # `Solicitud` ya guarda quién y cuándo; lo que esto añade es que
        # el dictamen aparezca **en la misma línea de tiempo** que el
        # dinero — aceptar es lo que habilita a reservar (`RN-16`), así
        # que es el primer eslabón de todo lo que viene después.
        bitacora.anotar(
            persona=revisor,
            accion=BitacoraSTD.Accion.SOLICITUD_DICTAMINADA,
            objeto=actual,
            editorial=actual.datos_editorial.get("nombre", ""),
            resultado=estado,
            motivo=motivo,
        )

    logger.info("Solicitud %s resuelta como %s", actual.pk, estado)

    # El aviso va **fuera** de la transacción, y es deliberado: un correo
    # que no sale no puede deshacer un dictamen que ya se tomó. Lo que
    # hace `avisar_resultado` es dejar la notificación como `fallida`
    # para que se pueda reintentar (`CU-STD-008` E1).
    solicitud.__dict__.update(actual.__dict__)
    avisos.avisar_resultado(actual)
    return actual


def aceptar(solicitud: Solicitud, *, revisor) -> Solicitud:
    """Habilita a la editorial para reservar stands (`RN-16`).

    A partir de aquí `Editorial` puede entrar al mapa y armar su reserva;
    es la puerta que abre todo el resto del dominio.
    """
    return _resolver(solicitud, estado=Solicitud.Estado.ACEPTADA, revisor=revisor)


def rechazar(solicitud: Solicitud, *, revisor, motivo: str = "") -> Solicitud:
    """Invalida la solicitud para este ciclo (`CU-STD-006` A2).

    El motivo es opcional: el caso de uso la describe como una acción
    directa. Lo que **no** cierra es la puerta — tras un rechazo la misma
    persona puede volver a aplicar con la misma editorial (`RN-22`),
    mientras la convocatoria siga abierta.
    """
    return _resolver(
        solicitud,
        estado=Solicitud.Estado.RECHAZADA,
        revisor=revisor,
        motivo=(motivo or "").strip(),
    )


def solicitar_cambios(solicitud: Solicitud, *, revisor, motivo: str) -> Solicitud:
    """Devuelve la solicitud para que se corrija (`CU-STD-007`).

    El motivo es **obligatorio** (E1): es literalmente el contenido del
    correo que recibe el aplicante, y sin él la persona no sabe qué
    corregir.
    """
    motivo = (motivo or "").strip()
    if not motivo:
        raise DictamenRechazado(
            "Escribe qué cambios hacen falta: es lo que la persona recibe "
            "por correo."
        )
    return _resolver(
        solicitud,
        estado=Solicitud.Estado.CAMBIOS_SOLICITADOS,
        revisor=revisor,
        motivo=motivo,
    )


def reintentar_aviso(solicitud: Solicitud) -> Notificacion:
    """Vuelve a mandar el correo del desenlace (`CU-STD-008` E1).

    Existe porque `avisar_resultado` se traga el fallo del transporte: el
    dictamen queda bien y la notificación queda `fallida`. Sin una forma
    de reintentar, el aplicante no se entera nunca.
    """
    return avisos.avisar_resultado(solicitud)
