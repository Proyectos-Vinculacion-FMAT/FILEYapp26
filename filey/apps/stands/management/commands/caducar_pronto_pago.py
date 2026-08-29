"""
Retira el pronto pago de las reservas que no liquidaron a tiempo
(`CU-STD-023` A1).

Es la mitad de `RN-04` que necesita reloj: el descuento se aplica al
reservar, pero **es condicional**, y quien llega a la fecha de corte sin
cubrir el total lo pierde. Sin algo que lo dispare, la nota que el
carrito enseñó —"después de esa fecha se retira y el total vuelve a
subir"— no se cumple nunca.

Vive como comando y no como una comprobación al pintar la pantalla a
propósito: **cambia lo que se debe**, y una escritura escondida en un GET
se dispara con cualquier recarga y no deja a nadie decir cuándo pasó.

Lo llamará la barrida diaria de la fase 6; mientras tanto es lo que hay
que poner en el cron:

    python manage.py caducar_pronto_pago --feria 2027
    python manage.py caducar_pronto_pago --todas --seco
"""

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias.models import Feria
from apps.stands.models import DescuentoAplicado, Reserva
from apps.stands.servicios import pagos


class Command(BaseCommand):
    help = "Retira el pronto pago de las reservas vencidas sin liquidar."

    def add_arguments(self, parser):
        parser.add_argument(
            "--feria",
            help="Slug de una edición. Sin esto hace falta --todas.",
        )
        parser.add_argument(
            "--todas",
            action="store_true",
            help="Recorre todas las ediciones reales.",
        )
        parser.add_argument(
            "--seco",
            action="store_true",
            help="Dice qué haría y no toca nada.",
        )

    def handle(self, *args, **opciones):
        if not opciones["feria"] and not opciones["todas"]:
            raise CommandError("Dime --feria <slug> o --todas.")

        ferias = list(Feria.reales.all())
        if opciones["feria"]:
            ferias = [f for f in ferias if f.slug == opciones["feria"]]
            if not ferias:
                raise CommandError(
                    f"No hay ninguna feria con el slug «{opciones['feria']}»."
                )

        total = 0
        for feria in ferias:
            # Cada feria en su schema (`ADR-0003`): un comando no pasa por
            # el middleware que lo fija en una petición.
            with schema_context(feria.schema_name):
                for convocatoria in Convocatoria.objects.filter(
                    tipo=TipoConvocatoria.STD
                ):
                    total += self._una(convocatoria, feria, opciones["seco"])

        self.stdout.write(
            self.style.SUCCESS(f"{total} reserva(s) perdieron el pronto pago.")
        )

    def _una(self, convocatoria, feria, seco: bool) -> int:
        if seco:
            # En seco se pregunta sin escribir: se mira cuáles **tendrían**
            # que perderlo, con la misma condición que el servicio.
            candidatas = [
                r
                for r in Reserva.objects.filter(
                    registro__convocatoria=convocatoria,
                    estado__in=Reserva.VIVAS,
                ).prefetch_related("descuentos")
                if self._le_toca(r)
            ]
            for reserva in candidatas:
                self.stdout.write(
                    f"  [seco] {feria.slug} · {convocatoria.nombre} · "
                    f"reserva {reserva.pk} ({reserva.editorial.nombre})"
                )
            return len(candidatas)

        tocadas = pagos.caducar_los_pronto_pago(convocatoria)
        for reserva in tocadas:
            self.stdout.write(
                f"  {feria.slug} · {convocatoria.nombre} · reserva {reserva.pk} "
                f"({reserva.editorial.nombre}) → ${reserva.monto_total}"
            )
        return len(tocadas)

    @staticmethod
    def _le_toca(reserva) -> bool:
        """La misma condición del servicio, sin escribir."""
        from django.utils import timezone

        limite = reserva.configuracion.fecha_limite_pronto_pago
        return (
            limite is not None
            and timezone.localdate() > limite
            and reserva.descuentos.filter(
                tipo=DescuentoAplicado.Tipo.PRONTO_PAGO
            ).exists()
            and reserva.monto_abonado < reserva.monto_total
        )
