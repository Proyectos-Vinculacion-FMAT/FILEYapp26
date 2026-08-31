"""
El showfloor: la pantalla y los datos que come el canvas.

`CU-STD-009` (aplicante), `CU-STD-032` (admin) y los dos endpoints que
los alimentan, `CU-STD-037` y `CU-STD-038`. El mapa lo dibuja un canvas
de Godot (`ADR-0008`); aquí no hay nada de dibujo, y eso es justo lo que
hace que estas pruebas importen más que antes: **lo único que separa a un
aplicante de saber quién reservó qué es el JSON que sale del servidor.**

Lo que más se defiende:

1. **`RN-09` recorta antes de serializar.** El contrato del componente lo
   exige — *"el mapa nunca decide qué esconder"*. Si el estado real
   viajara en la respuesta, aunque el canvas no lo pintara, cualquiera
   con las herramientas de desarrollo abiertas vería qué editorial tiene
   apartado qué espacio. Es un fallo mudo: la pantalla se ve idéntica.

2. **Que el formato sea el del contrato.** `grid` / `stands` /
   `decorations`, con `disponible` / `reservado` / `ocupado`. Mandar los
   nombres de antes daría espacios grises y mensajes de `error`.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria
from apps.registros.models import Persona

from ..models import Solicitud, Stand
from ..servicios import configuracion, mapa_json, mapas, solicitudes
from . import fabricas

pytestmark = pytest.mark.django_db

MAPA_2026 = Path(__file__).resolve().parents[1] / "mapas" / "filey-2026.json"


def _url(feria, nombre, **kwargs):
    return f"{feria.url.rstrip('/')}" + reverse(
        nombre, kwargs=kwargs, urlconf=settings.ROOT_URLCONF
    )


def _mapa_chico():
    return {
        "grid": {"salon": "Salón de pruebas", "cols": 20, "rows": 10,
                 "meters_per_cell": 1.0, "cell_size": 32},
        "stands": [
            {"id": "A1", "label": "A1", "col": 0, "row": 0, "w": 3, "h": 2},
            {"id": "A2", "label": "A2", "col": 3, "row": 0, "w": 3, "h": 2},
            {"id": "A3", "label": "A3", "col": 6, "row": 0, "w": 3, "h": 2},
        ],
        "decorations": [
            {"type": "rect", "label": "Bodega", "col": 0, "row": 6, "w": 5, "h": 3},
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


def _admin_de(feria, correo="rita@filey.org"):
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


# ── RN-09 · el recorte ocurre en el servidor ──────────────────


def test_al_aplicante_no_le_llega_cual_esta_reservado(client, escenario):
    """El fallo que esta prueba cubre no se ve en pantalla.

    El canvas pintaría los dos igual de todas formas; lo que cambiaría es
    que el dato estaría en la respuesta, al alcance de cualquiera que
    abra las herramientas de desarrollo.
    """
    feria, conv, ana = escenario
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)
        Stand.objects.filter(clave="A2").update(estado=Stand.Estado.OCUPADO)
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:mapa_datos", convocatoria_id=conv.pk)
    ).content.decode()

    assert "reservado" not in cuerpo, "el estado real viajó al navegador"
    estados = {s["id"]: s["status"] for s in json.loads(cuerpo)["stands"]}
    assert estados == {"A1": "ocupado", "A2": "ocupado", "A3": "disponible"}


def test_a_quien_administra_le_llegan_los_tres(client, escenario):
    """`RN-18`: el administrador ve el mapa sin censura."""
    feria, conv, _ = escenario
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(estado=Stand.Estado.RESERVADO)
        Stand.objects.filter(clave="A2").update(estado=Stand.Estado.OCUPADO)
    client.force_login(_admin_de(feria))

    datos = client.get(
        _url(feria, "stands:mapa_datos_completo", convocatoria_id=conv.pk)
    ).json()

    estados = {s["id"]: s["status"] for s in datos["stands"]}
    assert estados == {"A1": "reservado", "A2": "ocupado", "A3": "disponible"}


def test_la_respuesta_no_la_puede_cachear_un_intermediario(client, escenario):
    """Dos cargas distintas en URLs de aspecto público.

    Sin `private`, un proxy podría servirle a un aplicante la respuesta
    que se generó para quien administra.
    """
    feria, conv, ana = escenario
    client.force_login(ana)

    respuesta = client.get(_url(feria, "stands:mapa_datos", convocatoria_id=conv.pk))

    assert "private" in respuesta["Cache-Control"]
    assert "no-store" in respuesta["Cache-Control"]


def test_el_aplicante_no_alcanza_los_datos_del_administrador(client, escenario):
    feria, conv, ana = escenario
    client.force_login(ana)

    respuesta = client.get(
        _url(feria, "stands:mapa_datos_completo", convocatoria_id=conv.pk)
    )

    assert respuesta.status_code == 403


def test_sin_solicitud_aceptada_no_hay_datos(client, escenario):
    """`RN-16`, y con 404: un 403 confirmaría que ese mapa existe."""
    feria, conv, _ = escenario
    with schema_context(feria.schema_name):
        otro = fabricas.persona(correo="otro@ejemplo.com", nombre="Otro")
    client.force_login(otro)

    respuesta = client.get(_url(feria, "stands:mapa_datos", convocatoria_id=conv.pk))

    assert respuesta.status_code == 404


# ── El formato es el del contrato del componente ──────────────


def test_el_json_tiene_la_forma_que_el_canvas_espera(client, escenario):
    """`grid` / `stands` / `decorations`, de `bridge_protocol.md`."""
    feria, conv, ana = escenario
    client.force_login(ana)

    datos = client.get(
        _url(feria, "stands:mapa_datos", convocatoria_id=conv.pk)
    ).json()

    assert set(datos) == {"grid", "stands", "decorations"}
    assert datos["grid"] == {
        "cell_size": 32, "cols": 20, "rows": 10, "meters_per_cell": 1.0,
    }
    assert datos["stands"][0] == {
        "id": "A1", "label": "A1", "status": "disponible",
        "price": 15000, "col": 0, "row": 0, "w": 3, "h": 2,
    }
    assert datos["decorations"] == [
        {"type": "rect", "col": 0, "row": 6, "w": 5, "h": 3, "label": "Bodega"}
    ]


def test_los_estados_son_los_del_dominio_sin_traducir(client, escenario):
    """El componente los renombró el 2026-08-27 a los de FILEY.

    Mandar `available`/`reserved`/`unavailable` daría tres espacios
    grises y tres mensajes de `error`, y nadie los estaría mirando.
    """
    feria, conv, _ = escenario
    client.force_login(_admin_de(feria))

    datos = client.get(
        _url(feria, "stands:mapa_datos_completo", convocatoria_id=conv.pk)
    ).json()

    assert {s["status"] for s in datos["stands"]} <= {
        "disponible", "reservado", "ocupado"
    }


def test_no_se_manda_dimensions_text(client, escenario):
    """El canvas lo deriva de la forma y de `meters_per_cell`.

    Mandarlo sería una segunda fuente para la misma cifra — la misma
    razón por la que `metros_cuadrados` no es una columna.
    """
    feria, conv, ana = escenario
    client.force_login(ana)

    datos = client.get(
        _url(feria, "stands:mapa_datos", convocatoria_id=conv.pk)
    ).json()

    assert all("dimensions_text" not in s for s in datos["stands"])


def test_un_stand_en_l_viaja_como_rects(feria_2027):
    """El contrato admite formas irregulares; el de 2026 tiene tres."""
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(
            convocatoria=conv,
            datos=json.loads(MAPA_2026.read_text(encoding="utf-8")),
        )
        datos = mapa_json.para_el_canvas(
            mapas.mapa_de(conv), costo_m2=Decimal("2500")
        )

    por_id = {s["id"]: s for s in datos["stands"]}
    assert "rects" in por_id["62"]
    assert "w" not in por_id["62"], "un irregular no lleva el rectángulo simple"
    assert por_id["62"]["rects"] == [
        {"col": 56, "row": 36, "w": 12, "h": 2},
        {"col": 62, "row": 38, "w": 6, "h": 2},
    ]
    # Y su precio es el de su forma, no el de su envolvente.
    assert por_id["62"]["price"] == 36 * 2500


def test_el_mapa_real_entra_y_sale_igual(feria_2027):
    """Importar y servir cierran el círculo sobre los 151 espacios."""
    archivo = json.loads(MAPA_2026.read_text(encoding="utf-8"))
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(convocatoria=conv, datos=archivo)
        datos = mapa_json.para_el_canvas(
            mapas.mapa_de(conv), costo_m2=Decimal("2500")
        )

    assert len(datos["stands"]) == len(archivo["stands"]) == 151
    assert {s["id"] for s in datos["stands"]} == {s["id"] for s in archivo["stands"]}
    assert datos["grid"]["cols"] == archivo["grid"]["cols"]
    assert datos["grid"]["rows"] == archivo["grid"]["rows"]


def test_servir_el_mapa_real_no_hace_una_consulta_por_espacio(
    django_assert_num_queries, feria_2027
):
    """`Stand.precio` mide la superficie, que sale de `metros_por_celda`.

    Sin `select_related` son 151 consultas — y esto se sirve cada vez que
    alguien abre el mapa.
    """
    with schema_context(feria_2027.schema_name):
        conv = fabricas.convocatoria()
        mapas.importar(
            convocatoria=conv,
            datos=json.loads(MAPA_2026.read_text(encoding="utf-8")),
        )
        mapa = mapas.mapa_de(conv)

        with django_assert_num_queries(2):
            datos = mapa_json.para_el_canvas(mapa, costo_m2=Decimal("2500"))
            assert sum(s["price"] for s in datos["stands"]) == 2628 * 2500


# ── La pantalla ───────────────────────────────────────────────


def test_la_pantalla_monta_el_canvas_con_su_origen(client, escenario):
    """`?hostOrigin=` fija a quién habla y de quién acepta mensajes.

    Sin él el canvas usa `*`, que vale en desarrollo y no en producción.
    """
    feria, conv, ana = escenario
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'id="mapa-canvas"' in cuerpo
    assert "hostOrigin=http://testserver" in cuerpo
    assert 'data-datos="' in cuerpo


def test_la_pantalla_del_aplicante_apunta_a_sus_propios_datos(client, escenario):
    """Y no a los del administrador, que es el único fallo que importa."""
    feria, conv, ana = escenario
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    assert _url(feria, "stands:mapa_datos", convocatoria_id=conv.pk) in cuerpo
    assert "showfloor/datos" not in cuerpo


def test_la_pantalla_del_admin_apunta_a_los_suyos(client, escenario):
    feria, conv, _ = escenario
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:mapa_completo", convocatoria_id=conv.pk)
    ).content.decode()

    assert (
        _url(feria, "stands:mapa_datos_completo", convocatoria_id=conv.pk) in cuerpo
    )
    # Y no ofrece «agregar»: quien administra no compra espacios.
    assert 'data-campo="agregar"' not in cuerpo


def test_el_velo_tapa_el_arranque_de_godot(client, escenario):
    """Mientras el WASM baja se ve el chasis de FILEY, no el de Godot."""
    feria, conv, ana = escenario
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'id="mapa-velo"' in cuerpo
    assert "Cargando el plano" in cuerpo
    # Y su mensaje para cuando los datos no llegan: un canvas vacío sin
    # explicación se lee como "no hay espacios libres".
    assert "No se pudo cargar el plano" in cuerpo


def test_sin_habilitacion_ni_se_monta_el_canvas(client, escenario):
    """`RN-16`. Ni el marco: bajar 39 MB para no poder usarlos es cruel."""
    feria, conv, _ = escenario
    with schema_context(feria.schema_name):
        otro = fabricas.persona(correo="otro@ejemplo.com", nombre="Otro")
    client.force_login(otro)

    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    assert "Todavía no puedes elegir espacios" in cuerpo
    assert 'id="mapa-canvas"' not in cuerpo


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

    cuerpo = client.get(
        _url(feria_2027, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    assert "El mapa todavía no está listo" in cuerpo
    assert 'id="mapa-canvas"' not in cuerpo


# ── CU-STD-010 · el detalle, que sigue siendo del servidor ────


def test_el_detalle_del_espacio_sigue_teniendo_su_pantalla(client, escenario):
    """El contrato deja el detalle en manos de la página.

    La tarjeta del mapa lo resuelve sin recargar; esta pantalla es a
    donde lleva su enlace, y es la que funciona pegando la URL.
    """
    feria, conv, ana = escenario
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")
    ).content.decode()

    assert "6 m²" in cuerpo
    assert "15000" in cuerpo.replace(",", "")


# ── El puente y su origen ─────────────────────────────────────


def test_el_canvas_se_sirve_del_mismo_origen_que_la_pagina(client, escenario):
    """De lo que depende que el puente pueda comprobar el origen.

    El `filey.js` deduce el origen del canvas de su propio `src` en vez
    de leerlo de un atributo: un `data-origen` que la plantilla olvide
    poner deja el puente en `"*"`, y con `"*"` no se comprueba de quién
    llega un mensaje **ni a quién se le manda**. Para quien administra,
    "a quién se le manda" incluye qué editorial reservó qué espacio.

    Si algún día los estáticos salieran a otro dominio, esta prueba es la
    que avisa de que el puente se queda sin su ancla.
    """
    feria, conv, ana = escenario
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    src = cuerpo.split('id="mapa-canvas"', 1)[1].split('src="', 1)[1].split('"', 1)[0]
    assert src.startswith("/"), f"el canvas salió a otro origen: {src}"
    # Y el canvas recibe **nuestro** origen para fijar su lado.
    assert "hostOrigin=http://testserver" in src


def test_la_pantalla_no_declara_un_origen_aparte(client, escenario):
    """Un segundo sitio donde decir el origen es un sitio donde olvidarlo.

    Lo deduce el JavaScript del `src`; si alguien reintroduce un
    `data-origen`, esta prueba lo señala antes de que empiecen a
    divergir.
    """
    feria, conv, ana = escenario
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    assert "data-origen" not in cuerpo


def test_lo_que_el_canvas_ignora_no_se_manda(client, escenario):
    """El JSON se sirve en cada visita: no lleva lo que nadie va a leer.

    `includes` es de FILEY y lo pinta el servidor en el detalle del
    espacio; mandarlo serían 151 textos libres viajando para nada.
    """
    feria, conv, ana = escenario
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(
            incluye="Mesa, dos sillas y contacto eléctrico"
        )
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:mapa_datos", convocatoria_id=conv.pk)
    ).content.decode()

    assert "contacto eléctrico" not in cuerpo


def test_pero_el_detalle_si_lo_ensena(client, escenario):
    """Que el recorte anterior no sea una pérdida, sino un reparto."""
    feria, conv, ana = escenario
    with schema_context(feria.schema_name):
        Stand.objects.filter(clave="A1").update(
            incluye="Mesa, dos sillas y contacto eléctrico"
        )
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1")
    ).content.decode()

    assert "contacto eléctrico" in cuerpo


def test_el_velo_se_puede_esconder_de_verdad():
    """El fallo que dejaba el mapa dibujado detrás de «Cargando el plano…».

    `.mapa-velo` fija `display: flex`, y eso **gana** sobre el
    `display: none` con el que el navegador esconde lo que lleva
    `hidden`. Sin una regla explícita, `velo.hidden = true` no hace nada:
    el canvas termina de cargar, dibuja sus 151 espacios, y nadie los ve.

    Es un fallo que ninguna prueba de Django puede cazar mirando HTML
    —solo aparece pintado en un navegador— así que lo que se vigila es
    que la regla siga en la hoja, y que vaya **después** de la que la
    hace falta.
    """
    from pathlib import Path

    from django.conf import settings

    hoja = (Path(settings.BASE_DIR) / "estaticos" / "css" / "filey.css").read_text(
        encoding="utf-8"
    )

    assert ".mapa-velo[hidden]" in hoja, "sin esto el velo no se puede esconder"
    # Después del `display: flex`, o volvería a perder por orden.
    assert hoja.index(".mapa-velo {") < hoja.index(".mapa-velo[hidden]")


# ── El lienzo es el mismo para los dos públicos ───────────────


def test_las_dos_vistas_montan_el_mismo_lienzo(client, escenario):
    """El arreglo de una tiene que ser el arreglo de la otra.

    Estaba escrito en línea en la plantilla, y así el velo que no se
    quitaba se arregló primero solo para quien aplica. Ahora las dos
    incluyen `parciales/lienzo_mapa.html`, y esta prueba es la que se
    entera si alguien vuelve a copiarlo.
    """
    feria, conv, ana = escenario
    client.force_login(ana)
    del_aplicante = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    client.force_login(_admin_de(feria))
    del_admin = client.get(
        _url(feria, "stands:mapa_completo", convocatoria_id=conv.pk)
    ).content.decode()

    # Las piezas del lienzo, en las dos.
    for pieza in (
        'id="mapa-velo"',
        'id="mapa-canvas"',
        'id="mapa-tarjeta"',
        'id="mapa-tarjeta-fondo"',
        "Cargando el plano",
        "No se pudo cargar el plano",
    ):
        assert pieza in del_aplicante, f"falta en el aplicante: {pieza}"
        assert pieza in del_admin, f"falta en el admin: {pieza}"


def test_lo_unico_que_cambia_entre_las_dos_es_el_carrito(client, escenario):
    """Y de qué URL bajan los datos. Nada más."""
    feria, conv, ana = escenario
    client.force_login(ana)
    del_aplicante = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()
    client.force_login(_admin_de(feria))
    del_admin = client.get(
        _url(feria, "stands:mapa_completo", convocatoria_id=conv.pk)
    ).content.decode()

    assert 'id="carrito-lateral"' in del_aplicante
    assert 'id="carrito-lateral"' not in del_admin
    # El «agregar» ya no está en el HTML inicial: vive en el detalle que
    # el modal pide por htmx. Lo que sí distingue a las dos aquí es el
    # carrito y el ancho del lienzo.
    # Y el suyo va a todo el ancho, sin la columna vacía al lado.
    assert 'class="mapa-solo"' in del_admin
    assert 'class="mapa-con-carrito"' in del_aplicante


def test_el_detalle_va_centrado_y_no_anclado_al_espacio(client, escenario):
    """Anclado quedaba dentro del marco, que recorta lo que se sale.

    Un espacio de la orilla abría su tarjeta medio cortada, y en el resto
    de los casos tapaba justo los espacios de al lado — que son los que
    uno está comparando.
    """
    from pathlib import Path

    from django.conf import settings

    feria, conv, ana = escenario
    client.force_login(ana)
    cuerpo = client.get(
        _url(feria, "stands:mapa", convocatoria_id=conv.pk)
    ).content.decode()

    # Es un diálogo, con su fondo y su etiqueta.
    assert 'role="dialog"' in cuerpo
    assert 'aria-modal="true"' in cuerpo
    assert 'id="mapa-tarjeta-fondo"' in cuerpo
    # Y va **fuera** del marco, o volvería a recortarse.
    marco = cuerpo.split('class="mapa-marco"', 1)[1]
    assert marco.index("</div>") < marco.index('id="mapa-tarjeta"')

    hoja = (Path(settings.BASE_DIR) / "estaticos" / "css" / "filey.css").read_text(
        encoding="utf-8"
    )
    reglas = hoja.split(".mapa-tarjeta {", 1)[1].split("}", 1)[0]
    assert "position: fixed" in reglas, "sigue anclada dentro del marco"


# ── CU-STD-032 · el detalle que ve quien administra ───────────


def _reservar(feria, conv, persona, clave):
    from ..servicios import reservas

    with schema_context(feria.schema_name):
        return reservas.crear(convocatoria=conv, persona=persona, claves=[clave])


def test_el_modal_del_admin_carga(client, escenario):
    """Se quedaba en «Cargando el detalle…» para siempre.

    La vista exigía una solicitud aceptada, y quien administra no tiene
    ninguna: devolvía 404 y htmx no intercambia nada ante un error.
    """
    feria, conv, _ = escenario
    client.force_login(_admin_de(feria))

    respuesta = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1"),
        headers={"HX-Request": "true"},
    )

    assert respuesta.status_code == 200
    assert "Superficie" in respuesta.content.decode()


def test_quien_administra_ve_quien_reservo_y_cuanto_debe(client, escenario):
    """`CU-STD-032` con `RN-18`: el mapa completo, sin censura."""
    feria, conv, ana = escenario
    _reservar(feria, conv, ana, "A1")
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1"),
        headers={"HX-Request": "true"},
    ).content.decode()

    assert "Ediciones del Mayab" in cuerpo
    assert "Pendiente" in cuerpo
    assert "15,000.00" in cuerpo
    assert "Ver la reserva" in cuerpo


def test_y_dice_cuando_no_lo_tiene_nadie(client, escenario):
    feria, conv, _ = escenario
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1"),
        headers={"HX-Request": "true"},
    ).content.decode()

    assert "Nadie lo tiene apartado" in cuerpo


def test_al_aplicante_no_se_le_dice_quien_reservo(client, escenario):
    """`RN-09`, y la consulta **ni se hace**.

    Lo que no se pide no puede acabar en la respuesta por un descuido de
    plantilla — que es la única forma en la que este dato se filtraría.
    """
    feria, conv, ana = escenario
    with schema_context(feria.schema_name):
        beto = fabricas.persona(correo="beto@ejemplo.com", nombre="Beto")
        solicitud = solicitudes.enviar_solicitud(
            convocatoria=conv, persona=beto, editorial=fabricas.editorial(beto)
        )
        solicitud.estado = Solicitud.Estado.ACEPTADA
        solicitud.fecha_revision = solicitud.fecha_envio
        solicitud.save()
    _reservar(feria, conv, beto, "A1")
    client.force_login(ana)

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1"),
        headers={"HX-Request": "true"},
    ).content.decode()

    assert "ya está tomado" in cuerpo
    assert "Ediciones del Mayab" not in cuerpo
    assert "Pendiente" not in cuerpo


def test_quien_administra_no_puede_agregar_a_un_carrito(client, escenario):
    """No compra espacios, así que el botón no existe para él."""
    feria, conv, _ = escenario
    client.force_login(_admin_de(feria))

    cuerpo = client.get(
        _url(feria, "stands:detalle_stand", convocatoria_id=conv.pk, clave="A1"),
        headers={"HX-Request": "true"},
    ).content.decode()

    assert 'data-campo="agregar"' not in cuerpo
