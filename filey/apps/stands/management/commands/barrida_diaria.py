"""
La barrida diaria de `STD` (`CU-STD-022`, `023` A1, `024`, `025`).

**Es una sola tarea, no seis.** El plan llegó a decir "los seis procesos
temporizados" y los casos de uso no lo sostienen: los umbrales del 50% y
del 100% se disparan dentro de la petición que cambia el saldo, y el
pronto pago se aplica al reservar. Lo único que hay que mirar con un
calendario delante es qué plazos se agotaron, y eso se hace una vez al
día:

1. **Retirar el pronto pago** de quien llegó a la fecha de corte sin
   liquidar (`CU-STD-023` A1). Cambia lo que se debe.
2. **Avisar de las reservas vencidas** a la editorial (`CU-STD-025`) y a
   quien administra (`CU-STD-024`). No cambia nada: `RN-12` dice que
   vencer no libera, así que la decisión es de una persona.

Los dos pasos van juntos y en este orden porque el primero **sube el
total**, y con él sube el anticipo: una reserva que estaba al filo puede
quedar corta el mismo día que pierde el descuento, y el aviso tiene que
salir con las cifras de después.

    python manage.py barrida_diaria --todas
    python manage.py barrida_diaria --feria 2027 --seco

Lo invoca un workflow programado de GitHub Actions
(`.github/workflows/barrida-diaria.yml`).

.. warning:: Recorre schemas, no filas

   `Reserva` vive en el schema de cada feria y ninguna consulta lleva
   filtro de edición (`ADR-0003`). Un ``Reserva.objects.filter(...)``
   desde `public` no ve **nada**: no falla, no devuelve nada, y el
   comando parecería no tener trabajo.

.. warning:: Solo ediciones vivas

   Una feria archivada se consulta, no se opera (`CU-FER-006` E1). No le
   manda avisos de vencimiento a nadie ni le retira descuentos: sus
   reservas ya no están en juego y el correo solo confundiría.
"""

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias.models import Feria
from apps.stands.models import Notificacion
from apps.stands.servicios import pagos, vencimientos


class Command(BaseCommand):
    help = (
        "Retira los pronto pago vencidos y avisa de las reservas que se "
        "quedaron sin plazo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--feria", help="Slug de una edición. Sin esto hace falta --todas."
        )
        parser.add_argument(
            "--todas", action="store_true", help="Recorre todas las ediciones vivas."
        )
        parser.add_argument(
            "--seco",
            action="store_true",
            help="Dice qué haría y no toca nada: ni escribe ni manda correos.",
        )

    def handle(self, *args, **opciones):
        if not opciones["feria"] and not opciones["todas"]:
            raise CommandError("Dime --feria <slug> o --todas.")

        ferias = [
            f for f in Feria.reales.all() if f.estado != Feria.Estado.ARCHIVADA
        ]
        if opciones["feria"]:
            ferias = [f for f in ferias if f.slug == opciones["feria"]]
            if not ferias:
                raise CommandError(
                    f"No hay ninguna edición viva con el slug "
                    f"«{opciones['feria']}»."
                )

        caducados = avisadas = 0
        for feria in ferias:
            # Cada feria en su schema (`ADR-0003`): un comando no pasa por
            # el middleware que lo fija en una petición.
            with schema_context(feria.schema_name):
                for convocatoria in Convocatoria.objects.filter(
                    tipo=TipoConvocatoria.STD
                ):
                    caducados += self._pronto_pago(
                        feria, convocatoria, opciones["seco"]
                    )
                    avisadas += self._vencidas(feria, convocatoria, opciones["seco"])

        self.stdout.write(
            self.style.SUCCESS(
                f"{caducados} reserva(s) perdieron el pronto pago · "
                f"{avisadas} reserva(s) vencidas avisadas."
            )
        )

    # ── 1 · CU-STD-023 A1 ─────────────────────────────────────

    def _pronto_pago(self, feria, convocatoria, seco: bool) -> int:
        if seco:
            self.stdout.write(
                f"  [seco] {feria.slug} · {convocatoria.nombre}: mira "
                "`manage.py caducar_pronto_pago --seco` para el detalle."
            )
            return 0
        tocadas = pagos.caducar_los_pronto_pago(convocatoria)
        for reserva in tocadas:
            self.stdout.write(
                f"  pronto pago retirado · {feria.slug} · reserva {reserva.pk} "
                f"({reserva.editorial.nombre}) → ${reserva.monto_total}"
            )
        return len(tocadas)

    # ── 2 · CU-STD-022, 024 y 025 ─────────────────────────────

    def _vencidas(self, feria, convocatoria, seco: bool) -> int:
        if seco:
            # En seco se enseña **lo que se avisaría**, no todo lo vencido:
            # lo ya avisado no vuelve a salir, y confundir las dos cosas
            # haría creer que la barrida manda correos todos los días.
            candidatas = [
                r
                for r in vencimientos.vencidas(convocatoria)
                if vencimientos.falta_avisar(
                    r, Notificacion.Tipo.POSIBLE_CANCELACION
                )
            ]
            for reserva in candidatas:
                self.stdout.write(
                    f"  [seco] vencida · {feria.slug} · reserva {reserva.pk} "
                    f"({reserva.editorial.nombre}) desde el "
                    f"{reserva.fecha_vencimiento_anticipo:%d/%m/%Y}"
                )
            return len(candidatas)

        tocadas = vencimientos.barrer(convocatoria)
        for reserva in tocadas:
            self.stdout.write(
                f"  vencida avisada · {feria.slug} · reserva {reserva.pk} "
                f"({reserva.editorial.nombre})"
            )
        return len(tocadas)
