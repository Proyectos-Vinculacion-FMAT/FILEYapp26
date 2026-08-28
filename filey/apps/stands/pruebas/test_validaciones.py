"""
Barrido de validación de la ficha de expositor.

Salió de auditar campo por campo qué valida cada uno de verdad, y no de
suponerlo. La mayoría estaba cubierta por el tipo —un `EmailField` valida
correo, un `ChoiceField` valida su catálogo— y aparecieron seis huecos en
campos que solo tenían `max_length`, que **no valida nada**: acepta
cualquier texto de esa longitud.

Los seis, y por qué importaban:

1. `cp` aceptaba `"abc"`. Es un dato que nadie mira hasta que hay que
   mandar algo por correo postal.
2. Los dos teléfonos aceptaban cualquier texto, y la ficha pide «clave
   lada + número».
3. `num_personas_atienden` aceptaba cero: un stand que no atiende nadie.
4. `plazo_reserva_dias` aceptaba cero: una reserva que vence al crearse.
5. `nombre` de la editorial aceptaba una letra.
6. Un sello podía llamarse `"x"`.

.. note:: Lo que **no** se validó, a propósito

   `cantidad_libros_aprox` y `cantidad_titulos_aprox` admiten cero: son
   aproximados y una editorial que todavía no lo sabe tiene que poder
   enviar. Y los nombres de personas y lugares no llevan longitud mínima
   más allá de la editorial: un apellido corto existe, y rechazarlo
   cuesta más que un dato imperfecto que alguien va a leer igual.
"""

import pytest
from django.core.exceptions import ValidationError
from django_tenants.utils import schema_context

from comun.validadores import telefono, validar_cp

from apps.registros.models import Persona

from ..formularios import EditorialForm, SellosForm
from ..models import ConfiguracionSistema
from . import fabricas
from .fabricas import FICHA

pytestmark = pytest.mark.django_db


def _ficha(**cambios):
    """Un `EditorialForm` ligado, válido salvo por lo que se cambie."""
    datos = {
        **fabricas.FICHA,
        "materiales": ["Libro"],
        "tematicas": ["Literatura"],
        **cambios,
    }
    return EditorialForm(datos)


# ── El código postal ──────────────────────────────────────────


@pytest.mark.parametrize("malo", ["abc", "970", "9700000", "97 000", ""])
def test_en_mexico_el_cp_son_cinco_digitos(malo):
    with pytest.raises(ValidationError):
        validar_cp(malo or "x", "MX")


def test_fuera_de_mexico_se_admite_otro_formato():
    """Canadá usa letras; exigir cinco dígitos dejaría fuera a Toronto."""
    validar_cp("M5V 3L9", "CA")
    validar_cp("SW1A 1AA", "GB")


def test_el_cp_se_valida_contra_el_pais_del_formulario():
    """No es un validador del campo: necesita los dos valores limpios."""
    en_mexico = _ficha(cp="M5V 3L9", pais="MX")
    assert not en_mexico.is_valid()
    assert "cp" in en_mexico.errors

    assert _ficha(cp="M5V 3L9", pais="CA").is_valid()


# ── Los teléfonos ─────────────────────────────────────────────


@pytest.mark.parametrize("malo", ["hola", "1234", "999-ABC-4567", "+"])
def test_un_telefono_que_no_es_un_telefono_se_rechaza(malo):
    with pytest.raises(ValidationError):
        telefono(malo)


@pytest.mark.parametrize(
    "bueno", ["9991112233", "999 123 4567", "+52 999 123 4567", "(999) 123-4567"]
)
def test_los_formatos_que_de_verdad_escribe_la_gente_se_admiten(bueno):
    telefono(bueno)


def test_el_celular_es_obligatorio_y_con_formato():
    # Se comprueba **en qué campo** cae el error: un formulario inválido
    # por otra cosa daría este mismo `assert not is_valid()`.
    con_texto = _ficha(telefono_celular="no tengo")
    assert not con_texto.is_valid()
    assert "telefono_celular" in con_texto.errors

    vacio = _ficha(telefono_celular="")
    assert not vacio.is_valid()
    assert "telefono_celular" in vacio.errors


def test_el_de_oficina_es_opcional_pero_si_se_escribe_se_valida():
    assert _ficha(telefono_oficina="").is_valid()

    con_basura = _ficha(telefono_oficina="x")
    assert not con_basura.is_valid()
    assert "telefono_oficina" in con_basura.errors


# ── Números que no pueden ser cero ────────────────────────────


def test_un_stand_lo_atiende_al_menos_una_persona():
    con_cero = _ficha(num_personas_atienden=0)
    assert not con_cero.is_valid()
    assert "num_personas_atienden" in con_cero.errors

    assert _ficha(num_personas_atienden=1).is_valid()


def test_traer_cero_libros_si_se_admite():
    """Es un aproximado: quien todavía no lo sabe tiene que poder enviar."""
    assert _ficha(cantidad_libros_aprox=0, cantidad_titulos_aprox=0).is_valid()


def test_un_plazo_de_cero_dias_no_es_un_plazo(feria_2027):
    """Vencería la reserva en el mismo instante de crearla."""
    with schema_context(feria_2027.schema_name):
        cfg = ConfiguracionSistema(
            convocatoria=fabricas.convocatoria(), plazo_reserva_dias=0
        )
        with pytest.raises(ValidationError):
            cfg.full_clean()


@pytest.mark.parametrize("campo", ["porcentaje_anticipo", "descuento_pronto_pago"])
def test_un_porcentaje_no_pasa_del_cien(feria_2027, campo):
    with schema_context(feria_2027.schema_name):
        cfg = ConfiguracionSistema(
            convocatoria=fabricas.convocatoria(), **{campo: 150}
        )
        with pytest.raises(ValidationError):
            cfg.full_clean()


# ── Nombres demasiado cortos ──────────────────────────────────


def test_el_nombre_de_la_editorial_no_es_una_letra():
    """Mismo mínimo que `Convocatoria.nombre`, y por lo mismo."""
    corto = _ficha(nombre="X")
    assert not corto.is_valid()
    assert "nombre" in corto.errors

    assert _ficha(nombre="Era").is_valid()


def test_un_sello_no_se_llama_con_una_letra():
    form = SellosForm({"sello_0": "x"})

    assert not form.is_valid()
    assert "sello_0" in form.errors


# ── Lo que ya estaba cubierto por el tipo ─────────────────────


def test_el_giro_solo_admite_los_tres_de_la_ficha():
    form = _ficha(giro="universidad")
    assert not form.is_valid()
    assert "giro" in form.errors


def test_una_tematica_fuera_del_catalogo_se_rechaza():
    form = _ficha(tematicas=["Alquimia"])
    assert not form.is_valid()
    assert "tematicas" in form.errors


def test_los_correos_se_validan_los_cinco():
    """El de contacto y los cuatro de los directores."""
    for campo in (
        "correo_electronico",
        "director_general_email",
        "director_comercial_email",
        "director_editorial_email",
        "director_promocion_email",
    ):
        form = _ficha(**{campo: "arroba-no"})
        assert not form.is_valid(), campo
        assert campo in form.errors, campo


def test_ningun_campo_obligatorio_se_puede_dejar_vacio():
    """El barrido, al revés: que cada obligatorio de verdad lo sea.

    Sin esto, marcar un campo como obligatorio y que el formulario lo
    deje pasar no daría ningún síntoma hasta ver una ficha a medias.
    """
    obligatorios = [k for k, c in EditorialForm().fields.items() if c.required]
    # Que la lista no esté vacía por un cambio de la clase: sin esto el
    # bucle no recorrería nada y la prueba pasaría sin comprobar nada.
    assert len(obligatorios) >= 12

    for campo in obligatorios:
        form = _ficha(**{campo: ""})
        assert not form.is_valid(), f"{campo} se dejó enviar vacío"
        assert campo in form.errors, f"{campo} falló, pero no se señaló"


def test_la_ficha_de_las_pruebas_es_valida():
    """Que el resto de este archivo pruebe lo que dice.

    Si la ficha base no fuera válida, cada `assert not …is_valid()` de
    arriba pasaría por el motivo equivocado.
    """
    form = _ficha()

    assert form.is_valid(), form.errors


# ── Lo que la cuenta ya sabe ──────────────────────────────────


def _persona(**cambios):
    datos = {
        "correo": "ana@ejemplo.com",
        "nombre": "Ana María",
        "primer_apellido": "Pech",
        "telefono": "9990001234",
        "pais": "MX",
        **cambios,
    }
    return Persona.objects.create_user(**datos)


def test_la_ficha_en_blanco_llega_con_lo_de_la_cuenta():
    """Tres de los campos de la ficha ya se escribieron en el alta."""
    form = EditorialForm(persona=_persona())

    assert form.initial["responsable_stand"] == "Ana María Pech"
    assert form.initial["correo_electronico"] == "ana@ejemplo.com"
    assert form.initial["telefono_celular"] == "9990001234"


def test_lo_prellenado_se_puede_cambiar():
    """Son propuestas: el buzón comercial casi nunca es el personal."""
    form = _ficha(correo_electronico="ventas@mayab.mx")

    assert form.is_valid(), form.errors
    assert form.cleaned_data["correo_electronico"] == "ventas@mayab.mx"


def test_una_ficha_ya_guardada_no_se_repropone(feria_2027):
    """Si no, cambiar el teléfono personal cambiaría el de la editorial."""
    ana = _persona()
    with schema_context(feria_2027.schema_name):
        ficha = fabricas.editorial(ana)

        form = EditorialForm(instance=ficha, persona=ana)

        assert form.initial["telefono_celular"] == FICHA["telefono_celular"]
        assert form.prellenado == []


def test_no_se_anuncia_un_prellenado_en_un_formulario_ya_enviado():
    """Ligado se pinta lo enviado; el aviso hablaría de algo que no se ve."""
    form = EditorialForm({**FICHA}, persona=_persona())

    assert form.prellenado == []


def test_una_cuenta_sin_telefono_solo_propone_lo_que_tiene():
    """`Persona.telefono` es `blank=True` para las cuentas técnicas."""
    form = EditorialForm(persona=_persona(telefono=""))

    assert "telefono_celular" not in form.initial
    assert form.initial["correo_electronico"] == "ana@ejemplo.com"


def test_sin_persona_el_formulario_llega_en_blanco():
    """La vista siempre la pasa, pero el formulario no la exige."""
    form = EditorialForm()

    assert form.prellenado == []
    assert "correo_electronico" not in form.initial


def test_los_campos_propuestos_se_enumeran_para_decirlos():
    form = EditorialForm(persona=_persona())

    assert form.prellenado_texto == (
        "responsable del stand, correo de contacto y teléfono celular"
    )
