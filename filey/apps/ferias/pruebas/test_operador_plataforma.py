"""
El operador de la plataforma alcanza cualquier feria (`ADR-0005`).

ADR-0004 dejó al equipo técnico **fuera** de toda feria: crea ediciones
y designa dueños, y ahí acaba su alcance. ADR-0005 abre esa puerta, y lo
que se prueba aquí son sus dos bordes —el de más y el de menos—, porque
los dos fallan en silencio:

1. **Que la puerta sea la ancha correcta.** Un superusuario entra a las
   pantallas del dueño de una feria en la que no tiene fila en
   ``AdminFeria``. Si no entrara, una edición cuyo dueño se fue
   quedaría inoperable — el hueco que ADR-0004 dejó anotado.
2. **Que no sea más ancha de lo dicho.** `is_staff` abre los dos admin
   de Django, pero **no** sustituye a ser dueño: son dos techos
   distintos y confundirlos regalaría los accesos de todas las ferias a
   cualquier cuenta del equipo.
3. **Que la excepción no se lleve por delante los invariantes.** Ni el
   operador puede dejar una feria sin dueño.
"""

import pytest
from django.urls import reverse

from apps.registros.models import Persona

from ..models import AdminFeria

pytestmark = pytest.mark.django_db


def _operador(correo="raiz@filey.org"):
    """El equipo técnico: superusuario de Django, sin acceso a ninguna feria."""
    return Persona.objects.create_superuser(correo=correo, password="x")


def _del_equipo_sin_ser_raiz(correo="becario@filey.org"):
    """`is_staff` pero no `is_superuser`: abre el admin, no manda en la feria."""
    persona = Persona.objects.create_user(
        correo=correo, nombre="Beto", primer_apellido="Chan"
    )
    persona.is_staff = True
    persona.save(update_fields=["is_staff"])
    return persona


def _url(feria, nombre, *args):
    return feria.url + reverse(nombre, args=args).lstrip("/")


# ── La puerta que ADR-0005 abre ───────────────────────────────


def test_el_operador_entra_a_los_accesos_de_una_feria_ajena(client, feria_2027):
    """Sin fila en `AdminFeria`, y aun así pasa `requiere_dueno_feria`."""
    operador = _operador()
    assert not AdminFeria.objects.filter(persona=operador).exists()
    client.force_login(operador)

    respuesta = client.get(_url(feria_2027, "accesos:panel"))

    assert respuesta.status_code == 200


def test_el_operador_da_de_alta_un_administrador_en_una_feria_ajena(
    client, feria_2027
):
    """Es lo que desatasca una edición cuyo dueño se fue (ADR-0004, hueco abierto)."""
    client.force_login(_operador())

    client.post(
        _url(feria_2027, "accesos:panel"),
        {"correo": "nueva@uady.mx", "nombre": "Nueva", "primer_apellido": "Pech"},
    )

    acceso = AdminFeria.objects.get(persona__correo="nueva@uady.mx")
    assert acceso.feria == feria_2027
    assert not acceso.es_dueno  # el alta nunca crea un segundo dueño


# ── El borde de menos ─────────────────────────────────────────


def test_ser_del_equipo_no_basta_para_las_pantallas_del_dueno(client, feria_2027):
    """`is_staff` abre los admin de Django; solo `is_superuser` manda en la feria."""
    client.force_login(_del_equipo_sin_ser_raiz())

    respuesta = client.get(_url(feria_2027, "accesos:panel"))

    assert respuesta.status_code == 403


def test_una_cuenta_desactivada_no_es_operador(client, feria_2027):
    operador = _operador()
    operador.is_active = False
    operador.save(update_fields=["is_active"])
    client.force_login(operador)

    # Con la cuenta inactiva ni siquiera hay sesión que valga: se va al
    # acceso administrativo, no al 403.
    assert client.get(_url(feria_2027, "accesos:panel")).status_code == 302


# ── Los invariantes que la excepción no toca ──────────────────


def test_ni_el_operador_deja_una_feria_sin_dueno(client, feria_2027):
    """CU-FER-004 E2 sigue en pie: se transfiere la propiedad, no se retira."""
    dueno = AdminFeria.objects.get(feria=feria_2027, es_dueno=True)
    client.force_login(_operador())

    client.post(_url(feria_2027, "accesos:retirar", dueno.pk))

    assert AdminFeria.objects.filter(pk=dueno.pk).exists()


# ── El camino de entrada ──────────────────────────────────────


def test_el_listado_de_ferias_enlaza_hacia_dentro_de_cada_una(client, feria_2027):
    """Sin esto el operador tiene el permiso y no tiene por dónde entrar."""
    client.force_login(_operador())

    cuerpo = client.get("/django-admin/ferias/feria/").content.decode()

    assert f'href="{feria_2027.url}django-admin/"' in cuerpo
    assert f'href="{feria_2027.url}accesos/"' in cuerpo
