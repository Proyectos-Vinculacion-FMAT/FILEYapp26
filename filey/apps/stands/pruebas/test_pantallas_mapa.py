"""
Las tres pantallas del showfloor: `CU-STD-009`, `010` y `032`.

Lo que más se defiende aquí es **`RN-09`**: quien aplica no distingue
`reservado` de `ocupado`. No es una preferencia de diseño — saber cuál de
los dos es no le sirve para nada, porque no puede tomar ninguno, y sí
dice quién va ganando el reparto del recinto. El fallo, además, sería
mudo: la pantalla se vería perfecta y estaría contando de más.

La otra mitad es `RN-16`: el mapa solo se abre con una solicitud
`aceptada`. Un mapa visible antes de tiempo invita a elegir un espacio a
quien todavía no puede tomarlo.
"""

import json
import re
from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Solicitud, Stand
from ..servicios import configuracion, dibujo, mapas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db

MAPA_2026 = Path(__file__).resolve().parents[1] / "mapas" / "filey-2026.json"


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _mapa_chico():
    return {
        "formato": "filey-mapa/1",
        "mapa": {"salon": "Salón de pruebas", "columnas": 20, "filas": 10,
                 "metros_por_celda": 1.0, "tamano_celda": 12},
        "stands": [
            {"clave": "A1", "etiqueta": "A1", "col": 0, "fila": 0,
             "ancho_celdas": 3, "alto_celdas": 2},
            {"clave": "A2", "etiqueta": "A2", "col": 3, "fila": 0,
             "ancho_celdas": 3, "alto_celdas": 2},
            {"clave": "A3", "etiqueta": "A3", "col": 6, "fila": 0,
             "ancho_celdas": 3, "alto_celdas": 2},
        ],
        "decoraciones": [
            {"tipo": "rectangulo", "etiqueta": "Bodega", "col": 0, "fila": 6,
             "ancho_celdas": 5, "alto_celdas": 3},
        ],
    }


@pytest.fixture
def escenario(feria_2027):
    """Una convocatoria con mapa y una editorial ya aceptada."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=_mapa_chico())
        cfg = configuracion.de_la_convocatoria(conv)
        cfg.costo_m2 = 2500
        cfg.save(update_fields=["costo_m2"])
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
    return feria_2027, conv, ana


# ── RN-16 · el mapa solo se abre con solicitud aceptada ───────


def test_sin_solicitud_aceptada_no_se_ve_el_mapa(client, escenario):
    """`E1`. Y se ofrece el sitio donde sí puede hacer algo."""
    feria, conv, _ = escenario
    with schema_context(feria.schema_name):
        otro = fabricas.persona(correo="otro@ejemplo.com", nombre="Otro")
    client.force_login(otro)

    cuerpo = client.get(_url(feria, "stands:mapa", convocatoria_id=conv.pk)).content.decode()

    assert "Todavía no puedes elegir espacios" in cuerpo
    assert "<svg" not in cuerpo
    assert "Ver cómo va la mía" in cuerpo


def test_con_la_solicitud_pendiente_tampoco(client, escenario):
    """Aceptada, no enviada: `RN-16` dice `aceptada`."""
    feria, conv, ana = escenario
    with schema_context(feria.schema_name):
        Solicitud.objects.update(estado=Solicitud.Estado.PENDIENTE)
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "stands:mapa", convocatoria_id=conv.pk)).content.decode()

    assert "<svg" not in cuerpo


def test_aceptada_ve_el_mapa_con_sus_espacios(client, escenario):
    feria, conv, ana = escenario
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "stands:mapa", convocatoria_id=conv.pk)).content.decode()

    assert "<svg" in cuerpo
    assert "Salón de pruebas" in cuerpo
    # Con el prefijo completo: `mapa-espacios` (el grupo) también
    # empieza por `mapa-espacio` y contaría de más.
    assert cuerpo.count('class="mapa-espacio es-') == 3
    assert "3 espacios disponibles de 3" in cuerpo


def test_el_detalle_pide_la_misma_habilitacion_que_el_mapa(client, escenario):
    """Si no, la URL del detalle sería la puerta de atrás del mapa."""
    feria, conv, _ = escenario
    with schema_context(feria.schema_name):
        otro = fabricas.persona(correo="otro@ejemplo.com", nombre="Otro")
    client.force_login(otro)

    respuesta = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")
    )

    assert respuesta.status_code == 404


# ── RN-09 · el aplicante no distingue reservado de ocupado ────


def test_el_aplicante_ve_ocupado_donde_hay_reservado(client, escenario):
    """El fallo que esta prueba cubre sería mudo.

    La pantalla se vería perfecta y estaría diciendo quién va ganando el
    reparto del recinto a alguien que solo necesita saber si puede tomar
    el espacio o no.
    """
    feria, conv, ana = escenario
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)
        Stand.objects.filter(clave="A2").update(estado=Stand.Estado.OCUPADO)
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "stands:mapa", convocatoria_id=conv.pk)).content.decode()

    assert "es-reservado" not in cuerpo, "se le está diciendo cuál está reservado"
    assert cuerpo.count("es-ocupado") >= 2
    assert "1 espacios disponibles de 3" in cuerpo


def test_quien_administra_ve_los_tres_estados(client, escenario):
    """`RN-18`: el administrador ve el mapa sin censura."""
    feria, conv, _ = escenario
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)
        Stand.objects.filter(clave="A2").update(estado=Stand.Estado.OCUPADO)
        admin = Persona.objects.create_user(
            correo="rita@filey.org", nombre="Rita", primer_apellido="Uc"
        )
    AdminFeria.objects.create(feria=feria, persona=admin, es_dueno=False)
    client.force_login(admin)

    cuerpo = client.get(
        _url(feria, "stands:mapa_completo", convocatoria_id=conv.pk)
    ).content.decode()

    assert "es-reservado" in cuerpo
    assert "es-ocupado" in cuerpo


def test_solo_lo_reservable_es_un_enlace(client, escenario):
    """Un `<a>` a un espacio que no se puede tomar promete lo que no hay.

    Y mete en el recorrido del tabulador tantas paradas muertas como
    espacios ocupados tenga el recinto.
    """
    feria, conv, ana = escenario
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.OCUPADO)
    client.force_login(ana)

    cuerpo = client.get(_url(feria, "stands:mapa", convocatoria_id=conv.pk)).content.decode()

    enlaces = re.findall(r'<a href="[^"]*/mapa/([^/]+)/"', cuerpo)
    assert sorted(enlaces) == ["A2", "A3"]


def test_el_admin_no_navega_al_detalle_del_aplicante(client, escenario):
    """Su mapa es de consulta; el detalle con precio es la pantalla de compra."""
    feria, conv, _ = escenario
    with schema_context(feria.schema_name):
        admin = Persona.objects.create_user(
            correo="rita@filey.org", nombre="Rita", primer_apellido="Uc"
        )
    AdminFeria.objects.create(feria=feria, persona=admin, es_dueno=False)
    client.force_login(admin)

    cuerpo = client.get(
        _url(feria, "stands:mapa_completo", convocatoria_id=conv.pk)
    ).content.decode()

    assert "<a href" not in cuerpo.split('class="mapa-espacios"')[1].split("</svg>")[0]


# ── CU-STD-010 · el detalle ───────────────────────────────────


def test_el_detalle_dice_medidas_superficie_y_precio(client, escenario):
    """`RN-01`: 3 × 2 m a 2 500 el metro son 15 000."""
    feria, conv, ana = escenario
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")
    ).content.decode()

    assert "6 m²" in cuerpo
    assert "3 × 2 m" in cuerpo
    assert "15000" in cuerpo.replace(",", "")


def test_el_detalle_de_uno_tomado_lo_dice(client, escenario):
    """Se puede mirar, pero no se calla que ya no está."""
    feria, conv, ana = escenario
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.OCUPADO)
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")
    ).content.decode()

    assert "ya está tomado" in cuerpo


def test_un_espacio_que_no_existe_es_un_404(client, escenario):
    feria, conv, ana = escenario
    client.force_login(ana)

    respuesta = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="ZZZ")
    )

    assert respuesta.status_code == 404


def test_la_url_del_detalle_lleva_la_clave_y_no_el_id(client, escenario):
    """La clave es lo que la gente dice en voz alta, y sobrevive a
    reimportar el mapa —que borra las filas y las recrea con ids nuevos."""
    feria, conv, ana = escenario
    client.force_login(ana)
    url = _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")

    assert url.endswith("/mapa/A1/")
    assert client.get(url).status_code == 200


# ── E2 · la convocatoria todavía no tiene mapa ────────────────


def test_sin_mapa_se_dice_y_no_se_rompe(client, feria_2027):
    """`CU-STD-009` E2: es el estado normal de una convocatoria nueva."""
    with schema_context(feria_2027.schema_name):
        ana = fabricas.persona()
        conv = fabricas.convocatoria()
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=ana, editorial=fabricas.editorial(ana)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
    client.force_login(ana)

    respuesta = client.get(_url(feria_2027, "stands:mapa", convocatoria_id=conv.pk))

    assert respuesta.status_code == 200
    assert "El mapa todavía no está listo" in respuesta.content.decode()


# ── El dibujo ─────────────────────────────────────────────────


def test_un_stand_en_l_se_dibuja_de_una_pieza():
    """Dos rectángulos sueltos se verían como dos stands pegados."""
    celdas = {(c, 0) for c in range(4)} | {(c, 1) for c in range(2, 4)}

    d = dibujo.contorno(celdas)

    # Un solo bucle: si fueran dos, habría dos `M`.
    assert d.count("M") == 1
    assert d.count("Z") == 1
    # Una L tiene seis vértices, ni cuatro ni ocho.
    assert d.count("L") == 5


def test_el_rotulo_de_una_l_no_cae_en_el_hueco():
    """El centro de la envolvente de una L está encima de su vecino."""
    formas = [
        {"col": 0, "fila": 0, "ancho_celdas": 12, "alto_celdas": 2},
        {"col": 6, "fila": 2, "ancho_celdas": 6, "alto_celdas": 2},
    ]

    x, y, _ = dibujo._rotulo(formas)

    # En la banda de arriba, que es el trozo grande — no en (6, 2), que
    # es el centro de la envolvente y cae en el hueco.
    assert (x, y) == (6.0, 1.0)


def test_el_mapa_real_se_dibuja_entero(feria_2027):
    """151 espacios, con sus tres L, en un solo SVG."""
    from decimal import Decimal

    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(
            convocatoria=conv,
            datos=json.loads(MAPA_2026.read_text(encoding="utf-8")),
        )
        vista = dibujo.vista_para(
            mapas.mapa_de(conv), costo_m2=Decimal("2500")
        )

    assert vista.total == 151
    assert vista.libres == 151
    assert len(vista.decoraciones) == 10
    assert all(p.contorno for p in vista.piezas)
    # Los tres en L salen con más de cuatro vértices.
    en_l = [p for p in vista.piezas if p.contorno.count("L") > 3]
    assert {p.clave for p in en_l} == {"62", "97", "109"}


def test_pintar_el_mapa_real_no_hace_una_consulta_por_espacio(
    django_assert_num_queries, feria_2027
):
    """El `N+1` que se cuela por la puerta de `metros_cuadrados`.

    La superficie se deriva de `MapaShowfloor.metros_por_celda`, así que
    cada stand pregunta por su mapa. Con 151 espacios eso son 151
    consultas para un dato que ya está en la mano — y el mapa se pinta en
    cada visita, no una vez.
    """
    from decimal import Decimal

    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(
            convocatoria=conv, datos=json.loads(MAPA_2026.read_text(encoding="utf-8"))
        )
        mapa = mapas.mapa_de(conv)

        # Una por los stands y una por las decoraciones. Ni una más.
        with django_assert_num_queries(2):
            vista = dibujo.vista_para(mapa, costo_m2=Decimal("2500"))
            # Se tocan de verdad: sin esto el `assert` pasaría porque las
            # consultas perezosas no habrían corrido todavía.
            assert sum(p.metros_cuadrados for p in vista.piezas) == Decimal("2628")
