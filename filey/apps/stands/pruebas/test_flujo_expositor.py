"""
El flujo del expositor, de punta a punta (`CU-STD-003` y `RN-23`).

Lo que se defiende aquí no es una pantalla sino **el orden**: solicitud →
revisión → espacios → confirmación → cuenta. Cada paso se alcanza solo
desde el anterior, y quien vuelve a entrar cae donde lo dejó, no al
principio.

Es la parte que ninguna prueba de pantalla ve por su cuenta: cada una
comprueba que su vista pinta lo suyo, y el flujo se rompe **entre**
dos vistas —una puerta que manda al sitio de antes, un carrito que sigue
ofreciendo espacios a quien ya reservó—.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from django_tenants.utils import schema_context

from ..models import Movimiento, Reserva, Solicitud
from ..servicios import configuracion, mapas, reservas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


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


@pytest.fixture
def escenario(feria_2027):
    """Una convocatoria con mapa, precio y una persona sin solicitud."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_mapa())
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.instrucciones_pago = "BBVA · CLABE 012 345 678 901 234 567"
        # Con fecha: sin ella el pronto pago no aplica aunque el
        # porcentaje esté puesto (`RN-04`), y la cuenta saldría sin
        # descuento — que es justo lo que estas pruebas comprueban.
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timedelta(days=30)
        cfg.save()
    return feria_2027, conv, ana


def _aplica(feria, conv, persona, estado=Solicitud.Estado.PENDIENTE):
    with schema_context(feria.schema_name):
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=persona, editorial=fabricas.editorial(persona)
        )
        if estado != Solicitud.Estado.PENDIENTE:
            solicitud.estado = estado
            solicitud.fecha_revision = solicitud.fecha_envio
            solicitud.save()
    return solicitud


def _reserva(feria, conv, persona, claves=("A1",)):
    with schema_context(feria.schema_name):
        return reservas.crear(
            convocatoria=conv, persona=persona, claves=list(claves)
        )


# ── La puerta: a cada quien a su paso ─────────────────────────


def test_sin_solicitud_la_puerta_lleva_al_formulario(client, escenario):
    feria, conv, ana = escenario
    client.force_login(ana)

    respuesta = client.get(_url(feria, "stands:inicio", convocatoria_id=conv.pk))

    assert respuesta.status_code == 302
    assert respuesta.url.endswith(
        _url(feria, "stands:solicitud", convocatoria_id=conv.pk)
    )


def test_con_la_solicitud_en_revision_la_puerta_lleva_a_esperar(client, escenario):
    """El paso 2 no tiene pantalla propia: es el estado de la solicitud.

    Y la pantalla tiene que **decirlo**, no solo pintar el formulario en
    gris: quien vuelve a entrar viene a preguntar si ya le contestaron.
    """
    feria, conv, ana = escenario
    _aplica(feria, conv, ana)
    client.force_login(ana)

    respuesta = client.get(
        _url(feria, "stands:inicio", convocatoria_id=conv.pk), follow=True
    )
    cuerpo = respuesta.content.decode()

    assert "Tu solicitud está en revisión" in cuerpo
    # Y la barra de pasos lo marca, en vez de dejarla en el primero.
    assert 'aria-current="step"' in cuerpo
    assert "Revisión" in cuerpo


def test_aceptada_la_puerta_lleva_directo_a_elegir_espacios(client, escenario):
    """La primera de las dos reglas del ruteo."""
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    client.force_login(ana)

    respuesta = client.get(_url(feria, "stands:inicio", convocatoria_id=conv.pk))

    assert respuesta.status_code == 302
    assert respuesta.url.endswith(_url(feria, "stands:mapa", convocatoria_id=conv.pk))


def test_con_reserva_viva_la_puerta_lleva_directo_a_la_cuenta(client, escenario):
    """La segunda: quien ya reservó entra a pagar, no a elegir."""
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    _reserva(feria, conv, ana)
    client.force_login(ana)

    respuesta = client.get(_url(feria, "stands:inicio", convocatoria_id=conv.pk))

    assert respuesta.status_code == 302
    assert respuesta.url.endswith(_url(feria, "stands:cuenta", convocatoria_id=conv.pk))


def test_una_reserva_cancelada_devuelve_al_mapa(client, escenario):
    """Cancelar reabre el flujo: `RN-23` solo cuenta lo vivo."""
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    reserva = _reserva(feria, conv, ana)
    with schema_context(feria.schema_name):
        reserva.estado = Reserva.Estado.CANCELADA
        reserva.save(update_fields=["estado"])
    client.force_login(ana)

    respuesta = client.get(_url(feria, "stands:inicio", convocatoria_id=conv.pk))

    assert respuesta.url.endswith(_url(feria, "stands:mapa", convocatoria_id=conv.pk))


# ── RN-23 · una editorial, una reserva ────────────────────────


def test_no_se_puede_reservar_dos_veces(escenario):
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    _reserva(feria, conv, ana, ["A1"])

    with schema_context(feria.schema_name):
        with pytest.raises(reservas.YaTieneReserva) as exc:
            reservas.crear(convocatoria=conv, persona=ana, claves=["A2"])

    assert "una sola" in str(exc.value)
    with schema_context(feria.schema_name):
        assert Reserva.objects.count() == 1


def test_la_segunda_reserva_lleva_a_la_cuenta_y_no_a_un_error(client, escenario):
    """Es un paso más adelante, no una avería: se avisa y se le lleva."""
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    _reserva(feria, conv, ana, ["A1"])
    client.force_login(ana)
    # Se fuerza el carrito por debajo: la pantalla ya no deja llegar aquí.
    sesion = client.session
    sesion[f"stands:carrito:{conv.pk}"] = ["A2"]
    sesion.save()

    respuesta = client.post(
        _url(feria, "stands:reservar", convocatoria_id=conv.pk), follow=True
    )

    assert respuesta.status_code == 200
    assert "Ya tienes una reserva" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        assert Reserva.objects.count() == 1


def test_cancelada_no_estorba_a_la_siguiente(escenario):
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    reserva = _reserva(feria, conv, ana, ["A1"])
    with schema_context(feria.schema_name):
        reserva.estado = Reserva.Estado.CANCELADA
        reserva.save(update_fields=["estado"])

        otra = reservas.crear(convocatoria=conv, persona=ana, claves=["A2"])

        assert otra.pk != reserva.pk
        assert Reserva.objects.count() == 2


def test_con_reserva_viva_el_mapa_y_el_carrito_mandan_a_la_cuenta(client, escenario):
    """Con una reserva en pie no hay nada que elegir."""
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    _reserva(feria, conv, ana)
    client.force_login(ana)

    for nombre in ("stands:mapa", "stands:carrito"):
        respuesta = client.get(_url(feria, nombre, convocatoria_id=conv.pk))
        assert respuesta.status_code == 302, nombre
        assert respuesta.url.endswith(
            _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
        ), nombre


def test_el_carrito_lateral_responde_con_hx_redirect(client, escenario):
    """htmx seguiría un 302 y metería la página dentro de la columna."""
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    _reserva(feria, conv, ana)
    client.force_login(ana)

    respuesta = client.get(
        _url(feria, "stands:carrito_lateral", convocatoria_id=conv.pk),
        headers={"hx-request": "true"},
    )

    assert respuesta.status_code == 204
    assert respuesta["HX-Redirect"].endswith(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
    )


# ── El último paso: la cuenta y sus pagos ─────────────────────


def test_la_cuenta_dice_total_anticipo_y_saldo(client, escenario):
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    _reserva(feria, conv, ana, ["A1", "A2"])
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
    ).content.decode()

    # Dos de 6 m² a 2 500, con el 10% de pronto pago por omisión.
    assert "30000.00" in cuerpo
    assert "27000.00" in cuerpo  # total con descuento
    assert "13500.00" in cuerpo  # anticipo del 50%
    assert "A1" in cuerpo and "A2" in cuerpo

    # Las instrucciones de pago viven en su pestaña (`CU-STD-015`), que
    # va por URL para no bajar los 39 MB del mapa en cada visita.
    pagos = client.get(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk) + "?ver=pagos"
    ).content.decode()

    assert "CLABE" in pagos


def test_reportar_un_abono_lo_deja_pendiente_de_validar(client, escenario):
    """`CU-STD-016`: es una declaración, no un cobro. No baja el saldo."""
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    reserva = _reserva(feria, conv, ana)
    client.force_login(ana)

    respuesta = client.post(
        _url(feria, "stands:registrar_abono", convocatoria_id=conv.pk),
        {
            "monto": "1000.00",
            "metodo": "transferencia",
            "comprobante": SimpleUploadedFile("recibo.pdf", b"%PDF-1.4"),
        },
        follow=True,
    )
    cuerpo = respuesta.content.decode()

    assert "Registramos tu abono" in cuerpo
    assert "En revisión" in cuerpo
    with schema_context(feria.schema_name):
        movimiento = Movimiento.objects.get()
        assert movimiento.estado == Movimiento.Estado.PENDIENTE
        assert movimiento.origen == Movimiento.Origen.APLICANTE
        assert movimiento.comprobante is not None
        # Y el saldo no se movió: solo lo validado cuenta.
        assert reserva.monto_abonado == Decimal("0.00")


def test_un_abono_sin_comprobante_no_pasa(client, escenario):
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    _reserva(feria, conv, ana)
    client.force_login(ana)

    respuesta = client.post(
        _url(feria, "stands:registrar_abono", convocatoria_id=conv.pk),
        {"monto": "1000.00", "metodo": "transferencia"},
        follow=True,
    )

    assert "Adjunta el comprobante" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        assert not Movimiento.objects.exists()


def test_un_abono_mayor_que_el_saldo_se_rechaza(client, escenario):
    """`CU-STD-016` E2. La regla es del servicio, el aviso de la pantalla."""
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    _reserva(feria, conv, ana)
    client.force_login(ana)

    respuesta = client.post(
        _url(feria, "stands:registrar_abono", convocatoria_id=conv.pk),
        {
            "monto": "999999.00",
            "metodo": "transferencia",
            "comprobante": SimpleUploadedFile("recibo.pdf", b"%PDF-1.4"),
        },
        follow=True,
    )

    assert "mayor que el saldo" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        assert not Movimiento.objects.exists()


def test_sin_reserva_la_cuenta_ofrece_el_mapa(client, escenario):
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Todavía no tienes ninguna reserva" in cuerpo
    assert _url(feria, "stands:mapa", convocatoria_id=conv.pk) in cuerpo


def test_sin_habilitacion_no_hay_cuenta(client, escenario):
    """`RN-16` con 404: un 403 confirmaría que esa cuenta existe."""
    feria, conv, ana = escenario
    client.force_login(ana)

    respuesta = client.get(_url(feria, "stands:cuenta", convocatoria_id=conv.pk))

    assert respuesta.status_code == 404


# ── La barra de pasos ─────────────────────────────────────────


def test_la_barra_de_pasos_acompana_las_cuatro_pantallas(client, escenario):
    feria, conv, ana = escenario
    _aplica(feria, conv, ana, Solicitud.Estado.ACEPTADA)
    client.force_login(ana)

    for nombre in ("stands:solicitud", "stands:mapa", "stands:carrito"):
        cuerpo = client.get(
            _url(feria, nombre, convocatoria_id=conv.pk)
        ).content.decode()
        assert 'class="pasos"' in cuerpo, nombre
        assert "Confirmación" in cuerpo, nombre


def test_el_mapa_del_administrador_no_lleva_barra_de_pasos(client, escenario):
    """No es su trámite: quien administra no aplica ni reserva."""
    from apps.ferias.models import AdminFeria
    from apps.registros.models import Persona

    feria, conv, _ = escenario
    # Administra sin ser dueña: la feria ya trae la suya y
    # `un_solo_dueno_por_feria` no admite otra.
    rita = Persona.objects.create_user(
        correo="rita@filey.org", nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=rita, es_dueno=False)
    client.force_login(rita)

    cuerpo = client.get(
        _url(feria, "stands:mapa_completo", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'class="pasos"' not in cuerpo
