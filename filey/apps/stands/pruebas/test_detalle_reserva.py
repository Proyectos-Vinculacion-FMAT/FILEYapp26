"""
A4 · El expediente de una reserva y lo que se opera desde él.

`CU-STD-029` no describe una ficha de consulta sino una **vista
contenedor**: el sitio desde el que se validan abonos (`CU-STD-018`), se
asientan los manuales (`CU-STD-019`) y se aplica o retira el descuento
especial (`CU-STD-020`). Hasta hoy los tres servicios existían y estaban
probados, y ninguno tenía puerta: `019` y `020` eran código inalcanzable
desde el navegador.

Lo que se defiende aquí:

1. **El abono manual nace validado.** `CU-STD-019` pasos 6 y 8: lo
   asienta quien coteja contra el banco, así que no tiene a quién
   esperar, y el saldo se mueve en el acto.
2. **Aplicar y retirar el especial nunca se ofrecen a la vez** (`RN-05`).
3. **La marca del umbral cae donde de verdad confirma.** El porcentaje es
   de la convocatoria (`RN-02`) y `A10` lo cambia.
"""

from decimal import Decimal

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import DescuentoAplicado, Movimiento, Reserva, Solicitud
from ..servicios import configuracion, mapas, pagos, reservas, solicitudes
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


def _pdf(nombre="respaldo.pdf"):
    return SimpleUploadedFile(nombre, b"%PDF-1.4 respaldo")


@pytest.fixture
def con_reserva(feria_2027):
    """Una reserva de $15 000 —6 m² a $2 500— sin abonos ni descuentos."""
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
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    return feria_2027, conv, ana, reserva


# ── CU-STD-029 paso 5 · el historial ──────────────────────────


def test_la_pantalla_lista_los_abonos_de_la_reserva(client, con_reserva):
    feria, _, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        pagos.registrar(
            reserva=reserva, persona=ana, monto=Decimal("2500.00"),
            metodo="transferencia", archivo=_pdf("recibo.pdf"),
        )
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk)
    ).content.decode()

    assert "2500.00" in cuerpo
    assert "Transferencia" in cuerpo
    # Y el aviso de que eso todavía no baja el saldo, que es lo que evita
    # que alguien lo dé por cobrado al leer la tabla.
    assert "sin resolver" in cuerpo


def test_sin_abonos_lo_dice_en_vez_de_dejar_la_tabla_vacia(client, con_reserva):
    feria, _, _, reserva = con_reserva
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk)
    ).content.decode()

    assert "no tiene ningún abono todavía" in cuerpo


def test_decidir_desde_la_reserva_devuelve_a_la_reserva(client, con_reserva):
    """`CU-STD-018` tiene dos puertas, y cada una devuelve a la suya.

    Sin esto, validar desde A4 dejaba a quien lo hizo en la cola de A5,
    que es otra pantalla y otra tarea.
    """
    feria, _, ana, reserva = con_reserva
    with schema_context(feria.schema_name):
        abono = pagos.registrar(
            reserva=reserva, persona=ana, monto=Decimal("7500.00"),
            metodo="transferencia", archivo=_pdf(),
        )
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:movimiento", movimiento_id=abono.pk),
        {"accion": "validar", "desde": "reserva"},
    )

    assert respuesta.status_code == 302
    assert respuesta.url.endswith(f"/stands/reserva/{reserva.pk}/")


# ── CU-STD-019 · el abono manual ──────────────────────────────


def test_el_abono_manual_nace_validado_y_baja_el_saldo(client, con_reserva):
    """`CU-STD-019` pasos 6, 8 y 9, en una sola petición.

    $7 500 sobre $15 000 es justo el anticipo: además de sumarse, cruza
    `RN-13` y la reserva queda confirmada sin que nadie valide nada
    después.
    """
    feria, _, _, reserva = con_reserva
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk),
        {
            "accion": "abono_manual",
            "monto": "7500.00",
            "metodo": "deposito",
            "comprobante": _pdf("ficha-banco.pdf"),
        },
        follow=True,
    )

    assert "Asentaste $7500.00" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        movimiento = Movimiento.objects.get()
        assert movimiento.estado == Movimiento.Estado.VALIDADO
        assert movimiento.origen == Movimiento.Origen.ADMIN_MANUAL
        # La restricción de la base los exige en cuanto no está pendiente.
        assert movimiento.validado_por is not None
        assert movimiento.fecha_validacion is not None

        reserva.refresh_from_db()
        assert reserva.monto_abonado == Decimal("7500.00")
        assert reserva.estado == Reserva.Estado.CONFIRMADA


def test_un_abono_manual_sin_respaldo_no_se_registra(client, con_reserva):
    """`RN-15` y `CU-STD-019` E1: sin documento no hay abono."""
    feria, _, _, reserva = con_reserva
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk),
        {"accion": "abono_manual", "monto": "1000.00", "metodo": "cheque"},
        follow=True,
    )

    assert "documento de respaldo" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        assert not Movimiento.objects.exists()


def test_una_reserva_pagada_no_ofrece_registrar_mas(client, con_reserva):
    """Un formulario que solo puede contestar «el saldo es $0» no se pinta."""
    feria, _, _, reserva = con_reserva
    admin = _admin(feria)
    client.force_login(admin)
    with schema_context(feria.schema_name):
        pagos.registrar(
            reserva=reserva, persona=admin, monto=Decimal("15000.00"),
            metodo="transferencia", archivo=_pdf(), manual=True,
        )

    cuerpo = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk)
    ).content.decode()

    assert "Registrar un abono" not in cuerpo
    with schema_context(feria.schema_name):
        reserva.refresh_from_db()
        assert reserva.estado == Reserva.Estado.PAGADA


# ── CU-STD-020 · el descuento especial ────────────────────────


def test_aplicar_un_especial_baja_el_total(client, con_reserva):
    feria, _, _, reserva = con_reserva
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk),
        {
            "accion": "descuento_especial",
            "porcentaje": "20",
            "motivo": "Convenio con la Secretaría de Cultura.",
        },
        follow=True,
    )

    assert "Aplicaste un 20%" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        reserva.refresh_from_db()
        assert reserva.monto_total == Decimal("12000.00")
        descuento = reserva.descuentos.get(tipo=DescuentoAplicado.Tipo.ESPECIAL)
        assert descuento.motivo.startswith("Convenio")
        assert descuento.aplicado_por is not None


def test_sin_motivo_no_se_aplica(client, con_reserva):
    """`CU-STD-020` E1 y `RN-07`: es lo único que lo explica después."""
    feria, _, _, reserva = con_reserva
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk),
        {"accion": "descuento_especial", "porcentaje": "20", "motivo": "  "},
        follow=True,
    )

    assert "Escribe el motivo" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        reserva.refresh_from_db()
        assert reserva.monto_total == Decimal("15000.00")
        assert not reserva.descuentos.exists()


def test_con_uno_puesto_se_ofrece_retirarlo_y_no_aplicar_otro(client, con_reserva):
    """`RN-05`: uno por reserva. Ofrecer «aplicar» sería ofrecer un error."""
    feria, _, _, reserva = con_reserva
    admin = _admin(feria)
    client.force_login(admin)
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=reserva, administrador=admin, porcentaje=10, motivo="Convenio"
        )

    cuerpo = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk)
    ).content.decode()

    assert "Retirar el descuento" in cuerpo
    assert "Aplicar el descuento" not in cuerpo


def test_retirarlo_devuelve_el_total(client, con_reserva):
    feria, _, _, reserva = con_reserva
    admin = _admin(feria)
    client.force_login(admin)
    with schema_context(feria.schema_name):
        pagos.aplicar_descuento_especial(
            reserva=reserva, administrador=admin, porcentaje=10, motivo="Convenio"
        )

    respuesta = client.post(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk),
        {"accion": "retirar_descuento"},
        follow=True,
    )

    assert "Retiraste el descuento" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        reserva.refresh_from_db()
        assert reserva.monto_total == Decimal("15000.00")
        assert not reserva.descuentos.filter(
            tipo=DescuentoAplicado.Tipo.ESPECIAL
        ).exists()


# ── RN-02 · el umbral es de la convocatoria ───────────────────


def test_la_marca_del_umbral_sigue_a_la_convocatoria(client, con_reserva):
    """Con el anticipo al 40%, la barra no puede decir 50%.

    El porcentaje se configura en `A10` y `Reserva.anticipo` lo lee vivo;
    escrito a mano en la plantilla, la pantalla prometía confirmar en un
    sitio y el servicio confirmaba en otro.
    """
    feria, conv, _, reserva = con_reserva
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.porcentaje_anticipo = 40
        cfg.save(update_fields=["porcentaje_anticipo"])
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk)
    ).content.decode()

    assert "40% · se confirma" in cuerpo
    assert "50% · se confirma" not in cuerpo
    assert "left: 40%" in cuerpo


# ── La puerta ─────────────────────────────────────────────────


def test_un_participante_no_entra(client, con_reserva):
    feria, _, ana, reserva = con_reserva
    client.force_login(ana)

    respuesta = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva.pk)
    )

    assert respuesta.status_code == 403
