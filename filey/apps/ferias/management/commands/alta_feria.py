"""
Alta de una feria por consola (`CU-FER-001`).

El alta habitual se hace desde `/django-admin/`. Este comando no es
redundante: es la vía cuando el admin es justo lo que no está
disponible —una base recién creada sin superusuario, un entorno que se
está reconstruyendo, un despliegue automatizado—.

Ambos llaman al mismo servicio, así que hacen exactamente lo mismo.

Uso:
    python manage.py alta_feria --nombre "FILEY 2027" --slug 2027 \\
        --correo-dueno ana@uady.mx --nombre-dueno Ana --apellido-dueno Pech
"""

from django.core.management.base import BaseCommand, CommandError

from apps.ferias.servicios import altas


class Command(BaseCommand):
    help = "Crea una feria, su schema migrado y su dueño (CU-FER-001)."

    def add_arguments(self, parser):
        parser.add_argument("--nombre", required=True, help='P. ej. "FILEY 2027"')
        parser.add_argument(
            "--slug",
            required=True,
            help="Prefijo de URL y raíz del schema. No cambia nunca.",
        )
        parser.add_argument(
            "--correo-dueno", required=True, help="Correo de quien administrará la feria"
        )
        parser.add_argument("--nombre-dueno", default="", help="Solo si la cuenta es nueva")
        parser.add_argument("--apellido-dueno", default="", help="Primer apellido")
        parser.add_argument("--segundo-apellido-dueno", default="")
        parser.add_argument("--edicion", default="", help='Ordinal, p. ej. "XIV"')
        parser.add_argument("--sede", default="")
        parser.add_argument(
            "--sin-aviso",
            action="store_true",
            help="No enviar el correo al dueño (A2: preparar ediciones con antelación)",
        )

    def handle(self, *args, **opciones):
        try:
            resultado = altas.crear_feria(
                nombre=opciones["nombre"],
                slug=opciones["slug"],
                correo_dueno=opciones["correo_dueno"],
                nombre_dueno=opciones["nombre_dueno"],
                primer_apellido_dueno=opciones["apellido_dueno"],
                segundo_apellido_dueno=opciones["segundo_apellido_dueno"],
                edicion=opciones["edicion"],
                sede=opciones["sede"],
                enviar_aviso=not opciones["sin_aviso"],
            )
        except altas.AltaRechazada as exc:
            # E1: nada que deshacer, no se llegó a crear nada.
            raise CommandError(str(exc)) from exc

        feria = resultado.feria
        # Paso 9: confirmar indicando el schema y quién quedó como dueño.
        self.stdout.write(
            self.style.SUCCESS(
                f"Feria «{feria.nombre}» creada.\n"
                f"  schema : {feria.schema_name}\n"
                f"  URL    : {feria.url}\n"
                f"  dueño  : {resultado.dueno.correo}"
                f"{' (cuenta nueva)' if resultado.cuenta_creada else ' (cuenta existente)'}"
            )
        )

        if opciones["sin_aviso"]:
            self.stdout.write("Aviso omitido (--sin-aviso).")
        elif resultado.aviso_enviado:
            self.stdout.write(self.style.SUCCESS(f"Aviso enviado a {resultado.dueno.correo}."))
        else:
            # E3: el alta sigue siendo válida; solo no salió el correo.
            self.stdout.write(
                self.style.WARNING(
                    f"La feria quedó creada, pero el aviso a {resultado.dueno.correo} "
                    f"no se pudo enviar.\n  Detalle: {resultado.error_aviso}"
                )
            )
