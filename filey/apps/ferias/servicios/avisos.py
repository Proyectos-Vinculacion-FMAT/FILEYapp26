"""
Avisos por correo del Core Ferias.

Como en `registros/services/notificaciones.py`: estos correos son
informativos, no credenciales. Si el envío falla, la operación que lo
disparó sigue siendo válida, así que `AvisoFallido` se propaga para que
quien llama decida — en vez de deshacer nada.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class AvisoFallido(Exception):
    """El aviso no pudo enviarse (no invalida el alta de origen)."""


def avisar_dueno_de_feria(feria, persona) -> None:
    """Avisa a quien quedó como dueño de una feria (CU-FER-001, paso 8).

    El enlace no lleva token y no caduca: lo que autentica es el OTP que
    se envía a este mismo correo al entrar (CU-REG-003), así que la
    dirección no es un secreto.
    """
    contexto = {
        "nombre": persona.primer_nombre,
        "correo": persona.correo,
        "feria": feria.nombre,
        # `feria.url` y no una ruta escrita a mano: si el prefijo de
        # feria cambia, el enlace del correo lo sigue.
        "url_feria": settings.URL_BASE + feria.url,
        "correo_soporte": "contenidos@filey.org",
    }

    cuerpo_texto = render_to_string("ferias/correos/alta_feria.txt", contexto)
    cuerpo_html = render_to_string("ferias/correos/alta_feria.html", contexto)

    mensaje = EmailMultiAlternatives(
        subject=f"Ya administras {feria.nombre} en FILEY",
        body=cuerpo_texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[persona.correo],
    )
    mensaje.attach_alternative(cuerpo_html, "text/html")

    try:
        mensaje.send(fail_silently=False)
    except Exception as exc:  # noqa: BLE001 — cualquier fallo del proveedor
        logger.exception("Aviso de alta de feria no enviado a %s", persona.correo)
        raise AvisoFallido(str(exc)) from exc

    logger.info("Aviso de alta de la feria %s enviado a %s", feria.slug, persona.correo)


def avisar_admin_de_feria(feria, persona) -> None:
    """Avisa a quien acaba de recibir acceso a una feria (CU-FER-003, paso 6).

    Como el aviso al dueño: el enlace no lleva token y no caduca. Lo que
    autentica es el OTP que se envía a este mismo correo al entrar
    (CU-REG-003), así que la dirección del panel no es un secreto — y
    por eso mismo **aquí no se envía ningún código**: se genera cuando
    la persona escribe su correo en el acceso.
    """
    contexto = {
        "nombre": persona.primer_nombre,
        "correo": persona.correo,
        "feria": feria.nombre,
        "url_feria": settings.URL_BASE + feria.url,
        "correo_soporte": "contenidos@filey.org",
    }

    cuerpo_texto = render_to_string("ferias/correos/alta_admin.txt", contexto)
    cuerpo_html = render_to_string("ferias/correos/alta_admin.html", contexto)

    mensaje = EmailMultiAlternatives(
        subject=f"Ya administras {feria.nombre} en FILEY",
        body=cuerpo_texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[persona.correo],
    )
    mensaje.attach_alternative(cuerpo_html, "text/html")

    try:
        mensaje.send(fail_silently=False)
    except Exception as exc:  # noqa: BLE001 — cualquier fallo del proveedor
        logger.exception("Aviso de acceso a feria no enviado a %s", persona.correo)
        raise AvisoFallido(str(exc)) from exc

    logger.info(
        "Aviso de acceso a la feria %s enviado a %s", feria.slug, persona.correo
    )
