"""
Avisar al aplicante el resultado de su solicitud (`CU-STD-008`).

El reparto es el que decidió el equipo el 2026-08-27: **la tabla es de
`STD`, el envío no**. `Notificacion` vive en el schema de esta feria
porque apunta a una solicitud de esta edición; quién entrega el correo lo
decide `EMAIL_BACKEND`, como todo el correo del proyecto.

.. warning:: Nunca se llama a Resend desde aquí

   Se compone un `EmailMultiAlternatives` y se envía por
   ``django.core.mail``. Es lo que permite que en pruebas el correo caiga
   en ``mail.outbox`` en vez de salir a la red, con `RESEND_API_KEY` en
   el entorno o sin ella.
"""

import logging

from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape

from comun.urls import url_publica

from ..models import Notificacion, Solicitud

logger = logging.getLogger(__name__)

#: Qué tipo de notificación corresponde a cada desenlace.
TIPO_POR_ESTADO = {
    Solicitud.Estado.ACEPTADA: Notificacion.Tipo.APLICACION_ACEPTADA,
    Solicitud.Estado.RECHAZADA: Notificacion.Tipo.APLICACION_RECHAZADA,
    Solicitud.Estado.CAMBIOS_SOLICITADOS: Notificacion.Tipo.APLICACION_CAMBIOS,
}


def _cuerpo(solicitud: Solicitud) -> tuple[str, str, str]:
    """Asunto, texto y HTML según el desenlace (`CU-STD-008` paso 2)."""
    editorial = solicitud.datos_editorial.get("nombre", "tu editorial")
    convocatoria = solicitud.registro.convocatoria.nombre

    if solicitud.estado == Solicitud.Estado.ACEPTADA:
        asunto = f"Tu solicitud para {convocatoria} fue aceptada"
        parrafos = [
            f"La solicitud de {editorial} para «{convocatoria}» fue aceptada.",
            "Ya puedes elegir tus espacios en el mapa del showfloor y "
            "reservarlos.",
        ]
    elif solicitud.estado == Solicitud.Estado.RECHAZADA:
        asunto = f"Tu solicitud para {convocatoria} no fue aceptada"
        parrafos = [
            f"La solicitud de {editorial} para «{convocatoria}» no fue aceptada.",
            "Puedes volver a aplicar con la misma editorial corrigiendo lo "
            "que haga falta, mientras la convocatoria siga abierta.",
        ]
    else:
        asunto = f"Cambios pedidos en tu solicitud para {convocatoria}"
        parrafos = [
            f"Para poder resolver la solicitud de {editorial} hacen falta "
            "algunos cambios:",
            solicitud.motivo_peticion,
            "Entra a corregirla y vuelve a enviarla; conserva todo lo que ya "
            "habías capturado.",
        ]

    enlace = url_publica("ferias:elegir")
    texto = "\n\n".join(
        [*parrafos, f"Entra en: {enlace}", "FILEY — Feria Internacional de la Lectura Yucatán"]
    )
    html = (
        '<div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto;">'
        f'<h2 style="color: #1a1a1a;">{escape(asunto)}</h2>'
        + "".join(f"<p>{escape(p)}</p>" for p in parrafos if p)
        + f'<p><a href="{escape(enlace)}">Entrar a FILEY</a></p>'
        '<hr style="border: none; border-top: 1px solid #eaeaea; margin: 24px 0;" />'
        '<p style="color: #999; font-size: 12px;">'
        "FILEY — Feria Internacional de la Lectura Yucatán<br>"
        "Coordinación General de Contenidos · UADY"
        "</p></div>"
    )
    return asunto, texto, html


def avisar_resultado(solicitud: Solicitud) -> Notificacion:
    """Manda el correo del desenlace y lo deja registrado.

    **Nunca levanta la excepción del correo.** Un fallo de entrega no
    puede deshacer un dictamen ya tomado: el administrador aceptó la
    solicitud y eso pasó. Lo que hace es registrar la notificación como
    `fallida` con el motivo, que es lo que `CU-STD-008` E1 pide para
    poder reintentar a mano.

    Se llama **fuera** de la transacción del dictamen, por lo mismo: si
    corriera dentro, una notificación fallida escrita y luego revertida
    dejaría el dictamen sin rastro de que el aviso no salió.
    """
    tipo = TIPO_POR_ESTADO.get(solicitud.estado)
    if tipo is None:
        raise ValueError(
            f"Una solicitud {solicitud.estado} no tiene resultado que avisar."
        )

    # A quién: el correo de contacto de la ficha, que puede no ser el de
    # acceso —la cuenta personal de quien tramita frente al buzón
    # comercial de la editorial—. Si la ficha no lo trae, la cuenta.
    persona = solicitud.registro.persona
    destino = solicitud.datos_editorial.get("correo_electronico") or persona.correo

    asunto, texto, html = _cuerpo(solicitud)
    mensaje = EmailMultiAlternatives(subject=asunto, body=texto, to=[destino])
    mensaje.attach_alternative(html, "text/html")

    try:
        entregados = mensaje.send(fail_silently=False)
        if not entregados:
            raise RuntimeError("el backend de correo no entregó el mensaje")
        estado, detalle = Notificacion.Estado.ENVIADA, ""
    except Exception as exc:  # noqa: BLE001 — cualquier fallo del transporte
        logger.exception(
            "No se pudo avisar el resultado de la solicitud %s", solicitud.pk
        )
        estado, detalle = Notificacion.Estado.FALLIDA, str(exc)

    return Notificacion.objects.create(
        destinatario=persona,
        tipo=tipo,
        estado=estado,
        solicitud=solicitud,
        detalle_error=detalle,
    )
