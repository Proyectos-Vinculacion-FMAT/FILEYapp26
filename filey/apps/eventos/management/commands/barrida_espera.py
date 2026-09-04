"""
Borra los adjuntos en espera cuya sesión ya no existe (`CU-EVT-002`).

La cola de `servicios/en_espera.py` se vacía sola en cuatro momentos: al
enviarse la propuesta, al salir del formulario, al cerrar sesión y al
aparecer esa persona con otra sesión. **Ninguno ocurre si se cierra la
pestaña**, y quien cierra y no vuelve no los quita nunca. Este comando es
el suelo.

    python manage.py barrida_espera --todas
    python manage.py barrida_espera --feria 2027 --seco

.. warning:: El criterio es la sesión, **no una fecha**

   `EVT` no tiene política de días y no debe tenerla: aquí no se guardan
   borradores de solicitud, así que un adjunto suelto no significa nada
   fuera del rato en que alguien está llenando el formulario. Contar días
   sería inventarle una vida propia a algo que no la tiene — eso es de
   `STD`, donde los plazos son del negocio y los decide quien coordina.

   Así que se borra lo que quedó **sin dueño**: filas cuya `session_key`
   ya no está en la tabla de sesiones. La sesión dura 12 h deslizantes
   (`SESSION_COOKIE_AGE`), y ése es el único plazo que interviene — el
   del sistema, no uno de este dominio.

Lo invoca el mismo workflow programado que la barrida de `STD`
(`.github/workflows/barrida-diaria.yml`).

.. warning:: Recorre schemas, no filas

   `ArchivoEnEspera` vive en el schema de cada feria y ninguna consulta
   lleva filtro de edición (`ADR-0003`). Un ``ArchivoEnEspera.objects``
   desde `public` no ve **nada**: no falla, no devuelve nada, y el
   comando parecería no tener trabajo. Es el mismo aviso que lleva
   `apps/stands/management/commands/barrida_diaria.py`, y por lo mismo.

.. note:: Borra fila por fila, a propósito

   Un ``queryset.delete()`` sería una consulta en vez de N, pero lo que
   importa aquí no es la fila: es el **archivo**, que solo se va del
   disco cuando salta la señal `post_delete` de `models.py`. Django la
   emite también en un borrado en lote, así que lo que se gana yendo una
   a una es poder contar y registrar cuántas se fueron de cada feria —y
   que un archivo que no se pueda borrar no tumbe el resto de la barrida.
"""

import logging

from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.ferias.models import Feria

from ...models import ArchivoEnEspera

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Borra los adjuntos en espera de EVT a los que nadie volvió."

    def add_arguments(self, parser):
        parser.add_argument(
            "--feria", help="Slug de una edición. Sin esto hace falta --todas."
        )
        parser.add_argument(
            "--todas", action="store_true", help="Recorre todas las ediciones."
        )
        parser.add_argument(
            "--seco",
            action="store_true",
            help="Dice qué borraría y no toca nada.",
        )

    def handle(self, *args, **opciones):
        if not opciones["feria"] and not opciones["todas"]:
            raise CommandError("Hace falta --feria <slug> o --todas.")

        # Las sesiones vivas se leen **una vez y desde `public`**: la
        # tabla de sesiones es compartida (`SHARED_APPS`), mientras que
        # los adjuntos viven en el schema de cada feria. Preguntarlo
        # dentro de cada `schema_context` daría la misma respuesta N
        # veces.
        vivas = set(
            Session.objects.filter(expire_date__gt=timezone.now()).values_list(
                "session_key", flat=True
            )
        )

        if opciones["feria"]:
            ferias = Feria.reales.filter(slug=opciones["feria"])
            if not ferias:
                raise CommandError(f"No hay ninguna feria con el slug «{opciones['feria']}».")
        else:
            # `reales` y no `objects`: `django-tenants` exige una fila con
            # `schema_name="public"` que no es una feria, y entrar en su
            # schema a buscar tablas de `EVT` reventaría (`CLAUDE.md`).
            ferias = Feria.reales.all()

        total = 0
        for feria in ferias:
            total += self._de_una_feria(feria, vivas, opciones["seco"])

        marca = "Se borrarían" if opciones["seco"] else "Borrados"
        self.stdout.write(
            self.style.SUCCESS(f"{marca} {total} adjuntos en espera sin sesión viva.")
        )

    def _de_una_feria(self, feria, vivas: set, seco: bool) -> int:
        with schema_context(feria.schema_name):
            # `exclude(session_key__in=vivas)` se lleva también las filas
            # con `session_key` vacío, que son las que existían antes de
            # que la columna existiera. Es lo correcto: nacieron sin
            # dueño.
            huerfanos = list(ArchivoEnEspera.objects.exclude(session_key__in=vivas))
            if not huerfanos:
                return 0

            if seco:
                for archivo in huerfanos:
                    self.stdout.write(
                        f"  [{feria.slug}] {archivo.nombre_original or archivo.archivo.name}"
                        f" — subido el {archivo.subido_en:%Y-%m-%d}"
                    )
                return len(huerfanos)

            borrados = 0
            for archivo in huerfanos:
                try:
                    archivo.delete()
                except Exception:  # noqa: BLE001
                    # Un archivo que el almacén no deja borrar no puede
                    # tumbar la barrida de las demás ferias: se anota y se
                    # sigue. Mañana se vuelve a intentar.
                    logger.exception(
                        "No se pudo borrar el adjunto en espera %s de %s",
                        archivo.pk,
                        feria.schema_name,
                    )
                else:
                    borrados += 1

            self.stdout.write(f"  [{feria.slug}] {borrados}")
            return borrados
