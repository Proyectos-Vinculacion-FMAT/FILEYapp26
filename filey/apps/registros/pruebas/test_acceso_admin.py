"""
Acceso administrativo (CU-REG-003) y anti-enumeración de administradores.

Saber **quién es administrador** es lo que un atacante quiere para
dirigir phishing o fuerza bruta. Por eso lo que más se prueba aquí no es
que un admin entre —eso es lo fácil— sino que las tres situaciones
(admin real, participante sin permisos, correo inexistente) sean
indistinguibles desde fuera.
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


def test_pedir_codigo_responde_igual_para_los_tres_casos(
    client, django_user_model, admin_general, participante, codigo_fijo
):
    """Admin real, participante sin permisos y correo inexistente.

    Si estas tres respuestas se distinguen en algo, el acceso admin se
    convierte en un oráculo: una petición por correo y se tiene la lista
    de administradores.
    """
    observadas = {
        correo: _respuesta_comparable(_entrar(client, correo))
        for correo in (admin_general.correo, participante.correo, DESCONOCIDO)
    }

    assert len(set(observadas.values())) == 1


def test_solo_al_administrador_real_le_llega_el_correo(
    client, admin_general, participante, codigo_fijo
):
    """La respuesta es la misma; lo que cambia es la bandeja de entrada."""
    _entrar(client, participante.correo)
    _entrar(client, DESCONOCIDO)

    assert mail.outbox == []

    _entrar(client, admin_general.correo)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [admin_general.correo]


def test_verificar_responde_igual_para_los_tres_casos(
    client, admin_general, participante, codigo_fijo
):
    def intento(correo):
        cliente = client.__class__()
        cliente.post(reverse("registros:admin_acceso"), {"correo": correo})
        return _respuesta_comparable(
            cliente.post(reverse("registros:admin_codigo"), {"codigo": "000000"})
        )

    observadas = {
        correo: intento(correo)
        for correo in (admin_general.correo, participante.correo, DESCONOCIDO)
    }

    assert len(set(observadas.values())) == 1


def test_un_correo_desconocido_nunca_acierta(client, codigo_fijo):
    """El señuelo cuenta intentos, pero ningún código puede entrar."""
    _entrar(client, DESCONOCIDO)

    respuesta = client.post(reverse("registros:admin_codigo"), {"codigo": codigo_fijo})

    assert respuesta.status_code == 200
    assert "_auth_user_id" not in client.session


def test_un_participante_no_entra_por_la_puerta_administrativa(
    client, participante, codigo_fijo
):
    """Tiene cuenta y su OTP real existe, pero no en este contexto.

    El código que se le emitió en el flujo público no debe servirle
    aquí: al no ser administrador, lo atiende el señuelo.
    """
    from apps.registros.services import otp as otp_service

    otp_service.emitir(participante)  # código real, del flujo público
    _entrar(client, participante.correo)

    respuesta = client.post(reverse("registros:admin_codigo"), {"codigo": codigo_fijo})

    assert "_auth_user_id" not in client.session
    assert respuesta.status_code == 200


@pytest.mark.con_pisos_reales
def test_los_pisos_de_tiempo_estan_configurados(settings):
    """El tiempo tampoco debe delatar quién es administrador.

    El resto de las pruebas los desactiva para no tardar; esta comprueba
    que en la configuración real siguen puestos y por encima de lo que
    tarda el camino largo (hashear el código y encolar el correo).
    """
    assert settings.ADMIN_PISO_IDENTIFICAR_SEG >= 0.3
    assert settings.ADMIN_PISO_OTP_SEG >= 1.5


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
