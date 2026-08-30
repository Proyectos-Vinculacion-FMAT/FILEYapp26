"""
Resolver una reserva: prorrogar, mover el corte o cancelar
(`CU-STD-035` y `CU-STD-036`).

Es lo que hay **al otro lado** de la barrida diaria. `RN-12` dice que el
sistema no libera reservas por su cuenta ni siquiera cuando el plazo se
agota: notifica y espera una decisión. Hasta hoy esa decisión no tenía
dónde tomarse, así que:

- una reserva vencida se quedaba vencida para siempre, ocupando espacios;
- y **ninguna reserva podía cancelarse por ningún camino**, con lo que
  `cancelada` —el único estado de cierre de `RN-11`— era inalcanzable.

Lo que se defiende aquí:

1. **Cancelar libera los espacios y avisa**, y no toca los abonos: el
   dinero entró de verdad y borrarlo falsearía la contabilidad.
2. **Prorrogar solo hacia el futuro.** Una fecha pasada dejaría la
   reserva vencida en el mismo instante y la barrida volvería a avisar al
   día siguiente — justo lo que quien prorroga quiere evitar.
3. **La prórroga apaga la barrida**, porque ésta compara sus avisos
   contra la fecha de vencimiento vigente.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Movimiento, Notificacion, Reserva, Solicitud, Stand
from ..servicios import configuracion, mapas, pagos, reservas, solicitudes, vencimientos
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _admin(feria, correo="rita@filey.org"):
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


@pytest.fixture
def vencida(feria_2027):
    """Dos espacios, $30 000, con el plazo agotado hace tres días."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(
            convocatoria=conv,
            datos={
                "grid": {"salon": "S", "cols": 30, "rows": 10,
                         "meters_per_cell": 1.0, "cell_size": 32},
                "stands": [
                    {"id": "A1", "label": "A1", "col": 0, "row": 0, "w": 3, "h": 2},
                    {"id": "A2", "label": "A2", "col": 4, "row": 0, "w": 3, "h": 2},
                ],
                "decorations": [],
            },
        )
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.save(update_fields=["costo_m2"])
        ana = fabricas.persona()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        r = reservas.crear(convocatoria=conv, persona=ana, claves=["A1", "A2"])
        Reserva.objects.filter(pk=r.pk).update(
            fecha_vencimiento_anticipo=timezone.now() - timedelta(days=3)
        )
        r.refresh_from_db()
    return feria_2027, conv, ana, r


# ── CU-STD-035 A1 · cancelar ──────────────────────────────────


def test_cancelar_libera_los_espacios_y_avisa(
    vencida, django_capture_on_commit_callbacks
):
    feria, _, _, r = vencida
    admin = _admin(feria)
    mail.outbox.clear()

    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            reservas.cancelar(
                reserva=r, administrador=admin, motivo="No cubrió el anticipo."
            )

        r.refresh_from_db()
        assert r.estado == Reserva.Estado.CANCELADA
        assert r.cancelada_por == admin
        assert r.fecha_cancelacion is not None
        assert r.motivo_cancelacion == "No cubrió el anticipo."
        assert list(
            Stand.objects.filter(clave__in=["A1", "A2"]).values_list(
                "estado", flat=True
            )
        ) == [Stand.Estado.DISPONIBLE, Stand.Estado.DISPONIBLE]

    assert len(mail.outbox) == 1
    assert "cancelada" in mail.outbox[0].subject
    cuerpo = mail.outbox[0].body
    assert "A1, A2" in cuerpo
    assert "No cubrió el anticipo." in cuerpo


def test_cancelar_no_borra_los_abonos(
    vencida, django_capture_on_commit_callbacks
):
    """El dinero entró de verdad: borrarlo falsearía la contabilidad.

    Qué se hace con ese saldo se acuerda fuera del sistema, y el correo
    lo dice en vez de callarlo.
    """
    feria, _, ana, r = vencida
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("5000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA,
            archivo=SimpleUploadedFile("r.pdf", b"%PDF"),
        )
        pagos.validar(movimiento=movimiento, administrador=admin)
        mail.outbox.clear()

        with django_capture_on_commit_callbacks(execute=True):
            reservas.cancelar(reserva=r, administrador=admin)

        r.refresh_from_db()
        assert r.monto_abonado == Decimal("5000.00")
        assert r.movimientos.count() == 1

    assert "$5000.00 abonados" in mail.outbox[0].body


def test_cancelar_libera_a_la_editorial_para_reservar_otra_vez(
    vencida, django_capture_on_commit_callbacks
):
    """`RN-23`: el índice único parcial solo cuenta las vivas."""
    feria, conv, ana, r = vencida
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            reservas.cancelar(reserva=r, administrador=admin)

        nueva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        assert nueva.pk != r.pk
        assert nueva.estado == Reserva.Estado.POR_CONFIRMAR


def test_una_pagada_tambien_se_puede_cancelar(
    vencida, django_capture_on_commit_callbacks
):
    """`CU-STD-035` A1 paso 5 lo contempla: «de `Reservado` (u `Ocupado`)
    a `Disponible`»."""
    feria, _, _, r = vencida
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            pagos.registrar(
                reserva=r, persona=admin, monto=Decimal("30000"),
                metodo=Movimiento.Metodo.DEPOSITO,
                archivo=SimpleUploadedFile("r.pdf", b"%PDF"), manual=True,
            )
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.PAGADA
        assert Stand.objects.filter(estado=Stand.Estado.OCUPADO).count() == 2

        with django_capture_on_commit_callbacks(execute=True):
            reservas.cancelar(reserva=r, administrador=admin)

        assert Stand.objects.filter(estado=Stand.Estado.DISPONIBLE).count() == 2


def test_no_se_cancela_dos_veces(vencida, django_capture_on_commit_callbacks):
    feria, _, _, r = vencida
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            reservas.cancelar(reserva=r, administrador=admin)

        with pytest.raises(reservas.ResolucionRechazada, match="ya estaba cancelada"):
            reservas.cancelar(reserva=r, administrador=admin)


# ── CU-STD-035 · prorrogar ────────────────────────────────────


def test_prorrogar_deja_la_reserva_vigente(vencida):
    feria, _, _, r = vencida
    admin = _admin(feria)
    nueva = timezone.now() + timedelta(days=15)

    with schema_context(feria.schema_name):
        assert r.esta_vencida

        al_dia = reservas.prorrogar(reserva=r, administrador=admin, fecha=nueva)

        assert not al_dia.esta_vencida
        assert al_dia.estado == Reserva.Estado.POR_CONFIRMAR


def test_no_se_prorroga_hacia_atras(vencida):
    """Con una fecha pasada la reserva volvería a estar vencida hoy, y la
    barrida avisaría otra vez mañana."""
    feria, _, _, r = vencida
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        with pytest.raises(reservas.ResolucionRechazada, match="en el futuro"):
            reservas.prorrogar(
                reserva=r,
                administrador=admin,
                fecha=timezone.now() - timedelta(days=1),
            )
        r.refresh_from_db()
        assert r.esta_vencida


def test_una_confirmada_no_tiene_plazo_que_prorrogar(vencida):
    feria, _, ana, r = vencida
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("15000"),
            metodo=Movimiento.Metodo.TRANSFERENCIA,
            archivo=SimpleUploadedFile("r.pdf", b"%PDF"),
        )
        pagos.validar(movimiento=movimiento, administrador=admin)

        with pytest.raises(reservas.ResolucionRechazada, match="prorrogar"):
            reservas.prorrogar(
                reserva=Reserva.objects.get(pk=r.pk),
                administrador=admin,
                fecha=timezone.now() + timedelta(days=10),
            )


def test_prorrogar_apaga_la_barrida(vencida):
    """La barrida compara sus avisos contra la fecha vigente, así que
    mover la fecha hacia adelante la saca de la cola sin borrar nada."""
    feria, conv, _, r = vencida
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        assert [x.pk for x in vencimientos.barrer(conv)] == [r.pk]

        reservas.prorrogar(
            reserva=r, administrador=admin, fecha=timezone.now() + timedelta(days=20)
        )

        assert vencimientos.vencidas(conv).count() == 0


# ── CU-STD-036 · la fecha de corte ────────────────────────────


def test_mover_la_fecha_de_corte(vencida):
    feria, _, _, r = vencida
    admin = _admin(feria)
    nueva = timezone.localdate() + timedelta(days=60)

    with schema_context(feria.schema_name):
        al_dia = reservas.mover_fecha_de_corte(
            reserva=r, administrador=admin, fecha=nueva
        )
        assert al_dia.fecha_corte_pago_total == nueva


def test_la_fecha_de_corte_puesta_a_mano_sobrevive_a_confirmar(vencida):
    """`CU-STD-026` paso 4 hereda **solo si no hay una propia**."""
    feria, conv, ana, r = vencida
    admin = _admin(feria)
    puesta = timezone.localdate() + timedelta(days=90)
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_corte_pago_total = timezone.localdate() + timedelta(days=30)
        cfg.save(update_fields=["fecha_corte_pago_total"])
        reservas.mover_fecha_de_corte(
            reserva=r, administrador=admin, fecha=puesta
        )

        movimiento = pagos.registrar(
            reserva=Reserva.objects.get(pk=r.pk), persona=ana,
            monto=Decimal("15000"), metodo=Movimiento.Metodo.TRANSFERENCIA,
            archivo=SimpleUploadedFile("r.pdf", b"%PDF"),
        )
        pagos.validar(movimiento=movimiento, administrador=admin)

        r.refresh_from_db()
        assert r.estado == Reserva.Estado.CONFIRMADA
        assert r.fecha_corte_pago_total == puesta


def test_una_cancelada_ya_no_tiene_nada_que_liquidar(
    vencida, django_capture_on_commit_callbacks
):
    feria, _, _, r = vencida
    admin = _admin(feria)
    with schema_context(feria.schema_name):
        with django_capture_on_commit_callbacks(execute=True):
            reservas.cancelar(reserva=r, administrador=admin)

        with pytest.raises(reservas.ResolucionRechazada, match="cancelada"):
            reservas.mover_fecha_de_corte(
                reserva=r, administrador=admin,
                fecha=timezone.localdate() + timedelta(days=10),
            )


# ── La pantalla (A4) ──────────────────────────────────────────


def test_la_pantalla_ofrece_resolverla(client, vencida):
    feria, _, _, r = vencida
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=r.pk)
    ).content.decode()

    assert "Ampliar el plazo" in cuerpo
    assert "Cancelar la reserva" in cuerpo
    assert "Guardar el corte" in cuerpo


def test_cancelar_desde_la_pantalla_exige_la_casilla(client, vencida):
    """El paso 2 pide confirmación explícita: es la única acción
    irreversible del dominio y la única que libera espacios."""
    feria, _, _, r = vencida
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=r.pk),
        {"accion": "cancelar", "motivo": "Ya no viene"},
        follow=True,
    )

    assert "Marca la casilla" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.POR_CONFIRMAR


def test_cancelar_desde_la_pantalla(
    client, vencida, django_capture_on_commit_callbacks
):
    feria, _, _, r = vencida
    client.force_login(_admin(feria))
    mail.outbox.clear()

    with django_capture_on_commit_callbacks(execute=True):
        respuesta = client.post(
            _url(feria, "stands:detalle_reserva", reserva_id=r.pk),
            {"accion": "cancelar", "motivo": "Ya no viene", "entiendo": "on"},
            follow=True,
        )

    cuerpo = respuesta.content.decode()
    assert "volvieron al mapa" in cuerpo
    assert "Reserva cancelada" in cuerpo
    # Y ya no ofrece nada que hacer sobre ella.
    assert "Ampliar el plazo" not in cuerpo
    assert "Registrar un abono" not in cuerpo
    assert "Aplicar el descuento" not in cuerpo
    with schema_context(feria.schema_name):
        assert Notificacion.objects.filter(
            reserva=r, tipo=Notificacion.Tipo.RESERVA_CANCELADA
        ).exists()


def test_prorrogar_desde_la_pantalla(client, vencida):
    feria, _, _, r = vencida
    client.force_login(_admin(feria))
    dia = timezone.localdate() + timedelta(days=20)

    respuesta = client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=r.pk),
        {"accion": "prorrogar", "fecha": dia.isoformat()},
        follow=True,
    )

    assert "Ampliaste el plazo" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        r.refresh_from_db()
        # Hasta el final de ese día: «hasta el 15» incluye el 15.
        assert timezone.localtime(r.fecha_vencimiento_anticipo).date() == dia
        assert not r.esta_vencida


def test_una_fecha_pasada_no_se_guarda(client, vencida):
    feria, _, _, r = vencida
    client.force_login(_admin(feria))
    antes = r.fecha_vencimiento_anticipo

    respuesta = client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=r.pk),
        {
            "accion": "prorrogar",
            "fecha": (timezone.localdate() - timedelta(days=1)).isoformat(),
        },
        follow=True,
    )

    assert "ya pasó" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.fecha_vencimiento_anticipo == antes


def test_la_fecha_de_corte_se_puede_vaciar(client, vencida):
    """«Sin fecha de corte» es un estado legítimo, no un dato perdido."""
    feria, _, _, r = vencida
    admin = _admin(feria)
    client.force_login(admin)
    with schema_context(feria.schema_name):
        reservas.mover_fecha_de_corte(
            reserva=r, administrador=admin,
            fecha=timezone.localdate() + timedelta(days=30),
        )

    client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=r.pk),
        {"accion": "mover_corte", "fecha": ""},
        follow=True,
    )

    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.fecha_corte_pago_total is None
