"""
El estado y la ciudad de la persona (`CU-REG-001`).

Los dos **solo aplican dentro de México**, y esa es toda la regla: un
catálogo de 32 entidades mexicanas no describe una dirección en Bogotá,
y guardar «Yucatán» en la ficha de alguien que vive en Madrid haría que
una consulta por entidad contara personas que no viven ahí.

La pantalla los esconde con Alpine, pero eso es una comodidad: lo que
sostiene la regla es `RegistroForm.clean`, porque un POST fabricado a
mano no pasa por la pantalla.
"""

import pytest

from ..estados_mx import ESTADO_POR_DEFECTO
from ..forms import RegistroForm
from ..models import Persona

pytestmark = pytest.mark.django_db


def _datos(**cambios):
    base = {
        "nombre": "Ana",
        "primer_apellido": "Pech",
        "segundo_apellido": "",
        "telefono": "9990000000",
        "pais": "MX",
        "entidad": "YUC",
        "ciudad": "Mérida",
    }
    return {**base, **cambios}


# ── Dentro de México ──────────────────────────────────────────


def test_se_guardan_los_dos(client):
    form = RegistroForm(_datos(entidad="JAL", ciudad="Guadalajara"))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["entidad"] == "JAL"
    assert form.cleaned_data["ciudad"] == "Guadalajara"


def test_yucatan_viene_marcado_por_omision():
    """FILEY es la feria de Yucatán y de ahí viene la mayoría."""
    assert RegistroForm().fields["entidad"].initial == ESTADO_POR_DEFECTO == "YUC"


def test_la_ciudad_puede_ir_vacia():
    """Lo que sitúa a la persona es el estado; la ciudad es opcional."""
    form = RegistroForm(_datos(ciudad=""))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["ciudad"] == ""


def test_sin_estado_no_se_puede_enviar():
    """Solo lo ve quien manda el formulario a mano —el desplegable nace
    en Yucatán—, pero es lo que impide que la columna quede a medias."""
    form = RegistroForm(_datos(entidad=""))

    assert not form.is_valid()
    assert "entidad" in form.errors


def test_un_estado_inventado_se_rechaza():
    form = RegistroForm(_datos(entidad="ZZZ"))

    assert not form.is_valid()
    assert "entidad" in form.errors


# ── Fuera de México ───────────────────────────────────────────


def test_fuera_de_mexico_no_se_exigen():
    form = RegistroForm(_datos(pais="CO", entidad="", ciudad=""))

    assert form.is_valid(), form.errors


def test_fuera_de_mexico_se_descartan_aunque_lleguen():
    """Un POST fabricado a mano no pasa por la pantalla que los esconde."""
    form = RegistroForm(_datos(pais="ES", entidad="YUC", ciudad="Mérida"))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["entidad"] == ""
    assert form.cleaned_data["ciudad"] == ""


def test_un_estado_invalido_desde_fuera_no_bloquea():
    """El error sería incorregible: la pantalla no enseñó ese campo, así
    que quien lo ve no encuentra dónde arreglarlo. El valor ya se
    descartó, y con él sobra el error."""
    form = RegistroForm(_datos(pais="AR", entidad="ZZZ"))

    assert form.is_valid(), form.errors
    assert form.cleaned_data["entidad"] == ""


# ── Lo que acaba en la cuenta ─────────────────────────────────


def test_el_nombre_del_estado_se_deriva_del_codigo():
    """La cuenta guarda el código —no cambia—; lo que se copia a un
    domicilio es el nombre."""
    ana = Persona(entidad="CMX")

    assert ana.estado_nombre == "Ciudad de México"


def test_sin_entidad_el_nombre_es_vacio():
    assert Persona(entidad="").estado_nombre == ""
