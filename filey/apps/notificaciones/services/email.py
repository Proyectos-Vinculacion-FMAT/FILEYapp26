"""High-level email notifications.

This module owns the *content* of the emails the project sends (subject, body,
templating). Other apps import these functions and never build email bodies or
touch Resend themselves.
"""
from .resend_client import EmailDeliveryError, send_email

__all__ = ["EmailDeliveryError", "send_otp_email"]


def send_otp_email(correo: str, nombre: str, codigo: str, minutos: int):
    """Send a login one-time password.

    Args:
        correo: Email del destinatario.
        nombre: Nombre del destinatario.
        codigo: El OTP generado.
        minutos: Tiempo de vigencia.

    Returns:
        El ID del mensaje de Resend.

    Raises:
        EmailDeliveryError: Si la entrega falla.
    """
    saludo = f"Hola {nombre}," if nombre else "Hola,"
    subject = f"{codigo} es tu código de acceso a FILEY"
    
    html = (
        '<div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;">'
        '<h2 style="color: #1a1a1a;">Código de acceso</h2>'
        f'<p>{saludo}</p>'
        '<p>Tu código de acceso de un solo uso es:</p>'
        f'<p style="font-size: 32px; font-weight: bold; letter-spacing: 6px; '
        f'color: #1a1a1a; margin: 24px 0;">{codigo}</p>'
        f'<p style="color: #666;">Vence en {minutos} minutos. Si tú no lo solicitaste, '
        'ignora este correo.</p>'
        '<hr style="border: none; border-top: 1px solid #eaeaea; margin: 24px 0;" />'
        '<p style="color: #999; font-size: 12px;">'
        'FILEY — Feria Internacional de la Lectura Yucatán<br>'
        'Coordinación General de Contenidos · UADY'
        '</p>'
        '</div>'
    )
    text = (
        f"{saludo}\n\n"
        f"Tu código de acceso de un solo uso es: {codigo}\n\n"
        f"Vence en {minutos} minutos. Si tú no lo solicitaste, "
        "ignora este correo.\n\n"
        "FILEY — Feria Internacional de la Lectura Yucatán\n"
        "Coordinación General de Contenidos · UADY"
    )
    
    return send_email(to=correo, subject=subject, html=html, text=text)
