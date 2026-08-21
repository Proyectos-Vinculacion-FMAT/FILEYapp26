"""
El señuelo del acceso administrativo (anti-enumeración de admins).

Lo que hay que comprobar no es que "funcione", sino que sea
**indistinguible** del OTP real: mismos estados, mismos límites, mismo
conteo de intentos. Cualquier diferencia observable vuelve a convertir
el acceso admin en un oráculo para averiguar quién es administrador.
"""

import pytest

from apps.registros.services import otp as otp_service
from apps.registros.services import senuelo as senuelo_service

pytestmark = pytest.mark.django_db

CORREO_CUALQUIERA = "desconocido@ejemplo.com"


def test_no_toca_la_base_ni_manda_correo(participante):
    """El señuelo no debe dejar rastro de las cuentas que alguien probó."""
    from django.core import mail

    from apps.registros.models import SesionOTP

    senuelo_service.emitir(CORREO_CUALQUIERA)
    senuelo_service.verificar(CORREO_CUALQUIERA, "123456")

    assert SesionOTP.objects.count() == 0
    assert mail.outbox == []


def test_devuelve_los_mismos_metadatos_que_el_real(participante, codigo_fijo):
    real = otp_service.emitir(participante)
    falso = senuelo_service.emitir(CORREO_CUALQUIERA)

    assert real == falso


def test_ningun_codigo_acierta_jamas():
    senuelo_service.emitir(CORREO_CUALQUIERA)

    for codigo in ("000000", "123456", "999999"):
        assert senuelo_service.verificar(CORREO_CUALQUIERA, codigo).ok is False


def test_cuenta_los_intentos_igual_que_el_real(settings):
    senuelo_service.emitir(CORREO_CUALQUIERA)

    for restantes in (2, 1, 0):
        resultado = senuelo_service.verificar(CORREO_CUALQUIERA, "000000")
        assert resultado.incorrecto
        assert resultado.intentos_restantes == restantes

    # Agotado: mismo estado "ya no vale" que da el real.
    assert senuelo_service.verificar(CORREO_CUALQUIERA, "000000").invalidado


def test_aplica_el_mismo_cooldown_entre_emisiones():
    senuelo_service.emitir(CORREO_CUALQUIERA)

    with pytest.raises(otp_service.CooldownActivo):
        senuelo_service.emitir(CORREO_CUALQUIERA)


def test_aplica_el_mismo_tope_de_emisiones(settings):
    settings.OTP_REENVIO_COOLDOWN_SEG = 0

    for _ in range(settings.OTP_EMISIONES_MAX_VENTANA):
        senuelo_service.emitir(CORREO_CUALQUIERA)

    with pytest.raises(otp_service.CuentaBloqueada):
        senuelo_service.emitir(CORREO_CUALQUIERA)


def test_bloquea_tras_los_mismos_fallos_acumulados(settings):
    settings.OTP_REENVIO_COOLDOWN_SEG = 0
    settings.OTP_EMISIONES_MAX_VENTANA = 99

    fallos = 0
    while fallos < settings.OTP_FALLOS_MAX_VENTANA:
        senuelo_service.emitir(CORREO_CUALQUIERA)
        for _ in range(settings.OTP_INTENTOS_MAX):
            if fallos >= settings.OTP_FALLOS_MAX_VENTANA:
                break
            senuelo_service.verificar(CORREO_CUALQUIERA, "000000")
            fallos += 1

    senuelo_service.emitir(CORREO_CUALQUIERA)
    assert senuelo_service.verificar(CORREO_CUALQUIERA, "000000").bloqueado


def test_sin_emision_previa_responde_invalidado():
    """Mismo estado que da el real cuando no hay código vigente."""
    assert senuelo_service.verificar("nadie@ejemplo.com", "123456").invalidado


def test_el_correo_no_se_guarda_en_claro_en_la_cache():
    """La caché no debe delatar qué correos anduvo probando alguien."""
    senuelo_service.emitir(CORREO_CUALQUIERA)

    assert CORREO_CUALQUIERA not in senuelo_service._clave(CORREO_CUALQUIERA)
