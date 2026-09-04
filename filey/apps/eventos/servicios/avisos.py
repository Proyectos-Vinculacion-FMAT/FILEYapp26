"""
Los dos correos que `EVT` manda en el momento.

El **acuse** de recepción, al enviar una propuesta (`CU-EVT-002`, paso
13), y la **solicitud de cambios**, al dictaminarla (`CU-EVT-009` A1).
Son los dos que no pueden esperar: el primero porque lleva el folio, y el
segundo porque abre un plazo para corregir. Las aceptaciones y los
rechazos **no están aquí** — salen en lote (`CU-EVT-010`).

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

    return _enviar(
        solicitud,
        asunto=asunto,
        parrafos=parrafos,
        enlace=enlace,
        texto_enlace="Ver el acuse",
        que_es="el acuse",
    )


def avisar_cambios_solicitados(solicitud) -> bool:
    """Le dice qué debe corregir (`CU-EVT-009` A1, paso 5).

    Es el **único** desenlace del dictamen que sale en el momento. Las
    aceptaciones y los rechazos esperan al lote de `CU-EVT-010` porque son
    definitivos y conviene comunicarlos todos juntos; esto no lo es: es
    una petición con plazo, y quien la recibe tiene que poder corregir y
    reenviar antes de que cierre la convocatoria.

    El cuerpo lleva el mensaje **tal cual lo escribió quien revisa**, sin
    reformular. Es la razón por la que el servicio lo exige no vacío: si
    aquí no hay nada, el correo no dice nada.
    """
    persona = solicitud.registro.persona
    convocatoria = solicitud.registro.convocatoria
    # Lleva al acuse y no a una pantalla de edición porque `CU-EVT-004`
    # —corregir y reenviar— todavía no está construido. Desde ahí se ve la
    # propuesta y su folio, que es lo que hace falta para contestar.
    enlace = url_de_esta_feria("eventos:confirmacion", solicitud_id=solicitud.pk)

    asunto = f"Tu propuesta necesita cambios — folio {solicitud.folio}"
    parrafos = [
        f"Hola, {persona.primer_nombre}:",
        f"Revisamos tu propuesta «{solicitud.titulo_actividad}» "
        f"({solicitud.folio}) en {convocatoria.nombre} y necesitamos que "
        "corrijas lo siguiente antes de poder dictaminarla:",
        solicitud.mensaje_cambios_solicitados,
        "Cuando la tengas lista, respóndenos por este medio. Tienes hasta "
        "que cierre la convocatoria.",
    ]
    return _enviar(
        solicitud,
        asunto=asunto,
        parrafos=parrafos,
        enlace=enlace,
        texto_enlace="Ver mi propuesta",
        que_es="la solicitud de cambios",
    )


def _enviar(
    solicitud,
    *,
    asunto: str,
    parrafos: list[str],
    enlace: str,
    texto_enlace: str,
    que_es: str,
) -> bool:
    """Arma el sobre y lo entrega. Devuelve si salió.

    **Nunca levanta.** Los dos correos de este módulo se mandan cuando la
    fila ya está guardada —la propuesta tiene folio, o el dictamen ya está
    escrito—, así que un buzón que rebota no puede deshacer nada: lo que
    corresponde es dejar constancia en el log. Quien llama decide si le
    importa el falso; hoy ninguno de los dos lo mira, y es correcto.
    """
    persona = solicitud.registro.persona
    texto = "\n\n".join([*parrafos, f"{texto_enlace}: {enlace}", _PIE_TEXTO])
    html = _maquetar(asunto, parrafos, enlace, texto_enlace)

    mensaje = EmailMultiAlternatives(subject=asunto, body=texto, to=[persona.correo])
    mensaje.attach_alternative(html, "text/html")
    try:
        entregados = mensaje.send(fail_silently=False)
        if not entregados:
            raise RuntimeError("el backend de correo no entregó el mensaje")
    except Exception:  # noqa: BLE001 — cualquier fallo del transporte
        logger.exception(
            "No se pudo entregar %s de la propuesta %s a %s",
            que_es,
            solicitud.pk,
            persona.correo,
        )
        return False
    return True


_PIE_TEXTO = (
    "FILEY — Feria Internacional de la Lectura Yucatán\n"
    "Coordinación General de Contenidos · UADY"
)


def _maquetar(
    asunto: str,
    parrafos: list[str],
    enlace: str,
    texto_enlace: str = "Ver el acuse",
) -> str:
    """El sobre en HTML. Estilos en línea: es lo único que lee un correo.

    ``texto_enlace`` existe desde que hay dos correos distintos: el acuse
    lleva a mirar lo enviado y la solicitud de cambios lleva a corregirlo.
    Un rótulo fijo obligaba a que el segundo dijera «Ver el acuse», que es
    justo lo que no hay que hacer ahí.
    """
    return (
        '<div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto;">'
        f'<h2 style="color: #1a1a1a;">{escape(asunto)}</h2>'
        + "".join(f"<p>{escape(p)}</p>" for p in parrafos if p)
        + f'<p><a href="{escape(enlace)}">{escape(texto_enlace)}</a></p>'
        '<hr style="border: none; border-top: 1px solid #eaeaea; margin: 24px 0;" />'
        '<p style="color: #999; font-size: 12px;">'
        "FILEY — Feria Internacional de la Lectura Yucatán<br>"
        "Coordinación General de Contenidos · UADY"
        "</p></div>"
    )
