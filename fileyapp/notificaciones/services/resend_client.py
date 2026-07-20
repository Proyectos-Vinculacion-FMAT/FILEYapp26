"""Low-level Resend transport.

This is the only module in the project that talks to Resend directly. Everything
else goes through the higher-level helpers in ``notificaciones.services.email``.
"""
import logging

import resend
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    """Raised when an email could not be handed off to Resend."""


def send_email(*, to, subject, html, text=None):
    """Send a single email through Resend.

    Args:
        to: Recipient address (str) or list of addresses.
        subject: Email subject line.
        html: HTML body.
        text: Optional plain-text body.

    Returns:
        The Resend message id on success.

    Raises:
        EmailDeliveryError: if the API key is missing or Resend rejects the send.
    """
    if not settings.RESEND_API_KEY:
        raise EmailDeliveryError('RESEND_API_KEY is not configured.')

    resend.api_key = settings.RESEND_API_KEY

    params = {
        'from': settings.DEFAULT_FROM_EMAIL,
        'to': [to] if isinstance(to, str) else list(to),
        'subject': subject,
        'html': html,
    }
    if text:
        params['text'] = text

    try:
        result = resend.Emails.send(params)
    except Exception as exc:  # resend raises its own exception types
        logger.exception('Resend failed to send email to %s', to)
        raise EmailDeliveryError(str(exc)) from exc

    return result.get('id') if isinstance(result, dict) else result
