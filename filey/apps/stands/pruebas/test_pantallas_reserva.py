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
from ..servicios import carrito, configuracion, mapas, reservas, solicitudes
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

    # Y volver al carrito ya no enseña nada que elegir: con una reserva
    # viva, el carrito manda a la cuenta (`RN-23`).
    respuesta = client.get(_url(feria, "stands:carrito", convocatoria_id=conv.pk))

    assert respuesta.status_code == 302
    assert respuesta.url.endswith(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
    )
    with schema_context(feria.schema_name):
        assert carrito.claves_en(client.session, conv) == []


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
    assert "Alguien reservó antes que tú A1" in cuerpo
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
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
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
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
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
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
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
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk)
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

    assert "ya no coincide con lo cobrado" in cuerpo
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

    assert "ya no coincide" not in cuerpo


# ── El panel del módulo ───────────────────────────────────────


def test_el_panel_no_repite_el_menu_de_la_barra_lateral(client, listo):
    """Dos menús del mismo sistema es uno que se queda atrás.

    Las secciones las lista la barra lateral, que está en todas las
    pantallas del módulo. Repetirlas en el panel obligaría a acordarse de
    los dos sitios el día que se añada una.
    """
    feria, conv, _ = listo
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    # Una sola vez cada enlace, y el que las pinta es el `<aside>`.
    solicitudes_url = _url(feria, "stands:solicitudes", convocatoria_id=conv.pk)
    assert cuerpo.count(f'href="{solicitudes_url}"') == 1
    assert cuerpo.index("<aside") < cuerpo.index(f'href="{solicitudes_url}"')


def test_el_panel_avisa_de_lo_que_falta_configurar(client, feria_2027):
    """Sin precio y sin mapa el módulo se ve entero y no se puede operar.

    Las solicitudes entran, nadie puede reservar y todos los precios
    salen en cero. Hasta ahora eso solo se descubría abriendo una
    pantalla y encontrándola vacía.
    """
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
    client.force_login(_admin_de(feria_2027))

    cuerpo = client.get(
        _url(feria_2027, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Falta configurar los stands" in cuerpo
    assert "costo por m² está en cero" in cuerpo
    assert "No hay mapa del salón" in cuerpo


def test_configurado_el_panel_no_da_la_lata(client, listo):
    """El aviso tiene que ser señal, no ruido de fondo."""
    feria, conv, _ = listo
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Falta configurar los stands" not in cuerpo


def test_el_panel_saca_las_vencidas_a_la_cara(client, listo):
    """`RN-12`: vencer no cancela, así que alguien tiene que decidir."""
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))
    with schema_context(feria.schema_name):
        Reserva.objects.update(
            fecha_vencimiento_anticipo=timezone.now() - timezone.timedelta(days=1)
        )

    client.force_login(_admin_de(feria))
    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    # Como tarjeta pulsable, no como aviso suelto: lo que hace falta es
    # llegar a resolverla, no enterarse.
    assert "Reservas vencidas" in cuerpo
    assert "estado=vencidas" in cuerpo


def test_el_aplicante_no_entra_al_panel(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)

    respuesta = client.get(_url(feria, "stands:panel", convocatoria_id=conv.pk))

    assert respuesta.status_code == 403


def test_el_panel_no_ensena_ceros_cuando_no_hay_nada(client, listo):
    """Tres tarjetas diciendo «0» se leen como trabajo pendiente.

    Durante el medio segundo que se tarda en leer el número, «0
    solicitudes por revisar» y «3 solicitudes por revisar» ocupan el
    mismo sitio y tienen la misma forma.
    """
    feria, conv, _ = listo
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Nada pendiente" in cuerpo
    assert "Solicitudes por revisar" not in cuerpo


def test_lo_accionable_enlaza_y_el_estado_no(client, listo):
    """La diferencia entre las dos zonas del panel.

    Una cifra que pide algo tiene que llevar a donde se hace; una que
    describe cómo va, no lleva a ninguna parte. Mezclarlas deja «3
    solicitudes por revisar» con el mismo peso que «$2 500 el m²».
    """
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        # Una solicitud de otra persona, sin dictaminar.
        beto = fabricas.persona(correo="beto@ejemplo.com", nombre="Beto")
        solicitudes.enviar_solicitud(
            convocatoria=conv, persona=beto, editorial=fabricas.editorial(beto)
        )
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    # Lo accionable es un `<a>`.
    assert '<a class="stat-card accent-blue"' in cuerpo
    # El estado no: va en la zona de abajo, sin enlace.
    zona = cuerpo.split("Cómo va el recinto", 1)[1]
    assert "Comprometido" in zona
    assert "stat-card" not in zona


def test_la_ocupacion_se_mide_en_metros_y_no_en_espacios(client, listo):
    """Vender treinta espacios chicos no es vender tres grandes.

    Lo que sigue el dinero es la superficie; contar cajas daría una barra
    que avanza mientras la recaudación no se mueve.
    """
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))

    client.force_login(_admin_de(feria))
    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    # Cinco espacios de 6 m² = 30; uno reservado deja 24 libres.
    assert "24 m²" in cuerpo
    assert "libres de 30" in cuerpo
    # Y la barra lleva los tres tramos con los mismos colores del mapa.
    assert 'class="ocupacion-barra"' in cuerpo
    assert 'class="es-reservado"' in cuerpo


def test_el_dinero_separa_lo_comprometido_de_lo_cobrado(client, listo):
    """Son dos cifras distintas y confundirlas es contar dinero que no
    ha entrado: una reserva viva compromete su total, y lo cobrado son
    solo los abonos validados."""
    feria, conv, ana = listo
    client.force_login(ana)
    _agregar(client, feria, conv, "A1")
    client.post(_url(feria, "stands:reservar", convocatoria_id=conv.pk))

    client.force_login(_admin_de(feria))
    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Comprometido" in cuerpo and "15000.00" in cuerpo
    assert "Cobrado" in cuerpo and "0.00" in cuerpo


def test_sin_mapa_no_se_inventa_una_barra(client, feria_2027):
    """Una barra plana sin explicación se lee como «todo vendido»."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
    client.force_login(_admin_de(feria_2027))

    cuerpo = client.get(
        _url(feria_2027, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert "ocupacion-barra" not in cuerpo
    assert "Todavía no hay ningún mapa cargado" in cuerpo


# ── El carrito al lado del mapa (CU-STD-011) ──────────────────
#
# El prototipo de STD pone el mapa a la izquierda y la selección a la
# derecha, y agregar un espacio actualiza la columna **sin sacarte del
# plano**. Aquí eso lo hace htmx: recargar costaría volver a bajar los
# 39 MB del canvas y perder el zoom donde estabas.


def _mapa_url(feria, conv):
    return _url(feria, "stands:mapa", convocatoria_id=conv.pk)


def _lateral(feria, conv):
    return _url(feria, "stands:carrito_lateral", convocatoria_id=conv.pk)


def test_el_mapa_trae_el_carrito_al_lado(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)

    cuerpo = client.get(_mapa_url(feria, conv)).content.decode()

    assert 'class="mapa-con-carrito"' in cuerpo
    assert 'id="carrito-lateral"' in cuerpo
    assert "Tu selección está vacía" in cuerpo


def test_el_carrito_llega_pintado_con_la_pagina(client, listo):
    """Y no vacío para llenarse al primer intercambio.

    Nacer vacío y llenarse de golpe se lee como si se hubiera perdido lo
    elegido antes.
    """
    feria, conv, ana = listo
    client.force_login(ana)
    client.post(_lateral(feria, conv), {"accion": "agregar", "clave": "A1"})

    cuerpo = client.get(_mapa_url(feria, conv)).content.decode()

    assert "A1" in cuerpo.split('id="carrito-lateral"', 1)[1]


def test_agregar_no_saca_del_mapa(client, listo):
    """Devuelve **solo el carrito**, no una redirección ni la página.

    Es lo que hace que el plano se quede donde estaba.
    """
    feria, conv, ana = listo
    client.force_login(ana)

    respuesta = client.post(
        _lateral(feria, conv), {"accion": "agregar", "clave": "A1"}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.content.decode()
    assert cuerpo.lstrip().startswith("<aside")
    assert "mapa-canvas" not in cuerpo, "devolvió la página entera"
    assert "15000" in cuerpo.replace(",", "")


def test_el_carrito_lateral_suma_y_resta(client, listo):
    feria, conv, ana = listo
    client.force_login(ana)

    client.post(_lateral(feria, conv), {"accion": "agregar", "clave": "A1"})
    cuerpo = client.post(
        _lateral(feria, conv), {"accion": "agregar", "clave": "A2"}
    ).content.decode()
    assert "30000" in cuerpo.replace(",", "")
    assert "12 m²" in cuerpo

    cuerpo = client.post(
        _lateral(feria, conv), {"accion": "quitar", "clave": "A1"}
    ).content.decode()
    assert "15000" in cuerpo.replace(",", "")

    cuerpo = client.post(_lateral(feria, conv), {"accion": "vaciar"}).content.decode()
    assert "Tu selección está vacía" in cuerpo


def test_lo_que_alguien_tomo_antes_no_suma_pero_se_ve(client, listo):
    """`E1`, también en la columna de al lado."""
    feria, conv, ana = listo
    client.force_login(ana)
    client.post(_lateral(feria, conv), {"accion": "agregar", "clave": "A1"})
    client.post(_lateral(feria, conv), {"accion": "agregar", "clave": "A2"})
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)

    cuerpo = client.get(_lateral(feria, conv)).content.decode()

    # Con los espacios colapsados: la plantilla parte la frase en dos
    # líneas y esa aserción se rompería con cualquier reindentado.
    plano = re.sub(r"\s+", " ", cuerpo)
    assert "Alguien reservó antes que tú A1" in plano
    assert "es-no-disponible" in cuerpo
    # Y el subtotal cuenta solo lo tomable.
    assert "15000" in cuerpo.replace(",", "")


def test_la_misma_cifra_en_el_carrito_lateral_y_en_el_de_confirmar(client, listo):
    """Salen de la misma función a propósito.

    Dos cálculos para lo mismo es cómo se llega a que una pantalla
    prometa un total y la siguiente cobre otro.
    """
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.fecha_limite_pronto_pago = timezone.localdate() + timezone.timedelta(days=5)
        cfg.save(update_fields=["fecha_limite_pronto_pago"])
    client.force_login(ana)

    lateral = client.post(
        _lateral(feria, conv), {"accion": "agregar", "clave": "A1"}
    ).content.decode()
    confirmar = client.get(
        _url(feria, "stands:carrito", convocatoria_id=conv.pk)
    ).content.decode()

    # 15 000 − 10% de pronto pago.
    assert "13500.00" in lateral
    assert "13500.00" in confirmar


def test_el_admin_no_lleva_carrito_al_lado(client, listo):
    """Quien administra no compra espacios."""
    feria, conv, _ = listo
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:mapa_completo", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'id="carrito-lateral"' not in cuerpo
    assert 'data-campo="agregar"' not in cuerpo


def test_sin_habilitacion_no_hay_carrito_lateral(client, listo):
    """`RN-16`, con 404 como el resto de las pantallas de reserva."""
    feria, conv, _ = listo
    with schema_context(feria.schema_name):
        otro = fabricas.persona(correo="otro@ejemplo.com", nombre="Otro")
    client.force_login(otro)

    assert client.get(_lateral(feria, conv)).status_code == 404


def test_el_modal_pide_el_detalle_al_servidor(client, listo):
    """Y no lo compone en JavaScript con lo que manda el canvas.

    El canvas no conoce la zona ni el «qué incluye», así que un modal
    armado en el navegador enseñaba un detalle recortado — y calculaba el
    precio por su cuenta, que es la parte cara del error.
    """
    feria, conv, ana = listo
    client.force_login(ana)

    cuerpo = client.get(_mapa_url(feria, conv)).content.decode()

    tarjeta = cuerpo.split('id="mapa-tarjeta"', 1)[1]
    assert "data-url-detalle=" in tarjeta
    assert 'id="mapa-tarjeta-cuerpo"' in tarjeta
    # Y no lleva el botón de «ver detalle»: el modal **es** el detalle.
    assert "Ver detalle" not in tarjeta


def test_el_detalle_para_el_modal_llega_sin_chasis(client, listo):
    """Devolver la página entera metería otro chasis dentro del diálogo."""
    feria, conv, ana = listo
    client.force_login(ana)

    respuesta = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1"),
        headers={"HX-Request": "true"},
    )

    cuerpo = respuesta.content.decode()
    assert "<html" not in cuerpo
    assert "topbar" not in cuerpo
    # Y trae el detalle entero, con el «agregar» apuntando al carrito.
    assert "Superficie" in cuerpo and "15000" in cuerpo.replace(",", "")
    assert f'hx-post="{_lateral(feria, conv)}"' in cuerpo
    assert 'hx-target="#carrito-lateral"' in cuerpo
    # Sin «volver al mapa»: ya se está en él.
    assert "Volver al mapa" not in cuerpo


def test_la_pantalla_propia_del_espacio_sigue_completa(client, listo):
    """Es la que funciona pegando la URL, y sin JavaScript."""
    feria, conv, ana = listo
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")
    ).content.decode()

    assert "<html" in cuerpo
    assert "Volver al mapa" in cuerpo
    assert "Superficie" in cuerpo


def test_un_espacio_tomado_no_ofrece_agregarlo(client, listo):
    feria, conv, ana = listo
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1"),
        headers={"HX-Request": "true"},
    ).content.decode()

    assert "ya está tomado" in cuerpo
    assert 'data-campo="agregar"' not in cuerpo
