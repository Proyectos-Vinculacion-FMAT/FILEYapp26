"""
Formalizar y consultar una reserva (`CU-STD-012`, `013`, `021`, `023`).

Aquí vive **el cálculo del dinero**, que es lo que hace que este módulo
importe más que ningún otro de `STD`: si el total sale mal, sale mal en
una factura.

.. important:: Los descuentos se aplican en secuencia, no sumando

   Un 10% y un 15% dan un **23.5%** efectivo, no un 25%. Sumar los
   porcentajes es el error natural y da de más en cada reserva con dos
   descuentos (`RN-06`). Por eso `total_con_descuentos` los recorre
   multiplicando y nadie más calcula un total.
"""

import logging
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import registros

from ..models import DescuentoAplicado, Reserva, ReservaStand, Solicitud, Stand
from . import configuracion as servicio_configuracion

logger = logging.getLogger(__name__)

CENTAVO = Decimal("0.01")


class ReservaRechazada(Exception):
    """No se puede reservar. El mensaje dice qué falta."""


class HayEspaciosTomados(ReservaRechazada):
    """`CU-STD-012` E1: alguien llegó antes.

    Excepción propia porque la pantalla hace algo distinto con ella: en
    vez de un aviso genérico, nombra los espacios perdidos y los saca del
    carrito para que la persona pueda reintentar en un clic.
    """

    def __init__(self, claves):
        self.claves = list(claves)
        super().__init__(
            "Alguien reservó antes " + ", ".join(self.claves) + ". "
            "Los quitamos de tu selección; elige otros y vuelve a intentarlo."
        )


# ── El dinero ─────────────────────────────────────────────────


@dataclass(frozen=True)
class Renglon:
    """Un paso del desglose, para poder enseñarlo tal como se calcula."""

    concepto: str
    porcentaje: int | None
    importe: Decimal
    subtotal: Decimal


def total_con_descuentos(
    bruto: Decimal, descuentos: list[tuple[str, int]]
) -> tuple[Decimal, list[Renglon]]:
    """El total y su desglose, aplicando los descuentos en secuencia.

    Es **la única** función que calcula un total. Devuelve también el
    desglose para que la pantalla no tenga que recalcularlo por su
    cuenta: dos sitios calculando lo mismo es cómo se llega a que la
    pantalla diga una cifra y el cobro otra.

    :param descuentos: pares ``(concepto, porcentaje)`` ya ordenados.
    :returns: ``(total, renglones)``.
    """
    subtotal = bruto.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    renglones = [Renglon("Subtotal", None, subtotal, subtotal)]
    for concepto, porcentaje in descuentos:
        importe = (subtotal * porcentaje / 100).quantize(
            CENTAVO, rounding=ROUND_HALF_UP
        )
        subtotal -= importe
        renglones.append(Renglon(concepto, porcentaje, -importe, subtotal))
    return subtotal, renglones


def desglose_de(reserva: Reserva) -> list[Renglon]:
    """El desglose de una reserva ya creada, recalculado desde el mapa.

    **No cuadra necesariamente con `monto_total`**, y es la contrapartida
    conocida de que `ReservaStand` no guarde snapshots: si alguien
    corrigió el mapa o cambió `costo_m2`, el subtotal de aquí sale con
    los valores de ahora. Lo cobrado no se mueve — eso es `monto_total`,
    que está congelado.
    """
    costo_m2 = reserva.configuracion.costo_m2
    bruto = sum(
        (linea.stand.precio(costo_m2) for linea in reserva.lineas.all()),
        start=Decimal("0.00"),
    )
    _, renglones = total_con_descuentos(bruto, _pares_de(reserva))
    return renglones


def _pares_de(reserva: Reserva) -> list[tuple[str, int]]:
    """Los descuentos de la reserva, en el orden en que se aplican."""
    por_tipo = {d.tipo: d for d in reserva.descuentos.all()}
    return [
        (por_tipo[tipo].get_tipo_display(), por_tipo[tipo].porcentaje)
        for tipo in DescuentoAplicado.ORDEN
        if tipo in por_tipo
    ]


def pronto_pago_vigente(convocatoria: Convocatoria) -> int:
    """El porcentaje de pronto pago que aplica hoy, o cero.

    Cero cuando la convocatoria no lo ofrece o cuando la fecha ya pasó:
    `RN-04` dice que el plazo es **una fecha de la convocatoria**, igual
    para todos, y no un contador por reserva. Quien reserva tarde tiene
    menos días — es una campaña con corte, y es deliberado.
    """
    # Se pide al servicio y no por `convocatoria.configuracion_stands`:
    # ese descriptor **cachea** la fila en la instancia, así que quien
    # acabe de cambiar la fecha límite en otra instancia —el admin, un
    # comando, la pantalla de configuración— seguiría leyendo la de
    # antes, y aquí lo que se decide es cuánto se cobra.
    configuracion = servicio_configuracion.de_la_convocatoria(convocatoria)
    limite = configuracion.fecha_limite_pronto_pago
    if not configuracion.descuento_pronto_pago or limite is None:
        return 0
    if timezone.localdate() > limite:
        return 0
    return configuracion.descuento_pronto_pago


# ── Crear la reserva ──────────────────────────────────────────


def cotizar(convocatoria: Convocatoria, stands: list[Stand]):
    """Lo que costaría reservar estos espacios, sin reservar nada.

    Es lo que enseña el paso 2 de `CU-STD-012` antes de confirmar, y lo
    mismo que se usa al confirmar: cotizar y cobrar con dos cálculos
    distintos es cómo se llega a que el resumen prometa una cifra y el
    cargo sea otra.
    """
    costo_m2 = servicio_configuracion.de_la_convocatoria(convocatoria).costo_m2
    bruto = sum((s.precio(costo_m2) for s in stands), start=Decimal("0.00"))
    porcentaje = pronto_pago_vigente(convocatoria)
    descuentos = [("Pronto pago", porcentaje)] if porcentaje else []
    return total_con_descuentos(bruto, descuentos)


@transaction.atomic
def crear(*, convocatoria: Convocatoria, persona, claves: list[str]) -> Reserva:
    """Formaliza la reserva de los espacios seleccionados (`CU-STD-012`).

    Todo lo que importa de esta función es que sea **una transacción con
    los stands bloqueados**. Sin el bloqueo, dos editoriales que
    confirman a la vez leen los dos "disponible", los dos escriben, y el
    mismo espacio queda vendido dos veces con dos anticipos cobrados.

    :raises ReservaRechazada: y no se crea nada.
    :raises HayEspaciosTomados: `E1`, con las claves perdidas.
    """
    if convocatoria.tipo != TipoConvocatoria.STD:
        raise ReservaRechazada(
            f"«{convocatoria.nombre}» no es una convocatoria de stands."
        )
    if convocatoria.estado != Convocatoria.Estado.ABIERTA:
        raise ReservaRechazada(
            f"«{convocatoria.nombre}» no está abierta: no admite reservas."
        )
    try:
        registros.exigir_edicion_operable()
    except registros.RegistroRechazado as exc:
        raise ReservaRechazada(str(exc)) from exc

    if not claves:
        # `E2`. No es un fallo del sistema: es que no eligió nada.
        raise ReservaRechazada(
            "Tu selección está vacía. Elige espacios en el mapa para reservar."
        )

    # `RN-16`: solo una solicitud aceptada habilita a reservar.
    aceptada = (
        Solicitud.objects.filter(
            registro__convocatoria=convocatoria,
            registro__persona=persona,
            estado=Solicitud.Estado.ACEPTADA,
        )
        .select_related("editorial", "registro")
        .first()
    )
    if aceptada is None:
        raise ReservaRechazada(
            "Para reservar hace falta una solicitud de expositor aceptada."
        )

    # `select_for_update` es lo que sostiene "primero en confirmar gana".
    # Se ordena por `pk` a propósito: dos peticiones que bloqueen las
    # mismas filas en orden distinto se abrazan y una muere por deadlock.
    stands = list(
        Stand.objects.select_for_update()
        .select_related("mapa")
        .filter(mapa__convocatoria=convocatoria, clave__in=claves)
        .order_by("pk")
    )
    encontradas = {s.clave for s in stands}
    if faltan := [c for c in claves if c not in encontradas]:
        raise ReservaRechazada(
            "Estos espacios ya no existen en el mapa: " + ", ".join(faltan) + "."
        )
    if tomados := [s.clave for s in stands if not s.esta_libre]:
        raise HayEspaciosTomados(tomados)

    total, _ = cotizar(convocatoria, stands)
    configuracion = servicio_configuracion.de_la_convocatoria(convocatoria)

    reserva = Reserva.objects.create(
        registro=aceptada.registro,
        editorial=aceptada.editorial,
        estado=Reserva.Estado.POR_CONFIRMAR,
        # `RN-03`. La fecha se congela: cambiar el plazo en la
        # convocatoria no debe mover el vencimiento de las que ya corren.
        fecha_vencimiento_anticipo=(
            timezone.now() + timezone.timedelta(days=configuracion.plazo_reserva_dias)
        ),
        monto_total=total,
    )
    ReservaStand.objects.bulk_create(
        [ReservaStand(reserva=reserva, stand=s) for s in stands]
    )

    # `CU-STD-021`: los espacios pasan a `reservado` al confirmarse. En
    # la misma transacción que la reserva — si no, un fallo entre las dos
    # dejaría stands bloqueados sin reserva que los explique, y nadie
    # sabría por qué no se pueden tomar.
    Stand.objects.filter(pk__in=[s.pk for s in stands]).update(
        estado=Stand.Estado.RESERVADO
    )

    if porcentaje := pronto_pago_vigente(convocatoria):
        # `aplicado_por` nulo: lo aplica el sistema (`CU-STD-023`), y
        # ponerle una persona sería atribuirle una decisión que no tomó.
        DescuentoAplicado.objects.create(
            reserva=reserva,
            tipo=DescuentoAplicado.Tipo.PRONTO_PAGO,
            porcentaje=porcentaje,
        )

    logger.info(
        "Reserva %s creada: %s espacios de «%s» para «%s», total %s",
        reserva.pk,
        len(stands),
        convocatoria.nombre,
        aceptada.editorial.nombre,
        total,
    )
    return reserva


# ── Consultarla ───────────────────────────────────────────────


def reservas_de(convocatoria: Convocatoria, persona):
    """Las reservas de esta persona en esta convocatoria (`CU-STD-013`).

    Devuelve todas y no "la suya": el modelo dice `Editorial 1—N
    Reserva`, y quien reserva en dos tandas tiene dos. Enseñar solo la
    última escondería una que sigue debiendo dinero.
    """
    return (
        Reserva.objects.filter(
            registro__convocatoria=convocatoria, registro__persona=persona
        )
        .select_related("editorial", "registro__convocatoria")
        .prefetch_related("lineas__stand__mapa", "descuentos")
    )


def de_la_convocatoria(convocatoria: Convocatoria):
    """Todas las reservas de la convocatoria (`CU-STD-028`)."""
    return (
        Reserva.objects.filter(registro__convocatoria=convocatoria)
        .select_related("editorial", "registro__persona")
        .prefetch_related("lineas__stand", "descuentos")
    )
