"""
Los accesos de una feria (`CU-FER-003`, `CU-FER-004`).

Es el CRUD que justifica que el dueño exista, así que lo que se prueba
aquí no es que la lista salga —eso es lo fácil— sino los cuatro límites
que, si se rompen, no dan ningún síntoma:

1. **Que administrar no sea lo mismo que ser dueño.** Un administrador
   legítimo, con acceso a todo el contenido, no puede tocar los accesos.
   Si pudiera, cualquiera crearía administradores y la responsabilidad
   volvería a diluirse: el problema que resuelve ADR-0004.
2. **Que la feria no se quede sin dueño.** Nadie podría volver a dar
   acceso a nadie sin entrar por consola.
3. **Que un identificador de otra feria no sirva aquí.** ``AdminFeria``
   vive en `public`, así que la conexión **no** acota la feria: la acota
   la vista, y esa es la línea que hay que vigilar.
4. **Que un correo que falla no deshaga el alta.** El acceso ya es
   válido; el aviso es informativo, no una credencial.

Estas pruebas necesitan schemas de verdad: las pantallas viven dentro de
`/f/<slug>/` y solo el middleware de `django-tenants` resuelve eso.
"""

import pytest
from django.core import mail
from django.urls import reverse

from apps.registros.models import Persona

from ..models import AdminFeria, Feria
from ..servicios import accesos

pytestmark = pytest.mark.django_db


def _persona(correo, nombre="Rita", primer_apellido="Uc"):
    return Persona.objects.create_user(
        correo=correo, nombre=nombre, primer_apellido=primer_apellido
    )


def _duena_de(feria):
    """La feria ya nace con dueña: la creó `altas.crear_feria`."""
    return AdminFeria.objects.get(feria=feria, es_dueno=True).persona


def _admin_de(feria, correo="rita@filey.org"):
    persona = _persona(correo)
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=False)
    return persona


def _url(feria, nombre, *args):
    """`reverse` de una ruta de dentro de la feria, sin pedir el urlconf.

    Se compone a mano porque el prefijo `/f/<slug>/` lo antepone
    `django-tenants` en tiempo de petición, no el urlconf.
    """
    return feria.url + reverse(nombre, args=args).lstrip("/")


# ── Quién puede ver esta pantalla (CU-FER-003 E1) ─────────────


def test_la_duena_ve_quien_administra_su_feria(client, feria_2027):
    _admin_de(feria_2027)
    client.force_login(_duena_de(feria_2027))

    cuerpo = client.get(_url(feria_2027, "accesos:panel")).content.decode()

    assert "ana@uady.mx" in cuerpo  # la dueña
    assert "rita@filey.org" in cuerpo  # la administradora
    assert "Dueño" in cuerpo
    assert "Administrador" in cuerpo


def test_un_administrador_no_dueno_no_entra(client, feria_2027):
    """El límite que justifica que el dueño exista (ADR-0004).

    Y se rechaza **en el servidor**: ocultar el enlace en el catálogo no
    es la protección (CU-FER-003 E1).
    """
    client.force_login(_admin_de(feria_2027))

    respuesta = client.get(_url(feria_2027, "accesos:panel"))

    assert respuesta.status_code == 403


def test_administrar_otra_feria_no_abre_los_accesos_de_esta(
    client, feria_2027, feria_2028
):
    """Ser dueña de la 2028 no da nada en la 2027 (ADR-0004)."""
    client.force_login(_duena_de(feria_2028))

    respuesta = client.get(_url(feria_2027, "accesos:panel"))

    assert respuesta.status_code == 403


def test_sin_sesion_manda_al_acceso_administrativo(client, feria_2027, settings):
    respuesta = client.get(_url(feria_2027, "accesos:panel"))

    settings.ROOT_URLCONF = settings.PUBLIC_SCHEMA_URLCONF
    assert respuesta["Location"] == reverse("registros:admin_acceso")


def test_el_enlace_a_accesos_solo_lo_ve_el_dueno(client, feria_2027):
    """La cortesía que acompaña al rechazo: no ofrecer lo que se negaría."""
    client.force_login(_admin_de(feria_2027))
    de_admin = client.get(feria_2027.url).content.decode()

    client.force_login(_duena_de(feria_2027))
    de_duena = client.get(feria_2027.url).content.decode()

    assert "Administradores de esta feria" not in de_admin
    assert "Administradores de esta feria" in de_duena


# ── Dar acceso (CU-FER-003) ───────────────────────────────────


def test_dar_acceso_a_una_cuenta_nueva(client, feria_2027):
    duena = _duena_de(feria_2027)
    client.force_login(duena)

    client.post(
        _url(feria_2027, "accesos:panel"),
        {"correo": "Nueva@Filey.org", "nombre": "Nueva", "primer_apellido": "Canto"},
    )

    persona = Persona.objects.get(correo="nueva@filey.org")  # normalizado
    acceso = AdminFeria.objects.get(feria=feria_2027, persona=persona)
    assert acceso.es_dueno is False  # este alta nunca crea otro dueño
    assert acceso.creado_por == duena
    # Paso 6: se avisa, y el correo no lleva ningún código (CU-REG-003).
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["nueva@filey.org"]


def test_dar_acceso_reutiliza_la_cuenta_que_ya_existia(client, feria_2027):
    """A1: la misma persona puede ser proponente en otra edición."""
    ya_estaba = _persona("beto@ejemplo.com", nombre="Beto", primer_apellido="Chan")
    client.force_login(_duena_de(feria_2027))

    client.post(
        _url(feria_2027, "accesos:panel"),
        {"correo": "beto@ejemplo.com", "nombre": "Otro", "primer_apellido": "Nombre"},
    )

    ya_estaba.refresh_from_db()
    assert ya_estaba.nombre == "Beto"  # no se le corrige el nombre
    assert Persona.objects.filter(correo="beto@ejemplo.com").count() == 1
    assert AdminFeria.objects.filter(feria=feria_2027, persona=ya_estaba).exists()


def test_dar_acceso_a_quien_ya_lo_tiene_no_duplica_ni_reavisa(client, feria_2027):
    """E2: no hay nivel que actualizar; el acceso a una feria no tiene grados."""
    persona = _admin_de(feria_2027)
    mail.outbox.clear()
    client.force_login(_duena_de(feria_2027))

    respuesta = client.post(
        _url(feria_2027, "accesos:panel"), {"correo": persona.correo}, follow=True
    )

    assert AdminFeria.objects.filter(feria=feria_2027, persona=persona).count() == 1
    assert mail.outbox == []
    assert "ya administraba esta feria" in respuesta.content.decode()


def test_un_correo_invalido_no_crea_nada(client, feria_2027):
    client.force_login(_duena_de(feria_2027))
    antes = AdminFeria.objects.count()

    cuerpo = client.post(
        _url(feria_2027, "accesos:panel"), {"correo": "esto-no-es-un-correo"}
    ).content.decode()

    assert AdminFeria.objects.count() == antes
    assert "no parece válido" in cuerpo


def test_una_feria_archivada_no_admite_administradores_nuevos(client, feria_2027):
    """E4: una edición cerrada se consulta, no se opera."""
    feria_2027.estado = Feria.Estado.ARCHIVADA
    feria_2027.save()
    client.force_login(_duena_de(feria_2027))

    client.post(_url(feria_2027, "accesos:panel"), {"correo": "tarde@filey.org"})

    assert not Persona.objects.filter(correo="tarde@filey.org").exists()


def test_el_fallo_del_correo_no_deshace_el_alta(feria_2027, monkeypatch):
    """E3: el aviso es informativo, no la credencial.

    Se prueba contra el servicio y no contra la vista porque lo que
    importa es que el acceso sobreviva, no cómo se rotula.
    """

    def revienta(*args, **kwargs):
        raise accesos.avisos.AvisoFallido("el proveedor devolvió 500")

    monkeypatch.setattr(accesos.avisos, "avisar_admin_de_feria", revienta)

    resultado = accesos.dar_acceso(feria=feria_2027, correo="sin.correo@filey.org")

    assert resultado.aviso_enviado is False
    assert resultado.error_aviso
    assert AdminFeria.objects.filter(id=resultado.acceso.id).exists()


# ── Retirar acceso (CU-FER-004) ───────────────────────────────


def test_retirar_un_acceso_deja_la_cuenta_intacta(client, feria_2027, feria_2028):
    """Retirar se parece a borrar una cuenta, y no lo es."""
    persona = _admin_de(feria_2027)
    otra = AdminFeria.objects.create(feria=feria_2028, persona=persona)
    acceso = AdminFeria.objects.get(feria=feria_2027, persona=persona)
    client.force_login(_duena_de(feria_2027))

    client.post(_url(feria_2027, "accesos:retirar", acceso.id))

    assert not AdminFeria.objects.filter(id=acceso.id).exists()
    assert Persona.objects.filter(id=persona.id).exists()
    assert AdminFeria.objects.filter(id=otra.id).exists()  # su otra feria sigue


def test_la_confirmacion_dice_lo_que_no_pasa(client, feria_2027):
    """Paso 4: es el motivo de que la confirmación sea una pantalla."""
    acceso = AdminFeria.objects.get(persona=_admin_de(feria_2027))
    client.force_login(_duena_de(feria_2027))

    cuerpo = client.get(_url(feria_2027, "accesos:retirar", acceso.id)).content.decode()

    assert "su cuenta de filey sigue existiendo" in cuerpo.lower()
    assert "cualquier otra edición" in cuerpo


def test_el_get_de_la_confirmacion_no_retira_nada(client, feria_2027):
    """Si retirar ocurriera en un GET, bastaría con precargar el enlace."""
    acceso = AdminFeria.objects.get(persona=_admin_de(feria_2027))
    client.force_login(_duena_de(feria_2027))

    client.get(_url(feria_2027, "accesos:retirar", acceso.id))

    assert AdminFeria.objects.filter(id=acceso.id).exists()


def test_no_se_puede_retirar_al_dueno(client, feria_2027):
    """E2: la feria se quedaría sin nadie que pueda dar acceso a nadie."""
    duena = _duena_de(feria_2027)
    acceso = AdminFeria.objects.get(feria=feria_2027, es_dueno=True)
    client.force_login(duena)

    client.post(_url(feria_2027, "accesos:retirar", acceso.id))

    assert AdminFeria.objects.filter(id=acceso.id).exists()


def test_no_se_puede_retirar_un_acceso_de_otra_feria(client, feria_2027, feria_2028):
    """`AdminFeria` es global: la feria la acota la vista, no la conexión."""
    ajeno = AdminFeria.objects.get(feria=feria_2028, es_dueno=True)
    client.force_login(_duena_de(feria_2027))

    respuesta = client.post(_url(feria_2027, "accesos:retirar", ajeno.id))

    assert respuesta.status_code == 404
    assert AdminFeria.objects.filter(id=ajeno.id).exists()


def test_un_administrador_no_dueno_no_puede_retirar(client, feria_2027):
    """E1 de CU-FER-004, y el mismo rechazo en el servidor."""
    victima = AdminFeria.objects.get(persona=_admin_de(feria_2027, "victima@filey.org"))
    client.force_login(_admin_de(feria_2027, "otro@filey.org"))

    respuesta = client.post(_url(feria_2027, "accesos:retirar", victima.id))

    assert respuesta.status_code == 403
    assert AdminFeria.objects.filter(id=victima.id).exists()
