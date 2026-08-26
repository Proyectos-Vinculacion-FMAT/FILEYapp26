"""
Permisos por feria — el contrato que usarán EVT, TAL, STD y VIS.

Estas reglas todavía no las ejercita ninguna pantalla de dominio (no
existen), y por eso mismo conviene probarlas ahora: es lo que van a dar
por sentado los módulos cuando se construyan.

Hasta el 2026-08-25 este archivo probaba permisos por **módulo** y
**nivel** (`RolPermiso`). ADR-0004 los sustituyó por acceso **por
feria** sin niveles, así que lo que se prueba aquí cambió de forma: ya
no hay «lectura no alcanza para editar», y sí hay «administrar una
feria no da acceso a otra» — que es el error que de verdad importa.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory

from apps.ferias.permisos import requiere_admin_feria, requiere_dueno_feria
from apps.registros.permisos import requiere_admin, requiere_participante

pytestmark = pytest.mark.django_db


def _vista(peticion):
    return HttpResponse("panel")


def _peticion(usuario, tenant=None):
    peticion = RequestFactory().get("/admin/ferias/")
    peticion.user = usuario
    if tenant is not None:
        # Lo pone `TenantSubfolderMiddleware` en cada petición bajo
        # `/f/<slug>/`; aquí se simula porque no hay middleware.
        peticion.tenant = tenant
    return peticion


# ── Persona.es_administrativa ─────────────────────────────────


def test_quien_administra_una_feria_es_administrativa(admin_feria):
    assert admin_feria.es_administrativa


def test_el_dueno_tambien_es_administrativa(dueno_feria):
    assert dueno_feria.es_administrativa


def test_un_participante_no_administra_nada(participante):
    assert not participante.es_administrativa


# ── Decoradores fuera de una feria ────────────────────────────


def test_sin_sesion_el_participante_va_al_acceso():
    protegida = requiere_participante(_vista)
    respuesta = protegida(_peticion(AnonymousUser()))

    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/acceso/"


def test_sin_sesion_el_admin_va_al_acceso_administrativo():
    protegida = requiere_admin(_vista)
    respuesta = protegida(_peticion(AnonymousUser()))

    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/admin/acceso/"


def test_un_participante_con_sesion_no_entra_al_panel(participante):
    protegida = requiere_admin(_vista)

    with pytest.raises(PermissionDenied):
        protegida(_peticion(participante))


# ── Decoradores dentro de una feria ───────────────────────────


def test_quien_administra_la_feria_entra(admin_feria, feria):
    protegida = requiere_admin_feria(_vista)

    assert protegida(_peticion(admin_feria, tenant=feria)).status_code == 200


def test_administrar_una_feria_no_da_acceso_a_otra(admin_feria, otra_feria):
    """El fallo que este modelo existe para impedir.

    Con `RolPermiso` el permiso era global al sistema, así que esta
    pregunta ni siquiera se podía formular.
    """
    protegida = requiere_admin_feria(_vista)

    with pytest.raises(PermissionDenied):
        protegida(_peticion(admin_feria, tenant=otra_feria))


def test_un_participante_no_entra_a_ninguna_feria(participante, feria):
    protegida = requiere_admin_feria(_vista)

    with pytest.raises(PermissionDenied):
        protegida(_peticion(participante, tenant=feria))


def test_el_dueno_pasa_por_donde_pasa_un_administrador(dueno_feria, feria):
    protegida = requiere_admin_feria(_vista)

    assert protegida(_peticion(dueno_feria, tenant=feria)).status_code == 200


def test_solo_el_dueno_administra_accesos_y_convocatorias(dueno_feria, feria):
    protegida = requiere_dueno_feria(_vista)

    assert protegida(_peticion(dueno_feria, tenant=feria)).status_code == 200


def test_un_administrador_no_es_dueno(admin_feria, feria):
    """Enmienda del 2026-08-25 a ADR-0004.

    El ADR original daba todo el contenido de la feria a cualquier
    administrador. Dar de alta administradores y abrir convocatorias
    quedó reservado al dueño.
    """
    protegida = requiere_dueno_feria(_vista)

    with pytest.raises(PermissionDenied):
        protegida(_peticion(admin_feria, tenant=feria))


def test_fuera_de_toda_feria_no_se_administra_nada(dueno_feria):
    """Sin `request.tenant` no hay feria contra la que comprobar.

    Pasa en las rutas que no cuelgan de `/f/<slug>/`. Denegar es lo
    único seguro: dejar pasar equivaldría a comprobar el permiso contra
    una feria que nadie eligió.
    """
    protegida = requiere_admin_feria(_vista)

    with pytest.raises(PermissionDenied):
        protegida(_peticion(dueno_feria))
