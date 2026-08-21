"""
Permisos por módulo — el contrato que usarán EVT, TAL, STD y VIS.

Estas reglas todavía no las ejercita ninguna pantalla de dominio (no
existen), y por eso mismo conviene probarlas ahora: es lo que van a dar
por sentado los módulos cuando se construyan.
"""

import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory

from apps.registros.models import Modulo, NivelPermiso, RolPermiso
from apps.registros.permisos import requiere_admin, requiere_modulo, requiere_participante

pytestmark = pytest.mark.django_db


def _vista(peticion):
    return HttpResponse("panel")


def _peticion(usuario):
    peticion = RequestFactory().get("/admin/modulos/")
    peticion.user = usuario
    return peticion


# ── Persona.puede_administrar ─────────────────────────────────


def test_el_rol_comodin_cubre_todos_los_modulos(admin_general):
    for modulo in (Modulo.EVT, Modulo.TAL, Modulo.STD, Modulo.VIS):
        assert admin_general.puede_administrar(modulo)


def test_edicion_cubre_lo_que_solo_pide_lectura(admin_general):
    assert admin_general.puede_administrar(Modulo.EVT, NivelPermiso.LECTURA)
    assert admin_general.puede_administrar(Modulo.EVT, NivelPermiso.EDICION)


def test_lectura_no_alcanza_para_editar(admin_evt):
    assert admin_evt.puede_administrar(Modulo.EVT, NivelPermiso.LECTURA)
    assert not admin_evt.puede_administrar(Modulo.EVT, NivelPermiso.EDICION)


def test_el_permiso_de_un_modulo_no_se_extiende_a_otro(admin_evt):
    assert not admin_evt.puede_administrar(Modulo.STD)


def test_un_participante_no_administra_nada(participante):
    assert not participante.puede_administrar(Modulo.EVT)
    assert not participante.es_administrativa


def test_varios_roles_se_suman(participante):
    RolPermiso.objects.create(persona=participante, modulo=Modulo.EVT)
    RolPermiso.objects.create(
        persona=participante, modulo=Modulo.VIS, nivel=NivelPermiso.LECTURA
    )

    assert participante.puede_administrar(Modulo.EVT, NivelPermiso.EDICION)
    assert participante.puede_administrar(Modulo.VIS, NivelPermiso.LECTURA)
    assert not participante.puede_administrar(Modulo.VIS, NivelPermiso.EDICION)
    assert not participante.puede_administrar(Modulo.STD)


# ── Decoradores ───────────────────────────────────────────────


def test_sin_sesion_el_participante_va_al_acceso(client):
    from django.contrib.auth.models import AnonymousUser

    protegida = requiere_participante(_vista)
    respuesta = protegida(_peticion(AnonymousUser()))

    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/acceso/"


def test_sin_sesion_el_admin_va_al_acceso_administrativo():
    from django.contrib.auth.models import AnonymousUser

    protegida = requiere_admin(_vista)
    respuesta = protegida(_peticion(AnonymousUser()))

    assert respuesta.status_code == 302
    assert respuesta["Location"] == "/admin/acceso/"


def test_un_participante_con_sesion_no_entra_al_panel(participante):
    protegida = requiere_admin(_vista)

    with pytest.raises(PermissionDenied):
        protegida(_peticion(participante))


def test_requiere_modulo_deja_entrar_a_quien_tiene_el_permiso(admin_evt):
    protegida = requiere_modulo(Modulo.EVT)(_vista)

    assert protegida(_peticion(admin_evt)).status_code == 200


def test_requiere_modulo_corta_al_que_no_tiene_el_nivel(admin_evt):
    protegida = requiere_modulo(Modulo.EVT, NivelPermiso.EDICION)(_vista)

    with pytest.raises(PermissionDenied):
        protegida(_peticion(admin_evt))


def test_requiere_modulo_corta_al_admin_de_otro_modulo(admin_evt):
    protegida = requiere_modulo(Modulo.STD)(_vista)

    with pytest.raises(PermissionDenied):
        protegida(_peticion(admin_evt))
