"""High-level email notifications.

This module owns the *content* of the emails the project sends (subject, body,
templating). Other apps import these functions and never build email bodies or
touch Resend themselves.
"""
from .resend_client import EmailDeliveryError, send_email

__all__ = ['EmailDeliveryError', 'send_otp_email']


def send_otp_email(to, code):
    """Send a login one-time password to ``to``.

    Args:
        to: Recipient email address.
        code: The OTP code to include.

    Returns:
        The Resend message id.

    Raises:
        EmailDeliveryError: if delivery fails.
    """
    subject = 'Tu código de acceso FILEY'
    html = (
        '<div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto;">'
        '<h2 style="color: #1a1a1a;">Código de acceso</h2>'
        '<p>Usa el siguiente código para iniciar sesión en FILEY:</p>'
        f'<p style="font-size: 32px; font-weight: bold; letter-spacing: 6px; '
        f'color: #1a1a1a; margin: 24px 0;">{code}</p>'
        '<p style="color: #666;">Este código expira en unos minutos. '
        'Si no solicitaste iniciar sesión, puedes ignorar este mensaje.</p>'
        '</div>'
    )
    text = (
        f'Tu código de acceso FILEY es: {code}\n\n'
        'Este código expira en unos minutos. '
        'Si no solicitaste iniciar sesión, ignora este mensaje.'
    )
    return send_email(to=to, subject=subject, html=html, text=text)
