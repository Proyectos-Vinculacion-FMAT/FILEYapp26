"""
Backend de correo de Django que entrega por Resend.

Existe para que **todo el correo del proyecto salga por el mismo sitio**:
`django.core.mail`. Antes, el OTP hablaba con Resend directamente
(`services/email.py` → `resend_client`) mientras el resto de los avisos
usaba `EmailMultiAlternatives`. Esa asimetría tenía dos consecuencias
malas:

1. Las pruebas no podían ver el OTP. Django sustituye el backend por
   `locmem` durante los tests, así que `mail.outbox` recogía los avisos
   pero no los códigos — y las pruebas que los verificaban fallaban
   siempre.
2. Peor: como el envío del OTP no pasaba por el backend, ejecutar la
   suite con `RESEND_API_KEY` configurada **mandaba correos de verdad**
   a las direcciones de las fixtures.

Con el transporte detrás de un backend, `EMAIL_BACKEND` decide a dónde
va el correo y las pruebas quedan aisladas por construcción, sin que
nadie tenga que acordarse de parchear nada.
"""

import logging

from django.core.mail.backends.base import BaseEmailBackend

from .services.resend_client import EmailDeliveryError, send_email

logger = logging.getLogger(__name__)


class ResendBackend(BaseEmailBackend):
    """Entrega cada mensaje por la API de Resend.

    Respeta el contrato de Django: devuelve cuántos mensajes se
    entregaron y, si ``fail_silently`` es falso, deja subir el error.
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        enviados = 0
        for mensaje in email_messages:
            try:
                # El acuse se cuelga del mensaje porque `send_messages`
                # solo puede devolver un conteo, y quien lo necesita es
                # quien compuso el correo —para poder casar su fila con
                # el panel del proveedor cuando alguien pregunte si
                # llegó—. Con `locmem` nadie lo pone y queda vacío.
                mensaje.acuse_proveedor = self._enviar_uno(mensaje)
            except EmailDeliveryError:
                if not self.fail_silently:
                    raise
                logger.exception("Correo no entregado a %s", mensaje.to)
                continue
            enviados += 1
        return enviados

    def _enviar_uno(self, mensaje):
        """Traduce un mensaje de Django a lo que espera Resend.

        Django modela el cuerpo principal en ``body`` y las variantes en
        ``alternatives``. Resend quiere ``html`` y ``text`` por separado,
        así que hay que decidir cuál es cuál según el
        ``content_subtype`` del mensaje.
        """
        html = None
        texto = None

        if mensaje.content_subtype == "html":
            html = mensaje.body
        else:
            texto = mensaje.body

        for contenido, tipo in getattr(mensaje, "alternatives", []) or []:
            if tipo == "text/html":
                html = contenido

        if html is None:
            # Resend exige cuerpo HTML. Un mensaje solo-texto se manda
            # con el texto también como HTML: es preferible a rechazarlo.
            html = f"<pre>{mensaje.body}</pre>"

        destinatarios = list(mensaje.to)
        if not destinatarios:
            raise EmailDeliveryError("El mensaje no tiene destinatarios.")

        return send_email(
            to=destinatarios,
            subject=mensaje.subject,
            html=html,
            text=texto,
            from_email=mensaje.from_email,
        )
