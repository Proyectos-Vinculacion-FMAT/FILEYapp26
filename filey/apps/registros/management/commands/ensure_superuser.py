"""
Alta no interactiva del superusuario, para el despliegue (GitHub Actions).

Crea la cuenta del equipo técnico a partir de variables de entorno y le
da acceso irrestricto al panel administrativo FILEY. Es idempotente: si
la cuenta ya existe no la toca, así que se puede ejecutar en cada
despliegue sin efectos acumulativos.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.registros.models import Modulo, NivelPermiso, RolPermiso


class Command(BaseCommand):
    help = "Crea el superusuario si no existe, con credenciales del entorno."

    def handle(self, *args, **options):
        Usuario = get_user_model()
        correo = os.environ.get("SUPERUSER_EMAIL")
        contrasena = os.environ.get("SUPERUSER_PASSWORD")

        if not correo or not contrasena:
            self.stdout.write(
                self.style.ERROR(
                    "Falta SUPERUSER_EMAIL o SUPERUSER_PASSWORD en el entorno."
                )
            )
            return

        correo = correo.lower().strip()

        if Usuario.objects.filter(correo=correo).exists():
            self.stdout.write(self.style.SUCCESS(f"El superusuario {correo} ya existe."))
            return

        # El nombre va en tres campos desde el 2026-08-25. Son opcionales
        # aquí —una cuenta técnica puede no tener nombre de persona—, pero
        # si no se dan, la barra superior del panel saluda a nadie y el
        # avatar sale vacío. De ahí los valores por defecto.
        usuario = Usuario.objects.create_superuser(
            correo=correo,
            password=contrasena,
            # `or` y no el default de `get`: GitHub Actions define la
            # variable *vacía* cuando el secreto no existe, así que el
            # default nunca llegaría a aplicarse.
            nombre=os.environ.get("SUPERUSER_NOMBRE") or "Equipo",
            primer_apellido=os.environ.get("SUPERUSER_PRIMER_APELLIDO") or "FILEY",
            segundo_apellido=os.environ.get("SUPERUSER_SEGUNDO_APELLIDO") or "",
        )

        # Acceso irrestricto al panel administrativo FILEY (Modulo.TODOS).
        RolPermiso.objects.get_or_create(
            persona=usuario,
            modulo=Modulo.TODOS,
            defaults={"nivel": NivelPermiso.EDICION},
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superusuario {correo} creado con acceso administrativo completo."
            )
        )
