"""
Flujo completo del participante (CU-REG-001, 002, 004, 006).

Recorre las pantallas como lo haría una persona: correo → registro o
código → convocatorias. Es la prueba que confirma que la migración a
plantillas no cambió ningún comportamiento del acceso.
"""

import pytest
from django.core import mail
from django.urls import reverse

from apps.registros.models import Persona

pytestmark = pytest.mark.django_db


# ── Pantalla del correo ───────────────────────────────────────


def test_la_raiz_lleva_al_acceso(client):
    assert client.get("/").status_code == 302
    assert client.get("/", follow=True).redirect_chain[-1][0] == reverse(
        "registros:acceso"
    )


def test_la_pantalla_de_acceso_se_dibuja(client):
    respuesta = client.get(reverse("registros:acceso"))

    assert respuesta.status_code == 200
    assert "Acceso a FILEY" in respuesta.content.decode()


def test_un_correo_desconocido_lleva_a_crear_cuenta(client):
    respuesta = client.post(
        reverse("registros:acceso"), {"correo": "nueva@ejemplo.com"}
    )

    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("registros:registro")
    assert mail.outbox == []  # todavía no hay cuenta a la que mandarle nada


def test_un_correo_conocido_recibe_su_codigo(client, participante, codigo_fijo):
    respuesta = client.post(
        reverse("registros:acceso"), {"correo": participante.correo}
    )

    assert respuesta["Location"] == reverse("registros:codigo")
    assert len(mail.outbox) == 1
    assert codigo_fijo in mail.outbox[0].body


def test_el_correo_no_distingue_mayusculas(client, participante, codigo_fijo):
    respuesta = client.post(
        reverse("registros:acceso"), {"correo": "ANA@Ejemplo.com"}
    )

    assert respuesta["Location"] == reverse("registros:codigo")


def test_un_correo_mal_escrito_no_avanza(client):
    respuesta = client.post(reverse("registros:acceso"), {"correo": "esto-no-es"})

    assert respuesta.status_code == 200
    assert "no parece válido" in respuesta.content.decode()


# ── Crear cuenta ──────────────────────────────────────────────


def test_no_se_puede_entrar_al_registro_sin_haber_identificado(client):
    respuesta = client.get(reverse("registros:registro"))

    assert respuesta.status_code == 302
    assert respuesta["Location"] == reverse("registros:acceso")


def test_crear_cuenta_manda_el_codigo(client, codigo_fijo):
    client.post(reverse("registros:acceso"), {"correo": "nueva@ejemplo.com"})

    respuesta = client.post(
        reverse("registros:registro"),
        {
            "nombre": "Nueva",
            "primer_apellido": "Persona",
            "segundo_apellido": "Ejemplo",
            "telefono": "999 000 1234",
            "pais": "MX",
            "entidad": "YUC",
        },
    )

    assert respuesta["Location"] == reverse("registros:codigo")
    persona = Persona.objects.get(correo="nueva@ejemplo.com")
    assert persona.nombre == "Nueva"
    assert persona.primer_apellido == "Persona"
    assert persona.segundo_apellido == "Ejemplo"
    assert persona.pais == "MX"
    # El teléfono se guarda solo con dígitos, para que dos formas de
    # escribir el mismo número no pasen como números distintos.
    assert persona.telefono == "9990001234"
    assert len(mail.outbox) == 1


def test_el_correo_del_registro_sale_de_la_sesion_no_del_formulario(client, codigo_fijo):
    """Nadie debe poder registrar un correo distinto al que identificó."""
    client.post(reverse("registros:acceso"), {"correo": "nueva@ejemplo.com"})

    client.post(
        reverse("registros:registro"),
        {
            "nombre": "Impostora",
            "primer_apellido": "Anónima",
            "telefono": "9990009999",
            "pais": "MX",
            "entidad": "YUC",
            "correo": "victima@ejemplo.com",
        },
    )

    assert Persona.objects.filter(correo="nueva@ejemplo.com").exists()
    assert not Persona.objects.filter(correo="victima@ejemplo.com").exists()


def test_un_telefono_ya_usado_se_reporta_en_su_campo(client, participante, codigo_fijo):
    client.post(reverse("registros:acceso"), {"correo": "otra@ejemplo.com"})

    respuesta = client.post(
        reverse("registros:registro"),
        {
            "nombre": "Otra",
            "primer_apellido": "Persona",
            "telefono": participante.telefono,
            "pais": "MX",
            "entidad": "YUC",
        },
    )

    assert respuesta.status_code == 200
    assert "ya está registrado con otro correo" in respuesta.content.decode()
    assert not Persona.objects.filter(correo="otra@ejemplo.com").exists()


def test_un_telefono_corto_no_pasa(client, codigo_fijo):
    client.post(reverse("registros:acceso"), {"correo": "nueva@ejemplo.com"})

    respuesta = client.post(
        reverse("registros:registro"),
        {
            "nombre": "Nueva",
            "primer_apellido": "Persona",
            "telefono": "12345",
            "pais": "MX",
        },
    )

    assert "al menos 10 dígitos" in respuesta.content.decode()


# ── Código ────────────────────────────────────────────────────


def test_no_se_puede_entrar_al_codigo_sin_flujo(client):
    respuesta = client.get(reverse("registros:codigo"))

    assert respuesta["Location"] == reverse("registros:acceso")


def test_el_codigo_correcto_abre_la_sesion(client, participante, codigo_fijo):
    client.post(reverse("registros:acceso"), {"correo": participante.correo})

    respuesta = client.post(reverse("registros:codigo"), {"codigo": codigo_fijo})

    assert respuesta["Location"] == reverse("ferias:elegir")
    assert client.session["_auth_user_id"] == str(participante.pk)


def test_el_codigo_llega_repartido_en_seis_cajas(client, participante, codigo_fijo):
    """Así es como lo manda la pantalla, sin depender de JavaScript."""
    client.post(reverse("registros:acceso"), {"correo": participante.correo})

    respuesta = client.post(
        reverse("registros:codigo"), {"digito": list(codigo_fijo)}
    )

    assert respuesta["Location"] == reverse("ferias:elegir")


def test_un_codigo_equivocado_dice_cuantos_intentos_quedan(
    client, participante, codigo_fijo
):
    client.post(reverse("registros:acceso"), {"correo": participante.correo})

    respuesta = client.post(reverse("registros:codigo"), {"codigo": "000000"})

    assert respuesta.status_code == 200
    assert "Te quedan 2 intento" in respuesta.content.decode()
    assert "_auth_user_id" not in client.session


def test_al_agotar_los_intentos_se_pide_un_codigo_nuevo(client, participante, codigo_fijo):
    client.post(reverse("registros:acceso"), {"correo": participante.correo})

    for _ in range(3):
        respuesta = client.post(reverse("registros:codigo"), {"codigo": "000000"})

    assert "Se agotaron los intentos" in respuesta.content.decode()
    # La pantalla apaga el botón de verificar hasta pedir otro código.
    assert "requiereNuevo" in respuesta["HX-Trigger"]


def test_el_reenvio_respeta_el_cooldown(client, participante, codigo_fijo):
    client.post(reverse("registros:acceso"), {"correo": participante.correo})

    respuesta = client.post(reverse("registros:reenviar"))

    assert "Espera antes de solicitar" in respuesta.content.decode()
    assert len(mail.outbox) == 1  # no se mandó otro


def test_el_reenvio_manda_un_codigo_nuevo(client, participante, codigo_fijo, settings):
    settings.OTP_REENVIO_COOLDOWN_SEG = 0
    client.post(reverse("registros:acceso"), {"correo": participante.correo})

    respuesta = client.post(reverse("registros:reenviar"))

    assert "Código reenviado" in respuesta.content.decode()
    assert len(mail.outbox) == 2


# ── Después del login ─────────────────────────────────────────
#
# El destino ya no es de `REG`: se entrega la sesión y se manda a elegir
# feria. Lo que pasa a partir de ahí se prueba en
# `apps/ferias/pruebas/test_seleccion_feria.py`.


def test_elegir_feria_pide_sesion(client):
    respuesta = client.get(reverse("ferias:elegir"))

    assert respuesta["Location"] == reverse("registros:acceso")


def test_un_participante_no_entra_al_panel_administrativo(client, participante):
    client.force_login(participante)

    assert client.get(reverse("ferias:mis_ferias")).status_code == 403


def test_cerrar_sesion_vacia_la_sesion(client, participante):
    client.force_login(participante)

    respuesta = client.post(reverse("registros:salir"))

    assert respuesta["Location"] == reverse("registros:acceso")
    assert "_auth_user_id" not in client.session


def test_cerrar_sesion_no_se_puede_por_GET(client, participante):
    """Si fuera GET, bastaría una imagen apuntando ahí para sacar a alguien."""
    client.force_login(participante)

    assert client.get(reverse("registros:salir")).status_code == 405
    assert "_auth_user_id" in client.session


# ── El nombre en tres campos y el país (decisión 2026-08-25) ──


def test_el_segundo_apellido_se_puede_dejar_vacio(client, codigo_fijo):
    """CU-REG-001 E1: exigirlo dejaría fuera a casi todo participante extranjero."""
    client.post(reverse("registros:acceso"), {"correo": "jane@ejemplo.com"})

    respuesta = client.post(
        reverse("registros:registro"),
        {
            "nombre": "Jane",
            "primer_apellido": "Doe",
            "telefono": "9990005555",
            "pais": "US",
        },
    )

    assert respuesta["Location"] == reverse("registros:codigo")
    persona = Persona.objects.get(correo="jane@ejemplo.com")
    assert persona.segundo_apellido == ""
    assert persona.nombre_completo == "Jane Doe"
    assert persona.pais == "US"


def test_sin_primer_apellido_no_se_crea_la_cuenta(client, codigo_fijo):
    client.post(reverse("registros:acceso"), {"correo": "nueva@ejemplo.com"})

    respuesta = client.post(
        reverse("registros:registro"),
        {"nombre": "Nueva", "telefono": "9990006666", "pais": "MX"},
    )

    assert "Escribe tu primer apellido" in respuesta.content.decode()
    assert not Persona.objects.filter(correo="nueva@ejemplo.com").exists()


def test_un_pais_fuera_del_catalogo_no_se_guarda(client, codigo_fijo):
    """El valor no llega de un desplegable: llega de un POST fabricado."""
    client.post(reverse("registros:acceso"), {"correo": "nueva@ejemplo.com"})

    respuesta = client.post(
        reverse("registros:registro"),
        {
            "nombre": "Nueva",
            "primer_apellido": "Persona",
            "telefono": "9990007777",
            "pais": "Wakanda",
        },
    )

    assert respuesta.status_code == 200
    assert not Persona.objects.filter(correo="nueva@ejemplo.com").exists()


def test_el_formulario_de_registro_ofrece_el_desplegable_de_paises(client):
    """Sin JavaScript: un <select> nativo con el catálogo ya renderizado."""
    client.post(reverse("registros:acceso"), {"correo": "nueva@ejemplo.com"})

    html = client.get(reverse("registros:registro")).content.decode()

    assert 'name="pais"' in html
    assert '<option value="MX"' in html
    # México viene preseleccionado (PAIS_POR_DEFECTO). Se comprueba sobre
    # el HTML sin saltos ni sangría para no atarse a cómo esté formateada
    # la plantilla.
    compacto = " ".join(html.split())
    assert '<option value="MX" selected>México</option>' in compacto
    assert '<option value="ES" >España</option>' in compacto
