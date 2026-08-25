"""
El nombre de una `Persona` y su país (CU-REG-001, decisión 2026-08-25).

El nombre se guarda en tres campos y se muestra en varios formatos. Lo
que se prueba aquí es que **el segundo apellido de verdad es opcional**
en todos ellos: es el caso que rompe si alguien asume que siempre hay
dos apellidos, y afecta a cualquier participante extranjero.
"""

import importlib

import pytest

from apps.registros.models import Persona
from apps.registros.paises import NOMBRES_POR_CODIGO, PAISES, nombre_de

# El nombre del módulo empieza por dígito, así que no se puede importar
# con `from ... import ...`.
mig_0003 = importlib.import_module(
    "apps.registros.migrations.0003_persona_nombre_en_tres_campos_y_pais"
)

pytestmark = pytest.mark.django_db


def _persona(**campos):
    base = {
        "correo": "prueba@ejemplo.com",
        "nombre": "María del Carmen",
        "primer_apellido": "Pech",
        "segundo_apellido": "Uc",
    }
    return Persona(**{**base, **campos})


# ── Formatos del nombre ───────────────────────────────────────


def test_nombre_completo_junta_los_tres_campos():
    assert _persona().nombre_completo == "María del Carmen Pech Uc"


def test_nombre_completo_sin_segundo_apellido_no_deja_espacio_de_sobra():
    persona = _persona(segundo_apellido="")
    assert persona.nombre_completo == "María del Carmen Pech"


def test_nombre_para_orden_pone_los_apellidos_delante():
    assert _persona().nombre_para_orden == "Pech Uc, María del Carmen"


def test_nombre_para_orden_sin_segundo_apellido():
    assert _persona(segundo_apellido="").nombre_para_orden == "Pech, María del Carmen"


def test_nombre_para_orden_sin_ningun_apellido_no_deja_coma_colgando():
    """Las cuentas administrativas se dan de alta sin apellidos."""
    persona = _persona(primer_apellido="", segundo_apellido="")
    assert persona.nombre_para_orden == "María del Carmen"


def test_iniciales_son_nombre_y_primer_apellido():
    assert _persona().iniciales == "MP"


def test_iniciales_de_quien_solo_tiene_nombre():
    assert _persona(primer_apellido="", segundo_apellido="").iniciales == "M"


def test_primer_nombre_ignora_los_nombres_de_pila_siguientes():
    """Es lo que saluda el correo del OTP: 'Hola María', no el nombre entero."""
    assert _persona().primer_nombre == "María"


def test_una_persona_sin_nombre_no_revienta_ninguna_propiedad():
    """El comando `alta_admin` permite crear una cuenta sin nombre."""
    persona = _persona(nombre="", primer_apellido="", segundo_apellido="")
    assert persona.nombre_completo == ""
    assert persona.iniciales == ""
    assert persona.primer_nombre == ""


# ── Catálogo de países ────────────────────────────────────────


def test_el_catalogo_no_tiene_codigos_repetidos():
    codigos = [codigo for codigo, _ in PAISES]
    assert len(codigos) == len(set(codigos))
    assert len(codigos) == len(NOMBRES_POR_CODIGO)


def test_el_catalogo_no_tiene_nombres_repetidos():
    """Dos etiquetas iguales harían indistinguibles dos opciones del desplegable."""
    nombres = [nombre for _, nombre in PAISES]
    assert len(nombres) == len(set(nombres))


def test_todos_los_codigos_son_iso_de_dos_letras():
    """`Persona.pais` es un CharField(max_length=2): uno más largo se truncaría."""
    for codigo, _ in PAISES:
        assert len(codigo) == 2 and codigo.isupper() and codigo.isalpha()


def test_mexico_va_primero():
    """No es cosmético: ahorra desplazarse en un desplegable de ~200 entradas."""
    assert PAISES[0][0] == "MX"


def test_nombre_de_un_codigo_desconocido_devuelve_el_codigo():
    assert nombre_de("MX") == "México"
    assert nombre_de("ZZ") == "ZZ"
    assert nombre_de("") == ""


def test_el_pais_se_guarda_como_codigo_no_como_nombre():
    persona = Persona.objects.create_user(correo="pais@ejemplo.com", pais="ES")
    persona.refresh_from_db()
    assert persona.pais == "ES"
    assert persona.get_pais_display() == "España"


# ── La heurística de la migración 0003 ────────────────────────
#
# Se prueba la función pura, no la migración: lo que puede equivocarse
# en silencio es el reparto, no el `RunPython` que lo recorre.


@pytest.mark.parametrize(
    "completo, esperado",
    [
        ("María del Carmen Pech Uc", ("María del Carmen", "Pech", "Uc")),
        ("Hugo Janssen", ("Hugo", "Janssen", "")),
        ("Cher", ("Cher", "", "")),
        ("", ("", "", "")),
        (None, ("", "", "")),
        ("  Hugo   Janssen  ", ("Hugo", "Janssen", "")),
    ],
)
def test_reparto_de_un_nombre_en_un_solo_campo(completo, esperado):
    assert mig_0003.repartir(completo) == esperado


@pytest.mark.parametrize(
    "completo, mal_repartido",
    [
        # Un nombre de pila compuesto de dos palabras y un solo apellido
        # tiene exactamente la misma forma que nombre + dos apellidos.
        ("Ana María Pech", ("Ana", "María", "Pech")),
        # Un apellido compuesto no se distingue de dos apellidos.
        ("Juan Pérez de la Cruz", ("Juan Pérez de", "la", "Cruz")),
    ],
)
def test_el_reparto_se_equivoca_donde_la_forma_es_ambigua(completo, mal_repartido):
    """Documenta el fallo conocido, no lo aprueba.

    Estos casos son indistinguibles del caso correcto mirando solo el
    texto: ninguna heurística los acierta. Por eso la migración 0003
    avisa de que las filas migradas hay que revisarlas a mano, y por eso
    el formulario de alta pide los tres campos por separado — para que
    esto no vuelva a ocurrir con los registros nuevos.
    """
    assert mig_0003.repartir(completo) == mal_repartido
