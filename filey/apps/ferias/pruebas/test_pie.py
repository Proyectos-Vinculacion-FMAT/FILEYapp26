"""
El pie de página: el de la edición, o el de la plataforma.

Lo que se defiende aquí es la **herencia campo a campo**. Un pie por
feria es fácil; lo que se rompe sin que nadie lo note es que una edición
que solo quiso cambiar su correo de contacto se quede sin dependencia,
porque el bloque entero se sustituyó en vez de cada campo por su lado.

Y la otra mitad: fuera de toda feria —el acceso, «mis ferias», elegir
edición— el pie sale del entorno, para que una instalación de otra
universidad lo cambie sin tocar el repositorio.
"""

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from apps.ferias.templatetags.chasis import pie

from ..models import Feria

pytestmark = pytest.mark.django_db


def _pie(feria=None, **ajustes):
    """El contexto que arma el tag, con `request.tenant` puesto a mano."""
    peticion = RequestFactory().get("/")
    peticion.tenant = feria
    return pie(Context({"request": peticion}))


# ── Fuera de toda feria: manda el entorno ─────────────────────


def test_sin_feria_el_pie_es_el_de_la_plataforma(settings):
    settings.PIE_ENTIDAD = "FILEY"
    settings.PIE_DEPENDENCIA = "Coordinación General de Contenidos · UADY"
    settings.PIE_CONTACTO = "Tanlum, Mérida · contenidos@filey.org"

    datos = _pie()

    assert datos["entidad"] == "FILEY"
    assert datos["dependencia"] == "Coordinación General de Contenidos · UADY"
    assert datos["contacto"] == "Tanlum, Mérida · contenidos@filey.org"


def test_la_fila_de_sistema_no_tiene_pie_propio(settings):
    """`schema_name="public"` no es una feria (ver `Feria`).

    Es la fila que el middleware deja puesta en todo lo que no cuelga de
    `/f/<slug>/`, así que si contara como edición el pie de la
    plataforma no saldría **nunca**.
    """
    settings.PIE_ENTIDAD = "FILEY"
    sistema = Feria(schema_name="public", nombre="(sistema)", pie_entidad="No usar")

    assert _pie(sistema)["entidad"] == "FILEY"


# ── Dentro de una feria: manda la feria, campo a campo ────────


def test_una_feria_declara_su_propio_pie(settings):
    settings.PIE_ENTIDAD = "FILEY"
    settings.PIE_CONTACTO = "contenidos@filey.org"
    feria = Feria(
        schema_name="feria_2027",
        nombre="FILEY 2027",
        pie_entidad="FILEY 2027",
        pie_dependencia="Comité organizador",
        pie_contacto="Centro de Convenciones Yucatán Siglo XXI",
    )

    datos = _pie(feria)

    assert datos["entidad"] == "FILEY 2027"
    assert datos["dependencia"] == "Comité organizador"
    assert datos["contacto"] == "Centro de Convenciones Yucatán Siglo XXI"


def test_lo_que_la_feria_deja_en_blanco_lo_hereda(settings):
    """Es la razón de que sean tres campos y no un bloque.

    Cambiar solo el contacto no puede costarle a nadie la dependencia:
    en blanco significa «el de la plataforma», no «vacío».
    """
    settings.PIE_ENTIDAD = "FILEY"
    settings.PIE_DEPENDENCIA = "Coordinación General de Contenidos · UADY"
    settings.PIE_CONTACTO = "contenidos@filey.org"
    feria = Feria(
        schema_name="feria_2027",
        nombre="FILEY 2027",
        pie_contacto="stands2027@filey.org",
    )

    datos = _pie(feria)

    assert datos["entidad"] == "FILEY"
    assert datos["dependencia"] == "Coordinación General de Contenidos · UADY"
    assert datos["contacto"] == "stands2027@filey.org"


def test_un_campo_con_solo_espacios_tambien_hereda(settings):
    """Lo que llega de un formulario no siempre viene limpio."""
    settings.PIE_ENTIDAD = "FILEY"
    feria = Feria(schema_name="feria_2027", nombre="FILEY 2027", pie_entidad="   ")

    assert _pie(feria)["entidad"] == "FILEY"


def test_un_tenant_sin_los_campos_no_tumba_la_pantalla(settings):
    """Dentro de un `schema_context` hay un `FakeTenant` que solo sabe su
    `schema_name`: pedirle `pie_entidad` sería un `AttributeError`, y un
    pie es lo último que debería tumbar una pantalla."""
    settings.PIE_ENTIDAD = "FILEY"

    class FakeTenant:
        schema_name = "feria_2027"
        es_la_de_sistema = False

    assert _pie(FakeTenant())["entidad"] == "FILEY"


# ── Y lo que acaba en el HTML ─────────────────────────────────


def test_la_plantilla_pinta_los_tres_valores(settings):
    settings.PIE_ENTIDAD = "FILEY"
    settings.PIE_DEPENDENCIA = "Coordinación General de Contenidos · UADY"
    settings.PIE_CONTACTO = "Tanlum, Mérida · contenidos@filey.org"
    peticion = RequestFactory().get("/")
    peticion.tenant = None

    html = Template("{% load chasis %}{% pie %}").render(
        Context({"request": peticion})
    )

    assert "<strong>FILEY</strong>" in html
    assert "Coordinación General de Contenidos · UADY" in html
    assert "Tanlum, Mérida · contenidos@filey.org" in html
