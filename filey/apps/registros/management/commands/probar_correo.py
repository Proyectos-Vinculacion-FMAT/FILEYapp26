"""
Diagnóstico del envío de correo (apoyo a CU-REG-002).

Comprueba la configuración SMTP y manda un correo de prueba sin
pasar por toda la pantalla de acceso. Es la forma rápida de saber
si "el OTP no llega" es un problema de credenciales, de remitente
o de que el backend está cayendo a consola.

Uso:
    python manage.py probar_correo destino@ejemplo.com
    python manage.py probar_correo destino@ejemplo.com --solo-config
"""

import smtplib

from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Verifica la configuración de correo y envía un mensaje de prueba."

    def add_arguments(self, parser):
        parser.add_argument("destino", help="Correo al que enviar la prueba")
        parser.add_argument(
            "--solo-config",
            action="store_true",
            help="Muestra la configuración sin enviar nada",
        )

    def handle(self, *args, **opciones):
        usa_consola = "console" in settings.EMAIL_BACKEND

        self.stdout.write("Configuración de correo actual:")
        self.stdout.write(f"  EMAIL_BACKEND      {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  EMAIL_HOST_USER    {settings.EMAIL_HOST_USER or '(vacío)'}")
        self.stdout.write(
            "  EMAIL_HOST_PASSWORD "
            + (
                f"({len(settings.EMAIL_HOST_PASSWORD)} caracteres)"
                if settings.EMAIL_HOST_PASSWORD
                else "(vacío)"
            )
        )
        self.stdout.write(f"  DEFAULT_FROM_EMAIL {settings.DEFAULT_FROM_EMAIL}")
        if not usa_consola:
            self.stdout.write(
                f"  SERVIDOR           {settings.EMAIL_HOST}:{settings.EMAIL_PORT} "
                f"(SSL={settings.EMAIL_USE_SSL}, TLS={settings.EMAIL_USE_TLS})"
            )

        if usa_consola:
            raise CommandError(
                "El backend es el de consola: los correos se imprimen aquí y no "
                "salen a internet. Llena EMAIL_HOST_USER y EMAIL_HOST_PASSWORD "
                "en backend/.env con una contraseña de aplicación de Google "
                "(https://myaccount.google.com/apppasswords)."
            )

        if opciones["solo_config"]:
            return

        destino = opciones["destino"]

        # Autenticar por separado distingue "credenciales malas" de
        # "el mensaje fue rechazado", que se arreglan distinto.
        self.stdout.write("\nAbriendo conexión SMTP…")
        try:
            conexion = get_connection()
            conexion.open()
        except smtplib.SMTPAuthenticationError as exc:
            raise CommandError(
                "Gmail rechazó las credenciales. Revisa que EMAIL_HOST_PASSWORD "
                "sea una contraseña de aplicación de 16 caracteres (no la "
                "contraseña normal de la cuenta) y que la verificación en dos "
                f"pasos esté activa.\nDetalle: {exc}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 — red, DNS, TLS, timeout…
            raise CommandError(
                f"No se pudo conectar a {settings.EMAIL_HOST}:{settings.EMAIL_PORT}. "
                f"Puede ser la red, un firewall o el puerto.\nDetalle: {exc}"
            ) from exc

        self.stdout.write(self.style.SUCCESS("Conexión y autenticación correctas."))

        try:
            enviados = send_mail(
                subject="Prueba de correo · FILEY Registros",
                message=(
                    "Si estás leyendo esto, el envío de correo del Core "
                    "Registros funciona y los códigos OTP van a llegar.\n\n"
                    "FILEY — Feria Internacional de la Lectura Yucatán"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destino],
                connection=conexion,
                fail_silently=False,
            )
        except Exception as exc:  # noqa: BLE001 — remitente rechazado, cuota…
            raise CommandError(f"El servidor aceptó la sesión pero rechazó el mensaje.\nDetalle: {exc}") from exc
        finally:
            conexion.close()

        if not enviados:
            raise CommandError("El proveedor no aceptó el mensaje (0 enviados).")

        self.stdout.write(
            self.style.SUCCESS(
                f"Correo de prueba enviado a {destino}. "
                "Si no aparece en la bandeja, revisa spam."
            )
        )
