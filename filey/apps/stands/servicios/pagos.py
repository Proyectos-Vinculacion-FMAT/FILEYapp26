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
    BitacoraSTD,
    DescuentoAplicado,
    Documento,
    Movimiento,
    Reserva,
    Stand,
)
from . import avisos, bitacora
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
        el comprobante **es obligatorio** (`RN-15`), el abono **nace
        validado** —quien lo registra es quien valida, no tiene a quién
        esperar— y el saldo se mueve en el acto.
    :raises PagoRechazado: y no se crea nada.
    """
    if monto is None or monto <= 0:
        raise PagoRechazado("El monto tiene que ser mayor que cero.")
    if metodo not in Movimiento.Metodo.values:
        # `RN-08`: nunca efectivo. Los tres que quedan dejan rastro
        # bancario, que es lo que hace comprobable la validación.
        raise PagoRechazado(f"«{metodo}» no es un método de pago admitido.")
    if manual and archivo is None:
        raise PagoRechazado(
            "Un pago que registra la administración necesita comprobante. "
            "Adjúntalo para poder guardarlo."
        )

    # A partir de aquí se decide con cifras que cambian con cada abono,
    # así que la reserva se bloquea antes de leerlas. Sin el bloqueo, dos
    # envíos simultáneos —un doble clic en «Registrar el pago»— leen los
    # dos el mismo hueco y crean los dos el abono, que es exactamente lo
    # que el tope de abajo existe para impedir.
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)

    if reserva.estado == Reserva.Estado.CANCELADA:
        raise PagoRechazado("Esta reserva está cancelada: no admite abonos.")

    # `CU-STD-016` E2. Se compara contra lo pendiente y no contra el
    # total: con un abono ya validado, el tope es lo que falta.
    pendiente = reserva.monto_pendiente
    if monto > pendiente:
        raise PagoRechazado(
            f"El pago de ${monto} es mayor que el saldo pendiente de "
            f"${pendiente}. Ajusta el monto."
        )

    # Y para el aplicante, lo ya reportado también ocupa sitio. Sin esto,
    # quien vuelve a reportar la misma transferencia porque no la ve
    # sumada deja dos declaraciones idénticas en la cola, y quien las
    # valide a las dos cobra el doble de lo que entró al banco.
    #
    # No es lo mismo que el tope de arriba: `monto_pendiente` solo
    # descuenta lo **validado** (`CU-STD-018`), a propósito. Esto de aquí
    # es el hueco que queda **después** de lo que está en revisión, y se
    # libera solo si alguien rechaza un abono.
    #
    # **No aplica al abono manual**: quien lo registra es quien resuelve
    # la cola y tiene el estado de cuenta delante. Si lo que hay en
    # revisión duplica lo que está asentando, lo que procede es
    # rechazarlo, no que el sistema le impida asentar lo que sí entró.
    # Lo que sigue protegido en los dos casos es el saldo, arriba, y la
    # comprobación de `validar`, que impide cobrar de más por ese camino.
    if not manual:
        en_revision = suma_en_revision(reserva)
        hueco = pendiente - en_revision
        if hueco <= 0:
            raise PagoRechazado(
                f"Ya reportaste ${en_revision} y siguen en revisión: cubren "
                f"todo el saldo de ${pendiente}. Espera a que los validemos "
                "contra el banco."
            )
        if monto > hueco:
            raise PagoRechazado(
                f"Tienes ${en_revision} en revisión. Sobre el saldo de "
                f"${pendiente}, puedes registrar hasta ${hueco}."
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
        # `CU-STD-019` paso 6: el abono manual nace `validado`. No es una
        # excepción a `CU-STD-018`, es que ya pasó por él — lo asienta
        # quien coteja contra el banco. Dejarlo pendiente crearía una cola
        # en la que la administración se valida a sí misma.
        estado=(
            Movimiento.Estado.VALIDADO if manual else Movimiento.Estado.PENDIENTE
        ),
        # La restricción `un_movimiento_resuelto_dice_quien_y_cuando` los
        # exige en cuanto el estado no es pendiente.
        validado_por=persona if manual else None,
        fecha_validacion=timezone.now() if manual else None,
        comprobante=comprobante,
        registrado_por=persona,
    )
    logger.info(
        "Abono registrado: %s en la reserva %s (%s, %s)",
        monto,
        reserva.pk,
        movimiento.origen,
        movimiento.estado,
    )
    if manual:
        bitacora.anotar(
            persona=persona,
            accion=BitacoraSTD.Accion.ABONO_MANUAL,
            objeto=reserva,
            movimiento=movimiento.pk,
            monto=str(monto),
            metodo=metodo,
        )
        # `CU-STD-019` pasos 8 y 9: suma en el acto y pasa por los
        # umbrales, igual que si alguien acabara de validarlo.
        reevaluar(reserva)
    return movimiento


def suma_en_revision(reserva: Reserva) -> Decimal:
    """Lo reportado y todavía sin resolver, en pesos.

    Ocupa sitio sobre el saldo aunque no lo baje: es lo que impide
    reportar dos veces la misma transferencia (`CU-STD-016` E2), y lo que
    la pantalla del expositor y la del administrador enseñan para que
    nadie lo intente.
    """
    return reserva.movimientos.filter(
        estado=Movimiento.Estado.PENDIENTE
    ).aggregate(models.Sum("monto"))["monto__sum"] or Decimal("0.00")


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

    Los dos bloqueos importan, y en este orden —el mismo en `rechazar`,
    porque dos órdenes distintos sobre las mismas filas se abrazan—:

    - **la reserva**, porque dos abonos validados a la vez leerían los dos
      el mismo `monto_abonado` de antes y la reserva podría quedarse en
      `por_confirmar` habiendo cobrado el total;
    - **el movimiento**, y su estado se vuelve a leer ya bloqueado. La
      instancia que llega la trajo la vista antes de la transacción, así
      que comprobar sobre ella es comprobar sobre una foto vieja: validar
      y rechazar a la vez dejaban la reserva confirmada por un abono que
      acababa de quedar rechazado.
    """
    reserva = Reserva.objects.select_for_update().get(pk=movimiento.reserva_id)
    movimiento = Movimiento.objects.select_for_update().get(pk=movimiento.pk)

    if movimiento.estado != Movimiento.Estado.PENDIENTE:
        raise PagoRechazado(
            f"Este movimiento ya está {movimiento.get_estado_display().lower()}."
        )

    # El tope se comprobó al registrarlo, pero entre aquel momento y éste
    # el saldo pudo cubrirse por otro lado —un abono manual, o un
    # descuento que bajó el total—. Validar igualmente cobraría de más y
    # dejaría `monto_pendiente` en negativo. Lo que procede entonces es
    # rechazarlo, y el mensaje lo dice.
    if reserva.monto_abonado + movimiento.monto > reserva.monto_total:
        raise PagoRechazado(
            f"El saldo de esta reserva ya está cubierto: quedan "
            f"${reserva.monto_pendiente} y este abono es de "
            f"${movimiento.monto}. Si duplica uno ya validado, recházalo."
        )

    movimiento.estado = Movimiento.Estado.VALIDADO
    movimiento.validado_por = administrador
    movimiento.fecha_validacion = timezone.now()
    movimiento.save(update_fields=["estado", "validado_por", "fecha_validacion"])

    logger.info("Abono %s validado por %s", movimiento.pk, administrador.pk)
    bitacora.anotar(
        persona=administrador,
        accion=BitacoraSTD.Accion.ABONO_VALIDADO,
        objeto=reserva,
        movimiento=movimiento.pk,
        monto=str(movimiento.monto),
    )
    return reevaluar(reserva)


@transaction.atomic
def rechazar(*, movimiento: Movimiento, administrador, motivo: str = "") -> Movimiento:
    """`A1`: el comprobante no vale. El monto no toca el saldo.

    El motivo es opcional según el caso de uso, y aun así conviene: el
    aplicante ve el rechazo en su historial (`CU-STD-017`), y sin motivo
    solo ve que se rechazó.

    Bloquea la reserva y el movimiento en el mismo orden que `validar`
    aunque no toque el saldo: es lo que serializa las dos decisiones
    sobre el mismo abono.
    """
    Reserva.objects.select_for_update().get(pk=movimiento.reserva_id)
    movimiento = Movimiento.objects.select_for_update().get(pk=movimiento.pk)

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
    bitacora.anotar(
        persona=administrador,
        accion=BitacoraSTD.Accion.ABONO_RECHAZADO,
        objeto=movimiento.reserva,
        movimiento=movimiento.pk,
        monto=str(movimiento.monto),
        motivo=movimiento.motivo_rechazo,
    )
    return movimiento


# ── CU-STD-020 · el descuento especial ────────────────────────


def _exigir_reserva_viva(reserva: Reserva, que_se_iba_a_hacer: str) -> Reserva:
    """Trae la reserva bloqueada y se niega si ya está cerrada.

    Las dos funciones que mueven un descuento son las únicas del dominio
    que reescriben `monto_total`, y `RN-01` acota esa licencia a las
    reservas **vivas**: «los descuentos sí lo mueven, y en reservas
    vivas». Sobre una cancelada no hay nada que descontar — `RN-11` dice
    que cancelar cierra, y el importe pasa a ser el registro de lo que
    esa reserva costó.

    Hasta el 2026-08-30 la comprobación existía **solo en la plantilla**
    de A4 (``{% if esta_viva %}``), así que un POST con
    ``accion=descuento_especial`` sobre una cancelada le reescribía el
    total sin que nada protestara: la vista despacha la acción sin
    volver a preguntar, y `reevaluar` sale temprano en las canceladas,
    de modo que el estado quedaba bien y la cifra mal. Es la regla 3 de
    `CLAUDE.md` — lo que no se puede llamar desde `manage.py` sin pasar
    por HTTP está en el sitio equivocado.

    Bloquea la fila, como `validar` y `cancelar`: se decide sobre el
    estado que hay ahora, no sobre el que traía la instancia que pintó
    la pantalla.
    """
    reserva = Reserva.objects.select_for_update().get(pk=reserva.pk)
    if reserva.estado not in Reserva.VIVAS:
        raise PagoRechazado(
            f"Esta reserva está {reserva.get_estado_display().lower()}: ya no "
            f"tiene sentido {que_se_iba_a_hacer}."
        )
    return reserva


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

    Solo sobre una reserva **viva**: ver `_exigir_reserva_viva`.
    """
    if not motivo or not motivo.strip():
        raise PagoRechazado(
            "Escribe el motivo del descuento: es dinero que la feria decide "
            "no cobrar."
        )
    if not 1 <= porcentaje <= 100:
        raise PagoRechazado("El porcentaje tiene que estar entre 1 y 100.")

    reserva = _exigir_reserva_viva(reserva, "aplicarle un descuento")

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
    bitacora.anotar(
        persona=administrador,
        accion=BitacoraSTD.Accion.DESCUENTO_APLICADO,
        objeto=reserva,
        porcentaje=porcentaje,
        motivo=motivo.strip()[:200],
        total_antes=str(reserva.monto_total),
    )
    # Instancia recién traída, por lo mismo que en `caducar_pronto_pago`:
    # `_recalcular_total` lee los descuentos con `reserva.descuentos.all()`
    # y quien llame desde una pantalla llega con `prefetch_related`
    # puesto. Esa caché se llenó **antes** de insertar el descuento, así
    # que el total salía idéntico: el descuento quedaba guardado y no
    # descontaba nada.
    return _recalcular_total(Reserva.objects.get(pk=reserva.pk))


@transaction.atomic
def retirar_descuento_especial(*, reserva: Reserva, administrador) -> Reserva:
    """Quita el descuento especial y devuelve el total a lo que era.

    Es la otra mitad de `RN-05`: como solo cabe uno por reserva, cambiar
    el porcentaje es retirar el que hay y aplicar otro. Sin esta función,
    el error de `aplicar_descuento_especial` —«retíralo antes de aplicar
    otro»— pedía algo que no se podía hacer desde ninguna parte.

    El total **sube**, y eso no baja el estado de la reserva: `reevaluar`
    no retrocede a propósito (`CU-STD-035` es quien deshace un cobro, no
    un efecto lateral). Una reserva que quedó pagada con el descuento
    sigue pagada, con saldo pendiente otra vez.

    El pronto pago no se toca: son independientes (`RN-06`).

    Solo sobre una reserva **viva**: ver `_exigir_reserva_viva`.
    """
    reserva = _exigir_reserva_viva(reserva, "retirarle el descuento")

    descuento = reserva.descuentos.filter(
        tipo=DescuentoAplicado.Tipo.ESPECIAL
    ).first()
    if descuento is None:
        raise PagoRechazado("Esta reserva no tiene ningún descuento especial.")

    logger.info(
        "Se retira el especial del %s%% de la reserva %s por %s",
        descuento.porcentaje,
        reserva.pk,
        administrador.pk,
    )
    # Se anota **antes** de borrar: es de las pocas acciones que no dejan
    # rastro en ninguna otra parte, porque lo que hace es quitar la fila
    # que lo explicaba.
    bitacora.anotar(
        persona=administrador,
        accion=BitacoraSTD.Accion.DESCUENTO_RETIRADO,
        objeto=reserva,
        porcentaje=descuento.porcentaje,
        motivo=descuento.motivo,
        total_antes=str(reserva.monto_total),
    )
    descuento.delete()
    # Instancia recién traída, por lo mismo que en `caducar_pronto_pago`:
    # una caché de `descuentos` con la fila ya borrada dentro dejaría el
    # total idéntico.
    return _recalcular_total(Reserva.objects.get(pk=reserva.pk))


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
    # Sin persona: no lo decidió nadie, se cumplió `RN-04`. Y como el
    # descuento se borra, sin esta línea la subida del total no tendría
    # explicación en ninguna parte.
    bitacora.anotar(
        persona=None,
        accion=BitacoraSTD.Accion.PRONTO_PAGO_CADUCADO,
        objeto=reserva,
        porcentaje=descuento.porcentaje,
        vencio=limite.isoformat(),
        total_antes=str(reserva.monto_total),
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

    campos = {"estado": nuevo}
    if (
        nuevo == Reserva.Estado.CONFIRMADA
        and reserva.fecha_corte_pago_total is None
    ):
        # `CU-STD-026` paso 4: al confirmarse, la reserva **hereda** la
        # fecha de corte de su convocatoria. Solo si no tiene ya una
        # propia: si alguien se la movió a mano (`CU-STD-036`),
        # confirmar no puede pisarla.
        campos["fecha_corte_pago_total"] = (
            reserva.configuracion.fecha_corte_pago_total
        )

    Reserva.objects.filter(pk=reserva.pk).update(**campos)
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
    _avisar_del_umbral(reserva, nuevo)
    return reserva


def _avisar_del_umbral(reserva: Reserva, estado: str) -> None:
    """Programa el correo de `CU-STD-026` o `CU-STD-027`.

    **Después del commit, no aquí.** `reevaluar` corre siempre dentro de
    una transacción —validar un abono, asentar uno manual, mover un
    descuento— y un correo no se puede deshacer: si la transacción se
    revierte después, la editorial ya recibió el aviso de una
    confirmación que no ocurrió, y ni siquiera queda la `Notificacion`
    que lo explique, porque se iría con el rollback.

    Es la misma razón por la que el dictamen avisa **fuera** de su
    transacción (`servicios/dictamen.py`). Aquí no se puede sacar el
    aviso al llamador: `reevaluar` tiene cuatro puertas y la decisión de
    a quién se avisa es una sola.

    Un cambio de estado programa **un** correo. Quien liquida de una sola
    vez pasa de `por_confirmar` a `pagada` y recibe el de liquidación, no
    los dos: `CU-STD-027` lo contempla en sus precondiciones.
    """
    envio = {
        Reserva.Estado.CONFIRMADA: avisos.avisar_confirmacion,
        Reserva.Estado.PAGADA: avisos.avisar_liquidacion,
    }.get(estado)
    if envio is None:
        return
    transaction.on_commit(lambda: envio(reserva))


def _estado_para(reserva: Reserva, abonado: Decimal) -> str:
    """En qué estado deja a la reserva ese saldo (`RN-13`, `RN-14`).

    Pura: no escribe nada. La usan `reevaluar` —para mover la reserva— y
    `estado_si_se_valida` —para **anunciar** el efecto antes de que
    alguien pulse—. Que sea una sola función es lo que impide que la
    pantalla prometa "quedaría confirmada" y el cobro haga otra cosa.

    .. important:: Un total de cero está cubierto

       Hasta el 2026-08-30 esto exigía además ``monto_total > 0`` para
       dar una reserva por pagada, y eso dejaba atrapada en `confirmada`
       a la que recibía un descuento especial del 100% —que `RN-07`
       contempla, es el convenio institucional—: total cero, saldo cero,
       y `RN-14` sin cumplirse. Sus espacios se quedaban en
       `reservado` para siempre, no salía el correo de liquidación
       (`CU-STD-027`) y la ocupación del panel los contaba como
       apartados.

       La guarda existía para que una reserva de una convocatoria sin
       precio no se marcara pagada sola. Ya no hace falta:
       `reservas.crear` rechaza `costo_m2` en cero desde el
       2026-08-29, así que el único camino a un total de cero es un
       descuento deliberado — y ése **sí** está liquidado.
    """
    if abonado >= reserva.monto_total:
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
