"""
Reglas del OTP (CU-REG-002) — servicio, sin pasar por HTTP.

Son las reglas que sostienen la seguridad del acceso, así que se prueban
aquí, en el servicio, donde viven. Que se puedan probar sin levantar una
petición es la señal de que están en el lugar correcto.
"""

from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone

from apps.registros.models import SesionOTP
from apps.registros.services import otp as otp_service

pytestmark = pytest.mark.django_db


def test_emitir_guarda_el_codigo_hasheado_y_manda_correo(participante, codigo_fijo):
    otp_service.emitir(participante)

    sesion = participante.sesiones_otp.get()
    assert codigo_fijo not in sesion.codigo_hash  # nunca en claro
    assert sesion.codigo_coincide(codigo_fijo)
    assert len(mail.outbox) == 1
    assert codigo_fijo in mail.outbox[0].body


def test_el_codigo_correcto_abre_y_se_quema(participante, codigo_fijo):
    otp_service.emitir(participante)

    assert otp_service.verificar(participante, codigo_fijo).ok

    # Paso 9: un solo uso — el mismo código ya no sirve otra vez.
    assert otp_service.verificar(participante, codigo_fijo).invalidado


def test_tres_intentos_fallidos_invalidan_el_codigo(participante, codigo_fijo, settings):
    otp_service.emitir(participante)

    for restantes in (2, 1, 0):
        resultado = otp_service.verificar(participante, "000000")
        assert resultado.incorrecto
        assert resultado.intentos_restantes == restantes

    # E1: agotados los intentos, ni siquiera el código bueno entra.
    assert otp_service.verificar(participante, codigo_fijo).invalidado


def test_codigo_expirado_no_entra(participante, codigo_fijo, settings):
    otp_service.emitir(participante)

    sesion = participante.sesiones_otp.get()
    sesion.expira_en = timezone.now() - timedelta(seconds=1)
    sesion.save(update_fields=["expira_en"])

    assert otp_service.verificar(participante, codigo_fijo).expirado


def test_toda_emision_posterior_respeta_el_cooldown(participante, codigo_fijo):
    """A1: no solo el reenvío — también /solicitar.

    Sin esto, quien supiera el correo de un administrador podía
    regenerarle el código en bucle y dejarlo sin acceso (DoS de login),
    además de inundarlo de correos.
    """
    otp_service.emitir(participante)

    with pytest.raises(otp_service.CooldownActivo) as excepcion:
        otp_service.emitir(participante)

    assert 0 < excepcion.value.segundos_restantes <= 60


def test_emitir_invalida_los_codigos_anteriores(participante, codigo_fijo, settings):
    """A1/E5: solo el último código emitido sirve."""
    settings.OTP_REENVIO_COOLDOWN_SEG = 0
    otp_service.emitir(participante)
    primero = participante.sesiones_otp.first()

    otp_service.emitir(participante, es_reenvio=True)

    primero.refresh_from_db()
    assert primero.usado is True
    assert participante.sesiones_otp.filter(usado=False).count() == 1


def test_tope_de_emisiones_por_ventana(participante, codigo_fijo, settings):
    """Corta el mail bombing sostenido contra una misma cuenta."""
    settings.OTP_REENVIO_COOLDOWN_SEG = 0
    for _ in range(settings.OTP_EMISIONES_MAX_VENTANA):
        otp_service.emitir(participante)

    with pytest.raises(otp_service.CuentaBloqueada):
        otp_service.emitir(participante)


def test_lockout_tras_demasiados_fallos_en_la_ventana(participante, codigo_fijo, settings):
    """Frena la fuerza bruta repartida entre muchas IPs.

    El límite por IP no la ve; este contador va por cuenta destino, que
    es lo único que comparten todos los intentos contra una misma
    persona.
    """
    settings.OTP_REENVIO_COOLDOWN_SEG = 0
    settings.OTP_EMISIONES_MAX_VENTANA = 99

    fallos = 0
    while fallos < settings.OTP_FALLOS_MAX_VENTANA:
        otp_service.emitir(participante)  # cada código da 3 intentos
        for _ in range(settings.OTP_INTENTOS_MAX):
            if fallos >= settings.OTP_FALLOS_MAX_VENTANA:
                break
            otp_service.verificar(participante, "000000")
            fallos += 1

    otp_service.emitir(participante)
    resultado = otp_service.verificar(participante, codigo_fijo)

    assert resultado.bloqueado
    assert resultado.segundos_bloqueo > 0


def test_envio_fallido_anula_el_codigo(participante, codigo_fijo, monkeypatch):
    """E3: si el correo no sale, no puede quedar un OTP utilizable."""
    def revienta(*args, **kwargs):
        raise OSError("SMTP caído")

    monkeypatch.setattr(otp_service, "_enviar_correo", revienta)

    otp_service.emitir(participante)

    assert participante.sesiones_otp.get().usado is True
    assert otp_service.verificar(participante, codigo_fijo).invalidado


def test_sin_codigo_vigente_responde_invalidado(participante):
    assert otp_service.verificar(participante, "123456").invalidado


def test_el_codigo_tiene_seis_digitos():
    for _ in range(50):
        codigo = otp_service._generar_codigo()
        assert len(codigo) == 6 and codigo.isdigit()


def test_la_vigencia_sale_de_la_configuracion(participante, codigo_fijo, settings):
    antes = timezone.now()
    otp_service.emitir(participante)

    sesion = SesionOTP.objects.get()
    esperado = antes + timedelta(minutes=settings.OTP_VIGENCIA_MINUTOS)
    assert abs((sesion.expira_en - esperado).total_seconds()) < 5
