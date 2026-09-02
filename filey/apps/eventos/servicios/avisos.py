"""
El acuse de recepción de una propuesta (`CU-EVT-002`, paso 13).

Todo el correo del sistema sale por `django.core.mail`: quién entrega lo
decide `EMAIL_BACKEND`, y en pruebas Django lo sustituye por `locmem`, así
que ninguna prueba puede salir a la red aunque haya `RESEND_API_KEY` en el
entorno.

.. warning:: Un fallo de entrega **no deshace la propuesta**

   Cuando este correo se manda, la solicitud ya está guardada y tiene
   folio. Si el buzón rebota, lo que corresponde es dejar constancia en
   el log, no perder lo que alguien acaba de enviar. Por eso se llama
   desde `transaction.on_commit` y por eso no levanta.

.. note:: Todavía no hay rastro de entrega

   `STD` guarda cada aviso en una tabla `Notificacion` para poder
   contestar «¿a qué buzón salió?» un mes después. `EVT` lo necesitará
   igual, pero eso llega con `CU-EVT-010` —notificar resultados en
   lote—, que es quien de verdad lo pide. Añadirlo ahora sería una tabla
   con una sola fila por propuesta y ningún consumidor.
"""

import logging

from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape

from comun.urls import url_de_esta_feria

logger = logging.getLogger(__name__)


def avisar_recepcion(solicitud) -> bool:
    """Manda el acuse con el folio. Devuelve si se entregó.

    El folio es lo importante: es con lo que se identifica la solicitud
    en cualquier trámite posterior, y quien lo pierde no tiene otra forma
    de nombrar su propuesta.
    """
    persona = solicitud.registro.persona
    convocatoria = solicitud.registro.convocatoria
    enlace = url_de_esta_feria(
        "eventos:confirmacion", solicitud_id=solicitud.pk
    )

    asunto = f"Recibimos tu propuesta — folio {solicitud.folio}"
    parrafos = [
        f"Hola, {persona.primer_nombre}:",
        f"Registramos tu propuesta «{solicitud.titulo_actividad}» "
        f"({solicitud.actividad.tipo}) en {convocatoria.nombre}. "
        f"Su folio es {solicitud.folio}.",
        "Queda pendiente de revisión: el comité dictamina cada solicitud y "
        "te avisaremos del resultado. Enviarla no garantiza su aceptación, y "
        "la sala, el día y el horario los asigna la Coordinación.",
    ]

    texto = "\n\n".join([*parrafos, f"Ver el acuse: {enlace}", _PIE_TEXTO])
    html = _maquetar(asunto, parrafos, enlace)

    mensaje = EmailMultiAlternatives(subject=asunto, body=texto, to=[persona.correo])
    mensaje.attach_alternative(html, "text/html")
    try:
        entregados = mensaje.send(fail_silently=False)
        if not entregados:
            raise RuntimeError("el backend de correo no entregó el mensaje")
    except Exception:  # noqa: BLE001 — cualquier fallo del transporte
        logger.exception(
            "No se pudo entregar el acuse de la propuesta %s a %s",
            solicitud.pk,
            persona.correo,
        )
        return False
    return True


_PIE_TEXTO = (
    "FILEY — Feria Internacional de la Lectura Yucatán\n"
    "Coordinación General de Contenidos · UADY"
)


def _maquetar(asunto: str, parrafos: list[str], enlace: str) -> str:
    """El sobre en HTML. Estilos en línea: es lo único que lee un correo."""
    return (
        '<div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto;">'
        f'<h2 style="color: #1a1a1a;">{escape(asunto)}</h2>'
        + "".join(f"<p>{escape(p)}</p>" for p in parrafos if p)
        + f'<p><a href="{escape(enlace)}">Ver el acuse</a></p>'
        '<hr style="border: none; border-top: 1px solid #eaeaea; margin: 24px 0;" />'
        '<p style="color: #999; font-size: 12px;">'
        "FILEY — Feria Internacional de la Lectura Yucatán<br>"
        "Coordinación General de Contenidos · UADY"
        "</p></div>"
    )
