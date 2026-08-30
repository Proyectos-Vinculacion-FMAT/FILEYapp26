"""
La barrida diaria: qué reservas vencieron y a quién hay que decírselo
(`CU-STD-022`, `024`, `025`).

Es **lo único del dominio que necesita reloj**. Los umbrales del 50% y
del 100% se evalúan dentro de la petición que cambia el saldo
(`servicios/pagos.py`), y el pronto pago se aplica al reservar. Lo que
no puede saberse sin mirar el calendario es que un plazo se agotó: nadie
hace nada, y justamente por eso hay que avisar.

.. important:: Vencer **no** libera nada

   `RN-12` y el paso 7 de `CU-STD-022`: la reserva se queda donde está,
   con sus espacios apartados, hasta que una persona la cancele o la
   prorrogue (`CU-STD-035`). Este módulo **no escribe en `Reserva`**, y
   es deliberado: una barrida que "limpia" reservas vencidas liberaría
   espacios que nadie decidió liberar, y lo haría de madrugada y sin
   testigos.

   Lo único que escribe son `Notificacion`.

.. important:: Se avisa una vez por vencimiento, no una vez por reserva

   La barrida corre a diario y el aviso no se repite; pero si alguien
   prorroga la reserva (`CU-STD-035`) y el plazo nuevo también se agota,
   hay que volver a avisar. Por eso la pregunta no es "¿ya se avisó de
   esta reserva?" sino "¿ya se avisó **de este vencimiento**?", que se
   contesta comparando la fecha del aviso con la fecha de vencimiento
   vigente. Una prórroga mueve la fecha hacia adelante y deja atrás los
   avisos viejos, sin tener que borrar nada.

   Un aviso `fallida` no cuenta como avisado: `CU-STD-024` E1 dice que se
   reintenta en el ciclo siguiente.
"""

import logging

from django.utils import timezone

from apps.ferias.models import AdminFeria, Feria

from ..models import Notificacion, Reserva
from . import avisos

logger = logging.getLogger(__name__)


def vencidas(convocatoria):
    """Las reservas de esta convocatoria a las que se les pasó el plazo.

    `CU-STD-022` pasos 3 a 5: solo las `por_confirmar` —una confirmada ya
    cubrió el anticipo y su plazo dejó de correr (`A1`)— con la fecha de
    vencimiento pasada.

    No se comprueba el saldo aparte: cubrir el anticipo mueve la reserva
    a `confirmada` en la misma petición (`RN-13`), así que una que sigue
    `por_confirmar` es exactamente una que no llegó.
    """
    return (
        Reserva.objects.filter(
            registro__convocatoria=convocatoria,
            estado=Reserva.Estado.POR_CONFIRMAR,
            fecha_vencimiento_anticipo__lt=timezone.now(),
        )
        .select_related("editorial", "registro__persona", "registro__convocatoria")
        .prefetch_related("lineas__stand")
    )


def falta_avisar(reserva: Reserva, tipo: str, destinatario=None) -> bool:
    """Si este vencimiento todavía no se ha avisado a quien toca.

    Se compara contra ``fecha_vencimiento_anticipo`` y no contra la
    existencia del aviso: ver la nota de arriba sobre las prórrogas.
    """
    avisados = reserva.notificaciones.filter(
        tipo=tipo,
        estado=Notificacion.Estado.ENVIADA,
        fecha_envio__gte=reserva.fecha_vencimiento_anticipo,
    )
    if destinatario is not None:
        avisados = avisados.filter(destinatario=destinatario)
    return not avisados.exists()


def avisar_de_una(reserva: Reserva, administradores) -> list[Notificacion]:
    """Los dos avisos de una reserva vencida (`CU-STD-024` y `025`).

    A la editorial va uno; a quien administra, **uno por persona**. No es
    un correo con varios destinatarios en copia porque `Notificacion`
    registra a quién se le dijo algo, y una fila con tres destinatarios
    dentro no contesta esa pregunta — que es la que se hace cuando
    alguien dice que no se enteró.

    Devuelve solo los avisos que se intentaron ahora: los que ya habían
    salido no se repiten.
    """
    mandados = []

    if falta_avisar(reserva, Notificacion.Tipo.POSIBLE_CANCELACION):
        mandados.append(avisos.avisar_posible_cancelacion(reserva))

    for administrador in administradores:
        if falta_avisar(
            reserva, Notificacion.Tipo.RESERVA_VENCIDA, destinatario=administrador
        ):
            mandados.append(
                avisos.avisar_vencimiento_al_equipo(reserva, administrador)
            )

    return mandados


def barrer(convocatoria) -> list[Reserva]:
    """Avisa de todo lo vencido en esta convocatoria.

    :returns: las reservas por las que salió al menos un aviso. Las que
        ya estaban avisadas no vuelven a contarse, para que el comando
        pueda decir lo que hizo y no lo que miró.
    """
    administradores = _quienes_administran()
    tocadas = []
    for reserva in vencidas(convocatoria):
        if avisar_de_una(reserva, administradores):
            logger.info(
                "Reserva %s vencida el %s: avisada",
                reserva.pk,
                reserva.fecha_vencimiento_anticipo,
            )
            tocadas.append(reserva)
    return tocadas


def _quienes_administran() -> list:
    """Las personas que administran la edición en la que estamos.

    `AdminFeria` vive en `public` y la feria es el schema (`ADR-0003`),
    así que se llega por ahí y no por una columna. Sin nadie que
    administre —una feria a medio dar de alta— el aviso del aplicante
    sale igual: `CU-STD-025` no depende de `CU-STD-024`.
    """
    feria = Feria.de_la_conexion()
    if feria is None:
        return []
    return [
        acceso.persona
        for acceso in AdminFeria.objects.filter(feria=feria).select_related("persona")
    ]
