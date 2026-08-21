"""
Sesión del sistema (CU-REG-002/003/004).

Reemplaza al par access/refresh token que emitía SimpleJWT. La sesión
ahora es la de Django: un identificador en una cookie ``HttpOnly`` que
JavaScript no puede leer, con los datos guardados del lado del servidor.
Eso quita del cliente el token que antes vivía en ``localStorage``
—accesible para cualquier XSS— y hace que cerrar sesión sea inmediato y
total, sin listas de revocación.

Este módulo guarda además el **flujo de acceso**: el correo y el
contexto con los que alguien está a medio entrar, entre la pantalla del
correo y la del código. Antes vivía en el ``sessionStorage`` del
navegador; ahora vive en la sesión del servidor, lo que cierra un hueco
real — el correo a verificar ya no lo elige el cliente en cada paso.
"""

from dataclasses import asdict, dataclass

from django.contrib.auth import login, logout
from django.utils import timezone

from ..models import Persona

# ModelBackend sigue siendo el backend de autenticación del proyecto
# (lo usa el admin de Django), pero aquí no se le pide que verifique
# nada: quien autentica es el OTP, ya validado por `services/otp.py`.
# `login()` exige saber con qué backend se autenticó, y este es.
BACKEND = "django.contrib.auth.backends.ModelBackend"

CLAVE_FLUJO = "flujo_acceso"

CONTEXTO_PUBLICO = "publico"
CONTEXTO_ADMIN = "admin"


@dataclass
class FlujoAcceso:
    """Estado de un acceso a medio camino (correo → código)."""

    correo: str
    contexto: str  # CONTEXTO_PUBLICO | CONTEXTO_ADMIN
    origen: str = "login"  # "login" | "registro" (cambia el texto de la pantalla)
    vigencia_segundos: int = 0
    cooldown_segundos: int = 0
    intentos_max: int = 0

    @property
    def es_admin(self) -> bool:
        return self.contexto == CONTEXTO_ADMIN


# ── Flujo de acceso ───────────────────────────────────────────


def guardar_flujo(peticion, flujo: FlujoAcceso) -> None:
    peticion.session[CLAVE_FLUJO] = asdict(flujo)


def leer_flujo(peticion, contexto: str) -> FlujoAcceso | None:
    """Flujo en curso para este contexto, o None si no hay.

    El contexto se comprueba aquí: un flujo iniciado en el acceso
    público no sirve para entrar por la pantalla administrativa.
    """
    crudo = peticion.session.get(CLAVE_FLUJO)
    if not crudo:
        return None
    try:
        flujo = FlujoAcceso(**crudo)
    except TypeError:
        # Sesión vieja con otra forma de dato: se descarta.
        return None
    return flujo if flujo.contexto == contexto else None


def limpiar_flujo(peticion) -> None:
    peticion.session.pop(CLAVE_FLUJO, None)


def actualizar_otp(peticion, meta: dict) -> None:
    """Refresca los contadores del flujo tras emitir un código nuevo."""
    crudo = peticion.session.get(CLAVE_FLUJO)
    if not crudo:
        return
    crudo["vigencia_segundos"] = meta["vigencia_segundos"]
    crudo["cooldown_segundos"] = meta["reenvio_cooldown_segundos"]
    crudo["intentos_max"] = meta["intentos_max"]
    peticion.session[CLAVE_FLUJO] = crudo


# ── Sesión autenticada ────────────────────────────────────────


def iniciar(peticion, persona: Persona) -> None:
    """Abre la sesión tras validar el OTP (paso 10-12).

    ``login()`` rota el identificador de sesión, así que el que tuviera
    el navegador antes de autenticarse deja de servir — la defensa
    estándar contra fijación de sesión.
    """
    login(peticion, persona, backend=BACKEND)

    # El flujo ya cumplió: dejarlo vivo permitiría reusar el paso
    # intermedio de un acceso que ya terminó.
    limpiar_flujo(peticion)

    persona.ultimo_acceso = timezone.now()
    persona.save(update_fields=["ultimo_acceso"])


def cerrar(peticion) -> None:
    """CU-REG-004: cierra la sesión y borra sus datos del servidor.

    ``logout()`` vacía la sesión en la base y manda al navegador una
    cookie caducada. A diferencia del JWT anterior, no queda nada que
    revocar ni ninguna credencial que siga siendo válida hasta expirar.
    """
    logout(peticion)
