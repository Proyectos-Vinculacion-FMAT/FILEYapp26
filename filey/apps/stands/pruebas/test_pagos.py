"""
Abonos, validación y los umbrales que disparan (`CU-STD-016` a `020`).

Tres cosas se defienden más que ninguna otra, y las tres cuestan dinero
si fallan:

1. **Nada suma al saldo hasta que alguien lo valida.** Lo que el
   aplicante registra es una declaración con un papel adjunto; hasta que
   alguien comprueba contra el banco no es dinero. Contar los pendientes
   confirmaría reservas que nadie pagó.

2. **Los umbrales se evalúan al cambiar el saldo, no con un reloj.** Y
   son idempotentes: reevaluar dos veces no mueve nada.

3. **La reserva no retrocede.** Rechazar un abono viejo no devuelve una
   `pagada` a `confirmada` — deshacer un cobro es una decisión de una
   persona, no un efecto lateral.
"""

from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import DescuentoAplicado, Movimiento, Reserva, Solicitud, Stand
from ..servicios import configuracion, mapas, pagos, reservas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _mapa():
    return {
        "grid": {"salon": "Salón de pruebas", "cols": 30, "rows": 10,
                 "meters_per_cell": 1.0, "cell_size": 32},
        "stands": [
            {"id": f"A{i}", "label": f"A{i}", "col": i * 3, "row": 0, "w": 3, "h": 2}
            for i in range(1, 6)
        ],
        "decorations": [],
    }


def _comprobante(nombre="pago.pdf"):
    return SimpleUploadedFile(nombre, b"%PDF-1.4 comprobante")


@pytest.fixture
def reserva(feria_2027):
    """Una reserva de un espacio: 6 m² a 2 500 = 15 000, sin descuentos."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_mapa())
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.save(update_fields=["costo_m2"])
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        r = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    return feria_2027, conv, ana, r


@pytest.fixture
def admin(feria_2027):
    persona = Persona.objects.create_user(
        correo="rita@filey.org", nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria_2027, persona=persona, es_dueno=False)
    return persona


# ── Nada suma hasta que alguien valida ────────────────────────


def test_un_abono_registrado_no_toca_el_saldo(reserva):
    """`CU-STD-016` paso 6: nace `pendiente_validacion` y ahí se queda."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )

        assert movimiento.estado == Movimiento.Estado.PENDIENTE
        r.refresh_from_db()
        assert r.monto_abonado == Decimal("0.00")
        assert r.monto_pendiente == Decimal("15000.00")
        assert r.estado == Reserva.Estado.POR_CONFIRMAR


def test_validarlo_lo_suma_y_confirma_la_reserva(reserva, admin):
    """`RN-13`: cubierto el anticipo del 50%, queda confirmada."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )

        actualizada = pagos.validar(movimiento=movimiento, administrador=admin)

        assert actualizada.monto_abonado == Decimal("7500.00")
        assert actualizada.monto_pendiente == Decimal("7500.00")
        assert actualizada.estado == Reserva.Estado.CONFIRMADA
        # Y los espacios siguen `reservado`: solo el 100% los ocupa.
        assert Stand.objects.get(clave="A1").estado == Stand.Estado.RESERVADO


def test_cubrir_el_total_la_deja_pagada_y_ocupa_los_espacios(reserva, admin):
    """`RN-14`, y con ella `RN-10`: los stands pasan a `ocupado`."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        for monto in (Decimal("7500"), Decimal("7500")):
            movimiento = pagos.registrar(
                reserva=r, persona=ana, monto=monto,
                metodo=Movimiento.Metodo.DEPOSITO, archivo=_comprobante(),
            )
            actualizada = pagos.validar(movimiento=movimiento, administrador=admin)

        assert actualizada.monto_abonado == Decimal("15000.00")
        assert actualizada.monto_pendiente == Decimal("0.00")
        assert actualizada.estado == Reserva.Estado.PAGADA
        assert Stand.objects.get(clave="A1").estado == Stand.Estado.OCUPADO


def test_rechazarlo_no_suma_nada(reserva, admin):
    """`A1`: el monto no toca el saldo y la reserva se queda donde está."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.CHEQUE, archivo=_comprobante(),
        )

        pagos.rechazar(
            movimiento=movimiento, administrador=admin,
            motivo="El comprobante no se lee.",
        )

        r.refresh_from_db()
        assert r.monto_abonado == Decimal("0.00")
        assert r.estado == Reserva.Estado.POR_CONFIRMAR
        movimiento.refresh_from_db()
        assert movimiento.motivo_rechazo == "El comprobante no se lee."


def test_no_se_valida_dos_veces(reserva, admin):
    """El doble clic no debe cobrar dos veces el mismo papel."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        pagos.validar(movimiento=movimiento, administrador=admin)

        with pytest.raises(pagos.PagoRechazado, match="ya está validado"):
            pagos.validar(movimiento=movimiento, administrador=admin)

        r.refresh_from_db()
        assert r.monto_abonado == Decimal("7500.00")


# ── Lo que no se admite ───────────────────────────────────────


def test_el_abono_no_puede_pasar_del_saldo_pendiente(reserva):
    """`CU-STD-016` E2, contra lo **pendiente** y no contra el total."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(pagos.PagoRechazado, match="mayor que el saldo"):
            pagos.registrar(
                reserva=r, persona=ana, monto=Decimal("15000.01"),
                metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
            )

        assert not Movimiento.objects.exists()


def test_el_tope_baja_conforme_se_abona(reserva, admin):
    """Con la mitad ya validada, el tope es la otra mitad."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        primero = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        pagos.validar(movimiento=primero, administrador=admin)
        r.refresh_from_db()

        with pytest.raises(pagos.PagoRechazado, match="mayor que el saldo"):
            pagos.registrar(
                reserva=r, persona=ana, monto=Decimal("7501"),
                metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
            )


@pytest.mark.parametrize("monto", [Decimal("0"), Decimal("-100")])
def test_un_abono_de_cero_o_negativo_no_existe(reserva, monto):
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(pagos.PagoRechazado, match="mayor que cero"):
            pagos.registrar(
                reserva=r, persona=ana, monto=monto,
                metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
            )


def test_no_se_admite_efectivo(reserva):
    """`RN-08`. Los tres métodos válidos dejan rastro bancario, que es lo
    que hace comprobable el paso 4 de `CU-STD-018`."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(pagos.PagoRechazado, match="no es un método"):
            pagos.registrar(
                reserva=r, persona=ana, monto=Decimal("100"),
                metodo="efectivo", archivo=_comprobante(),
            )


def test_una_reserva_cancelada_no_admite_abonos(reserva):
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        Reserva.objects.filter(pk=r.pk).update(estado=Reserva.Estado.CANCELADA)
        r.refresh_from_db()

        with pytest.raises(pagos.PagoRechazado, match="cancelada"):
            pagos.registrar(
                reserva=r, persona=ana, monto=Decimal("100"),
                metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
            )


# ── RN-15 · el abono manual exige comprobante ─────────────────


def test_un_abono_manual_sin_comprobante_no_se_registra(reserva, admin):
    """`RN-15`: *sin comprobante no se registra el abono*."""
    feria, _, _, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(pagos.PagoRechazado, match="comprobante"):
            pagos.registrar(
                reserva=r, persona=admin, monto=Decimal("7500"),
                metodo=Movimiento.Metodo.DEPOSITO, manual=True,
            )

        assert not Movimiento.objects.exists()


def test_la_base_tampoco_lo_admite(reserva, admin):
    """En la base y no solo en el servicio: un `manage.py shell` también
    es un sitio desde el que se registran abonos."""
    from django.db.utils import IntegrityError

    feria, _, _, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(IntegrityError):
            Movimiento.objects.create(
                reserva=r, monto=Decimal("100"),
                metodo=Movimiento.Metodo.DEPOSITO,
                origen=Movimiento.Origen.ADMIN_MANUAL,
                registrado_por=admin,
            )


def test_el_abono_manual_queda_marcado_como_tal(reserva, admin):
    """El historial tiene que decir quién lo metió (`CU-STD-017`)."""
    feria, _, _, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=admin, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.DEPOSITO, archivo=_comprobante(),
            manual=True,
        )

        assert movimiento.origen == Movimiento.Origen.ADMIN_MANUAL
        assert movimiento.comprobante is not None
        # Y el comprobante cuelga de la editorial, como los demás papeles:
        # así `servicios/archivos.py` ya sabe quién puede verlo.
        assert movimiento.comprobante.editorial == r.editorial


def test_un_movimiento_resuelto_dice_quien_y_cuando(reserva, admin):
    from django.db.utils import IntegrityError

    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(IntegrityError):
            Movimiento.objects.create(
                reserva=r, monto=Decimal("100"),
                metodo=Movimiento.Metodo.TRANSFERENCIA,
                origen=Movimiento.Origen.APLICANTE,
                estado=Movimiento.Estado.VALIDADO,
                registrado_por=ana,
            )


# ── CU-STD-020 · el descuento especial mueve el total ─────────


def test_un_descuento_especial_baja_el_total_y_reevalua(reserva, admin):
    """El caso que el plan avisa: **bajar el total puede dejar una
    reserva pagada sin que entre un peso más.**"""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        pagos.validar(movimiento=movimiento, administrador=admin)
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.CONFIRMADA

        # 50% de descuento: los 7 500 ya abonados pasan a ser el total.
        actualizada = pagos.aplicar_descuento_especial(
            reserva=r, administrador=admin, porcentaje=50,
            motivo="Editorial recurrente",
        )

        assert actualizada.monto_total == Decimal("7500.00")
        assert actualizada.estado == Reserva.Estado.PAGADA
        assert Stand.objects.get(clave="A1").estado == Stand.Estado.OCUPADO


def test_un_especial_sin_motivo_no_se_aplica(reserva, admin):
    """Es dinero que alguien decidió no cobrar."""
    feria, _, _, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(pagos.PagoRechazado, match="motivo"):
            pagos.aplicar_descuento_especial(
                reserva=r, administrador=admin, porcentaje=15, motivo="   "
            )


def test_no_se_aplican_dos_especiales(reserva, admin):
    """`RN-05`, y aquí **sí es un error que se enseña**.

    Al revés que el pronto pago, que es automático e idempotente: para
    cambiar el porcentaje hay que retirar el que hay.
    """
    feria, _, _, r = reserva
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=r, administrador=admin, porcentaje=10, motivo="Primero"
        )

        with pytest.raises(pagos.PagoRechazado, match="ya tiene un descuento"):
            pagos.aplicar_descuento_especial(
                reserva=r, administrador=admin, porcentaje=20, motivo="Segundo"
            )

        assert r.descuentos.filter(tipo=DescuentoAplicado.Tipo.ESPECIAL).count() == 1


def test_el_especial_se_encadena_con_el_pronto_pago(feria_2027, admin):
    """`RN-06`: en secuencia, no sumando. 10% y 15% dan 23.5%."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_mapa())
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timezone.timedelta(days=5)
        cfg.save()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        r = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        assert r.monto_total == Decimal("13500.00")  # 15 000 − 10%

        actualizada = pagos.aplicar_descuento_especial(
            reserva=r, administrador=admin, porcentaje=15, motivo="Recurrente"
        )

        # 15 000 → −10% → 13 500 → −15% → 11 475. Sumando serían 11 250.
        assert actualizada.monto_total == Decimal("11475.00")


# ── La reserva no retrocede ───────────────────────────────────


def test_reevaluar_dos_veces_no_mueve_nada(reserva, admin):
    """Idempotente: es lo que permite llamarlo sin pensar."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        pagos.validar(movimiento=movimiento, administrador=admin)

        antes = Reserva.objects.get(pk=r.pk).estado
        pagos.reevaluar(Reserva.objects.get(pk=r.pk))
        pagos.reevaluar(Reserva.objects.get(pk=r.pk))

        assert Reserva.objects.get(pk=r.pk).estado == antes == Reserva.Estado.CONFIRMADA


def test_una_pagada_no_vuelve_atras(reserva, admin):
    """Deshacer un cobro es decisión de una persona (`CU-STD-035`), no un
    efecto lateral de recalcular."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        for _ in range(2):
            movimiento = pagos.registrar(
                reserva=r, persona=ana, monto=Decimal("7500"),
                metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
            )
            pagos.validar(movimiento=movimiento, administrador=admin)
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.PAGADA

        # Se anula un abono a mano, como haría una corrección.
        Movimiento.objects.filter(pk=movimiento.pk).update(
            estado=Movimiento.Estado.RECHAZADO
        )
        pagos.reevaluar(Reserva.objects.get(pk=r.pk))

        assert Reserva.objects.get(pk=r.pk).estado == Reserva.Estado.PAGADA


def test_una_cancelada_no_la_mueve_ningun_umbral(reserva, admin):
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("15000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        Reserva.objects.filter(pk=r.pk).update(estado=Reserva.Estado.CANCELADA)

        pagos.validar(movimiento=movimiento, administrador=admin)

        assert Reserva.objects.get(pk=r.pk).estado == Reserva.Estado.CANCELADA


def test_el_saldo_cuenta_solo_los_validados(reserva, admin):
    """Uno pendiente y uno rechazado no son dinero."""
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        validado = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("5000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        pagos.validar(movimiento=validado, administrador=admin)
        rechazado = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("5000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        pagos.rechazar(movimiento=rechazado, administrador=admin)
        pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("5000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )

        r.refresh_from_db()
        assert r.monto_abonado == Decimal("5000.00")
        assert Movimiento.objects.count() == 3


# ── CU-STD-019 · el abono manual nace validado ────────────────


def test_el_abono_manual_nace_validado_y_mueve_el_saldo(reserva, admin):
    """`CU-STD-019` pasos 6, 8 y 9.

    Lo asienta quien coteja contra el banco, así que no tiene a quién
    esperar: dejarlo pendiente creaba una cola en la que la
    administración se validaba a sí misma. $7 500 sobre $15 000 es el
    anticipo, así que además cruza `RN-13` en la misma llamada.
    """
    feria, _, _, r = reserva
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=admin, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.DEPOSITO, archivo=_comprobante(),
            manual=True,
        )

        assert movimiento.estado == Movimiento.Estado.VALIDADO
        assert movimiento.validado_por == admin
        assert movimiento.fecha_validacion is not None
        r.refresh_from_db()
        assert r.monto_abonado == Decimal("7500.00")
        assert r.estado == Reserva.Estado.CONFIRMADA


def test_lo_reportado_ocupa_sitio_solo_para_el_aplicante(reserva, admin):
    """El tope de lo que está en revisión protege del doble reporte.

    A quien reporta le frena: no puede volver a mandar la misma
    transferencia porque no la ve sumada. A quien administra no, porque
    tiene el estado de cuenta delante y es quien resuelve esa cola — si
    lo que hay en revisión duplica lo que asienta, lo que procede es
    rechazarlo, no que el sistema le impida asentar lo que sí entró.
    """
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("15000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )

        with pytest.raises(pagos.PagoRechazado, match="Espera a que los validemos"):
            pagos.registrar(
                reserva=r, persona=ana, monto=Decimal("100"),
                metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
            )

        manual = pagos.registrar(
            reserva=r, persona=admin, monto=Decimal("100"),
            metodo=Movimiento.Metodo.DEPOSITO, archivo=_comprobante(),
            manual=True,
        )
        assert manual.estado == Movimiento.Estado.VALIDADO


def test_ningun_tope_ofrece_una_cifra_negativa(reserva, admin):
    """El mensaje decía «puedes registrar hasta $-6 500».

    Pasa cuando lo que está en revisión supera al saldo, que es lo que
    abre el abono manual: baja el pendiente sin resolver lo reportado.
    """
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("14000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        pagos.registrar(
            reserva=r, persona=admin, monto=Decimal("8000"),
            metodo=Movimiento.Metodo.DEPOSITO, archivo=_comprobante(),
            manual=True,
        )

        with pytest.raises(pagos.PagoRechazado) as fallo:
            pagos.registrar(
                reserva=r, persona=ana, monto=Decimal("100"),
                metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
            )

        assert "$-" not in str(fallo.value)


def test_validar_no_cobra_de_mas_si_el_saldo_ya_se_cubrio(reserva, admin):
    """Entre reportar y validar, el saldo pudo cubrirse por otro lado.

    Validar igualmente dejaría `monto_pendiente` en negativo — cobrado
    más de lo que la reserva cuesta. Lo que procede es rechazar el
    duplicado, y el mensaje lo dice.
    """
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        reportado = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("15000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_comprobante(),
        )
        pagos.registrar(
            reserva=r, persona=admin, monto=Decimal("15000"),
            metodo=Movimiento.Metodo.DEPOSITO, archivo=_comprobante(),
            manual=True,
        )

        with pytest.raises(pagos.PagoRechazado, match="ya está cubierto"):
            pagos.validar(movimiento=reportado, administrador=admin)

        r.refresh_from_db()
        assert r.monto_abonado == Decimal("15000.00")
        assert r.monto_pendiente == Decimal("0.00")


# ── CU-STD-020 · retirar el especial ──────────────────────────


def test_retirar_el_especial_devuelve_el_total(reserva, admin):
    """La otra mitad de `RN-05`.

    Como solo cabe uno por reserva, cambiar el porcentaje es retirar el
    que hay y aplicar otro. Sin esta función, el error de
    `aplicar_descuento_especial` pedía algo que no se podía hacer.
    """
    feria, _, _, r = reserva
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=r, administrador=admin, porcentaje=20, motivo="Convenio"
        )
        r.refresh_from_db()
        assert r.monto_total == Decimal("12000.00")

        devuelta = pagos.retirar_descuento_especial(reserva=r, administrador=admin)

        assert devuelta.monto_total == Decimal("15000.00")
        assert not devuelta.descuentos.filter(
            tipo=DescuentoAplicado.Tipo.ESPECIAL
        ).exists()


def test_retirar_lo_que_no_hay_lo_dice(reserva, admin):
    feria, _, _, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(pagos.PagoRechazado, match="no tiene ningún descuento"):
            pagos.retirar_descuento_especial(reserva=r, administrador=admin)


def test_retirarlo_no_baja_de_estado_una_reserva_pagada(reserva, admin):
    """Subir el total no deshace un cobro (`CU-STD-035` es quien lo hace).

    Queda pagada con saldo pendiente otra vez, que es exactamente lo que
    describe la situación: se cobró de menos y hay que cobrar la
    diferencia.
    """
    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=r, administrador=admin, porcentaje=20, motivo="Convenio"
        )
        abono = pagos.registrar(
            reserva=Reserva.objects.get(pk=r.pk), persona=ana,
            monto=Decimal("12000"), metodo=Movimiento.Metodo.TRANSFERENCIA,
            archivo=_comprobante(),
        )
        pagos.validar(movimiento=abono, administrador=admin)
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.PAGADA

        devuelta = pagos.retirar_descuento_especial(reserva=r, administrador=admin)

        assert devuelta.estado == Reserva.Estado.PAGADA
        assert devuelta.monto_pendiente == Decimal("3000.00")
