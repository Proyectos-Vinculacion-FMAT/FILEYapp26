"""
Pantallas del Core Registros (REG).

Mapa pantalla → caso de uso:

- /acceso                → CU-REG-001/002 (paso 1-2: correo y bifurcación)
- /acceso/registro       → CU-REG-001 (crear Persona + dispara OTP)
- /acceso/codigo         → CU-REG-002 (verificar y abrir sesión)
- /admin/acceso          → CU-REG-003 (paso 1-3: correo administrativo)
- /admin/acceso/codigo   → CU-REG-003 (verificar y abrir sesión admin)
- /salir                 → CU-REG-004 (cerrar sesión)

`REG` termina en el momento en que hay sesión. Lo que se ve después ya
no es suyo: elegir feria es de `FER` (`apps/ferias/views.py`, CU-FER-002
y CU-FER-010) y las convocatorias son de la feria elegida
(`apps/convocatorias/`, CU-FER-006). CU-REG-005 y CU-REG-006 quedaron
reemplazados por esos: el acceso se otorga por feria (ADR-0004) y el
catálogo cuelga de una edición, no del sistema.

Estas vistas son **delgadas**: validan el formulario, llaman al servicio
y traducen el resultado a una página o a un fragmento. Toda regla de
negocio —cool-down, topes, lockout— vive en `services/`, donde se puede
probar y llamar sin pasar por HTTP.

Cada pantalla funciona **sin JavaScript**: HTMX evita la recarga, pero
si no carga, el mismo POST devuelve la página completa.
"""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from comun.htmx import disparar, es_htmx, redirigir, reintentar_en
from comun.limites import limitar

from .forms import CodigoForm, IdentificarForm, RegistroForm
from .models import Persona
from .services import otp as otp_service
from .services import sesion as sesion_service
from .services.sesion import CONTEXTO_ADMIN, CONTEXTO_PUBLICO, FlujoAcceso

MENSAJE_GENERICO = (
    "No pudimos procesar tu solicitud. Intenta de nuevo en unos minutos."
)


# ── Ayudas compartidas ────────────────────────────────────────


def _persona_por_correo(correo: str):
    return Persona.objects.filter(correo=correo, estado=Persona.Estado.ACTIVA).first()


def _es_admin(persona) -> bool:
    """True solo si la cuenta existe, está activa y administra alguna feria."""
    return persona is not None and persona.es_administrativa


def _emitir(persona):
    """Emite un OTP y traduce sus errores a algo que la pantalla entiende.

    Devuelve ``(meta, mensaje_error, segundos_espera)``.
    """
    try:
        meta = otp_service.emitir(persona)
    except otp_service.CooldownActivo as exc:
        return None, "Espera antes de solicitar un nuevo código.", exc.segundos_restantes
    except otp_service.CuentaBloqueada as exc:
        # Tope de emisiones por cuenta (mail bombing sostenido). Mismo
        # mensaje que el cool-down para no revelar cuál de los dos
        # límites se tocó (ni, por tanto, si el correo existe).
        return (
            None,
            "Demasiadas solicitudes para esta cuenta. Intenta de nuevo más tarde.",
            exc.segundos_restantes,
        )
    except otp_service.EnvioCorreoFallido:
        # E3: el correo no pudo enviarse; no queda OTP utilizable.
        # Desde que el envío pasó a segundo plano, este camino ya no se
        # alcanza en la práctica: el fallo se maneja dentro del hilo, que
        # anula el código. Se conserva por si vuelve a haber envío
        # síncrono.
        return (
            None,
            "No pudimos enviar el correo. Intenta de nuevo en unos minutos.",
            0,
        )
    return meta, None, 0


def _mensaje_de_verificacion(resultado) -> tuple[str, bool]:
    """Traduce un resultado fallido a ``(texto, requiere_codigo_nuevo)``.

    Compartido por el acceso público y el administrativo: los dos dicen
    exactamente lo mismo ante el mismo error.
    """
    if resultado.bloqueado:
        # Lockout por fallos acumulados en la ventana (fuerza bruta
        # distribuida).
        return (
            "Demasiados intentos fallidos. "
            "Espera unos minutos antes de volver a intentar.",
            True,
        )
    if resultado.expirado:
        return "El código expiró. Solicita uno nuevo.", True
    if resultado.invalidado:
        return "Ese código ya no es válido. Solicita uno nuevo.", True
    if resultado.intentos_restantes == 0:
        # E1: al agotar los intentos se fuerza un código nuevo.
        return "Se agotaron los intentos. Solicita un código nuevo.", True
    return (
        "Código incorrecto, inténtalo de nuevo. "
        f"Te quedan {resultado.intentos_restantes} intento(s).",
        False,
    )


def _pantalla_acceso(peticion, contexto: str, formulario):
    """Renderiza la pantalla del correo (o solo su tarjeta, si es HTMX)."""
    plantilla = (
        "registros/parciales/respuesta_acceso.html"
        if es_htmx(peticion)
        else "registros/acceso.html"
    )
    return render(
        peticion,
        plantilla,
        {"form": formulario, "es_admin": contexto == CONTEXTO_ADMIN},
    )


def _estado_otp(peticion, texto: str, *, error: bool = True):
    """Fragmento con el renglón de estado bajo las cajas del código."""
    return render(
        peticion,
        "registros/parciales/estado_otp.html",
        {"estado": texto, "estado_error": error},
    )


def _codigo_enviado(peticion) -> dict:
    """Junta las seis cajas del formulario en un solo código.

    La pantalla manda seis campos ``digito`` en vez de uno, para que
    escribir el código no dependa de que JavaScript los una. Se acepta
    también un campo ``codigo`` ya armado, que es como lo mandan las
    pruebas y cualquier cliente que no use la pantalla.
    """
    digitos = "".join(peticion.POST.getlist("digito"))
    return {"codigo": digitos or peticion.POST.get("codigo", "")}


# ── Portada ───────────────────────────────────────────────────


def raiz(peticion):
    """La raíz del sitio es el acceso del participante."""
    return redirect("registros:acceso")


# ── Acceso del participante (CU-REG-001 / 002) ────────────────


@require_http_methods(["GET", "POST"])
@limitar("auth-identificar")
def acceso(peticion):
    """Paso 1-2: se pide el correo y se bifurca según exista o no.

    La bifurcación nueva/existente es la UX aprobada del prototipo REG
    (CU-REG-001) y se mantiene a propósito: el riesgo de enumeración de
    correos aquí es asumido. Es el mismo dato —y solo ese— que revela el
    acceso administrativo; lo que ninguno de los dos revela es quién
    administra (ver `admin_acceso`).
    """
    if peticion.method == "GET":
        return render(
            peticion,
            "registros/acceso.html",
            {"form": IdentificarForm(), "contexto": CONTEXTO_PUBLICO, "es_admin": False},
        )

    formulario = IdentificarForm(peticion.POST)
    if not formulario.is_valid():
        return _pantalla_acceso(peticion, CONTEXTO_PUBLICO, formulario)

    correo = formulario.cleaned_data["correo"]
    persona = _persona_por_correo(correo)

    if persona is None:
        # CU-REG-001: correo no reconocido → crear cuenta.
        sesion_service.guardar_flujo(
            peticion,
            FlujoAcceso(correo=correo, contexto=CONTEXTO_PUBLICO, origen="registro"),
        )
        return redirigir(peticion, "registros:registro")

    meta, error, espera = _emitir(persona)
    if error:
        messages.error(peticion, error)
        respuesta = _pantalla_acceso(peticion, CONTEXTO_PUBLICO, formulario)
        return reintentar_en(respuesta, espera) if espera else respuesta

    sesion_service.guardar_flujo(
        peticion,
        FlujoAcceso(
            correo=correo,
            contexto=CONTEXTO_PUBLICO,
            origen="login",
            vigencia_segundos=meta["vigencia_segundos"],
            cooldown_segundos=meta["reenvio_cooldown_segundos"],
            intentos_max=meta["intentos_max"],
        ),
    )
    return redirigir(peticion, "registros:codigo")


@require_http_methods(["GET", "POST"])
@limitar("auth-otp")
def registro(peticion):
    """CU-REG-001: crea la Persona y continúa en CU-REG-002 (envío de OTP).

    El correo sale del flujo guardado en la sesión, no del formulario:
    quien llegue aquí sin haber pasado por la pantalla de acceso no
    tiene nada que registrar.
    """
    flujo = sesion_service.leer_flujo(peticion, CONTEXTO_PUBLICO)
    if flujo is None:
        return redirect("registros:acceso")

    contexto_plantilla = {"correo": flujo.correo}

    if peticion.method == "GET":
        return render(
            peticion,
            "registros/registro.html",
            {"form": RegistroForm(), **contexto_plantilla},
        )

    formulario = RegistroForm(peticion.POST)
    if not formulario.is_valid():
        return _render_registro(peticion, formulario, contexto_plantilla)

    datos = formulario.cleaned_data

    # A1: el correo ya tenía cuenta (p. ej. dos pestañas abiertas) →
    # no es un error para la persona, se le manda su código y sigue.
    if Persona.objects.filter(correo=flujo.correo).exists():
        return _continuar_con_cuenta_existente(peticion, flujo)

    # E2: teléfono ya asociado a otra cuenta con correo distinto.
    if Persona.objects.filter(telefono=datos["telefono"]).exists():
        formulario.add_error(
            "telefono",
            "Ese teléfono ya está registrado con otro correo. "
            "Usa otro teléfono o contacta a soporte.",
        )
        return _render_registro(peticion, formulario, contexto_plantilla)

    persona = Persona.objects.create_user(
        correo=flujo.correo,
        nombre=datos["nombre"],
        primer_apellido=datos["primer_apellido"],
        segundo_apellido=datos["segundo_apellido"],
        telefono=datos["telefono"],
        pais=datos["pais"],
    )

    # Paso 8: continúa automáticamente en CU-REG-002.
    meta, error, espera = _emitir(persona)
    if error:
        messages.error(peticion, error)
        respuesta = _render_registro(peticion, formulario, contexto_plantilla)
        return reintentar_en(respuesta, espera) if espera else respuesta

    _guardar_flujo_con_otp(peticion, flujo.correo, CONTEXTO_PUBLICO, "registro", meta)
    return redirigir(peticion, "registros:codigo")


def _render_registro(peticion, formulario, contexto_plantilla):
    plantilla = (
        "registros/parciales/respuesta_registro.html"
        if es_htmx(peticion)
        else "registros/registro.html"
    )
    return render(peticion, plantilla, {"form": formulario, **contexto_plantilla})


def _continuar_con_cuenta_existente(peticion, flujo):
    """A1 de CU-REG-001: ya había cuenta → directo al flujo de código."""
    persona = _persona_por_correo(flujo.correo)
    if persona is None:
        messages.error(peticion, MENSAJE_GENERICO)
        return redirigir(peticion, "registros:acceso")

    meta, error, espera = _emitir(persona)
    if error:
        messages.error(peticion, error)
        respuesta = redirigir(peticion, "registros:acceso")
        return reintentar_en(respuesta, espera) if espera else respuesta

    _guardar_flujo_con_otp(peticion, flujo.correo, CONTEXTO_PUBLICO, "login", meta)
    return redirigir(peticion, "registros:codigo")


def _guardar_flujo_con_otp(peticion, correo, contexto, origen, meta):
    sesion_service.guardar_flujo(
        peticion,
        FlujoAcceso(
            correo=correo,
            contexto=contexto,
            origen=origen,
            vigencia_segundos=meta["vigencia_segundos"],
            cooldown_segundos=meta["reenvio_cooldown_segundos"],
            intentos_max=meta["intentos_max"],
        ),
    )


# ── Acceso administrativo (CU-REG-003) ────────────────────────


@require_http_methods(["GET", "POST"])
@limitar("auth-identificar")
def admin_acceso(peticion):
    """Paso 1-3 del acceso admin (CU-REG-003 A3).

    Esta pantalla responde "Correo incorrecto." cuando la cuenta no
    existe, y en cualquier otro caso emite el código y avanza — sin
    mirar todavía si la cuenta administra algo. Eso se comprueba en
    `_pantalla_codigo`, **después** de acertar el OTP.

    Dónde se hace esa comprobación es justo lo que decide si esta
    pantalla es o no un oráculo para enumerar administradores:

    - Comprobándolo aquí (como se hizo hasta el 2026-08-19), la
      respuesta distinguía a un administrador de quien no lo era, y
      bastaba un intento por correo para levantar la lista de cuentas
      con más poder del sistema.
    - Comprobándolo después del código, esta pantalla solo revela si un
      correo TIENE CUENTA — lo mismo que ya revela por diseño el acceso
      público al bifurcar entre entrar y registrarse (CU-REG-001). Para
      saber si esa cuenta administra hay que superar el OTP, es decir,
      hay que poder leer ese buzón.

    Entre agosto de 2026 y esta versión, el hueco se tapaba con un
    señuelo que simulaba un OTP inexistente. Funcionaba, pero dejaba a
    quien se equivocaba de pantalla esperando un correo que nunca
    llegaba. Esta versión conserva la garantía y devuelve un error que
    la persona entiende.
    """
    if peticion.method == "GET":
        return render(
            peticion,
            "registros/acceso.html",
            {"form": IdentificarForm(), "contexto": CONTEXTO_ADMIN, "es_admin": True},
        )

    formulario = IdentificarForm(peticion.POST)
    if not formulario.is_valid():
        return _pantalla_acceso(peticion, CONTEXTO_ADMIN, formulario)

    correo = formulario.cleaned_data["correo"]
    persona = _persona_por_correo(correo)

    # A3: solo se comprueba que la cuenta EXISTA. Si además administra
    # algo se decide después del código, no aquí.
    if persona is None:
        messages.error(peticion, "Correo incorrecto.")
        return _pantalla_acceso(peticion, CONTEXTO_ADMIN, formulario)

    meta, error, espera = _emitir(persona)

    if error:
        messages.error(peticion, error)
        respuesta = _pantalla_acceso(peticion, CONTEXTO_ADMIN, formulario)
        return reintentar_en(respuesta, espera) if espera else respuesta

    _guardar_flujo_con_otp(peticion, correo, CONTEXTO_ADMIN, "login", meta)
    return redirigir(peticion, "registros:admin_codigo")


# ── Pantalla del código (CU-REG-002 / 003) ────────────────────


@require_http_methods(["GET", "POST"])
@limitar("auth-otp")
def codigo(peticion):
    """Código del participante."""
    return _pantalla_codigo(peticion, CONTEXTO_PUBLICO)


@require_http_methods(["GET", "POST"])
@limitar("auth-otp")
def admin_codigo(peticion):
    """Código del administrador — mismo mecanismo, distinto destino."""
    return _pantalla_codigo(peticion, CONTEXTO_ADMIN)


def _pantalla_codigo(peticion, contexto: str):
    """Paso 7-12: valida el código y, si acierta, abre la sesión."""
    flujo = sesion_service.leer_flujo(peticion, contexto)
    if flujo is None:
        return redirect(_acceso_de(contexto))

    es_admin_contexto = contexto == CONTEXTO_ADMIN

    if peticion.method == "GET":
        return render(
            peticion,
            "registros/codigo.html",
            {
                "flujo": flujo,
                "es_admin": es_admin_contexto,
                # Las tres direcciones de la pantalla se resuelven aquí
                # para que la plantilla no repita el mismo `if` tres
                # veces; es la única diferencia entre los dos contextos.
                "url_verificar": reverse(
                    "registros:admin_codigo" if es_admin_contexto else "registros:codigo"
                ),
                "url_reenviar": reverse(
                    "registros:admin_reenviar"
                    if es_admin_contexto
                    else "registros:reenviar"
                ),
                "url_acceso": reverse(_acceso_de(contexto)),
            },
        )

    formulario = CodigoForm(_codigo_enviado(peticion))
    if not formulario.is_valid():
        return _estado_otp(peticion, "El código son 6 dígitos.")

    persona = _persona_por_correo(flujo.correo)

    if persona is None:
        # La cuenta desapareció a medio flujo (baja o borrado).
        sesion_service.limpiar_flujo(peticion)
        messages.error(peticion, MENSAJE_GENERICO)
        return redirigir(peticion, _acceso_de(contexto))

    resultado = otp_service.verificar(persona, formulario.cleaned_data["codigo"])

    if not resultado.ok:
        return _fallo_de_codigo(peticion, resultado)

    # E3 de CU-REG-003: el código es correcto, pero la cuenta no
    # administra nada. Se comprueba aquí y no en la pantalla del correo
    # —ver `admin_acceso`— porque es lo que impide enumerar
    # administradores. Aquí el mensaje sí puede ser explícito: quien
    # llega hasta este punto ya demostró ser dueño del buzón, así que
    # decirle qué permisos tiene su propia cuenta no revela nada.
    #
    # El código ya quedó quemado en `verificar`, y así se queda.
    if es_admin_contexto and not _es_admin(persona):
        sesion_service.limpiar_flujo(peticion)
        messages.error(
            peticion,
            "Tu cuenta no tiene permisos administrativos. "
            "Puedes entrar al portal de participante con este mismo correo.",
        )
        return redirigir(peticion, "registros:acceso")

    # Éxito — paso 10-12: sesión, último acceso y destino.
    #
    # El contexto viaja a la sesión: quien administra una feria **y**
    # participa en ella entra por la puerta que quiera, y por la de
    # participante se le enseña el portal de participante. Aquí no se
    # sabe qué significa eso —`registros` no conoce ferias—; solo se
    # anota la puerta.
    sesion_service.iniciar(peticion, persona, contexto=contexto)
    # Las dos son pantallas de elegir feria, y las dos se saltan solas
    # cuando solo hay una (CU-FER-002, CU-FER-010). REG no sabe cuántas
    # hay ni tiene por qué: entrega la sesión y manda a elegir.
    destino = "ferias:mis_ferias" if es_admin_contexto else "ferias:elegir"
    return redirigir(peticion, destino)


def _fallo_de_codigo(peticion, resultado):
    """Fragmento de error + aviso a Alpine para sacudir y limpiar cajas."""
    texto, requiere_nuevo = _mensaje_de_verificacion(resultado)
    respuesta = _estado_otp(peticion, texto)
    disparar(respuesta, "otp:fallo", {"requiereNuevo": requiere_nuevo})
    if resultado.bloqueado:
        reintentar_en(respuesta, resultado.segundos_bloqueo)
    return respuesta


@require_POST
@limitar("auth-otp")
def reenviar(peticion):
    """A1/E5: invalida el código anterior y emite uno nuevo."""
    return _reenviar(peticion, CONTEXTO_PUBLICO)


@require_POST
@limitar("auth-otp")
def admin_reenviar(peticion):
    return _reenviar(peticion, CONTEXTO_ADMIN)


def _reenviar(peticion, contexto: str):
    flujo = sesion_service.leer_flujo(peticion, contexto)
    if flujo is None:
        return redirigir(peticion, _acceso_de(contexto))

    persona = _persona_por_correo(flujo.correo)

    if persona is None:
        sesion_service.limpiar_flujo(peticion)
        messages.error(peticion, MENSAJE_GENERICO)
        return redirigir(peticion, _acceso_de(contexto))

    # No se mira aquí si la cuenta administra algo: reenviar es reenviar,
    # y el permiso se comprueba al validar el código (CU-REG-003 E3).
    meta, error, espera = _emitir(persona)

    if error:
        respuesta = _estado_otp(peticion, error)
        if espera:
            # El contador de la pantalla se resincroniza con la espera
            # real que dice el servidor.
            disparar(respuesta, "otp:reenviado", {"cooldown": espera})
            reintentar_en(respuesta, espera)
        return respuesta

    sesion_service.actualizar_otp(peticion, meta)
    respuesta = _estado_otp(peticion, "Código reenviado a tu correo.", error=False)
    return disparar(
        respuesta,
        "otp:reenviado",
        {
            "vigencia": meta["vigencia_segundos"],
            "cooldown": meta["reenvio_cooldown_segundos"],
        },
    )


def _acceso_de(contexto: str) -> str:
    return (
        "registros:admin_acceso"
        if contexto == CONTEXTO_ADMIN
        else "registros:acceso"
    )


# ── Cerrar sesión (CU-REG-004) ────────────────────────────────


@require_POST
def salir(peticion):
    """CU-REG-004: cierra la sesión y regresa a la pantalla de acceso."""
    era_admin = peticion.user.is_authenticated and peticion.user.es_administrativa
    sesion_service.cerrar(peticion)
    return redirigir(
        peticion, "registros:admin_acceso" if era_admin else "registros:acceso"
    )
