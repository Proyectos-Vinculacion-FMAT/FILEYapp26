"""
Da acceso administrativo a una persona sobre una feria (`CU-FER-003`).

Sustituye al `alta_admin` de `registros`, que otorgaba un `RolPermiso`
de módulo sobre todo el sistema. La diferencia no es de sintaxis: aquel
comando daba acceso a un **módulo**, éste lo da a una **feria**, y por
eso `--feria` es obligatorio (ADR-0004).

Lo normal es que el dueño de la feria dé de alta a sus administradores
desde el panel FILEY. Esa pantalla todavía no existe, así que hasta
entonces esta es la vía — y después sigue siendo la de emergencia.

Uso:
    python manage.py alta_admin_feria --feria 2027 --correo rita@filey.org \\
        --nombre Rita --apellido Uc
"""

from django.core.management.base import BaseCommand, CommandError

from apps.ferias.models import AdminFeria, Feria
from apps.registros.models import Persona


class Command(BaseCommand):
    help = "Da acceso administrativo a una persona sobre una feria (CU-FER-003)."

    def add_arguments(self, parser):
        parser.add_argument("--feria", required=True, help="Slug de la feria, p. ej. 2027")
        parser.add_argument("--correo", required=True)
        parser.add_argument("--nombre", default="", help="Solo si la cuenta es nueva")
        parser.add_argument("--apellido", default="", help="Primer apellido")

    def handle(self, *args, **opciones):
        slug = opciones["feria"].strip().lower()
        correo = opciones["correo"].strip().lower()

        # `reales` y no `objects`: la fila de sistema no es una feria y
        # nadie puede ser administrador de ella.
        feria = Feria.reales.filter(slug=slug).first()
        if feria is None:
            raise CommandError(
                f"No existe ninguna feria con el slug «{slug}». "
                "Créala primero con `manage.py alta_feria`."
            )

        persona = Persona.objects.filter(correo=correo).first()
        cuenta_creada = persona is None
        if cuenta_creada:
            persona = Persona.objects.create_user(
                correo=correo,
                nombre=opciones["nombre"],
                primer_apellido=opciones["apellido"],
            )

        acceso, creado = AdminFeria.objects.get_or_create(
            feria=feria,
            persona=persona,
            # `es_dueno` NO se toca aquí: el dueño se designa al crear la
            # feria (CU-FER-001) y transferirlo es otro caso de uso.
            defaults={"es_dueno": False},
        )
        if not creado:
            papel = "dueño" if acceso.es_dueno else "administrador"
            self.stdout.write(
                self.style.WARNING(f"{correo} ya era {papel} de «{feria.nombre}».")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"{correo} administra ahora «{feria.nombre}» ({feria.url})."
                f"{' Cuenta nueva.' if cuenta_creada else ''}"
            )
        )
