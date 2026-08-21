"""
Estado señuelo del acceso administrativo (anti-enumeración de admins).

El acceso admin no puede responder distinto según si el correo es o no
administrador: esa diferencia permite enumerar la lista de admins, que
es justo el blanco valioso para un atacante (phishing, fuerza bruta
dirigida). Este módulo produce, para los correos que **no** son
administradores, un comportamiento observable idéntico al del OTP real
de ``services/otp.py``:

- mismas respuestas de éxito y los mismos 429 de cool-down / tope,
- mismo conteo de intentos y mismos estados (incorrecto → agotado →
  invalidado, y expirado al vencer la vigencia),
- mismo costo de CPU (se calcula un hash PBKDF2 desechable, igual que
  al emitir o verificar un código real).

Diferencia esencial: **no se crea nada en la base ni se envía correo**.
El estado vive en caché y es desechable — no debe ensuciar los datos
reales ni dejar rastro de las cuentas que alguien anduvo probando.

Nota: con varios procesos de trabajo, cada uno ve su propia caché local
(``LocMemCache``). Para que el señuelo sea consistente en producción,
configurar una caché compartida (Redis/Memcached) en ``CACHES``.
"""

import hashlib
import time

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache

from .otp import (
    CooldownActivo,
    CuentaBloqueada,
    ResultadoVerificacion,
    _generar_codigo,
)

# Hash desechable contra el que se comparan los códigos del señuelo.
# Se calcula una vez al importar: da a ``check_password`` exactamente
# el mismo trabajo que en la verificación real (mismo algoritmo y
# número de iteraciones) sin depender de ningún dato de la BD.
_HASH_SEÑUELO = make_password(_generar_codigo())


def _clave(correo: str) -> str:
    """Clave de caché opaca: no guardar el correo en claro."""
    digest = hashlib.sha256(correo.encode()).hexdigest()[:32]
    return f"senuelo_admin:{digest}"


def _leer(correo: str) -> dict:
    return cache.get(_clave(correo)) or {
        "emisiones": [],   # timestamps de códigos "emitidos"
        "fallos": [],      # timestamps de intentos fallidos
        "intentos": 0,     # intentos contra el código vigente
        "quemado": False,  # el código vigente ya no sirve
    }


def _guardar(correo: str, estado: dict) -> None:
    # Vive lo que dura la ventana de conteo: pasado eso, el estado
    # real también habría caducado.
    ttl = max(settings.OTP_VENTANA_MINUTOS, settings.OTP_VIGENCIA_MINUTOS) * 60
    cache.set(_clave(correo), estado, ttl)


def _recientes(marcas: list, segundos: float) -> list:
    limite = time.time() - segundos
    return [t for t in marcas if t >= limite]


def emitir(correo: str) -> dict:
    """Espeja ``otp.emitir`` sin crear ni enviar nada.

    Lanza las mismas excepciones que la emisión real para que el
    cool-down y el tope por cuenta se vean idénticos desde fuera.
    """
    estado = _leer(correo)
    ahora = time.time()
    ventana_seg = settings.OTP_VENTANA_MINUTOS * 60

    # Cool-down entre emisiones (igual que el real).
    if estado["emisiones"]:
        transcurrido = ahora - estado["emisiones"][-1]
        if transcurrido < settings.OTP_REENVIO_COOLDOWN_SEG:
            raise CooldownActivo(
                int(settings.OTP_REENVIO_COOLDOWN_SEG - transcurrido) + 1
            )

    # Tope de emisiones por ventana (igual que el real).
    emisiones = _recientes(estado["emisiones"], ventana_seg)
    if len(emisiones) >= settings.OTP_EMISIONES_MAX_VENTANA:
        libera_en = emisiones[0] + ventana_seg
        raise CuentaBloqueada(max(int(libera_en - ahora) + 1, 0))

    # Mismo costo de CPU que hashear un código real.
    make_password(_generar_codigo())

    estado["emisiones"] = emisiones + [ahora]
    estado["intentos"] = 0
    estado["quemado"] = False
    _guardar(correo, estado)

    return {
        "vigencia_segundos": settings.OTP_VIGENCIA_MINUTOS * 60,
        "reenvio_cooldown_segundos": settings.OTP_REENVIO_COOLDOWN_SEG,
        "intentos_max": settings.OTP_INTENTOS_MAX,
    }


def verificar(correo: str, codigo: str) -> ResultadoVerificacion:
    """Espeja ``otp.verificar``. Ningún código puede acertar jamás."""
    estado = _leer(correo)
    ahora = time.time()
    ventana_seg = settings.OTP_VENTANA_MINUTOS * 60

    # Lockout por fallos acumulados (igual que el real).
    fallos = _recientes(estado["fallos"], ventana_seg)
    if len(fallos) >= settings.OTP_FALLOS_MAX_VENTANA:
        libera_en = fallos[-1] + settings.OTP_LOCKOUT_MINUTOS * 60
        estado["fallos"] = fallos
        _guardar(correo, estado)
        return ResultadoVerificacion(
            bloqueado=True, segundos_bloqueo=max(int(libera_en - ahora) + 1, 0)
        )

    # Sin código vigente / ya quemado → mismo 410 que el real.
    if not estado["emisiones"] or estado["quemado"]:
        return ResultadoVerificacion(invalidado=True)

    if ahora - estado["emisiones"][-1] >= settings.OTP_VIGENCIA_MINUTOS * 60:
        return ResultadoVerificacion(expirado=True)

    # Mismo costo de CPU que comparar un código real (siempre falla).
    check_password(codigo, _HASH_SEÑUELO)

    estado["intentos"] += 1
    estado["fallos"] = fallos + [ahora]
    if estado["intentos"] >= settings.OTP_INTENTOS_MAX:
        estado["quemado"] = True
    _guardar(correo, estado)

    return ResultadoVerificacion(
        incorrecto=True,
        intentos_restantes=max(settings.OTP_INTENTOS_MAX - estado["intentos"], 0),
    )
