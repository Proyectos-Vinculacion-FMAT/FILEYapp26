"""
Entrar por una puerta u otra: administrar y participar con la misma cuenta.

Quien coordina el showfloor de una feria puede además tener su propia
editorial dentro de ella. Hasta el 2026-08-29 no había forma de ser lo
segundo: el catálogo detectaba la autoridad y devolvía el panel, así que
un administrador que entraba por el acceso de participante aterrizaba en
la administración y la única salida era cerrar sesión.

Lo que estas pruebas fijan es la separación entre **autoridad** —lo que
puede hacer, que no cambia— y **cara** —desde qué lado está mirando—.
"""

import pytest
from django.conf import settings
from django.urls import reverse
from django_tenants.utils import schema_context

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from apps.ferias import permisos
from apps.ferias.models import AdminFeria
from apps.registros.models import Persona
from apps.registros.services import sesion

pytestmark = pytest.mark.django_db


@pytest.fixture
def coordinadora(feria_2027):
    """Administra la feria **y** participa en ella."""
    persona = Persona.objects.create_user(
        correo="rita@filey.org", nombre="Rita", primer_apellido="Uc"
    )
    AdminFeria.objects.create(feria=feria_2027, persona=persona, es_dueno=False)
    return persona


def _publica(nombre):
    """Una URL de fuera de toda feria.

    `ROOT_URLCONF` es el de **dentro** de una feria —de ahí saca
    `django-tenants` los patrones que prefija con `/f/<slug>/`—, así que
    `reverse("ferias:modo")` a secas no encuentra nada. No se cambia el
    ajuste global porque este módulo también prueba una pantalla de
    dentro de una feria.
    """
    return reverse(nombre, urlconf=settings.PUBLIC_SCHEMA_URLCONF)


def _entrar(client, persona, contexto):
    """Deja la sesión como la dejaría el acceso por esa puerta."""
    client.force_login(persona)
    sesion_navegador = client.session
    sesion_navegador[sesion.CLAVE_CONTEXTO] = contexto
    sesion_navegador.save()


# ── La cara depende de la puerta ──────────────────────────────


def test_por_la_puerta_de_participante_ve_el_catalogo_de_participante(
    client, feria_2027, coordinadora
):
    """El síntoma que originó todo esto."""
    _entrar(client, coordinadora, sesion.CONTEXTO_PUBLICO)

    cuerpo = client.get(feria_2027.url).content.decode()

    assert "Panel de administración" not in cuerpo
    assert "Volver a administración" in cuerpo, "y con la puerta de vuelta"


def test_por_la_puerta_de_administracion_ve_el_panel(
    client, feria_2027, coordinadora
):
    _entrar(client, coordinadora, sesion.CONTEXTO_ADMIN)

    cuerpo = client.get(feria_2027.url).content.decode()

    assert "Panel de administración" in cuerpo
    assert "Ver como participante" in cuerpo


def test_sin_constancia_de_la_puerta_se_comporta_como_antes(
    client, feria_2027, coordinadora
):
    """Una sesión abierta antes de que esto existiera no cambia de cara."""
    client.force_login(coordinadora)

    cuerpo = client.get(feria_2027.url).content.decode()

    assert "Panel de administración" in cuerpo


# ── El conmutador ─────────────────────────────────────────────


def _cambiar(client, feria, modo):
    return client.post(
        _publica("ferias:modo"), {"modo": modo, "feria": feria.slug}, follow=True
    )


def test_el_conmutador_cambia_de_cara_y_devuelve_a_la_feria(
    client, feria_2027, coordinadora
):
    _entrar(client, coordinadora, sesion.CONTEXTO_ADMIN)

    respuesta = _cambiar(client, feria_2027, sesion.CONTEXTO_PUBLICO)
    cuerpo = respuesta.content.decode()

    assert respuesta.redirect_chain[-1][0].startswith(feria_2027.url)
    assert "Panel de administración" not in cuerpo
    assert "Volver a administración" in cuerpo


def test_el_viaje_de_vuelta(client, feria_2027, coordinadora):
    _entrar(client, coordinadora, sesion.CONTEXTO_PUBLICO)

    cuerpo = _cambiar(client, feria_2027, sesion.CONTEXTO_ADMIN).content.decode()

    assert "Panel de administración" in cuerpo


def test_el_conmutador_no_acepta_un_get(client, feria_2027, coordinadora):
    """Un GET que cambia la sesión lo dispara cualquier precarga."""
    _entrar(client, coordinadora, sesion.CONTEXTO_ADMIN)

    respuesta = client.get(_publica("ferias:modo"))

    assert respuesta.status_code == 405


def test_una_feria_inventada_no_redirige_a_ninguna_parte(
    client, feria_2027, coordinadora
):
    """El destino se arma aquí; el POST solo dice de dónde venía."""
    _entrar(client, coordinadora, sesion.CONTEXTO_ADMIN)

    respuesta = client.post(
        _publica("ferias:modo"),
        {"modo": sesion.CONTEXTO_PUBLICO, "feria": "../otra-cosa"},
    )

    assert respuesta.status_code == 302
    assert respuesta.url == _publica("ferias:elegir")


def test_quien_no_administra_no_ve_el_conmutador(client, feria_2027):
    ana = Persona.objects.create_user(
        correo="ana@ejemplo.com", nombre="Ana", primer_apellido="Poot"
    )
    _entrar(client, ana, sesion.CONTEXTO_PUBLICO)

    cuerpo = client.get(feria_2027.url).content.decode()

    assert "Volver a administración" not in cuerpo


def test_cambiar_de_cara_no_da_permisos_a_quien_no_los_tiene(
    client, feria_2027, rf
):
    """`ve_como_admin` **solo quita**: nunca convierte a nadie en admin."""
    ana = Persona.objects.create_user(
        correo="ana@ejemplo.com", nombre="Ana", primer_apellido="Poot"
    )
    peticion = rf.get("/")
    peticion.user = ana
    peticion.tenant = feria_2027
    peticion.session = {sesion.CLAVE_CONTEXTO: sesion.CONTEXTO_ADMIN}

    assert not permisos.administra(peticion)
    assert not permisos.ve_como_admin(peticion)


# ── La autoridad no se mueve ──────────────────────────────────


def test_mirando_como_participante_sigue_administrando(
    client, feria_2027, coordinadora, rf
):
    """La diferencia entre `administra` y `ve_como_admin`, en una línea.

    Importa porque de `administra` cuelgan la entrega de archivos y el
    recorte de `RN-18`: si la cara moviera la autoridad, mirar el
    catálogo como participante abriría agujeros en otras pantallas.
    """
    peticion = rf.get("/")
    peticion.user = coordinadora
    peticion.tenant = feria_2027
    peticion.session = {sesion.CLAVE_CONTEXTO: sesion.CONTEXTO_PUBLICO}

    assert permisos.administra(peticion)
    assert not permisos.ve_como_admin(peticion)


def test_abrir_una_pantalla_de_administracion_devuelve_esa_cara(
    client, feria_2027, coordinadora
):
    """El modo se corrige solo, en vez de dar un 403 sobre algo que sí puede.

    Es el caso del marcador guardado: quien mira como participante abre
    una dirección del panel y entra, con su barra de administración.
    """
    _entrar(client, coordinadora, sesion.CONTEXTO_PUBLICO)
    with schema_context(feria_2027.schema_name):
        convocatoria = Convocatoria.objects.create(
            tipo=TipoConvocatoria.STD,
            nombre="Stands 2027",
            estado=Convocatoria.Estado.ABIERTA,
        )

    url = f"{feria_2027.url.rstrip('/')}" + reverse(
        "stands:panel", kwargs={"convocatoria_id": convocatoria.pk}
    )
    respuesta = client.get(url)

    assert respuesta.status_code == 200
    assert client.session[sesion.CLAVE_CONTEXTO] == sesion.CONTEXTO_ADMIN


def test_el_acceso_de_participante_deja_constancia_de_la_puerta(
    client, coordinadora, monkeypatch
):
    """Lo que hace que todo lo anterior arranque solo (`CU-REG-003`)."""
    from types import SimpleNamespace

    from apps.registros.services import sesion as servicio

    # `login()` rota la sesión de verdad y necesita una petición completa;
    # lo que se prueba aquí es lo que se escribe **después** de él.
    monkeypatch.setattr(servicio, "login", lambda *a, **k: None)
    peticion = SimpleNamespace(session={})

    servicio.iniciar(peticion, coordinadora, contexto=servicio.CONTEXTO_PUBLICO)

    assert peticion.session[servicio.CLAVE_CONTEXTO] == servicio.CONTEXTO_PUBLICO
