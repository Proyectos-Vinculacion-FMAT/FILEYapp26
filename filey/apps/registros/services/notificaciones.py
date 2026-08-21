"""
Avisos por correo que no son el OTP (CU-REG-005).

A diferencia del OTP —donde un envío fallido obliga a invalidar el
código (E3)— estos avisos son informativos: si el correo falla, la
operación de negocio que los disparó sigue siendo válida. Por eso
``AvisoFallido`` se propaga para que quien llame decida, en vez de
deshacer nada.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from ..models import Modulo, Persona

logger = logging.getLogger(__name__)


class AvisoFallido(Exception):
    """El aviso no pudo enviarse (no invalida la operación de origen)."""


def _describir_acceso(persona: Persona) -> str:
    """Texto legible de los módulos que administra la persona."""
    roles = list(persona.roles.all())
    if any(r.modulo == Modulo.TODOS for r in roles):
        return "Todos los módulos"
    return ", ".join(Modulo(r.modulo).label for r in roles)


def avisar_alta_admin(persona: Persona) -> None:
    """Avisa a la persona de que su cuenta ya entra al panel admin.

    El enlace apunta al login administrativo sin token: lo que
    autentica es el OTP que se envía a este mismo correo al entrar,
    así que el enlace no es un secreto y no caduca.
    """
    contexto = {
        "nombre": persona.nombre_completo or "",
        "correo": persona.correo,
        "acceso": _describir_acceso(persona),
        # La ruta se resuelve con `reverse`, no escrita a mano: si el
        # acceso administrativo cambia de dirección, el enlace del
        # correo la sigue sin que nadie tenga que acordarse de esto.
        "url_panel": settings.URL_BASE + reverse("registros:admin_acceso"),
        "correo_soporte": "contenidos@filey.org",
    }

    cuerpo_texto = render_to_string("registros/correos/alta_admin.txt", contexto)
    cuerpo_html = render_to_string("registros/correos/alta_admin.html", contexto)

    mensaje = EmailMultiAlternatives(
        subject="Ya tienes acceso al panel administrativo de FILEY",
        body=cuerpo_texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[persona.correo],
    )
    mensaje.attach_alternative(cuerpo_html, "text/html")

    try:
        mensaje.send(fail_silently=False)
    except Exception as exc:  # noqa: BLE001 — cualquier fallo del proveedor
        logger.exception("Aviso de alta admin no enviado a %s", persona.correo)
        raise AvisoFallido(str(exc)) from exc

    logger.info("Aviso de alta admin enviado a %s", persona.correo)
