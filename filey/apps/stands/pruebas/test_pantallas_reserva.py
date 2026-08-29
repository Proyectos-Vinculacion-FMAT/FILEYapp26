"""
Las pantallas del carrito y la reserva (`CU-STD-011`, `012`, `013`, `028`,
`029`).

Lo que más se defiende aquí es que **la pantalla y el cobro digan lo
mismo**. El resumen del carrito y el total que se guarda salen de la
misma función a propósito; si alguien los separa, la persona confirma
una cifra y se le cobra otra, y eso no lo delata ninguna excepción.
"""

import re
from decimal import Decimal

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Reserva, Solicitud, Stand
from ..servicios import configuracion, mapas, reservas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _mapa():
    return {
        "formato": "filey-mapa/1",
        "mapa": {"salon": "Salón de pruebas", "columnas": 30, "filas": 10,
                 "metros_por_celda": 1.0, "tamano_celda": 12},
        "stands": [
            {"clave": f"A{i}", "etiqueta": f"A{i}", "col": i * 3, "fila": 0,
             "ancho_celdas": 3, "alto_celdas": 2}
            for i in range(1, 6)
        ],
        "decoraciones": [],
    }


@pytest.fixture
def listo(feria_2027):
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
    return feria_2027, conv, ana


def _agregar(client, feria, conv, clave):
    return client.post(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk),
        {"accion": "agregar", "clave": clave},
        follow=True,
    )


# ── CU-STD-011 · el carrito ───────────────────────────────────


def test_agregar_y_quitar_espacios(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)

    _agregar(client, feria, conv, "A1")
    cuerpo = _agregar(client, feria, conv, "A2").content.decode()
    assert "A1" in cuerpo and "A2" in cuerpo
    # Dos de 6 m² a 2 500.
    assert "30000.00" in cuerpo

    cuerpo = client.post(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk),
        {"accion": "quitar", "clave": "A1"},
        follow=True,
    ).content.decode()

    assert "15000.00" in cuerpo


def test_agregar_dos_veces_el_mismo_no_lo_duplica(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)

    _agregar(client, feria, conv, "A1")
    cuerpo = _agregar(client, feria, conv, "A1").content.decode()

    assert cuerpo.count('name="clave" value="A1"') == 1
    assert "15000.00" in cuerpo


def test_el_carrito_no_aparta_nada(client, listo):
    """Es una selección de trabajo: los espacios se protegen al confirmar."""
    feria, conv, ana = listo
    client.force_login(ana)

    _agregar(client, feria, conv, "A1")

    with schema_context(feria.schema_name):
        assert Stand.objects.get(clave="A1").esta_libre


def test_el_carrito_de_una_convocatoria_no_se_mezcla_con_otro(client, listo):
    """Una feria puede tener una convocatoria general y otra de pabellón.

    Mezclar sus carritos daría una reserva con espacios de dos mapas.
    """
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        otra = fabricas.convocatoria(nombre="Pabellón infantil")
        mapas.importar(convocatoria=otra, datos=_mapa())
        # Habilitada **también** en la otra: `RN-16` se comprueba por
        # convocatoria, así que sin esto la pantalla daría 404 y la
        # prueba pasaría por el motivo equivocado.
        otra_solicitud = solicitudes.enviar_solicitud(
            convocatoria=otra,
            persona=ana,
            editorial=ana.editorial,
        )
        otra_solicitud.estado = Solicitud.Estado.ACEPTADA
        otra_solicitud.fecha_revision = otra_solicitud.fecha_envio
        otra_solicitud.save()
    client.force_login(ana)

    _agregar(client, feria, conv, "A1")
    cuerpo = client.get(
        _url(feria, "stands:carrito", convocatoria_id=otra.pk)
    ).content.decode()

    assert "Todavía no has elegido" in cuerpo


def test_un_espacio_que_se_perdio_se_nombra_y_no_suma(client, listo):
    """`E1`. Se enseña cuál, no se tira en silencio: quien armó una
    selección de ocho tiene que ver qué perdió."""
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    _agregar(client, feria, conv, "A2")

    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)

    cuerpo = client.get(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Alguien reservó antes que tú" in cuerpo
    assert "Ya no disponible" in cuerpo
    # El total cuenta solo lo tomable: 15 000, no 30 000.
    assert "15000.00" in cuerpo


def test_sin_habilitacion_no_hay_carrito(client, listo):
    """`RN-16`, y con 404: un 403 confirmaría que ese carrito existe."""
    feria, conv, _ = listo
    with schema_context(feria.schema_name):
        otro = fabricas.persona(correo="otro@ejemplo.com", nombre="Otro")
    client.force_login(otro)

    respuesta = client.get(_url(feria, "stands:carrito", convocatoria_id=conv.pk))

    assert respuesta.status_code == 404


# ── CU-STD-012 · confirmar ────────────────────────────────────


def test_confirmar_crea_la_reserva_y_vacia_el_carrito(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    _agregar(client, feria, conv, "A2")

    respuesta = client.post(
        _url(feria, "stands:reservar", convocatoria_id=conv.pk), follow=True
    )

    assert respuesta.status_code == 200
    with schema_context(feria.schema_name):
        reserva = Reserva.objects.get()
        assert reserva.monto_total == Decimal("30000.00")
        assert reserva.lineas.count() == 2

    # Y el carrito quedó vacío: si no, volver atrás reservaría otra vez.
    cuerpo = client.get(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk)
    ).content.decode()
    assert "Todavía no has elegido" in cuerpo


def test_lo_que_dice_el_resumen_es_lo_que_se_cobra(client, listo):
    """La pantalla y el cobro salen de la misma función, a propósito.

    Separarlas es cómo se llega a que alguien confirme una cifra y se le
    cargue otra — y no lo delata ninguna excepción.
    """
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timezone.timedelta(days=5)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")

    cuerpo = client.get(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk)
    ).content.decode()
    prometido = re.findall(r"13500\.00", cuerpo)
    assert prometido, "el resumen no enseña el total con descuento"

    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk), follow=True)

    with schema_context(feria.schema_name):
        assert Reserva.objects.get().monto_total == Decimal("13500.00")


def test_confirmar_por_GET_no_reserva_nada(client, listo):
    """Llegar por un enlace o por volver atrás crearía una reserva que
    nadie pidió."""
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")

    client.get(_url(feria, "stands:reservar", convocatoria_id=conv.pk))

    with schema_context(feria.schema_name):
        assert not Reserva.objects.exists()


def test_si_alguien_llego_antes_se_sacan_del_carrito_solos(client, listo):
    """Reintentar tiene que costar un clic, no quitar uno por uno lo que
    ya se perdió."""
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    _agregar(client, feria, conv, "A2")
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)

    respuesta = client.post(
        _url(feria, "stands:reservar", convocatoria_id=conv.pk), follow=True
    )

    cuerpo = respuesta.content.decode()
    assert "Alguien reservó antes A1" in cuerpo
    assert 'value="A1"' not in cuerpo, "A1 sigue en el carrito"
    assert 'value="A2"' in cuerpo, "A2 se perdió sin motivo"
    with schema_context(feria.schema_name):
        assert not Reserva.objects.exists()


def test_confirmar_con_el_carrito_vacio_no_revienta(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)

    respuesta = client.post(
        _url(feria, "stands:reservar", convocatoria_id=conv.pk), follow=True
    )

    assert respuesta.status_code == 200
    assert "vacía" in respuesta.content.decode()


# ── CU-STD-013 · mi reserva ───────────────────────────────────


def test_mi_reserva_dice_total_abonado_pendiente_y_fechas(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))

    cuerpo = client.get(
        _url(feria, "stands:mis_reservas", convocatoria_id=conv.pk)
    ).content.decode()

    assert "15000.00" in cuerpo
    assert "7500.00" in cuerpo  # el anticipo del 50%
    assert "Por confirmar" in cuerpo
    assert "Vence el anticipo" in cuerpo


def test_sin_reserva_se_manda_al_mapa(client, listo):
    """`E1`: no hay reserva, y se dice dónde empezar una."""
    feria, conv, ana = listo
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:mis_reservas", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Todavía no tienes ninguna reserva" in cuerpo
    assert "Ir al mapa" in cuerpo


def test_una_vencida_lo_avisa_sin_cambiar_de_estado(client, listo):
    """`A1` y `RN-12`: vencer escala, no cancela."""
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))
    with schema_context(feria.schema_name):
        Reserva.objects.update(
            fecha_vencimiento_anticipo=timezone.now() - timezone.timedelta(days=1)
        )

    cuerpo = client.get(
        _url(feria, "stands:mis_reservas", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Se venció el plazo" in cuerpo
    assert "Por confirmar" in cuerpo, "se pintó como si el sistema ya hubiera hecho algo"
    assert "Vencida" in cuerpo


def test_no_veo_las_reservas_de_otra_editorial(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))

    with schema_context(feria.schema_name):
        beto = fabricas.persona(correo="beto@ejemplo.com", nombre="Beto")
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=beto, editorial=fabricas.editorial(beto)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
    client.force_login(beto)

    cuerpo = client.get(
        _url(feria, "stands:mis_reservas", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Todavía no tienes ninguna reserva" in cuerpo


# ── CU-STD-028 y 029 · el panel ───────────────────────────────


def _admin_de(feria, correo="rita@filey.org"):
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def test_la_cola_de_reservas_las_lista(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))

    client.force_login(_admin_de(feria))
    cuerpo = client.get(
        _url(feria, "stands:reservas", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Ediciones del Mayab" in cuerpo
    assert "15000.00" in cuerpo


def test_el_filtro_de_vencidas_va_en_la_consulta(client, listo):
    """No es un estado del modelo: es `por_confirmar` con el plazo pasado."""
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))

    client.force_login(_admin_de(feria))
    url = _url(feria, "stands:reservas", convocatoria_id=conv.pk)

    # Al día: no sale en el filtro.
    assert "Ediciones del Mayab" not in client.get(url + "?estado=vencidas").content.decode()

    with schema_context(feria.schema_name):
        Reserva.objects.update(
            fecha_vencimiento_anticipo=timezone.now() - timezone.timedelta(days=1)
        )

    assert "Ediciones del Mayab" in client.get(url + "?estado=vencidas").content.decode()


def test_el_aplicante_no_entra_a_la_cola_de_reservas(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)

    respuesta = client.get(_url(feria, "stands:reservas", convocatoria_id=conv.pk))

    assert respuesta.status_code == 403


def test_el_detalle_avisa_si_el_desglose_dejo_de_cuadrar(client, listo):
    """La contrapartida conocida de no guardar snapshots por línea.

    Se dice en pantalla en vez de dejar que lo descubra quien cuadre una
    factura: lo cobrado no se mueve, lo que cambia es cómo se explica.
    """
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))

    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("3000")
        cfg.save(update_fields=["costo_m2"])
        reserva_pk = Reserva.objects.get().pk

    client.force_login(_admin_de(feria))
    cuerpo = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva_pk)
    ).content.decode()

    assert "ya no cuadra con lo cobrado" in cuerpo
    assert "15000.00" in cuerpo  # lo cobrado
    assert "18000.00" in cuerpo  # lo que saldría hoy


def test_el_detalle_no_avisa_cuando_todo_cuadra(client, listo):
    """El aviso tiene que ser señal, no ruido de fondo."""
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))
    with schema_context(feria.schema_name):
        reserva_pk = Reserva.objects.get().pk

    client.force_login(_admin_de(feria))
    cuerpo = client.get(
        _url(feria, "stands:detalle_reserva", reserva_id=reserva_pk)
    ).content.decode()

    assert "ya no cuadra" not in cuerpo
