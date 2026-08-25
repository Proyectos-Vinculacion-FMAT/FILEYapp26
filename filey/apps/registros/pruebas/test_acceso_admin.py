"""
Acceso administrativo (CU-REG-003) y anti-enumeración de administradores.

Saber **quién es administrador** es lo que un atacante quiere para
dirigir phishing o fuerza bruta. Por eso lo que más se prueba aquí no es
que un admin entre —eso es lo fácil— sino **dónde** se comprueba el
permiso.

La regla que sostienen estas pruebas: el acceso administrativo puede
revelar si un correo **tiene cuenta** (es el mismo dato que ya revela el
acceso público, y evita dejar a alguien esperando un correo que no va a
llegar), pero **nunca** si esa cuenta administra. Para eso hay que
superar el OTP, es decir, hay que poder leer ese buzón.

Traducido a pruebas: un administrador y un participante —dos cuentas que
existen— tienen que ser indistinguibles al pedir el código. Se separan
después, y solo para quien acertó el código.
"""

import pytest
from django.core import mail
from django.urls import reverse

pytestmark = pytest.mark.django_db

DESCONOCIDO = "nadie@ejemplo.com"


def _entrar(client, correo):
    return client.post(reverse("registros:admin_acceso"), {"correo": correo})


# ── Camino feliz ──────────────────────────────────────────────


def test_un_administrador_entra_al_panel(client, admin_general, codigo_fijo):
    _entrar(client, admin_general.correo)

    respuesta = client.post(reverse("registros:admin_codigo"), {"codigo": codigo_fijo})

    assert respuesta["Location"] == reverse("registros:admin_modulos")
    assert client.session["_auth_user_id"] == str(admin_general.pk)


def test_el_panel_muestra_el_chip_de_administrador_general(client, admin_general):
    client.force_login(admin_general)

    cuerpo = client.get(reverse("registros:admin_modulos")).content.decode()

    assert "Administrador general" in cuerpo
    assert "Entrar al panel" in cuerpo


def test_el_admin_de_un_modulo_solo_ve_navegable_el_suyo(client, admin_evt):
    client.force_login(admin_evt)

    cuerpo = client.get(reverse("registros:admin_modulos")).content.decode()

    # Los demás módulos siguen visibles (decisión A2 del CU-REG-006),
    # pero sin botón para entrar.
    assert "Actividades FILEY (Eventos)" in cuerpo
    assert "Convocatoria de Stands" in cuerpo
    assert "Disponible en una próxima versión" in cuerpo
    assert "Administrador general" not in cuerpo


# ── Anti-enumeración ──────────────────────────────────────────


def _respuesta_comparable(respuesta):
    """Lo que un atacante puede observar: estado, cuerpo y destino."""
    return (
        respuesta.status_code,
        respuesta.content,
        respuesta.get("Location", ""),
    )


def test_admin_y_participante_responden_igual_al_pedir_codigo(
    client, admin_general, participante, codigo_fijo
):
    """La prueba que sostiene todo el diseño de CU-REG-003 A3.

    Dos cuentas que existen, una administradora y otra no. Si estas dos
    respuestas se distinguen en algo, esta pantalla vuelve a ser un
    oráculo: una petición por correo y se tiene la lista de
    administradores.
    """
    observadas = {
        correo: _respuesta_comparable(_entrar(client.__class__(), correo))
        for correo in (admin_general.correo, participante.correo)
    }

    assert len(set(observadas.values())) == 1


def test_a_las_dos_cuentas_les_llega_su_codigo(
    client, admin_general, participante, codigo_fijo
):
    """El participante también recibe código: es lo que iguala el camino.

    Cuesta un correo de más y compra que la pantalla no distinga a un
    administrador. La separación ocurre después, al validar el código.
    """
    _entrar(client.__class__(), participante.correo)
    _entrar(client.__class__(), admin_general.correo)

    destinatarios = {m.to[0] for m in mail.outbox}
    assert destinatarios == {participante.correo, admin_general.correo}


def test_un_correo_sin_cuenta_recibe_correo_incorrecto(client, codigo_fijo):
    """A3: la cuenta no existe → se dice, y no se avanza.

    Es el dato que esta pantalla sí revela, a propósito: el mismo que ya
    revela el acceso público al bifurcar entre entrar y registrarse.
    """
    respuesta = _entrar(client, DESCONOCIDO)

    assert respuesta.status_code == 200
    assert "Correo incorrecto" in respuesta.content.decode()
    assert mail.outbox == []


def test_un_correo_sin_cuenta_no_llega_a_la_pantalla_de_codigo(client):
    """Sin cuenta no se guarda flujo, así que la pantalla del código rebota."""
    _entrar(client, DESCONOCIDO)

    respuesta = client.get(reverse("registros:admin_codigo"))

    assert respuesta["Location"] == reverse("registros:admin_acceso")


def test_un_participante_no_entra_por_la_puerta_administrativa(
    client, participante, codigo_fijo
):
    """E3: código correcto, pero la cuenta no administra nada.

    Recibe su código y lo acierta —es su cuenta—, pero no obtiene sesión
    administrativa: se le manda al portal que sí le corresponde, con una
    explicación. Decírselo aquí no revela nada, porque ya demostró ser
    dueño del buzón.
    """
    _entrar(client, participante.correo)

    respuesta = client.post(reverse("registros:admin_codigo"), {"codigo": codigo_fijo})

    assert "_auth_user_id" not in client.session
    assert respuesta["Location"] == reverse("registros:acceso")


def test_el_rechazo_llega_igual_por_htmx(client, participante, codigo_fijo):
    """La pantalla real manda el código por htmx, que no sigue un 302."""
    _entrar(client, participante.correo)

    respuesta = client.post(
        reverse("registros:admin_codigo"),
        {"codigo": codigo_fijo},
        headers={"hx-request": "true"},
    )

    assert "_auth_user_id" not in client.session
    assert respuesta["HX-Redirect"] == reverse("registros:acceso")


def test_el_codigo_del_participante_queda_quemado_tras_el_rechazo(
    client, participante, codigo_fijo
):
    """El código se gastó al validarlo, aunque no abriera sesión."""
    _entrar(client, participante.correo)
    client.post(reverse("registros:admin_codigo"), {"codigo": codigo_fijo})

    assert participante.sesiones_otp.get().usado is True


# ── Protección de las pantallas ───────────────────────────────


def test_el_panel_pide_sesion(client):
    respuesta = client.get(reverse("registros:admin_modulos"))

    assert respuesta["Location"] == reverse("registros:admin_acceso")


def test_no_se_llega_al_codigo_admin_sin_flujo(client):
    respuesta = client.get(reverse("registros:admin_codigo"))

    assert respuesta["Location"] == reverse("registros:admin_acceso")


def test_el_flujo_publico_no_sirve_para_el_codigo_admin(
    client, participante, codigo_fijo
):
    """Cruzar los contextos no debe abrir una puerta.

    El flujo se inicia en el acceso público y se intenta terminar en la
    pantalla administrativa.
    """
    client.post(reverse("registros:acceso"), {"correo": participante.correo})

    respuesta = client.get(reverse("registros:admin_codigo"))

    assert respuesta["Location"] == reverse("registros:admin_acceso")


def test_cerrar_sesion_del_admin_regresa_a_su_acceso(client, admin_general):
    client.force_login(admin_general)

    respuesta = client.post(reverse("registros:salir"))

    assert respuesta["Location"] == reverse("registros:admin_acceso")
    assert "_auth_user_id" not in client.session
