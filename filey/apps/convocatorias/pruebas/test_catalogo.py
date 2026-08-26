"""
El catálogo de convocatorias de una feria (`CU-FER-006`).

Es la misma pantalla para dos públicos, y toda su dificultad está ahí:
el participante ve un escaparate y quien administra ve un panel. Lo que
se prueba aquí no es que la lista salga —eso es lo fácil— sino las tres
formas en que la diferencia se rompe **sin dar ningún síntoma**:

1. Un `borrador` que se filtra al participante. La convocatoria en
   borrador no tiene revisada su configuración: alguien intentaría
   registrarse a algo que no está listo para recibirlo.
2. Que administrar la feria A conceda algo en la feria B.
3. Que la barra superior enlace **dentro** de la feria a direcciones que
   son globales — el cierre de sesión, sobre todo—, que es lo que rompe
   el urlconf doble de `django-tenants`.

Estas pruebas sí necesitan schemas de verdad: lo que se mira es qué hay
dentro de cada feria.
"""

import pytest
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.ferias.models import AdminFeria, Feria
from apps.registros.models import Persona

from ..models import Convocatoria, TipoConvocatoria

pytestmark = pytest.mark.django_db


def _convocatoria(nombre, estado, tipo=TipoConvocatoria.STD):
    return Convocatoria.objects.create(tipo=tipo, nombre=nombre, estado=estado)


@pytest.fixture
def con_catalogo(feria_2027):
    """Una feria con las tres situaciones a la vez."""
    with schema_context(feria_2027.schema_name):
        _convocatoria("Stands abiertos", Convocatoria.Estado.ABIERTA)
        _convocatoria("Eventos cerrados", Convocatoria.Estado.CERRADA, TipoConvocatoria.EVT)
        _convocatoria("Visitas en borrador", Convocatoria.Estado.BORRADOR, TipoConvocatoria.VIS)
    return feria_2027


@pytest.fixture
def participante(db):
    return Persona.objects.create_user(
        correo="ana@ejemplo.com",
        nombre="Ana María",
        primer_apellido="Pech",
        telefono="9990000001",
    )


def _admin_de(feria, correo="rita@filey.org"):
    """Administradora **no dueña**: la feria ya tiene dueño de su alta.

    Para este catálogo da igual cuál de los dos sea —lo que decide qué
    se ve es administrar *esta* feria (CU-FER-006)—, y así se comprueba
    de paso que no hace falta ser dueño para verlo.
    """
    persona = Persona.objects.create_user(
        correo=correo, nombre="Rita", primer_apellido="Uc", telefono="9990000003"
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _activar(*ferias):
    """Una feria nace `en_preparacion` y el participante no la ve.

    Ver `apps/ferias/servicios/seleccion.py`. Las pruebas que cuentan
    ferias desde el punto de vista del participante tienen que activarlas
    a mano, igual que hay que hacerlo desde `/django-admin/`.
    """
    for feria in ferias:
        feria.estado = Feria.Estado.ACTIVA
        feria.save()


# ── Quién ve el borrador ──────────────────────────────────────


def test_el_borrador_no_llega_al_participante(client, con_catalogo, participante):
    """No se oculta en la plantilla: no entra en la respuesta.

    Es la diferencia entre no enseñarlo y no mandarlo. Con un `{% if %}`
    el nombre viajaría en el HTML.
    """
    client.force_login(participante)

    cuerpo = client.get(con_catalogo.url).content.decode()

    assert "Stands abiertos" in cuerpo
    assert "Eventos cerrados" in cuerpo
    assert "Visitas en borrador" not in cuerpo


def test_el_borrador_tampoco_llega_a_quien_no_tiene_sesion(client, con_catalogo):
    cuerpo = client.get(con_catalogo.url).content.decode()

    assert "Stands abiertos" in cuerpo
    assert "Visitas en borrador" not in cuerpo


def test_quien_administra_la_feria_si_ve_el_borrador(client, con_catalogo):
    client.force_login(_admin_de(con_catalogo))

    cuerpo = client.get(con_catalogo.url).content.decode()

    assert "Visitas en borrador" in cuerpo
    assert "como administrador" in cuerpo


def test_administrar_otra_feria_no_descubre_los_borradores_de_esta(
    client, con_catalogo, feria_2028
):
    """El permiso es por feria, no por tener permisos en alguna (ADR-0004)."""
    client.force_login(_admin_de(feria_2028))

    cuerpo = client.get(con_catalogo.url).content.decode()

    assert "Stands abiertos" in cuerpo
    assert "Visitas en borrador" not in cuerpo


# ── Sin sesión, y el aislamiento ──────────────────────────────


def test_el_catalogo_se_mira_sin_cuenta(client, con_catalogo):
    """A1: pedir sesión para mirar rompería el embudo."""
    respuesta = client.get(con_catalogo.url)

    assert respuesta.status_code == 200
    assert "Entrar" in respuesta.content.decode()


def test_una_feria_no_ensena_las_convocatorias_de_otra(
    client, con_catalogo, feria_2028
):
    cuerpo = client.get(feria_2028.url).content.decode()

    assert "Stands abiertos" not in cuerpo
    assert "todavía no tiene convocatorias publicadas" in cuerpo


# ── La barra superior dentro de una feria ─────────────────────


def test_el_cierre_de_sesion_no_lleva_prefijo_de_feria(
    client, con_catalogo, participante, settings
):
    """La cuenta es única en todo el sistema; su sesión no es de una feria.

    Además de estar mal, `{% url 'registros:salir' %}` **revienta** aquí
    dentro: ese nombre vive en el urlconf público. Es lo que resuelve
    `{% url_publica %}` / el tag de la barra.
    """
    client.force_login(participante)

    cuerpo = client.get(con_catalogo.url).content.decode()

    settings.ROOT_URLCONF = settings.PUBLIC_SCHEMA_URLCONF
    assert f'action="{reverse("registros:salir")}"' in cuerpo
    assert f'action="{con_catalogo.url}salir/"' not in cuerpo


def test_con_una_sola_feria_la_barra_no_ofrece_cambiarla(
    client, con_catalogo, participante
):
    """El enlace de vuelta solo tiene sentido si hay a dónde volver."""
    _activar(con_catalogo)
    client.force_login(participante)

    cuerpo = client.get(con_catalogo.url).content.decode()

    assert "Cambiar de feria" not in cuerpo


def test_con_dos_ferias_la_barra_ofrece_cambiarla(
    client, con_catalogo, feria_2028, participante
):
    """Es la puerta de vuelta que compensa el salto de CU-FER-010."""
    _activar(con_catalogo, feria_2028)
    client.force_login(participante)

    cuerpo = client.get(con_catalogo.url).content.decode()

    assert "Cambiar de feria" in cuerpo
