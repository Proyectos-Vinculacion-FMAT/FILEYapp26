"""
El atajo al admin de Django de la edición, en la barra lateral.

Sin él solo se llega escribiendo `/f/<slug>/django-admin/` a mano, que es
donde viven el alta de convocatorias, la importación del mapa y la
bitácora de `STD`.

Lo que se defiende es **a quién se le ofrece**: la puerta de ese sitio es
`is_staff` (`comun/admin_feria.py`), así que enseñárselo al dueño de una
feria que no lo sea es mandarlo a un formulario de acceso que no va a
poder pasar.
"""

import pytest
from django.template import Context
from django.test import RequestFactory
from django_tenants.utils import schema_context

from apps.convocatorias.templatetags.panel_lateral import barra_lateral
from apps.registros.models import Persona

pytestmark = pytest.mark.django_db


def _entradas(feria, usuario):
    peticion = RequestFactory().get("/")
    peticion.tenant = feria
    peticion.user = usuario
    with schema_context(feria.schema_name):
        datos = barra_lateral(Context({"request": peticion}))
    return [e["etiqueta"] for grupo in datos["grupos"] for e in grupo["entradas"]]


def test_el_operador_ve_el_atajo(feria_2027):
    operador = Persona(correo="op@filey.org", is_staff=True)

    assert "Admin de Django" in _entradas(feria_2027, operador)


def test_el_enlace_apunta_al_admin_de_esta_edicion(feria_2027):
    """De **esta** feria y no al de `public`: son dos sitios distintos y
    sirven modelos distintos (`ADR-0003`)."""
    peticion = RequestFactory().get("/")
    peticion.tenant = feria_2027
    peticion.user = Persona(correo="op@filey.org", is_staff=True)

    with schema_context(feria_2027.schema_name):
        datos = barra_lateral(Context({"request": peticion}))

    atajo = next(
        e
        for grupo in datos["grupos"]
        for e in grupo["entradas"]
        if e["etiqueta"] == "Admin de Django"
    )
    assert atajo["url"] == f"/f/{feria_2027.slug}/django-admin/"


def test_quien_no_es_staff_no_lo_ve(feria_2027):
    """Incluye al dueño de la feria: administrar una edición y operar la
    plataforma son permisos distintos."""
    dueno = Persona(correo="ana@filey.org", is_staff=False)

    assert "Admin de Django" not in _entradas(feria_2027, dueno)


def test_sin_sesion_tampoco(feria_2027):
    from django.contrib.auth.models import AnonymousUser

    assert "Admin de Django" not in _entradas(feria_2027, AnonymousUser())
