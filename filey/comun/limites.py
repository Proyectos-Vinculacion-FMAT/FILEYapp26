"""
Límite de peticiones por IP.

Sustituye al ``ScopedRateThrottle`` de DRF, que se retiró junto con la
API REST (ADR-0002). Sin este archivo, la migración habría dejado los
endpoints de acceso sin ninguna defensa por IP: es la capa que frena el
abuso y la enumeración de correos desde un mismo origen.

Es **una de dos capas** y la más débil a propósito: un atacante con
muchas IPs la esquiva. La que resiste el abuso distribuido es la de
límites **por cuenta destino** en ``apps/registros/services/otp.py``
(cool-down, tope de emisiones, lockout). Esta capa está para el caso
común: un script desde una sola máquina.

Ventana fija sobre la caché: se cuenta cuántas peticiones lleva la IP en
el minuto/hora en curso y se rechaza al pasarse. Es el mismo algoritmo
que usaba DRF, con su misma limitación conocida — en el filo entre dos
ventanas caben hasta el doble de peticiones. Aceptable: lo que se quiere
frenar es el bucle sostenido, no la ráfaga de dos segundos.

Nota: con ``LocMemCache`` cada proceso lleva su propia cuenta, así que
el límite real se multiplica por el número de workers. En producción hay
que configurar una caché compartida (Redis/Memcached) en ``CACHES``.
"""

import functools
import time

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse

DURACIONES = {"s": 1, "m": 60, "h": 3600, "d": 86400}


class LimiteExcedido(Exception):
    """La IP superó su cuota para este ámbito."""

    def __init__(self, segundos_restantes: int):
        self.segundos_restantes = segundos_restantes
        super().__init__(f"Límite excedido; reintentar en {segundos_restantes} s")


def _leer_tasa(ambito: str) -> tuple[int, int]:
    """Traduce "20/min" a (20 peticiones, 60 segundos)."""
    tasa = settings.LIMITES_PETICIONES[ambito]
    veces, _, periodo = tasa.partition("/")
    return int(veces), DURACIONES[periodo[0]]


def ip_del_cliente(peticion) -> str:
    """IP de origen, respetando el proxy que termina TLS en producción.

    ``X-Forwarded-For`` lo pone el proxy y lo puede falsificar quien
    llegue directo a Django; se usa igual porque detrás del proxy es el
    único dato real, y porque falsificarlo solo permite saltarse **esta**
    capa, no los límites por cuenta destino.
    """
    reenviada = peticion.META.get("HTTP_X_FORWARDED_FOR", "")
    if reenviada:
        return reenviada.split(",")[0].strip()
    return peticion.META.get("REMOTE_ADDR", "desconocida")


def consumir(peticion, ambito: str) -> None:
    """Registra una petición de esta IP en el ámbito; lanza si se pasó."""
    veces_max, periodo = _leer_tasa(ambito)
    ahora = int(time.time())
    ventana = ahora // periodo
    clave = f"limite:{ambito}:{ip_del_cliente(peticion)}:{ventana}"

    # `add` + `incr` en vez de get/set: `incr` es atómica en los backends
    # reales (Redis/Memcached), así que dos peticiones simultáneas no se
    # pisan el contador.
    cache.add(clave, 0, periodo)
    try:
        usadas = cache.incr(clave)
    except ValueError:
        # La clave expiró entre el `add` y el `incr`: cuenta como la
        # primera petición de la ventana nueva.
        cache.set(clave, 1, periodo)
        usadas = 1

    if usadas > veces_max:
        siguiente_ventana = (ventana + 1) * periodo
        raise LimiteExcedido(max(siguiente_ventana - ahora, 1))


def limitar(ambito: str):
    """Decorador de vista: aplica el límite del ámbito antes de entrar.

    Al excederse devuelve **429 con cuerpo vacío**, igual para cualquier
    correo: el limitador no puede convertirse en un oráculo que revele
    si una cuenta existe.
    """

    def decorador(vista):
        @functools.wraps(vista)
        def envoltura(peticion, *args, **kwargs):
            # Los GET solo pintan la pantalla: no emiten códigos ni
            # consultan si un correo existe, así que no consumen cuota
            # (si no, recargar la página gastaría los intentos).
            if peticion.method in ("GET", "HEAD", "OPTIONS"):
                return vista(peticion, *args, **kwargs)
            try:
                consumir(peticion, ambito)
            except LimiteExcedido as exc:
                respuesta = HttpResponse(status=429)
                respuesta["Retry-After"] = str(exc.segundos_restantes)
                return respuesta
            return vista(peticion, *args, **kwargs)

        return envoltura

    return decorador
