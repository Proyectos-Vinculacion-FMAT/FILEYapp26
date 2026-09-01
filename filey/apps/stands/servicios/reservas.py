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
from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.convocatorias.servicios import registros

from ..models import (
    BitacoraSTD,
    DescuentoAplicado,
    Movimiento,
    Reserva,
    ReservaStand,
    Solicitud,
    Stand,
)
from . import avisos, bitacora
from . import configuracion as servicio_configuracion

logger = logging.getLogger(__name__)

CENTAVO = Decimal("0.01")


class ReservaRechazada(Exception):
    """No se puede reservar. El mensaje dice qué falta."""


class YaTieneReserva(ReservaRechazada):
    """`RN-23`: esta editorial ya tiene su reserva en esta convocatoria.

    Excepción propia porque no es un error del que haya que recuperarse:
    es que la persona ya está un paso más adelante del flujo. La vista la
    usa para mandarla a su cuenta en vez de dejarla en el carrito
    leyendo un aviso rojo — lleva la reserva encima para poder hacerlo
    sin volver a buscarla.
    """

    def __init__(self, reserva):
        self.reserva = reserva
        super().__init__(
            "Ya tienes una reserva en esta convocatoria. "
            "Cada editorial lleva una sola: revisa la tuya en tu cuenta."
        )


class HayEspaciosTomados(ReservaRechazada):
    """`CU-STD-012` E1: alguien llegó antes.

    Excepción propia porque la pantalla hace algo distinto con ella: en
    vez de un aviso genérico, nombra los espacios perdidos y los saca del
    carrito para que la persona pueda reintentar en un clic.
    """

    def __init__(self, claves):
        self.claves = list(claves)
        super().__init__(
            "Alguien reservó antes que tú " + ", ".join(self.claves) + ". "
            "Los quitamos de tu selección: elige otros y vuelve a intentarlo."
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


def bruto_de(reserva: Reserva) -> Decimal:
    """El precio de los espacios sin descuentos, con la tarifa **de hoy**.

    Es la contrapartida conocida de que `ReservaStand` no guarde
    importes: si alguien cambió el `costo_m2` entre la reserva y ahora,
    esto sale con la tarifa nueva. Por eso no se cobra de aquí —lo
    cobrado es `monto_total`, congelado (`RN-01`)— y solo se usa para
    enseñar el desglose y para recalcular cuando un descuento cambia,
    que ya es una decisión deliberada de alguien.
    """
    costo_m2 = reserva.configuracion.costo_m2
    return sum(
        (linea.stand.precio(costo_m2) for linea in reserva.lineas.all()),
        start=Decimal("0.00"),
    )


def desglose_de(reserva: Reserva) -> list[Renglon]:
    """El desglose de una reserva ya creada, recalculado desde el mapa.

    **No cuadra necesariamente con `monto_total`**, por lo que dice
    `bruto_de`. Lo cobrado no se mueve — eso es `monto_total`, que está
    congelado.
    """
    _, renglones = total_con_descuentos(bruto_de(reserva), _pares_de(reserva))
    return renglones


def total_sin_pronto_pago(reserva: Reserva) -> Decimal:
    """Lo que costaría esta reserva si perdiera el pronto pago.

    Es la cifra que `CU-STD-013` paso 5 pide enseñar junto a la fecha de
    corte: no basta decir "se retira el descuento", hay que decir a
    cuánto sube. Se calcula **igual que lo hará
    `pagos.caducar_pronto_pago`** —mismo bruto, mismos descuentos menos
    ése— para que el aviso prometa exactamente lo que se va a cobrar.
    """
    return total_con_descuentos(
        bruto_de(reserva),
        _pares_de(reserva, excluir=(DescuentoAplicado.Tipo.PRONTO_PAGO,)),
    )[0]


def _pares_de(reserva: Reserva, *, excluir=()) -> list[tuple[str, int]]:
    """Los descuentos de la reserva, en el orden en que se aplican."""
    por_tipo = {d.tipo: d for d in reserva.descuentos.all()}
    return [
        (por_tipo[tipo].get_tipo_display(), por_tipo[tipo].porcentaje)
        for tipo in DescuentoAplicado.ORDEN
        if tipo in por_tipo and tipo not in excluir
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
    :raises YaTieneReserva: `RN-23`, con la reserva que ya existe.
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

    # `RN-01`: el precio se deriva de la superficie, y sin tarifa toda la
    # reserva vale cero. Una de esas no es gratis, es rota: no admite
    # abonos —el saldo pendiente ya es cero—, así que no puede confirmarse
    # nunca y vence a los treinta días con los espacios apartados. Vale
    # más no dejarla nacer. El panel ya se lo avisa a quien administra
    # (`falta_precio`); esto es lo que impide que se le adelante alguien.
    configuracion = servicio_configuracion.de_la_convocatoria(convocatoria)
    if not configuracion.costo_m2:
        raise ReservaRechazada(
            "Esta convocatoria todavía no tiene precio por m², así que no "
            "podemos calcular lo que costarían tus espacios. Escríbenos y lo "
            "resolvemos."
        )

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

    # `RN-23`. Se pregunta **dentro** de la transacción y con la fila del
    # registro bloqueada: sin el bloqueo, dos pestañas que confirman a la
    # vez leen las dos "no tiene ninguna" y la restricción de la base es
    # la que acaba reventando, con un `IntegrityError` en la cara de
    # alguien en vez de este mensaje.
    ya = (
        Reserva.objects.select_for_update()
        .filter(registro=aceptada.registro, estado__in=Reserva.VIVAS)
        .first()
    )
    if ya is not None:
        raise YaTieneReserva(ya)

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

    Sigue devolviendo un conjunto y no una sola aunque `RN-23` deje una
    viva: las canceladas se quedan, y el historial de lo que se intentó
    es lo que explica por qué unos espacios estuvieron apartados una
    semana. Para el flujo —"a dónde mando a esta persona"— la que
    importa es `reserva_viva_de`.
    """
    return (
        Reserva.objects.filter(
            registro__convocatoria=convocatoria, registro__persona=persona
        )
        .select_related("editorial", "registro__convocatoria")
        .prefetch_related("lineas__stand__mapa", "descuentos")
    )


def reserva_viva_de(convocatoria: Convocatoria, persona) -> Reserva | None:
    """La reserva que esta persona tiene en pie, si la hay (`RN-23`).

    Es **la** pregunta del ruteo del expositor: quien tiene una está en
    el último paso del flujo —su cuenta— y no en el mapa. Vive aquí y no
    en la vista porque la responde igual un comando de `manage.py`.

    "En pie" es `VIVAS`, que incluye la vencida: vencer no libera nada
    (`RN-12`), así que quien tiene una vencida sigue teniéndola y lo que
    necesita es justamente llegar a la pantalla donde puede pagarla.
    """
    if persona is None or not getattr(persona, "is_authenticated", False):
        return None
    return (
        Reserva.objects.filter(
            registro__convocatoria=convocatoria,
            registro__persona=persona,
            estado__in=Reserva.VIVAS,
        )
        .select_related("editorial", "registro__convocatoria")
        .prefetch_related("lineas__stand__mapa", "descuentos")
        .first()
    )


def de_la_convocatoria(convocatoria: Convocatoria):
    """Todas las reservas de la convocatoria (`CU-STD-028`)."""
    return (
        Reserva.objects.filter(registro__convocatoria=convocatoria)
        .select_related("editorial", "registro__persona")
        .prefetch_related("lineas__stand", "descuentos")
    )


def con_saldo(consulta):
    """La misma consulta, con lo abonado ya sumado en la base.

    `Reserva.monto_abonado` agrega por reserva, así que una lista lo
    pregunta una vez por fila. Esto lo trae en la misma consulta y la
    propiedad lo prefiere cuando está.

    Se aplica **al final**, sobre la consulta ya filtrada, y nunca antes
    de un `.values(...).annotate(Count(...))`: la unión con los
    movimientos multiplicaría las filas y los conteos de los chips
    saldrían inflados.
    """
    return consulta.annotate(
        _abonado=Coalesce(
            Sum(
                "movimientos__monto",
                filter=Q(movimientos__estado=Movimiento.Estado.VALIDADO),
            ),
            Value(Decimal("0.00")),
            # Explícito porque la reserva sin abonos mezcla un `Sum` nulo
            # con un literal, y ahí Django no adivina el tipo.
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
    )


# ── CU-STD-035 y 036 · resolver una reserva ───────────────────
#
# Las tres decisiones que solo toma una persona. `RN-12` es explícita: el
# sistema no libera reservas por su cuenta, ni siquiera cuando el plazo
# se agotó — notifica y espera. Esto es lo que hay al otro lado de esa
# espera.


class ResolucionRechazada(ReservaRechazada):
    """No se puede resolver así. El mensaje dice por qué."""


@transaction.atomic
def prorrogar(*, reserva: Reserva, administrador, fecha) -> Reserva:
    """Le da más plazo para cubrir el anticipo (`CU-STD-035`, pasos 4 a 7).

    Solo tiene sentido en una `por_confirmar`: es la única que está
    esperando el anticipo. Una confirmada ya lo cubrió y su plazo dejó de
    correr; una pagada no espera nada.

    La fecha nueva **tiene que estar en el futuro**. Una en el pasado
    dejaría la reserva vencida en el mismo instante, y la barrida diaria
    volvería a avisar de ella al día siguiente —que es justo lo que quien
    prorroga está intentando evitar—.

    Prorrogar no manda correo: el aplicante lo nota porque el aviso de su
    cuenta se apaga solo (`CU-STD-014`). Lo que sí cambia es que la
    barrida deja de contarla, porque compara sus avisos contra **esta**
    fecha (`servicios/vencimientos.py`).
    """
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)

    if reserva.estado != Reserva.Estado.POR_CONFIRMAR:
        raise ResolucionRechazada(
            f"Esta reserva está {reserva.get_estado_display().lower()}: no "
            "hay ningún plazo de anticipo que prorrogar."
        )
    if fecha is None:
        raise ResolucionRechazada("Elige hasta cuándo se amplía el plazo.")
    if fecha <= timezone.now():
        raise ResolucionRechazada(
            "La fecha nueva tiene que estar en el futuro: con una pasada, la "
            "reserva volvería a estar vencida hoy mismo."
        )

    anterior = reserva.fecha_vencimiento_anticipo
    Reserva.objects.filter(pk=reserva.pk).update(fecha_vencimiento_anticipo=fecha)
    reserva.refresh_from_db()
    logger.info(
        "Reserva %s prorrogada de %s a %s por %s",
        reserva.pk,
        anterior,
        fecha,
        administrador.pk,
    )
    # Sin esto, prorrogar es invisible: la fecha vieja se sobreescribe y
    # no queda dónde leer que alguien dio más tiempo, ni cuánto.
    bitacora.anotar(
        persona=administrador,
        accion=BitacoraSTD.Accion.RESERVA_PRORROGADA,
        objeto=reserva,
        vencia=anterior.isoformat(),
        vence=fecha.isoformat(),
    )
    return reserva


@transaction.atomic
def mover_fecha_de_corte(*, reserva: Reserva, administrador, fecha) -> Reserva:
    """Cambia hasta cuándo hay para liquidar (`CU-STD-036`, `RN-13`).

    La base es de la convocatoria y cada reserva hereda la suya al
    confirmarse (`CU-STD-026` paso 4); esto es el "caso por caso" que
    `RN-13` contempla.

    Se admite también antes de confirmar, aunque el caso de uso hable de
    una reserva confirmada: adelantarla no rompe nada y confirmar
    **respeta** la que ya esté puesta, en vez de pisarla con la de la
    convocatoria.

    Se puede dejar en blanco: es volver a "sin fecha de corte", que es un
    estado legítimo —una convocatoria puede no tenerla— y no un dato
    perdido.
    """
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)

    if reserva.estado == Reserva.Estado.CANCELADA:
        raise ResolucionRechazada(
            "Esta reserva está cancelada: ya no hay nada que liquidar."
        )

    anterior = reserva.fecha_corte_pago_total
    Reserva.objects.filter(pk=reserva.pk).update(fecha_corte_pago_total=fecha)
    reserva.refresh_from_db()
    logger.info(
        "Reserva %s: corte del pago total de %s a %s por %s",
        reserva.pk,
        anterior,
        fecha,
        administrador.pk,
    )
    bitacora.anotar(
        persona=administrador,
        accion=BitacoraSTD.Accion.CORTE_MOVIDO,
        objeto=reserva,
        antes=anterior.isoformat() if anterior else None,
        ahora=fecha.isoformat() if fecha else None,
    )
    return reserva


@transaction.atomic
def cancelar(*, reserva: Reserva, administrador, motivo: str = "") -> Reserva:
    """Cierra la reserva y devuelve sus espacios al mapa (`CU-STD-035` A1).

    Es **la única acción irreversible del dominio** y la única que
    libera espacios. `RN-11`: `cancelada` es el único estado de cierre y
    solo lo pone una persona — ni la barrida diaria ni ningún umbral
    llegan hasta aquí.

    Lo que hace, en este orden:

    1. cierra la reserva y deja escrito quién, cuándo y por qué;
    2. devuelve sus stands a `disponible` (`RN-10`), estuvieran
       `reservado` u `ocupado` — el paso 5 del caso de uso contempla los
       dos, porque también se cancela una reserva ya pagada;
    3. avisa al aplicante, **después del commit**.

    Los abonos validados **no se tocan**: el dinero entró de verdad y
    borrarlo sería falsear la contabilidad. Qué se hace con él se acuerda
    fuera del sistema, y el correo lo dice cuando hay saldo.

    Al liberar la única reserva viva del registro, `RN-23` deja de
    estorbar: esa editorial puede volver a reservar desde cero.
    """
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)

    if reserva.estado == Reserva.Estado.CANCELADA:
        raise ResolucionRechazada("Esta reserva ya estaba cancelada.")

    claves = [linea.stand.clave for linea in reserva.lineas.select_related("stand")]

    Reserva.objects.filter(pk=reserva.pk).update(
        estado=Reserva.Estado.CANCELADA,
        cancelada_por=administrador,
        fecha_cancelacion=timezone.now(),
        motivo_cancelacion=(motivo or "").strip()[:200],
    )
    Stand.objects.filter(lineas_de_reserva__reserva=reserva).update(
        estado=Stand.Estado.DISPONIBLE
    )
    reserva.refresh_from_db()

    logger.info(
        "Reserva %s cancelada por %s; vuelven al mapa %s",
        reserva.pk,
        administrador.pk,
        ", ".join(claves) or "—",
    )
    bitacora.anotar(
        persona=administrador,
        accion=BitacoraSTD.Accion.RESERVA_CANCELADA,
        objeto=reserva,
        motivo=reserva.motivo_cancelacion,
        espacios=claves,
        abonado=str(reserva.monto_abonado),
    )
    # Como los avisos de los umbrales: después del commit. Un correo no
    # se puede deshacer, y si la transacción se revierte la editorial se
    # habría enterado de una cancelación que no ocurrió.
    transaction.on_commit(lambda: avisos.avisar_cancelacion(reserva))
    return reserva
