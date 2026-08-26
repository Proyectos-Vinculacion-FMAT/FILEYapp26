"""
Elegir feria al entrar (`CU-FER-010` y `CU-FER-002`).

Dos pantallas con la misma forma y **filtros distintos a propósito**:

- El participante ve solo las ediciones ``activa``. Una en preparación
  no tiene revisadas sus convocatorias; una archivada ya no admite a
  nadie.
- El administrador ve todas en las que tiene acceso, **sin mirar el
  estado**: montar una edición en preparación y consultar una archivada
  son cosas que hace.

Y la regla que comparten: **con una sola feria, la pantalla no se
enseña**. Es lo que más fácil se rompe sin que nadie lo note, porque hoy
—con una sola edición viva— el salto es el caso normal y la pantalla
casi no se ve.

Estas pruebas usan ferias **sin schema** (`fabricas.py`): lo que se
comprueba es a dónde va cada quien, no qué hay dentro de la feria.
"""

import pytest
from django.urls import reverse

from apps.registros.models import Persona

from ..models import AdminFeria, Feria
from .fabricas import feria_sin_schema

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def urlconf_publico(settings):
    """Las dos pantallas viven **fuera** de toda feria.

    `ROOT_URLCONF` es el de dentro de una feria —de ahí saca
    `django-tenants` los patrones que prefija con `/f/<slug>/`—, así que
    sin esto `reverse("ferias:elegir")` no encuentra nada.
    """
    settings.ROOT_URLCONF = settings.PUBLIC_SCHEMA_URLCONF


@pytest.fixture
def participante(db):
    return Persona.objects.create_user(
        correo="ana@ejemplo.com",
        nombre="Ana María",
        primer_apellido="Pech",
        telefono="9990000001",
    )


@pytest.fixture
def administradora(db):
    return Persona.objects.create_user(
        correo="hipolito@filey.org",
        nombre="Hipólito",
        primer_apellido="Canto",
        telefono="9990000002",
    )


def _administra(persona, feria, es_dueno=True):
    return AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=es_dueno)


# ── El participante (CU-FER-010) ──────────────────────────────


def test_sin_ferias_abiertas_lo_dice_en_vez_de_reventar(client, participante):
    client.force_login(participante)

    respuesta = client.get(reverse("ferias:elegir"))

    assert respuesta.status_code == 200
    assert "no hay ninguna edición abierta" in respuesta.content.decode()


def test_con_una_sola_feria_no_se_pregunta(client, participante):
    """Elegir entre una opción no es elegir: es un clic de peaje."""
    feria = feria_sin_schema("FILEY 2027", "2027")
    client.force_login(participante)

    respuesta = client.get(reverse("ferias:elegir"))

    assert respuesta.status_code == 302
    assert respuesta["Location"] == feria.url == "/f/2027/"


def test_con_dos_ferias_se_pregunta(client, participante):
    feria_sin_schema("FILEY 2027", "2027")
    feria_sin_schema("FILEY 2028", "2028")
    client.force_login(participante)

    cuerpo = client.get(reverse("ferias:elegir")).content.decode()

    assert "FILEY 2027" in cuerpo
    assert "FILEY 2028" in cuerpo


def test_el_participante_no_ve_las_que_no_estan_activas(client, participante):
    """Y como solo queda una activa, ni siquiera llega a preguntar."""
    feria_sin_schema("FILEY 2027", "2027")
    feria_sin_schema("FILEY 2028", "2028", estado=Feria.Estado.EN_PREPARACION)
    feria_sin_schema("FILEY 2026", "2026", estado=Feria.Estado.ARCHIVADA)
    client.force_login(participante)

    respuesta = client.get(reverse("ferias:elegir"))

    assert respuesta["Location"] == "/f/2027/"


def test_la_feria_de_sistema_no_es_una_feria(client, participante):
    """La fila `public` que exige `django-tenants`; ver `models.py`.

    Sale por `Feria.objects` y **no** por `Feria.reales`. Si la pantalla
    usara el manager equivocado, aquí habría dos ferias y esta prueba
    devolvería un 200 en vez del salto.
    """
    feria_sin_schema("FILEY 2027", "2027")
    client.force_login(participante)

    respuesta = client.get(reverse("ferias:elegir"))

    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/f/2027/"


# ── El administrador (CU-FER-002) ─────────────────────────────


def test_con_una_sola_feria_administrada_tampoco_se_pregunta(client, administradora):
    feria = feria_sin_schema("FILEY 2027", "2027")
    _administra(administradora, feria)
    client.force_login(administradora)

    respuesta = client.get(reverse("ferias:mis_ferias"))

    assert respuesta["Location"] == feria.url


def test_el_panel_lista_las_ferias_que_administro(client, administradora):
    primera = feria_sin_schema("FILEY 2027", "2027")
    segunda = feria_sin_schema("FILEY 2028", "2028")
    _administra(administradora, primera)
    _administra(administradora, segunda, es_dueno=False)
    client.force_login(administradora)

    cuerpo = client.get(reverse("ferias:mis_ferias")).content.decode()

    assert primera.nombre in cuerpo
    assert segunda.nombre in cuerpo
    assert primera.url in cuerpo
    # Y se distingue en cuál es dueña y en cuál no (ADR-0004).
    assert "Dueño" in cuerpo
    assert "Administrador" in cuerpo


def test_el_panel_no_lista_las_ferias_de_otro(client, administradora):
    """Administrar una feria no la asoma en la lista de otra persona."""
    mia = feria_sin_schema("FILEY 2027", "2027")
    otra = feria_sin_schema("FILEY 2028", "2028")
    ajena = feria_sin_schema("FILEY 2029", "2029")
    _administra(administradora, mia)
    _administra(administradora, otra)
    client.force_login(administradora)

    cuerpo = client.get(reverse("ferias:mis_ferias")).content.decode()

    assert ajena.nombre not in cuerpo


def test_el_administrador_si_ve_las_ferias_inactivas(client, administradora):
    """Al revés que el participante, y a propósito.

    Una edición en preparación es justo la que hay que entrar a montar,
    y una archivada se consulta. Lo que cambia con el estado es qué se
    puede hacer dentro, no si aparece en la lista.
    """
    preparandose = feria_sin_schema(
        "FILEY 2028", "2028", estado=Feria.Estado.EN_PREPARACION
    )
    archivada = feria_sin_schema("FILEY 2026", "2026", estado=Feria.Estado.ARCHIVADA)
    _administra(administradora, preparandose)
    _administra(administradora, archivada)
    client.force_login(administradora)

    cuerpo = client.get(reverse("ferias:mis_ferias")).content.decode()

    assert preparandose.nombre in cuerpo
    assert archivada.nombre in cuerpo


def test_el_panel_no_lista_la_feria_de_sistema(client, administradora):
    """La fila `public` no es una feria; ver `apps/ferias/models.py`."""
    feria = feria_sin_schema("FILEY 2027", "2027")
    otra = feria_sin_schema("FILEY 2028", "2028")
    _administra(administradora, feria)
    _administra(administradora, otra)
    client.force_login(administradora)

    cuerpo = client.get(reverse("ferias:mis_ferias")).content.decode()

    assert "(sistema)" not in cuerpo


# ── Las dos piden sesión ──────────────────────────────────────


def test_elegir_feria_pide_sesion(client):
    respuesta = client.get(reverse("ferias:elegir"))

    assert respuesta["Location"] == reverse("registros:acceso")


def test_mis_ferias_manda_al_acceso_administrativo(client):
    respuesta = client.get(reverse("ferias:mis_ferias"))

    assert respuesta["Location"] == reverse("registros:admin_acceso")
