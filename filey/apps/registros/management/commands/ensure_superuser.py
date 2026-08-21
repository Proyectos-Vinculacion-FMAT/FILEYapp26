"""
Management command to create a superuser non-interactively using environment variables.
Designed for CI/CD pipelines (e.g., GitHub Actions).
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.registros.models import Modulo, RolPermiso, NivelPermiso

class Command(BaseCommand):
    help = 'Creates a superuser if it does not exist, using credentials from env vars.'

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.environ.get('SUPERUSER_EMAIL')
        password = os.environ.get('SUPERUSER_PASSWORD')

        if not email or not password:
            self.stdout.write(self.style.ERROR('SUPERUSER_EMAIL or SUPERUSER_PASSWORD environment variable is missing.'))
            return

        # Comprobar si el usuario ya existe
        if User.objects.filter(correo=email).exists():
            self.stdout.write(self.style.SUCCESS(f'Superuser {email} already exists.'))
            return

        # Crear el superusuario
        user = User.objects.create_superuser(correo=email, password=password)
        
        # Darle acceso irrestricto al sistema administrativo FILEY (Modulo.TODOS)
        RolPermiso.objects.get_or_create(
            persona=user,
            modulo=Modulo.TODOS,
            defaults={'nivel': NivelPermiso.EDICION}
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser {email} with full admin access.'))
