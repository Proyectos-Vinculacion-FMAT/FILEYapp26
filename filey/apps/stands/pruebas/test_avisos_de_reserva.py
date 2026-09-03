"""
Los dos correos de los umbrales (`CU-STD-026` y `CU-STD-027`).

Hasta hoy cruzar el 50% o el 100% ocurría **en silencio**: los umbrales
se evaluaban bien, la reserva cambiaba de estado y la editorial se
enteraba si entraba a mirar. Los dos casos de uso piden el correo en su
paso 5, y el modelo ya tenía los dos tipos de `Notificacion` reservados
sin que nadie los escribiera nunca.

Lo que se defiende aquí:

1. **El correo sale después del commit.** `reevaluar` corre siempre
   dentro de una transacción, y un correo no se puede deshacer: si la
   transacción se revierte, la editorial ya recibió el aviso de una
   confirmación que no ocurrió.
2. **Un cambio de estado, un correo.** Quien liquida de una sola vez
   recibe el de liquidación, no los dos.
3. **Un correo que no sale no deshace el cobro.** Queda `fallida` con su
   motivo, como el aviso del dictamen (`CU-STD-008` E1).
4. **La fecha de corte se hereda al confirmarse** (`CU-STD-026` paso 4),
   y confirmar no pisa una que alguien ya movió a mano.
"""

import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Movimiento, Notificacion, Reserva, Solicitud
from ..servicios import configuracion, mapas, pagos, reservas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _pdf(nombre="recibo.pdf"):
    return SimpleUploadedFile(nombre, b"%PDF-1.4 banco")


def _admin(feria, correo="rita@filey.org"):
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


@pytest.fixture
def reserva(feria_2027):
    """Una reserva de $15 000 —6 m² a $2 500— con corte el 3 de noviembre."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(
            convocatoria=conv,
            datos={
                "grid": {"salon": "S", "cols": 30, "rows": 10,
                         "meters_per_cell": 1.0, "cell_size": 32},
                "stands": [{"id": "A1", "label": "A1", "col": 0, "row": 0,
                            "w": 3, "h": 2}],
                "decorations": [],
            },
        )
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.fecha_corte_pago_total = datetime.date(2027, 11, 3)
        cfg.save(update_fields=["costo_m2", "fecha_corte_pago_total"])
        ana = fabricas.persona()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        r = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    return feria_2027, conv, ana, r


def _abonar(feria, r, persona, monto, admin, capturar):
    """Reporta y valida un abono, ejecutando lo que quede pendiente al commit."""
    with schema_context(feria.schema_name):
        with capturar(execute=True):
            movimiento = pagos.registrar(
                reserva=r, persona=persona, monto=Decimal(monto),
                metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_pdf(),
            )
            pagos.validar(movimiento=movimiento, administrador=admin)


# ── CU-STD-026 · el 50% ───────────────────────────────────────


def test_confirmar_avisa_a_la_editorial(
    reserva, django_capture_on_commit_callbacks
):
    feria, _, ana, r = reserva
    admin = _admin(feria)
    mail.outbox.clear()

    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)

    assert len(mail.outbox) == 1
    correo = mail.outbox[0]
    assert "confirmada" in correo.subject
    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.CONFIRMADA
        aviso = Notificacion.objects.get(reserva=r)
        assert aviso.tipo == Notificacion.Tipo.RESERVA_CONFIRMADA
        assert aviso.estado == Notificacion.Estado.ENVIADA


def test_el_correo_dice_los_espacios_el_saldo_y_hasta_cuando(
    reserva, django_capture_on_commit_callbacks
):
    """Las tres cosas que cambian para quien lo recibe.

    Sin los espacios no dice **qué** quedó apartado; sin el saldo y la
    fecha, quien lo lee no sabe si le queda algo por hacer.
    """
    feria, _, ana, r = reserva
    admin = _admin(feria)
    mail.outbox.clear()

    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)

    cuerpo = mail.outbox[0].body
    assert "el espacio A1" in cuerpo
    assert "7500.00" in cuerpo
    assert "3 de noviembre de 2027" in cuerpo


def test_el_enlace_del_correo_lleva_dominio_y_apunta_a_mi_reserva(
    reserva, django_capture_on_commit_callbacks, settings
):
    """Un `/f/2027/...` suelto no es una dirección dentro de un cliente
    de correo. `REG` y `FER` ya anteponían `URL_BASE`; `STD` no."""
    settings.URL_BASE = "https://filey.uady.mx"
    feria, conv, ana, r = reserva
    admin = _admin(feria)
    mail.outbox.clear()

    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)

    assert (
        f"https://filey.uady.mx/f/{feria.slug}/stands/{conv.pk}/mi-reserva/"
        in mail.outbox[0].body
    )


def test_al_confirmarse_hereda_la_fecha_de_corte(
    reserva, django_capture_on_commit_callbacks
):
    """`CU-STD-026` paso 4. Antes el campo no lo escribía nadie: la
    pantalla del expositor lo pintaba «si lo tiene» y nunca lo tenía."""
    feria, _, ana, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        assert r.fecha_corte_pago_total is None

    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)

    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.fecha_corte_pago_total == datetime.date(2027, 11, 3)


def test_confirmar_no_pisa_una_fecha_puesta_a_mano(
    reserva, django_capture_on_commit_callbacks
):
    """`CU-STD-036`: si alguien se la movió, confirmar no la revierte."""
    feria, _, ana, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        Reserva.objects.filter(pk=r.pk).update(
            fecha_corte_pago_total=datetime.date(2027, 12, 15)
        )

    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)

    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.fecha_corte_pago_total == datetime.date(2027, 12, 15)


def test_sin_fecha_en_la_convocatoria_la_reserva_se_queda_sin_ella(
    reserva, django_capture_on_commit_callbacks
):
    """«si estuviera definida», dice el paso 4. Confirmar no la inventa."""
    feria, conv, ana, r = reserva
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_corte_pago_total = None
        cfg.save(update_fields=["fecha_corte_pago_total"])

    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)

    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.CONFIRMADA
        assert r.fecha_corte_pago_total is None
    # Y el correo no promete una fecha que no existe.
    assert "fecha límite" not in mail.outbox[-1].body


# ── CU-STD-027 · el 100% ──────────────────────────────────────


def test_liquidar_avisa_una_sola_vez(
    reserva, django_capture_on_commit_callbacks
):
    """Quien paga todo de una vez pasa de `por_confirmar` a `pagada`.

    Un cambio de estado, un correo: `CU-STD-027` lo contempla en sus
    precondiciones y el de confirmación sobraría — nunca estuvo
    confirmada.
    """
    feria, _, ana, r = reserva
    admin = _admin(feria)
    mail.outbox.clear()

    _abonar(feria, r, ana, "15000", admin, django_capture_on_commit_callbacks)

    assert len(mail.outbox) == 1
    assert "liquidada" in mail.outbox[0].subject
    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.PAGADA
        assert Notificacion.objects.filter(
            reserva=r, tipo=Notificacion.Tipo.RESERVA_PAGADA
        ).count() == 1
        assert not Notificacion.objects.filter(
            reserva=r, tipo=Notificacion.Tipo.RESERVA_CONFIRMADA
        ).exists()


def test_en_dos_pagos_salen_los_dos_correos(
    reserva, django_capture_on_commit_callbacks
):
    feria, _, ana, r = reserva
    admin = _admin(feria)
    mail.outbox.clear()

    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)
    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)

    assert [c.subject for c in mail.outbox] == [
        "Tu reserva de espacios quedó confirmada",
        "Tu reserva está liquidada",
    ]


def test_el_abono_manual_tambien_avisa(
    reserva, django_capture_on_commit_callbacks
):
    """`CU-STD-026` nombra a `CU-STD-019` en sus precondiciones: el aviso
    cuelga del umbral, no de por dónde entró el dinero."""
    feria, _, _, r = reserva
    admin = _admin(feria)
    mail.outbox.clear()

    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            pagos.registrar(
                reserva=r, persona=admin, monto=Decimal("7500"),
                metodo=Movimiento.Metodo.DEPOSITO, archivo=_pdf(),
                manual=True,
            )

    assert len(mail.outbox) == 1
    assert "confirmada" in mail.outbox[0].subject


def test_un_descuento_que_liquida_tambien_avisa(
    reserva, django_capture_on_commit_callbacks
):
    """`CU-STD-027`: bajar el total puede dejar pagada una reserva sin
    que entre un peso más, y eso también hay que decirlo."""
    feria, _, ana, r = reserva
    admin = _admin(feria)
    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)
    mail.outbox.clear()

    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            pagos.aplicar_descuento_especial(
                reserva=Reserva.objects.get(pk=r.pk), administrador=admin,
                porcentaje=50, motivo="Convenio institucional",
            )

    assert len(mail.outbox) == 1
    assert "liquidada" in mail.outbox[0].subject


# ── Lo que no puede pasar ─────────────────────────────────────


def test_reevaluar_dos_veces_no_manda_dos_correos(
    reserva, django_capture_on_commit_callbacks
):
    feria, _, ana, r = reserva
    admin = _admin(feria)
    mail.outbox.clear()

    _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)
    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            pagos.reevaluar(Reserva.objects.get(pk=r.pk))

    assert len(mail.outbox) == 1


def test_un_correo_que_no_sale_no_deshace_el_cobro(
    reserva, django_capture_on_commit_callbacks
):
    """Como el aviso del dictamen: queda `fallida` con su motivo.

    Lo contrario sería que un buzón lleno tumbara una validación de pago
    que el banco ya respaldó.
    """
    feria, _, ana, r = reserva
    admin = _admin(feria)

    with patch(
        "apps.stands.servicios.avisos.EmailMultiAlternatives.send",
        side_effect=OSError("el proveedor no contestó"),
    ):
        _abonar(feria, r, ana, "7500", admin, django_capture_on_commit_callbacks)

    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.CONFIRMADA
        aviso = Notificacion.objects.get(reserva=r)
        assert aviso.estado == Notificacion.Estado.FALLIDA
        assert "no contestó" in aviso.detalle_error


def test_sin_commit_no_sale_ningun_correo(reserva):
    """El aviso está enganchado al commit y no a la llamada.

    Sin ejecutar los callbacks —que es lo que ocurre si la transacción se
    revierte— no sale nada, aunque la reserva sí haya cambiado de estado
    dentro de ella.
    """
    feria, _, ana, r = reserva
    admin = _admin(feria)
    mail.outbox.clear()

    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA, archivo=_pdf(),
        )
        pagos.validar(movimiento=movimiento, administrador=admin)

    assert mail.outbox == []


def test_un_aviso_cuelga_de_exactamente_una_cosa(reserva):
    from django.db.utils import IntegrityError

    feria, _, ana, r = reserva
    with schema_context(feria.schema_name):
        with pytest.raises(IntegrityError):
            Notificacion.objects.create(
                destinatario=ana,
                tipo=Notificacion.Tipo.RESERVA_CONFIRMADA,
                estado=Notificacion.Estado.ENVIADA,
            )
