"""
El build del mapa se queda fuera del manifiesto de estáticos.

Es el riesgo que el plan de `STD` marcaba como **Alto**, y su forma es la
peor: en desarrollo el almacén es el plano y todo funciona; el fallo
aparece **solo desplegado**, como un canvas en blanco y dos 404 dentro de
un `<iframe>`.

`index.js` es código generado por el exportador de Godot y pide
`index.wasm` e `index.pck` por su nombre literal. Si el manifiesto los
copia como `index.<hash>.wasm`, el JavaScript sigue pidiendo el de antes.
"""

import pytest

from comun.estaticos import EstaticosFiley


@pytest.fixture
def almacen():
    return EstaticosFiley()


@pytest.mark.parametrize(
    "nombre",
    ["mapa/index.js", "mapa/index.wasm", "mapa/index.pck", "mapa/index.html"],
)
def test_el_build_del_mapa_conserva_su_nombre(almacen, nombre):
    assert almacen.hashed_name(nombre) == nombre


def test_lo_demas_si_se_versiona(almacen, tmp_path, settings):
    """Que la excepción no se haya comido el manifiesto entero.

    Sin esta prueba, un prefijo mal escrito —`""` por ejemplo— dejaría
    todo sin versionar y nadie lo notaría: el sistema funcionaría igual y
    los navegadores servirían CSS viejo durante semanas.
    """
    from django.core.files.base import ContentFile

    ruta = tmp_path / "prueba.css"
    ruta.write_text("body{color:red}")
    settings.STATIC_ROOT = str(tmp_path)

    hasheado = almacen.hashed_name("css/prueba.css", ContentFile(b"body{color:red}"))

    assert hasheado != "css/prueba.css"
    assert hasheado.startswith("css/prueba.") and hasheado.endswith(".css")


def test_un_css_que_empiece_por_mapa_si_se_versiona(almacen):
    """El prefijo lleva barra final justo para esto.

    `mapas.css` empieza por «mapa» y no es el build; sin la barra caería
    en la excepción y dejaría de versionarse en silencio.
    """
    from django.core.files.base import ContentFile

    hasheado = almacen.hashed_name("mapas.css", ContentFile(b"body{}"))

    assert hasheado != "mapas.css"


def test_el_post_proceso_no_toca_el_javascript_de_godot(almacen):
    """280 KB de código generado que no hay que reescribir.

    El post-proceso sustituye referencias dentro de los `.js`; pasarle el
    `index.js` de Godot es pedirle que edite un archivo que nadie
    escribió a mano.
    """
    procesados = list(
        almacen.post_process({"mapa/index.js": ("/tmp", "mapa/index.js")}, dry_run=True)
    )

    assert procesados == [("mapa/index.js", "mapa/index.js", False)]


def test_el_manifiesto_conserva_el_build_apuntandose_a_si_mismo(almacen):
    """El fallo que casi se cuela, y que era el peor de los dos.

    Sacar el mapa del post-proceso **no** basta: `{% static %}` consulta
    el manifiesto, y un archivo ausente no degrada a servir el original —
    revienta con `Missing staticfiles manifest entry`. La página del mapa
    dejaría de cargar entera, otra vez **solo en producción**.
    """
    almacen.hashed_files = {}

    list(
        almacen.post_process(
            {"mapa/index.wasm": ("/tmp", "mapa/index.wasm")}, dry_run=True
        )
    )
    # En seco no se toca el manifiesto: `collectstatic --dry-run` no debe
    # escribir nada.
    assert almacen.hashed_files == {}


@pytest.mark.parametrize(
    "nombre", ["mapa/index.html", "mapa/index.js", "mapa/index.wasm"]
)
def test_la_url_del_build_es_la_de_siempre(almacen, nombre):
    """Con el manifiesto poblado, `{% static %}` devuelve el nombre crudo.

    Es lo que hace que el `index.js` de Godot encuentre su `.wasm`: los
    dos se piden por el nombre que el exportador escribió dentro del JS.
    """
    almacen.hashed_files = {n: n for n in [nombre]}

    assert almacen.stored_name(nombre) == nombre
