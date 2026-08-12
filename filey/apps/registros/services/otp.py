"""
Servicio de OTP por correo (CU-REG-002 / CU-REG-003).

Generación con ``secrets`` (CSPRNG de la stdlib) y almacenamiento
hasheado con el hasher de contraseñas de Django — el patrón
estándar del sector para códigos de un solo uso por correo.

Defensas contra abuso (además del throttling por IP de DRF), todas
por **cuenta destino**, no por IP, para resistir el abuso distribuido:

- Cool-down entre emisiones (A1): frena el mail bombing y el brute
  force, e impide el DoS de login (regenerar el código de otra
  persona en bucle para que el suyo nunca sirva).
- Tope de emisiones por ventana: corta el mail bombing sostenido.
- Lockout de verificación tras demasiados fallos en la ventana:
  frena el brute force distribuido desde muchas IPs.
- Verificación bajo bloqueo de fila (``select_for_update``): cierra
  la carrera que permitía gastar más intentos de los debidos sobre
  un mismo código.
"""

import logging
import secrets
import threading
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import connections, transaction
from django.utils import timezone

from ..models import Persona, SesionOTP

logger = logging.getLogger(__name__)


class CooldownActivo(Exception):
    """Se pidió un código antes de cumplirse el cool-down (A1: 60 s)."""

    def __init__(self, segundos_restantes: int):
        self.segundos_restantes = segundos_restantes
        super().__init__(f"Reenvío disponible en {segundos_restantes} s")


class CuentaBloqueada(Exception):
    """Demasiadas emisiones o fallos recientes para esta cuenta."""

    def __init__(self, segundos_restantes: int):
        self.segundos_restantes = segundos_restantes
        super().__init__(f"Cuenta bloqueada por {segundos_restantes} s")


class EnvioCorreoFallido(Exception):
    """El proveedor de correo devolvió error (E3)."""


@dataclass
class ResultadoVerificacion:
    """Salida de ``verificar``; exactamente uno de los estados es True."""

    ok: bool = False
    expirado: bool = False
    invalidado: bool = False       # sin OTP vigente (usado/agotado/reenviado)
    incorrecto: bool = False
    bloqueado: bool = False        # lockout por fallos en la ventana
    intentos_restantes: int = 0
    segundos_bloqueo: int = 0


def _generar_codigo() -> str:
    """Código de 6 dígitos aleatorios (paso 3 del flujo principal)."""
    return f"{secrets.randbelow(1_000_000):06d}"


def _ventana_inicio():
    return timezone.now() - timedelta(minutes=settings.OTP_VENTANA_MINUTOS)


def _segundos_para_reenvio(persona: Persona) -> int:
    """Segundos que faltan para poder emitir otro código; 0 si ya se puede."""
    ultimo = persona.sesiones_otp.order_by("-creado_en").first()
    if ultimo is None:
        return 0
    disponible_en = ultimo.creado_en + timedelta(
        seconds=settings.OTP_REENVIO_COOLDOWN_SEG
    )
    restante = (disponible_en - timezone.now()).total_seconds()
    return max(int(restante) + 1, 0) if restante > 0 else 0


def _bloqueo_por_emisiones(persona: Persona) -> int:
    """Segundos de bloqueo si se superó el tope de emisiones por ventana.

    Cuenta los códigos emitidos en la ventana móvil. Al llegar al
    tope, la cuenta espera hasta que el más antiguo salga de la
    ventana; 0 si aún hay margen.
    """
    ventana = _ventana_inicio()
    recientes = list(
        persona.sesiones_otp.filter(creado_en__gte=ventana)
        .order_by("creado_en")
        .values_list("creado_en", flat=True)
    )
    if len(recientes) < settings.OTP_EMISIONES_MAX_VENTANA:
        return 0
    libera_en = recientes[0] + timedelta(minutes=settings.OTP_VENTANA_MINUTOS)
    restante = (libera_en - timezone.now()).total_seconds()
    return max(int(restante) + 1, 0)


def _bloqueo_por_fallos(persona: Persona) -> int:
    """Segundos de lockout si se acumularon demasiados fallos en la ventana.

    Suma los intentos fallidos de todos los códigos emitidos en la
    ventana. Los de un código que se acertó no cuentan: entrar bien
    limpia el historial. 0 si aún hay margen.
    """
    ventana = _ventana_inicio()
    sesiones = persona.sesiones_otp.filter(creado_en__gte=ventana)
    total_fallos = sum(s.intentos for s in sesiones if not s.acertado)
    if total_fallos < settings.OTP_FALLOS_MAX_VENTANA:
        return 0
    ultima = sesiones.order_by("-creado_en").first()
    libera_en = ultima.creado_en + timedelta(
        minutes=settings.OTP_LOCKOUT_MINUTOS
    )
    restante = (libera_en - timezone.now()).total_seconds()
    return max(int(restante) + 1, 0)


def emitir(persona: Persona, *, es_reenvio: bool = False) -> dict:
    """Genera, guarda (hasheado) y despacha un OTP nuevo.

    Toda emisión (primera, solicitud o reenvío) respeta el cool-down
    frente a la anterior y el tope de emisiones por ventana. Solo la
    primerísima emisión de la cuenta pasa sin cool-down. Cada emisión
    invalida los códigos anteriores (A1/E5).

    El **envío del correo ocurre en segundo plano**: hablar con el SMTP
    tarda segundos y de forma muy variable, y esa latencia dentro de la
    respuesta delataba quién es administrador (el señuelo del acceso
    admin no envía nada y contestaba mucho antes). Ver E3 más abajo.
    """
    codigo = _generar_codigo()

    # El PBKDF2 se calcula ANTES de tomar el bloqueo: es lo más caro
    # del proceso y no necesita la cuenta bloqueada.
    sesion = SesionOTP(
        persona=persona,
        canal=SesionOTP.Canal.CORREO,
        expira_en=timezone.now()
        + timedelta(minutes=settings.OTP_VIGENCIA_MINUTOS),
    )
    sesion.establecer_codigo(codigo)

    # Comprobar los límites y reservar la emisión de forma atómica, con
    # la cuenta bloqueada: si no, dos peticiones simultáneas pasan las
    # dos el cool-down y se emiten (y envían) dos códigos a la vez.
    with transaction.atomic():
        Persona.objects.select_for_update().filter(pk=persona.pk).first()

        # Cool-down: se aplica a CUALQUIER emisión posterior a la
        # primera, no solo al reenvío. Sin esto, /otp/solicitar
        # regenera códigos sin límite (mail bombing) y permite el DoS
        # de login.
        restante = _segundos_para_reenvio(persona)
        if restante > 0:
            raise CooldownActivo(restante)

        bloqueo = _bloqueo_por_emisiones(persona)
        if bloqueo > 0:
            raise CuentaBloqueada(bloqueo)

        # Invalidar los anteriores y guardar el nuevo (paso 4).
        persona.sesiones_otp.filter(usado=False).update(usado=True)
        sesion.save()

    _despachar_correo(persona.correo, persona.nombre_completo, codigo, sesion.pk)

    return {
        "vigencia_segundos": settings.OTP_VIGENCIA_MINUTOS * 60,
        "reenvio_cooldown_segundos": settings.OTP_REENVIO_COOLDOWN_SEG,
        "intentos_max": settings.OTP_INTENTOS_MAX,
    }


def _despachar_correo(correo: str, nombre: str, codigo: str, sesion_id: int):
    """Envía el OTP fuera de la respuesta HTTP (ver ``emitir``)."""
    hilo = threading.Thread(
        target=_tarea_envio,
        args=(correo, nombre, codigo, sesion_id),
        daemon=True,
        name=f"envio-otp-{sesion_id}",
    )
    hilo.start()


def _tarea_envio(correo: str, nombre: str, codigo: str, sesion_id: int):
    """Envío en segundo plano. Mantiene la garantía E3.

    E3 dice que un envío fallido no debe dejar un OTP utilizable: si el
    correo no sale, el código recién guardado se marca como usado. La
    diferencia con la versión síncrona es que la persona ya no ve un
    502 inmediato — ve la pantalla de código y, al no llegarle nada,
    usa "Enviar nuevo código".
    """
    try:
        _enviar_correo(correo, nombre, codigo)
        logger.info("OTP enviado a %s vía %s", correo, settings.EMAIL_BACKEND)
    except Exception:  # noqa: BLE001 — cualquier fallo del proveedor
        # El motivo real (credenciales, remitente rechazado, timeout)
        # solo existe aquí: sin este log el fallo es invisible.
        logger.exception("OTP no enviado a %s — el código queda anulado", correo)
        SesionOTP.objects.filter(pk=sesion_id).update(usado=True)
    finally:
        # Cada hilo abre su propia conexión: cerrarla o se acumulan.
        connections.close_all()


def verificar(persona: Persona, codigo: str) -> ResultadoVerificacion:
    """Valida el código contra el último OTP emitido (paso 8).

    Todo el bloque corre en una transacción con la fila del OTP
    bloqueada (``select_for_update``): dos peticiones simultáneas se
    serializan, así que el conteo de intentos no se puede burlar con
    concurrencia. Antes de tocar el código se comprueba el lockout de
    la cuenta (brute force distribuido).

    Orden de verificación: lockout → existencia → expiración →
    coincidencia, contando intentos y quemando el código en éxito
    (paso 9) o al agotar los 3 intentos (E1).
    """
    bloqueo = _bloqueo_por_fallos(persona)
    if bloqueo > 0:
        return ResultadoVerificacion(bloqueado=True, segundos_bloqueo=bloqueo)

    with transaction.atomic():
        sesion = (
            persona.sesiones_otp.select_for_update()
            .filter(usado=False)
            .order_by("-creado_en")
            .first()
        )
        if sesion is None:
            return ResultadoVerificacion(invalidado=True)

        if sesion.expirado:
            return ResultadoVerificacion(expirado=True)

        sesion.intentos += 1

        if sesion.codigo_coincide(codigo):
            sesion.usado = True  # quemado al validar
            sesion.acertado = True  # limpia el historial de fallos
            sesion.save(update_fields=["usado", "acertado", "intentos"])
            return ResultadoVerificacion(ok=True)

        agotado = sesion.intentos >= settings.OTP_INTENTOS_MAX
        if agotado:
            sesion.usado = True  # E1 paso 4: al agotar intentos queda invalidado
        sesion.save(update_fields=["usado", "intentos"])
        return ResultadoVerificacion(
            incorrecto=True,
            intentos_restantes=sesion.intentos_restantes,
        )


def _enviar_correo(correo: str, nombre: str, codigo: str):
    minutos = settings.OTP_VIGENCIA_MINUTOS
    saludo = f"Hola {nombre}," if nombre else "Hola,"
    send_mail(
        subject=f"{codigo} es tu código de acceso a FILEY",
        message=(
            f"{saludo}\n\n"
            f"Tu código de acceso de un solo uso es: {codigo}\n\n"
            f"Vence en {minutos} minutos. Si tú no lo solicitaste, "
            "ignora este correo.\n\n"
            "FILEY — Feria Internacional de la Lectura Yucatán\n"
            "Coordinación General de Contenidos · UADY"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[correo],
        fail_silently=False,
    )
