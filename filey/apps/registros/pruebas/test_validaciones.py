"""
Barrido de validación del alta de cuenta (`CU-REG-001`).

Salió del mismo barrido que el de `STD`, y aquí el hallazgo fue otro: los
formularios de `REG` estaban **bien** —nombre y apellido con mínimo, país
con catálogo, código con regex, correo con su tipo— y el hueco estaba un
piso más abajo.

**Las reglas vivían solo en el formulario.** `Persona` es el usuario del
sistema y se crea por tres caminos: la pantalla de alta, el admin de
Django y `create_user` desde un comando o el shell. `clean_telefono`
solo cubría el primero, así que una cuenta creada desde el admin podía
llamarse "X" y tener por teléfono "no tengo".

.. note:: El barrido tenía un punto ciego, y así se encontró esto

   La primera pasada listaba `field.validators` de cada campo y daba el
   teléfono de `REG` por no validado. Era falso: la regla estaba en
   `clean_telefono`, que ese listado no ve. Mirar los dos sitios es lo
   que dejó a la vista el problema real — que hubiera **dos** sitios.
"""

import pytest
from django.core.exceptions import ValidationError

from comun.validadores import MINIMO_DIGITOS_TELEFONO, solo_digitos, telefono

from ..forms import RegistroForm
from ..models import Persona

pytestmark = pytest.mark.django_db

FORMULARIO = {
    "nombre": "Ana María",
    "primer_apellido": "Pech",
    "segundo_apellido": "",
    "telefono": "999 000 1234",
    "pais": "MX",
}


def _alta(**cambios):
    return RegistroForm({**FORMULARIO, **cambios})


# ── La regla vive en un solo sitio ────────────────────────────


def test_el_modelo_valida_el_telefono_y_no_solo_el_formulario():
    """El hueco real de `REG`.

    `Persona` se crea también desde el admin y desde un comando, y ahí
    no pasa por `RegistroForm`. Con la regla solo en el formulario, esos
    dos caminos escribían cualquier cosa.
    """
    persona = Persona(
        correo="ana@ejemplo.com",
        nombre="Ana",
        primer_apellido="Pech",
        telefono="no tengo",
    )

    with pytest.raises(ValidationError) as fallo:
        # `password` se excluye porque lo pone `create_user` al guardar y
        # aquí la instancia no ha pasado por él; su error taparía el que
        # esta prueba mira.
        persona.full_clean(exclude=["password"])

    assert "telefono" in fallo.value.message_dict


def test_el_modelo_valida_el_largo_del_nombre():
    persona = Persona(correo="a@b.com", nombre="X", primer_apellido="Y")

    with pytest.raises(ValidationError) as fallo:
        persona.full_clean(exclude=["password"])

    assert "nombre" in fallo.value.message_dict
    assert "primer_apellido" in fallo.value.message_dict


def test_una_cuenta_tecnica_sin_telefono_se_sigue_pudiendo_crear():
    """`blank=True`, y los validadores no corren sobre el vacío.

    Las cuentas administrativas se dan de alta por comando sin pedirlo
    (ver `ensure_superuser`). Si el validador se aplicara al vacío,
    desplegar dejaría de funcionar.
    """
    persona = Persona.objects.create_user(
        correo="equipo@filey.org", nombre="Equipo", primer_apellido="FILEY"
    )

    persona.full_clean()  # no levanta: el vacío no pasa por el validador


def test_el_formulario_y_el_modelo_usan_la_misma_regla():
    """Dos reglas parecidas en dos sitios divergen en cuanto se toca una."""
    con_pocos = _alta(telefono="12345")

    assert not con_pocos.is_valid()
    assert "telefono" in con_pocos.errors


# ── Lo que el formulario ya hacía bien ────────────────────────


def test_el_telefono_se_guarda_solo_con_digitos():
    """Para que "999 000 0000" y "9990000000" sean el mismo al comparar."""
    form = _alta(telefono="(999) 000-1234")

    assert form.is_valid(), form.errors
    assert form.cleaned_data["telefono"] == "9990001234"


@pytest.mark.parametrize("malo", ["hola", "1234", "999-ABC-4567", ""])
def test_un_telefono_que_no_lo_es_se_rechaza_en_el_formulario(malo):
    form = _alta(telefono=malo)

    assert not form.is_valid()
    assert "telefono" in form.errors


def test_el_pais_solo_admite_los_del_catalogo():
    form = _alta(pais="ZZ")

    assert not form.is_valid()
    assert "pais" in form.errors


def test_el_segundo_apellido_sigue_siendo_opcional():
    """`CU-REG-001` E1: exigirlo dejaría fuera a quien no lo tiene."""
    assert _alta(segundo_apellido="").is_valid()


@pytest.mark.parametrize("campo", ["nombre", "primer_apellido"])
def test_un_nombre_de_una_letra_se_rechaza(campo):
    form = _alta(**{campo: "X"})

    assert not form.is_valid()
    assert campo in form.errors


def test_ningun_obligatorio_del_alta_se_puede_dejar_vacio():
    """El barrido al revés, igual que en `STD`."""
    obligatorios = [k for k, c in RegistroForm().fields.items() if c.required]
    assert len(obligatorios) >= 4

    for campo in obligatorios:
        form = _alta(**{campo: ""})
        assert not form.is_valid(), f"{campo} se dejó enviar vacío"
        assert campo in form.errors, f"{campo} falló, pero no se señaló"


def test_el_formulario_base_es_valido():
    """Si no lo fuera, todo lo de arriba pasaría por el motivo equivocado."""
    form = _alta()

    assert form.is_valid(), form.errors


# ── La regla compartida ───────────────────────────────────────


def test_el_minimo_es_el_que_documenta_el_caso_de_uso():
    """`CU-REG-001`: *"al menos 10 dígitos"*."""
    assert MINIMO_DIGITOS_TELEFONO == 10


def test_los_separadores_no_cuentan_como_dígitos():
    assert solo_digitos("+52 (999) 123-45-67") == "529991234567"


def test_el_mismo_validador_lo_usan_los_dos_dominios():
    """`REG` y `STD` piden el mismo dato; una sola regla lo gobierna."""
    from apps.stands.models import Editorial

    validadores_std = Editorial._meta.get_field("telefono_celular").validators

    assert telefono in validadores_std
