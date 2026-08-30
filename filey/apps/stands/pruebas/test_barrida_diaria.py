"""
El reloj del dominio: la barrida diaria (`CU-STD-022`, `024`, `025`).

Es **lo único de `STD` que necesita un calendario delante**. Los umbrales
del 50% y del 100% se disparan dentro de la petición que cambia el saldo,
y el pronto pago se aplica al reservar. Lo que no puede saberse sin
mirar el reloj es que un plazo se agotó: nadie hace nada, y por eso hay
que avisar.

Lo que se defiende aquí:

1. **Vencer no libera nada** (`RN-12`). La barrida no escribe en
   `Reserva`: los espacios siguen apartados y la decisión es de una
   persona (`CU-STD-035`). Una barrida que "limpia" vencidas liberaría
   espacios que nadie decidió liberar, de madrugada y sin testigos.
2. **Se avisa una vez por vencimiento, no una vez por reserva.** Correr
   dos veces no manda dos correos; pero una prórroga que también se agota
   sí vuelve a avisar.
3. **Un aviso que no salió no cuenta como avisado** (`CU-STD-024` E1).
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria, Feria
from apps.registros.models import Persona

from ..models import (
    DescuentoAplicado,
    Movimiento,
    Notificacion,
    Reserva,
    Solicitud,
    Stand,
)
from ..servicios import configuracion, mapas, pagos, reservas, solicitudes, vencimientos
from . import fabricas

pytestmark = pytest.mark.django_db


def _admin(feria, correo="rita@filey.org"):
    """Un administrador **más**. La feria de las pruebas ya trae a su
    dueña (`conftest.py`), que también administra y también recibe."""
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _quien_administra(feria):
    return [a.persona for a in AdminFeria.objects.filter(feria=feria)]


def _correo_de(feria, reserva) -> str:
    """El buzón de la editorial. Se lee **dentro** del schema: `Editorial`
    vive en el de la feria y desde `public` esa tabla no existe."""
    with schema_context(feria.schema_name):
        return Reserva.objects.get(pk=reserva.pk).editorial.correo_electronico


@pytest.fixture
def vencida(feria_2027):
    """Una reserva de $15 000 cuyo plazo se agotó hace tres días."""
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
        cfg.save(update_fields=["costo_m2"])
        ana = fabricas.persona()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        r = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        Reserva.objects.filter(pk=r.pk).update(
            fecha_vencimiento_anticipo=timezone.now() - timedelta(days=3)
        )
        r.refresh_from_db()
    return feria_2027, conv, ana, r


# ── Lo que sale ───────────────────────────────────────────────


def test_una_vencida_avisa_a_las_dos_partes(vencida):
    feria, conv, _, r = vencida
    duena = _quien_administra(feria)[0]

    with schema_context(feria.schema_name):
        tocadas = vencimientos.barrer(conv)

        assert [x.pk for x in tocadas] == [r.pk]
        tipos = set(r.notificaciones.values_list("tipo", flat=True))
        assert tipos == {
            Notificacion.Tipo.POSIBLE_CANCELACION,
            Notificacion.Tipo.RESERVA_VENCIDA,
        }
    destinos = sorted(c.to[0] for c in mail.outbox)
    assert destinos == sorted([_correo_de(feria, r), duena.correo])


def test_el_aviso_al_aplicante_no_dice_que_se_cancelo(vencida):
    """`RN-12`: vencer no libera nada.

    Decir «tu reserva fue cancelada» sería mentir y, peor, empujar a
    alguien a dejar de pagar algo que todavía es suyo.
    """
    feria, conv, _, r = vencida
    with schema_context(feria.schema_name):
        vencimientos.barrer(conv)

    cuerpo = next(c.body for c in mail.outbox if c.to == [_correo_de(feria, r)])
    assert "puede cancelarse" in cuerpo
    assert "fue cancelada" not in cuerpo
    # `CU-STD-014` paso 2: lo que falta para el anticipo, no el saldo.
    assert "faltan $7500.00" in cuerpo
    assert "A1" in cuerpo


def test_el_aviso_a_quien_administra_trae_con_que_decidir(vencida):
    """`CU-STD-024` paso 2: editorial, fecha vencida, total y abonado."""
    feria, conv, _, r = vencida
    duena = _quien_administra(feria)[0]
    with schema_context(feria.schema_name):
        vencimientos.barrer(conv)
        editorial = Reserva.objects.get(pk=r.pk).editorial.nombre

    correo = next(c for c in mail.outbox if c.to == [duena.correo])
    assert editorial in correo.subject
    assert "Total $15000.00" in correo.body
    assert "abonado $0.00" in correo.body
    assert f"/f/{feria.slug}/stands/reserva/{r.pk}/" in correo.body


def test_cada_quien_administra_recibe_el_suyo(vencida):
    """Una fila de `Notificacion` por persona: la tabla registra a quién
    se le dijo algo, y una con tres destinatarios dentro no contesta esa
    pregunta — que es la que se hace cuando alguien no se enteró."""
    feria, conv, _, r = vencida
    _admin(feria, "rita@filey.org")  # con la dueña, dos
    cuantos = len(_quien_administra(feria))

    with schema_context(feria.schema_name):
        vencimientos.barrer(conv)
        assert r.notificaciones.filter(
            tipo=Notificacion.Tipo.RESERVA_VENCIDA
        ).count() == cuantos == 2
    assert len(mail.outbox) == 3


def test_sin_nadie_que_administre_el_aplicante_igual_se_entera(vencida):
    """`CU-STD-025` no depende de `CU-STD-024`."""
    feria, conv, _, r = vencida
    AdminFeria.objects.filter(feria=feria).delete()

    with schema_context(feria.schema_name):
        vencimientos.barrer(conv)
        assert r.notificaciones.count() == 1
    assert len(mail.outbox) == 1


# ── Lo que NO pasa ────────────────────────────────────────────


def test_la_barrida_no_toca_la_reserva(vencida):
    """`RN-12` y el paso 7 de `CU-STD-022`. Lo único que escribe son
    avisos: cancelar o prorrogar es de una persona (`CU-STD-035`)."""
    feria, conv, _, r = vencida
    with schema_context(feria.schema_name):
        antes = (r.estado, r.fecha_vencimiento_anticipo, r.monto_total)

        vencimientos.barrer(conv)

        r.refresh_from_db()
        assert (r.estado, r.fecha_vencimiento_anticipo, r.monto_total) == antes
        assert r.estado == Reserva.Estado.POR_CONFIRMAR
        assert all(
            linea.stand.estado == Stand.Estado.RESERVADO for linea in r.lineas.all()
        )


def test_correr_dos_veces_no_avisa_dos_veces(vencida):
    feria, conv, _, r = vencida
    with schema_context(feria.schema_name):
        vencimientos.barrer(conv)
        segunda = vencimientos.barrer(conv)

        assert segunda == []
        assert r.notificaciones.count() == 2  # la editorial y la dueña
    assert len(mail.outbox) == 2


def test_una_confirmada_no_se_avisa(vencida):
    """`CU-STD-022` A1: cubrir el anticipo apaga el contador.

    La fecha se deja pasada a propósito: lo que saca a una reserva de la
    barrida es su estado, no que le hayan movido el plazo.
    """
    feria, conv, ana, r = vencida
    admin = _quien_administra(feria)[0]
    with schema_context(feria.schema_name):
        movimiento = pagos.registrar(
            reserva=r, persona=ana, monto=Decimal("7500"),
            metodo=Movimiento.Metodo.TRANSFERENCIA,
            archivo=SimpleUploadedFile("r.pdf", b"%PDF"),
        )
        pagos.validar(movimiento=movimiento, administrador=admin)
        r.refresh_from_db()
        assert r.estado == Reserva.Estado.CONFIRMADA

        assert vencimientos.barrer(conv) == []
        assert not r.notificaciones.filter(
            tipo=Notificacion.Tipo.POSIBLE_CANCELACION
        ).exists()


def test_una_que_todavia_esta_en_plazo_no_se_avisa(vencida):
    feria, conv, _, r = vencida
    with schema_context(feria.schema_name):
        Reserva.objects.filter(pk=r.pk).update(
            fecha_vencimiento_anticipo=timezone.now() + timedelta(days=5)
        )

        assert vencimientos.barrer(conv) == []


# ── Prórrogas y reintentos ────────────────────────────────────


def test_una_prorroga_que_tambien_se_agota_vuelve_a_avisar(vencida):
    """La pregunta no es «¿ya se avisó de esta reserva?» sino «¿ya se
    avisó de **este** vencimiento?».

    Con la primera, prorrogar (`CU-STD-035`) dejaría a la reserva sin
    avisos para siempre: la nueva fecha se agotaría en silencio.
    """
    feria, conv, _, r = vencida
    with schema_context(feria.schema_name):
        vencimientos.barrer(conv)

        # El primer aviso salió hace mes y medio; después alguien prorrogó
        # a una fecha posterior, y esa también se agotó. La foto queda:
        # aviso viejo < vencimiento nuevo < hoy.
        r.notificaciones.update(fecha_envio=timezone.now() - timedelta(days=45))
        Reserva.objects.filter(pk=r.pk).update(
            fecha_vencimiento_anticipo=timezone.now() - timedelta(days=2)
        )
        r.refresh_from_db()

        assert [x.pk for x in vencimientos.barrer(conv)] == [r.pk]
        assert r.notificaciones.filter(
            tipo=Notificacion.Tipo.POSIBLE_CANCELACION
        ).count() == 2


def test_un_aviso_que_no_salio_se_reintenta(vencida):
    """`CU-STD-024` E1: se reintenta en el ciclo siguiente.

    Sin esto, un proveedor de correo caído durante una noche dejaría a esa
    reserva marcada como avisada para siempre.
    """
    feria, conv, _, r = vencida
    with schema_context(feria.schema_name):
        with patch(
            "apps.stands.servicios.avisos.EmailMultiAlternatives.send",
            side_effect=OSError("el proveedor no contestó"),
        ):
            vencimientos.barrer(conv)

        assert r.notificaciones.filter(
            estado=Notificacion.Estado.FALLIDA
        ).count() == 2

        assert [x.pk for x in vencimientos.barrer(conv)] == [r.pk]
        assert r.notificaciones.filter(
            estado=Notificacion.Estado.ENVIADA
        ).count() == 2


# ── El comando ────────────────────────────────────────────────


def test_el_comando_avisa_y_retira_el_pronto_pago(vencida):
    """Los dos pasos, y **en este orden**: retirar el descuento sube el
    total, y con él el anticipo. Una reserva al filo puede quedarse corta
    el mismo día, y el aviso tiene que salir con las cifras de después.
    """
    feria, conv, _, r = vencida
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() - timedelta(days=1)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])
        DescuentoAplicado.objects.create(
            reserva=r, tipo=DescuentoAplicado.Tipo.PRONTO_PAGO, porcentaje=10
        )
        Reserva.objects.filter(pk=r.pk).update(monto_total=Decimal("13500.00"))

    call_command("barrida_diaria", "--todas")

    with schema_context(feria.schema_name):
        r.refresh_from_db()
        assert r.monto_total == Decimal("15000.00")
        assert not r.descuentos.exists()
        assert r.notificaciones.exists()
    # Y el aviso lleva el anticipo de después de retirarlo, no el de antes.
    cuerpo = next(c.body for c in mail.outbox if c.to == [_correo_de(feria, r)])
    assert "faltan $7500.00" in cuerpo


def test_en_seco_no_manda_nada(vencida):
    feria, _, _, r = vencida

    call_command("barrida_diaria", "--todas", "--seco")

    assert mail.outbox == []
    with schema_context(feria.schema_name):
        assert not r.notificaciones.exists()


def test_una_edicion_archivada_no_se_barre(vencida):
    """`CU-FER-006` E1: una feria archivada se consulta, no se opera.

    Sus reservas ya no están en juego; el correo solo confundiría.
    """
    feria, _, _, r = vencida
    feria.estado = Feria.Estado.ARCHIVADA
    feria.save(update_fields=["estado"])

    call_command("barrida_diaria", "--todas")

    assert mail.outbox == []
    with schema_context(feria.schema_name):
        assert not r.notificaciones.exists()
