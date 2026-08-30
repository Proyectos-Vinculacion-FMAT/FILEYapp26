"""
A10 · La pantalla de configuración de la convocatoria (`CU-STD-034`).

Hasta hoy esto vivía en `/f/<slug>/django-admin/` y era provisional por
dos motivos que estas pruebas fijan: el actor tenía que ser **quien
administra la feria** y no el equipo técnico (`is_staff`), y la pantalla
tenía que poder decir lo que un cambio de precio **no** hace —`RN-01`
congela lo ya reservado—.
"""

import re
from datetime import timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.convocatorias import modulos
from apps.convocatorias.models import TipoConvocatoria
from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import ConfiguracionSistema, Reserva, Solicitud
from ..servicios import configuracion, mapas, reservas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _admin(feria, correo="rita@filey.org"):
    """Administra la feria sin ser su dueña."""
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


@pytest.fixture
def convocatoria(feria_2027):
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("2500")
        cfg.save(update_fields=["costo_m2"])
    return feria_2027, conv


def _datos(**cambios):
    """Un POST completo. Los campos vacíos también viajan."""
    datos = {
        "costo_m2": "3000",
        "porcentaje_anticipo": "50",
        "plazo_reserva_dias": "30",
        "descuento_pronto_pago": "10",
        "fecha_limite_pronto_pago": "",
        "banco_titular": "Patronato de la UADY",
        "banco_nombre": "BBVA",
        "banco_cuenta": "0123 4567 8901 2345 67",
        "banco_clabe": "012 345 678 901 234 567",
        "banco_sucursal": "Mérida Centro",
        "banco_referencia": "El nombre de tu editorial",
        "instrucciones_pago": "Manda el comprobante el mismo día.",
    }
    datos.update(cambios)
    return datos


# ── Quién entra ───────────────────────────────────────────────


def test_la_sirve_quien_administra_la_feria(client, convocatoria):
    """El actor de `CU-STD-034`, y no el `is_staff` del admin de Django."""
    feria, conv = convocatoria
    client.force_login(_admin(feria))

    respuesta = client.get(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk)
    )

    assert respuesta.status_code == 200
    assert "Costos y plazos" in respuesta.content.decode()


def test_un_participante_no_entra(client, convocatoria):
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        ana = fabricas.persona()
    client.force_login(ana)

    respuesta = client.get(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk)
    )

    assert respuesta.status_code == 403


def test_la_seccion_del_menu_ya_no_esta_apagada(client, convocatoria):
    """Estaba en el plan del módulo y sin ruta; ahora enlaza."""
    feria, conv = convocatoria
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:panel", convocatoria_id=conv.pk)
    ).content.decode()

    assert _url(feria, "stands:configuracion", convocatoria_id=conv.pk) in cuerpo


def test_el_modulo_declara_la_seccion_con_su_ruta():
    seccion = next(
        s
        for s in modulos.modulo_de(TipoConvocatoria.STD).secciones_panel
        if s.etiqueta == "Configuración"
    )

    assert seccion.ruta == "stands:configuracion"


# ── Guardar ───────────────────────────────────────────────────


def test_guarda_precio_y_datos_bancarios_de_una_vez(client, convocatoria):
    """Una pantalla y un botón: son las dos mitades de abrir la venta."""
    feria, conv = convocatoria
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk),
        _datos(),
        follow=True,
    )

    assert "Guardamos la configuración" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        cfg = ConfiguracionSistema.objects.get(convocatoria=conv)
        assert cfg.costo_m2 == Decimal("3000")
        assert cfg.banco_clabe == "012 345 678 901 234 567"
        assert cfg.tiene_datos_bancarios


def test_lo_guardado_llega_a_la_pantalla_del_expositor(client, convocatoria):
    """El circuito entero: se declara aquí y se lee allá (`CU-STD-015`)."""
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
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
        ana = fabricas.persona()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()

    client.force_login(_admin(feria))
    client.post(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk), _datos()
    )

    with schema_context(feria.schema_name):
        reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
    client.force_login(ana)
    cuerpo = client.get(
        _url(feria, "stands:cuenta", convocatoria_id=conv.pk) + "?ver=pagos"
    ).content.decode()

    assert "Patronato de la UADY" in cuerpo
    assert "012 345 678 901 234 567" in cuerpo


def test_el_precio_nuevo_no_toca_las_reservas_que_ya_existen(client, convocatoria):
    """`RN-01`. Es lo que la pantalla promete, y lo que hay que sostener."""
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
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
        ana = fabricas.persona()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        reserva = reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])
        antes = reserva.monto_total

    client.force_login(_admin(feria))
    respuesta = client.post(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk),
        _datos(costo_m2="9999"),
        follow=True,
    )

    assert "conservan el precio que aceptaron" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        reserva.refresh_from_db()
        assert reserva.monto_total == antes


def test_avisa_de_las_reservas_en_curso_antes_de_tocar_el_precio(
    client, convocatoria
):
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
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
        ana = fabricas.persona()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
        reservas.crear(convocatoria=conv, persona=ana, claves=["A1"])

    client.force_login(_admin(feria))
    cuerpo = client.get(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk)
    ).content.decode()

    # Normalizado: el aviso se parte en dos renglones en la plantilla, y
    # el navegador colapsa los espacios igual que esto.
    assert "Hay 1 reserva en curso" in re.sub(r"\s+", " ", cuerpo)


# ── Lo que no deja guardar ────────────────────────────────────


def test_el_costo_en_cero_se_rechaza(client, convocatoria):
    """Con cero, cada espacio saldría gratis: es el fallo caro del módulo."""
    feria, conv = convocatoria
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk),
        _datos(costo_m2="0"),
        follow=True,
    )

    assert "saldría gratis" in respuesta.content.decode()
    with schema_context(feria.schema_name):
        assert ConfiguracionSistema.objects.get(
            convocatoria=conv
        ).costo_m2 == Decimal("2500")


def test_una_clabe_corta_se_rechaza_y_no_guarda_nada(client, convocatoria):
    feria, conv = convocatoria
    client.force_login(_admin(feria))

    respuesta = client.post(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk),
        _datos(banco_clabe="012 345 678"),
        follow=True,
    )
    cuerpo = respuesta.content.decode()

    assert "18 dígitos" in cuerpo
    assert "No guardamos nada" in cuerpo
    with schema_context(feria.schema_name):
        cfg = ConfiguracionSistema.objects.get(convocatoria=conv)
        assert cfg.banco_clabe == ""
        assert cfg.costo_m2 == Decimal("2500"), "tampoco lo que sí era válido"


def test_lo_que_falta_para_vender_se_dice_arriba(client, convocatoria):
    feria, conv = convocatoria
    with schema_context(feria.schema_name):
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = Decimal("0")
        cfg.save(update_fields=["costo_m2"])
    client.force_login(_admin(feria))

    cuerpo = client.get(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Falta algo para poder vender" in cuerpo
    assert "cada espacio saldría en cero" in cuerpo
    assert "quien reserve no sabrá a dónde pagar" in cuerpo


def test_la_fecha_del_pronto_pago_va_y_vuelve_en_iso(client, convocatoria):
    """El `<input type="date">` habla ISO, y el locale es `es-mx`.

    Es el campo que más fácil se rompe en silencio: si el formato de
    entrada del locale no admitiera `%Y-%m-%d`, el navegador mandaría una
    fecha válida y el formulario diría que no lo es. Y al revés — si el
    widget no la sacara en ISO, el selector nativo abriría vacío sobre
    una fecha que sí está guardada.
    """
    feria, conv = convocatoria
    limite = timezone.localdate() + timedelta(days=20)
    client.force_login(_admin(feria))

    client.post(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk),
        _datos(fecha_limite_pronto_pago=limite.isoformat()),
    )

    with schema_context(feria.schema_name):
        assert ConfiguracionSistema.objects.get(
            convocatoria=conv
        ).fecha_limite_pronto_pago == limite

    cuerpo = client.get(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk)
    ).content.decode()

    assert f'value="{limite.isoformat()}"' in cuerpo


def test_sin_fecha_no_hay_campana_de_pronto_pago(client, convocatoria):
    """Vaciarla es legítimo: `RN-04` deja de aplicar y no es un error."""
    feria, conv = convocatoria
    client.force_login(_admin(feria))

    client.post(
        _url(feria, "stands:configuracion", convocatoria_id=conv.pk),
        _datos(fecha_limite_pronto_pago=""),
    )

    with schema_context(feria.schema_name):
        cfg = ConfiguracionSistema.objects.get(convocatoria=conv)
        assert cfg.fecha_limite_pronto_pago is None
        assert reservas.pronto_pago_vigente(conv) == 0
