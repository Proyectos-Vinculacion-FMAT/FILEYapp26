"""
Abonos, su validación y lo que disparan (`CU-STD-015` a `020`, `026`, `027`).

Aquí vive la otra mitad del dinero. `servicios/reservas.py` calcula lo
que cuesta; esto lleva la cuenta de lo que se ha pagado y mueve la
reserva cuando el saldo cruza un umbral.

.. important:: Los umbrales **no necesitan reloj**

   `RN-13` (50% → `confirmada`) y `RN-14` (100% → `pagada`) se evalúan
   dentro de la misma petición que cambia el saldo — validar un abono,
   aplicar un descuento—, de forma síncrona. No hay nada que esperar, y
   un proceso temporizado solo añadiría un retraso entre pagar y verlo.

   Lo único que sí necesita reloj es la barrida de reservas vencidas
   (fase 6), que es otra cosa.

.. important:: Un descuento mueve el total y obliga a reevaluar

   `monto_total` se congela frente al **precio** —cambiar el `costo_m2`
   no alcanza a quien ya aceptó uno— pero **no frente a los descuentos**:
   aplicar o retirar uno es una modificación deliberada de lo que esa
   reserva cuesta. Y bajar el total puede dejar una reserva `pagada` sin
   que entre un peso más, así que después de tocarlo hay que volver a
   pasar por los umbrales.
"""

import logging
from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from ..models import (
    DescuentoAplicado,
    Documento,
    Movimiento,
    Reserva,
    Stand,
)
from . import reservas as servicio_reservas

logger = logging.getLogger(__name__)


class PagoRechazado(Exception):
    """El abono no se puede registrar o validar. El mensaje dice por qué."""


# ── CU-STD-016 y 019 · registrar un abono ─────────────────────


@transaction.atomic
def registrar(
    *,
    reserva: Reserva,
    persona,
    monto: Decimal,
    metodo: str,
    archivo=None,
    manual: bool = False,
) -> Movimiento:
    """Deja constancia de un abono, **sin sumarlo al saldo**.

    Nace `pendiente_validacion` y ahí se queda hasta que alguien
    compruebe contra el banco (`CU-STD-018`). Es la diferencia entre lo
    que alguien dice que pagó y lo que la feria cobró.

    :param manual: lo registra la administración (`CU-STD-019`). Entonces
        el comprobante **es obligatorio** (`RN-15`) y el origen queda
        marcado, para que el historial diga quién lo metió.
    :raises PagoRechazado: y no se crea nada.
    """
    if reserva.estado == Reserva.Estado.CANCELADA:
        raise PagoRechazado("Esta reserva está cancelada: no admite abonos.")
    if monto is None or monto <= 0:
        raise PagoRechazado("El monto tiene que ser mayor que cero.")
    if metodo not in Movimiento.Metodo.values:
        # `RN-08`: nunca efectivo. Los tres que quedan dejan rastro
        # bancario, que es lo que hace comprobable la validación.
        raise PagoRechazado(f"«{metodo}» no es un método de pago admitido.")

    # `CU-STD-016` E2. Se compara contra lo pendiente y no contra el
    # total: con un abono ya validado, el tope es lo que falta.
    pendiente = reserva.monto_pendiente
    if monto > pendiente:
        raise PagoRechazado(
            f"El pago de ${monto} es mayor que el saldo pendiente de "
            f"${pendiente}. Ajusta el monto."
        )

    # Y lo ya reportado también ocupa sitio. Sin esto, quien pulsa dos
    # veces —o vuelve a reportar la misma transferencia porque no la ve
    # sumada— deja dos declaraciones idénticas en la cola, y quien las
    # valide a las dos cobra el doble de lo que entró al banco.
    #
    # No es lo mismo que el tope de arriba: `monto_pendiente` solo
    # descuenta lo **validado** (`CU-STD-018`), a propósito. Esto de aquí
    # es el hueco que queda **después** de lo que está en revisión, y se
    # libera solo si alguien rechaza un abono.
    en_revision = reserva.movimientos.filter(
        estado=Movimiento.Estado.PENDIENTE
    ).aggregate(models.Sum("monto"))["monto__sum"] or Decimal("0.00")
    if monto > pendiente - en_revision:
        raise PagoRechazado(
            f"Tienes ${en_revision} en revisión. Sobre el saldo de "
            f"${pendiente}, puedes registrar hasta "
            f"${pendiente - en_revision}."
        )

    if manual and archivo is None:
        raise PagoRechazado(
            "Un pago que registra la administración necesita comprobante. "
            "Adjúntalo para poder guardarlo."
        )

    comprobante = None
    if archivo is not None:
        # El comprobante es un documento **de la editorial**, como la
        # constancia fiscal: quien lo puede ver es su dueña y quien
        # administra, y de eso ya se ocupa `servicios/archivos.py`.
        comprobante = Documento.objects.create(
            tipo=Documento.Tipo.COMPROBANTE_PAGO,
            archivo=archivo,
            nombre_original=archivo.name[:255],
            editorial=reserva.editorial,
        )

    movimiento = Movimiento.objects.create(
        reserva=reserva,
        monto=monto,
        metodo=metodo,
        origen=(
            Movimiento.Origen.ADMIN_MANUAL if manual else Movimiento.Origen.APLICANTE
        ),
        estado=Movimiento.Estado.PENDIENTE,
        comprobante=comprobante,
        registrado_por=persona,
    )
    logger.info(
        "Abono registrado: %s en la reserva %s (%s)",
        monto,
        reserva.pk,
        movimiento.origen,
    )
    return movimiento


def de_la_convocatoria(convocatoria, *, estado: str | None = None):
    """Los movimientos de esta convocatoria (`CU-STD-018`, vista A5).

    La cola de validación es **transversal**: cruza todas las reservas de
    la convocatoria, porque quien coteja el banco lo hace por lotes y no
    reserva por reserva. La otra puerta a la misma acción es el detalle
    de una reserva (A4).

    Sin `estado` vienen todos; la pantalla llega pidiendo los
    `pendiente_validacion`, que es su trabajo del día.
    """
    movimientos = Movimiento.objects.filter(
        reserva__registro__convocatoria=convocatoria
    ).select_related(
        "reserva__editorial",
        "reserva__registro__persona",
        "comprobante",
        "registrado_por",
        "validado_por",
    )
    if estado:
        movimientos = movimientos.filter(estado=estado)
    return movimientos


# ── CU-STD-018 · validar o rechazar ───────────────────────────


@transaction.atomic
def validar(*, movimiento: Movimiento, administrador) -> Reserva:
    """Da el abono por bueno y reevalúa la reserva (`CU-STD-018`).

    El bloqueo de la reserva es lo que importa: dos administradores
    validando dos abonos a la vez leerían los dos el mismo
    `monto_abonado` de antes, y la reserva podría quedarse en
    `por_confirmar` habiendo cobrado el total.
    """
    if movimiento.estado != Movimiento.Estado.PENDIENTE:
        raise PagoRechazado(
            f"Este movimiento ya está {movimiento.get_estado_display().lower()}."
        )

    reserva = Reserva.objects.select_for_update().get(pk=movimiento.reserva_id)

    movimiento.estado = Movimiento.Estado.VALIDADO
    movimiento.validado_por = administrador
    movimiento.fecha_validacion = timezone.now()
    movimiento.save(update_fields=["estado", "validado_por", "fecha_validacion"])

    logger.info("Abono %s validado por %s", movimiento.pk, administrador.pk)
    return reevaluar(reserva)


@transaction.atomic
def rechazar(*, movimiento: Movimiento, administrador, motivo: str = "") -> Movimiento:
    """`A1`: el comprobante no vale. El monto no toca el saldo.

    El motivo es opcional según el caso de uso, y aun así conviene: el
    aplicante ve el rechazo en su historial (`CU-STD-017`), y sin motivo
    solo ve que se rechazó.
    """
    if movimiento.estado != Movimiento.Estado.PENDIENTE:
        raise PagoRechazado(
            f"Este movimiento ya está {movimiento.get_estado_display().lower()}."
        )

    movimiento.estado = Movimiento.Estado.RECHAZADO
    movimiento.validado_por = administrador
    movimiento.fecha_validacion = timezone.now()
    movimiento.motivo_rechazo = (motivo or "")[:200]
    movimiento.save(
        update_fields=["estado", "validado_por", "fecha_validacion", "motivo_rechazo"]
    )
    logger.info("Abono %s rechazado por %s", movimiento.pk, administrador.pk)
    return movimiento


# ── CU-STD-020 · el descuento especial ────────────────────────


@transaction.atomic
def aplicar_descuento_especial(
    *, reserva: Reserva, administrador, porcentaje: int, motivo: str
) -> Reserva:
    """Un descuento manual, con su motivo (`CU-STD-020`, `RN-07`).

    Cambia lo que la reserva cuesta, así que **recalcula
    `monto_total` y vuelve a pasar por los umbrales**: bajar el total
    puede dejar pagada una reserva sin que entre un peso más.

    `RN-05` lo topa en uno por reserva, y lo topa la base. Aquí el
    segundo intento **sí es un error que se enseña** —al revés que el
    pronto pago, que es automático e idempotente—: para cambiar el
    porcentaje hay que retirar el que hay.
    """
    if not motivo or not motivo.strip():
        raise PagoRechazado(
            "Escribe el motivo del descuento: es dinero que la feria decide "
            "no cobrar."
        )
    if not 1 <= porcentaje <= 100:
        raise PagoRechazado("El porcentaje tiene que estar entre 1 y 100.")
    if reserva.descuentos.filter(tipo=DescuentoAplicado.Tipo.ESPECIAL).exists():
        raise PagoRechazado(
            "Esta reserva ya tiene un descuento especial. Retíralo antes de "
            "aplicar otro."
        )

    DescuentoAplicado.objects.create(
        reserva=reserva,
        tipo=DescuentoAplicado.Tipo.ESPECIAL,
        porcentaje=porcentaje,
        motivo=motivo.strip()[:200],
        aplicado_por=administrador,
    )
    logger.info(
        "Descuento especial del %s%% en la reserva %s por %s",
        porcentaje,
        reserva.pk,
        administrador.pk,
    )
    return _recalcular_total(reserva)


# ── CU-STD-023 A1 · el pronto pago que caduca ─────────────────


@transaction.atomic
def caducar_pronto_pago(reserva: Reserva) -> Reserva:
    """Retira el pronto pago de una reserva que no liquidó a tiempo.

    `RN-04`: el descuento se ofrece por adelantado —se aplica al reservar
    (`CU-STD-012` paso 3) para que la cifra que se acepta ya lo lleve—
    pero **es condicional**. Si llega la fecha de corte sin que el saldo
    esté cubierto, el beneficio se retira y el total vuelve a subir
    (`CU-STD-023` A1).

    Sin esto, quien reserva la víspera del corte y paga tres meses tarde
    conserva el descuento para siempre, y la nota que el carrito le
    enseñó —"después de esa fecha se retira"— sería mentira.

    Es **idempotente y conservadora**: no toca una reserva cancelada, ni
    una que ya liquidó, ni una sin pronto pago, ni una cuya fecha sigue
    vigente. Se puede llamar todos los días sobre todas las reservas.

    Un descuento **especial** que hubiera se conserva (`CU-STD-023` A1
    paso 3): son independientes, y vencer una campaña no revoca un
    convenio.

    :returns: la reserva, con el total ya al día si hubo que tocarlo.
    """
    if reserva.estado in (Reserva.Estado.CANCELADA, Reserva.Estado.PAGADA):
        return reserva

    configuracion = reserva.configuracion
    limite = configuracion.fecha_limite_pronto_pago
    if limite is None or timezone.localdate() <= limite:
        return reserva

    descuento = reserva.descuentos.filter(
        tipo=DescuentoAplicado.Tipo.PRONTO_PAGO
    ).first()
    if descuento is None:
        return reserva

    # "Liquidada" es cubrir el total **ya descontado** (`RN-04`). Quien
    # llegó a la fecha con todo pagado se lo queda: el descuento se
    # consolidó, y esta función no le quita nada.
    if reserva.monto_abonado >= reserva.monto_total:
        return reserva

    logger.info(
        "Reserva %s pierde el pronto pago del %s%%: venció el %s con %s de %s",
        reserva.pk,
        descuento.porcentaje,
        limite,
        reserva.monto_abonado,
        reserva.monto_total,
    )
    descuento.delete()
    # Se recalcula sobre una instancia **recién traída**, no sobre la que
    # llegó. `_recalcular_total` lee los descuentos con
    # `reserva.descuentos.all()`, y si quien llamó venía de un
    # `prefetch_related("descuentos")` esa llamada devuelve la caché —con
    # el descuento que se acaba de borrar todavía dentro—, así que el
    # total salía idéntico y la barrida no cambiaba nada.
    return _recalcular_total(Reserva.objects.get(pk=reserva.pk))


def caducar_los_pronto_pago(convocatoria) -> list[Reserva]:
    """Pasa `caducar_pronto_pago` por las reservas de una convocatoria.

    Es lo que corre la barrida diaria (fase 6) y, mientras no exista,
    `manage.py caducar_pronto_pago`. Devuelve **solo las que cambiaron**,
    para que quien la llame pueda decir qué hizo.
    """
    tocadas = []
    # `descuentos` **no** se precarga a propósito: `caducar_pronto_pago`
    # los borra, y una caché de lo que ya no está es exactamente lo que
    # haría que el recálculo saliera igual que antes.
    reservas_vivas = Reserva.objects.filter(
        registro__convocatoria=convocatoria, estado__in=Reserva.VIVAS
    ).select_related("registro__convocatoria", "editorial")
    for reserva in reservas_vivas:
        antes = reserva.monto_total
        despues = caducar_pronto_pago(reserva)
        if despues.monto_total != antes:
            tocadas.append(despues)
    return tocadas


# ── El motor: recalcular y reevaluar ──────────────────────────


def _recalcular_total(reserva: Reserva) -> Reserva:
    """Rehace `monto_total` con los descuentos de ahora, y reevalúa.

    **Solo lo llaman los cambios de descuento.** Un cambio de `costo_m2`
    o una corrección del mapa no pasan por aquí: `RN-01` congela el
    precio aceptado, y recalcular ahí movería lo cobrado a espaldas de
    quien lo aceptó.
    """
    total, _ = servicio_reservas.total_con_descuentos(
        servicio_reservas.bruto_de(reserva), servicio_reservas._pares_de(reserva)
    )
    Reserva.objects.filter(pk=reserva.pk).update(monto_total=total)
    reserva.refresh_from_db()
    return reevaluar(reserva)


def reevaluar(reserva: Reserva) -> Reserva:
    """Mueve la reserva si el saldo cruzó un umbral (`RN-13`, `RN-14`).

    Es idempotente y **no baja de estado**: una reserva `pagada` no
    vuelve a `confirmada` porque alguien rechace un abono viejo. Deshacer
    un cobro es una decisión de una persona (`CU-STD-035`), no un efecto
    lateral de esta función.

    Devuelve la reserva con su estado ya al día.
    """
    abonado = reserva.monto_abonado
    estado = reserva.estado
    nuevo = _estado_para(reserva, abonado)

    if nuevo == estado or estado == Reserva.Estado.CANCELADA:
        return reserva
    # No se retrocede: `pagada` → `confirmada` sería deshacer un cobro.
    if _orden(nuevo) < _orden(estado):
        return reserva

    Reserva.objects.filter(pk=reserva.pk).update(estado=nuevo)
    reserva.refresh_from_db()

    if nuevo == Reserva.Estado.PAGADA:
        Stand.objects.filter(lineas_de_reserva__reserva=reserva).update(
            estado=Stand.Estado.OCUPADO
        )

    logger.info(
        "Reserva %s pasa de %s a %s (abonado %s de %s)",
        reserva.pk,
        estado,
        nuevo,
        abonado,
        reserva.monto_total,
    )
    return reserva


def _estado_para(reserva: Reserva, abonado: Decimal) -> str:
    """En qué estado deja a la reserva ese saldo (`RN-13`, `RN-14`).

    Pura: no escribe nada. La usan `reevaluar` —para mover la reserva— y
    `estado_si_se_valida` —para **anunciar** el efecto antes de que
    alguien pulse—. Que sea una sola función es lo que impide que la
    pantalla prometa "quedaría confirmada" y el cobro haga otra cosa.
    """
    if abonado >= reserva.monto_total and reserva.monto_total > 0:
        # `RN-14`: cubierto el total, la reserva queda pagada y sus
        # espacios pasan a `ocupado` (`RN-10`).
        return Reserva.Estado.PAGADA
    if abonado >= reserva.anticipo:
        # `RN-13`: cubierto el anticipo, queda confirmada y bloqueada.
        return Reserva.Estado.CONFIRMADA
    return reserva.estado


def estado_si_se_valida(reserva: Reserva, monto: Decimal) -> str:
    """En qué estado quedaría la reserva si se validara ese abono.

    Es lo que la pantalla de validación enseña **antes** de decidir:
    `CU-STD-018` paso 8 dice que el sistema evalúa los umbrales al
    validar, y quien valida tiene que poder ver esa consecuencia sin
    hacer la resta de cabeza.

    No aplica el "no se retrocede" de `reevaluar` porque no hace falta:
    sumar un abono nunca baja de estado.
    """
    return _estado_para(reserva, reserva.monto_abonado + monto)


#: Cuánto ha avanzado una reserva. Solo para no retroceder.
_ESCALA = {
    Reserva.Estado.POR_CONFIRMAR: 0,
    Reserva.Estado.CONFIRMADA: 1,
    Reserva.Estado.PAGADA: 2,
    Reserva.Estado.CANCELADA: 3,
}


def _orden(estado: str) -> int:
    return _ESCALA.get(estado, 0)
