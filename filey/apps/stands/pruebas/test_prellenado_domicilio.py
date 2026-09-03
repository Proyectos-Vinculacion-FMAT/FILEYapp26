"""
El domicilio de la editorial, propuesto desde la cuenta (`CU-STD-001`).

El domicilio fiscal de una editorial no es el de la persona, pero empieza
igual de menudo: quien tramita desde Mérida registra una editorial
yucateca. Se **propone**, no se impone — como el resto de
`DE_LA_CUENTA`—, y una cuenta de fuera de México no propone nada, porque
ahí el estado y la ciudad nunca se preguntaron.
"""

import pytest

from apps.registros.models import Persona

from ..formularios import EditorialForm

pytestmark = pytest.mark.django_db


def _persona(**cambios):
    base = {
        "correo": "ana@ejemplo.com",
        "nombre": "Ana",
        "primer_apellido": "Pech",
        "telefono": "9990000000",
        "pais": "MX",
        "entidad": "YUC",
        "ciudad": "Mérida",
    }
    return Persona(**{**base, **cambios})


def test_se_proponen_los_dos():
    form = EditorialForm(persona=_persona())

    assert form.initial["estado"] == "Yucatán"
    assert form.initial["municipio"] == "Mérida"


def test_se_propone_el_nombre_del_estado_no_su_codigo():
    """`Editorial.estado` es texto libre —sale de un documento en papel—
    y la cuenta guarda `YUC`. Copiar el código dejaría «YUC» impreso en
    el domicilio fiscal de la ficha."""
    form = EditorialForm(persona=_persona(entidad="NLE"))

    assert form.initial["estado"] == "Nuevo León"


def test_una_cuenta_de_fuera_de_mexico_no_propone_nada():
    form = EditorialForm(persona=_persona(pais="CO", entidad="", ciudad=""))

    assert not form.initial.get("estado")
    assert not form.initial.get("municipio")


def test_sin_ciudad_solo_se_propone_el_estado():
    """La ciudad es opcional en la cuenta: no proponerla es correcto, y
    proponer una vacía borraría lo que ya hubiera en `initial`."""
    form = EditorialForm(persona=_persona(ciudad=""))

    assert form.initial["estado"] == "Yucatán"
    assert not form.initial.get("municipio")


def test_la_pantalla_lo_dice():
    """`prellenado` alimenta la frase que avisa de lo que se propuso: un
    campo que aparece lleno sin explicación se lee como un dato que el
    sistema sabe de ti y no te dijo cómo."""
    form = EditorialForm(persona=_persona())

    assert "estado" in form.prellenado_texto
    assert "municipio" in form.prellenado_texto
