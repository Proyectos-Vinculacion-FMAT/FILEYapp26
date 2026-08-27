"""
Da acceso administrativo a una persona sobre una feria (`CU-FER-003`).

Sustituye al `alta_admin` de `registros`, que otorgaba un `RolPermiso`
de módulo sobre todo el sistema. La diferencia no es de sintaxis: aquel
comando daba acceso a un **módulo**, éste lo da a una **feria**, y por
eso `--feria` es obligatorio (ADR-0004).

Lo normal es que el dueño lo haga desde el panel de su feria
(`/f/<slug>/accesos/`, construido el 2026-08-26). Esto es la vía de
emergencia: sirve cuando el dueño no puede entrar, o cuando hay que
reparar accesos desde el servidor.

No repite la regla de la pantalla: los dos llaman a
`servicios/accesos.py`, que es lo que garantiza que dar acceso por
consola y darlo desde el panel dejen el mismo estado.

Uso:
    python manage.py alta_admin_feria --feria 2027 --correo rita@filey.org \\
        --nombre Rita --apellido Uc
"""

from django.core.management.base import BaseCommand, CommandError

from apps.ferias.models import Feria
from apps.ferias.servicios import accesos


class Command(BaseCommand):
    help = "Da acceso administrativo a una persona sobre una feria (CU-FER-003)."

    def add_arguments(self, parser):
        parser.add_argument("--feria", required=True, help="Slug de la feria, p. ej. 2027")
        parser.add_argument("--correo", required=True)
        parser.add_argument("--nombre", default="", help="Solo si la cuenta es nueva")
        parser.add_argument("--apellido", default="", help="Primer apellido")
        parser.add_argument(
            "--sin-aviso",
            action="store_true",
            help="No enviar el correo de aviso (CU-FER-003, paso 6).",
        )

    def handle(self, *args, **opciones):
        slug = opciones["feria"].strip().lower()

        # `reales` y no `objects`: la fila de sistema no es una feria y
        # nadie puede ser administrador de ella.
        feria = Feria.reales.filter(slug=slug).first()
        if feria is None:
            raise CommandError(
                f"No existe ninguna feria con el slug «{slug}». "
                "Créala primero con `manage.py alta_feria`."
            )

        try:
            resultado = accesos.dar_acceso(
                feria=feria,
                correo=opciones["correo"],
                nombre=opciones["nombre"],
                primer_apellido=opciones["apellido"],
                # Nulo a propósito: no se lo dio nadie de dentro de la
                # feria, lo concedió el operador desde el servidor.
                concedido_por=None,
                enviar_aviso=not opciones["sin_aviso"],
            )
        except accesos.AccesoRechazado as exc:
            raise CommandError(str(exc)) from exc

        correo = resultado.persona.correo

        if resultado.ya_tenia_acceso:
            papel = "dueño" if resultado.acceso.es_dueno else "administrador"
            self.stdout.write(
                self.style.WARNING(f"{correo} ya era {papel} de «{feria.nombre}».")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"{correo} administra ahora «{feria.nombre}» ({feria.url})."
                f"{' Cuenta nueva.' if resultado.cuenta_creada else ''}"
            )
        )
        if resultado.error_aviso:
            # E3: el acceso vale; lo que falló es el aviso.
            self.stdout.write(
                self.style.WARNING(
                    f"El correo de aviso no salió ({resultado.error_aviso}). "
                    "Puede entrar igual: compártele la dirección de la feria."
                )
            )
