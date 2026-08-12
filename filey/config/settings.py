"""
Configuración Django — FILEY (monolito, ADR-0001).

Un solo proyecto sirve backend y frontend: vistas Django + plantillas
con HTMX/Alpine. No hay API REST ni frontend separado, así que aquí no
aparecen `rest_framework`, `simplejwt` ni `corsheaders` — existían solo
para hablar con el Angular que se retiró en la migración (ADR-0002).

Las variables sensibles se leen de `.env` (ver `.env.example`).
"""

from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# Seguro por defecto: si DJANGO_DEBUG no se declara, se asume
# producción (DEBUG=False). Un despliegue que olvide la variable
# NO queda con DEBUG=True filtrando trazas y datos. En desarrollo,
# el .env local trae DJANGO_DEBUG=true explícito.
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"

_SECRET_INSEGURO = "django-insecure-solo-para-desarrollo-cambiar-en-produccion"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", _SECRET_INSEGURO)

# La SECRET_KEY firma las cookies de sesión: con el valor de ejemplo,
# cualquiera puede forjar la sesión de un administrador. Abortar el
# arranque antes que servir así.
if not DEBUG and SECRET_KEY in (_SECRET_INSEGURO, "dev-filey-registro-2027", ""):
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY no está configurada con un valor propio. "
        "Genera una y ponla en el entorno antes de desplegar con DEBUG=False."
    )

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


# ── Aplicaciones ──────────────────────────────────────────────
# Cada dominio de FILEY es una app bajo `apps/`. `registros` es la
# base (identidad, sesión, permisos); los módulos verticales
# (EVT/TAL/STD/VIS) se agregan aquí conforme se construyan y
# dependen de `registros`, nunca al revés (ver CLAUDE.md).

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # FILEY
    "apps.registros",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Sirve los archivos de `estaticos/` en producción sin necesidad de
    # un servidor web aparte: es lo que permite desplegar el monolito
    # como un solo proceso (ADR-0001).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # `plantillas/` trae el esqueleto compartido (base, layouts);
        # cada app pone las suyas en `apps/<dominio>/templates/<dominio>/`.
        "DIRS": [BASE_DIR / "plantillas"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ── Base de datos (SQLite en desarrollo) ──────────────────────

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ── Autenticación ─────────────────────────────────────────────
# Persona es el usuario del sistema (Core Registros). No hay
# contraseñas para el login: todo acceso es por OTP (decisión
# del equipo, 2026-06-30 — ver CU-REG-003). La sesión la abre
# `apps/registros/services/sesion.py` tras validar el código.

AUTH_USER_MODEL = "registros.Persona"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

# A dónde manda Django a quien entra sin sesión a una vista protegida.
LOGIN_URL = "registros:acceso"

# La sesión dura lo mismo que duraba el refresh token que sustituye,
# para no cambiar de facto cuánto tiempo permanece alguien dentro.
SESSION_COOKIE_AGE = 12 * 60 * 60
SESSION_SAVE_EVERY_REQUEST = True  # la duración cuenta desde la última actividad

# La cookie de sesión reemplaza al JWT en localStorage: inaccesible
# desde JavaScript (HttpOnly) y no viaja en peticiones cross-site.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"


# ── Caché ─────────────────────────────────────────────────────
# La usan el estado señuelo del acceso admin (services/senuelo.py) y
# el limitador de peticiones (comun/limites.py). Con LocMemCache cada
# proceso ve la suya: en producción con varios workers hay que
# configurar aquí una caché compartida (Redis/Memcached) o ambas
# defensas quedan divididas entre procesos.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "filey",
    }
}


# ── Archivos estáticos ────────────────────────────────────────

STATIC_URL = "estaticos/"
STATICFILES_DIRS = [BASE_DIR / "estaticos"]
STATIC_ROOT = BASE_DIR / "estaticos_recolectados"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        # En producción se comprime y se versiona por hash: el navegador
        # puede cachear para siempre y aun así ver el CSS nuevo tras cada
        # despliegue. Eso exige haber corrido `collectstatic`, que en
        # desarrollo no se corre — de ahí las dos ramas.
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

# En desarrollo, servir el archivo tal como está en disco en cada
# petición: sin esto habría que reiniciar para ver un cambio de CSS.
WHITENOISE_AUTOREFRESH = DEBUG


# ── URL pública del sistema ───────────────────────────────────
# Base de los enlaces que van dentro de los correos (p. ej. el aviso
# de alta administrativa). En producción, el dominio real: si se queda
# en localhost, los enlaces no le sirven a nadie.

URL_BASE = os.getenv("URL_BASE", "http://localhost:8000").rstrip("/")


# ── Correo (envío del OTP) ────────────────────────────────────
# Con credenciales en .env se usa Gmail SMTP; sin ellas, los
# correos se imprimen en la consola (útil en desarrollo).

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()

# Google muestra la contraseña de aplicación en cuatro bloques
# ("abcd efgh ijkl mnop"); pegada tal cual, el AUTH de Gmail falla.
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "").replace(" ", "").strip()

CORREO_CONFIGURADO = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)

if CORREO_CONFIGURADO:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    # 587 es STARTTLS y 465 es SSL directo: cruzarlos deja la
    # conexión colgada hasta agotar el timeout.
    EMAIL_USE_SSL = EMAIL_PORT == 465
    EMAIL_USE_TLS = not EMAIL_USE_SSL
    # Sin timeout, un SMTP que no responde bloquea indefinidamente
    # el hilo que envía el OTP.
    EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "20"))
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Gmail solo deja enviar como la cuenta autenticada (o un alias
# verificado). Un remitente de otro dominio —como el noreply@filey.org
# que traía el .env— se reescribe o se rechaza, y falla SPF/DMARC,
# así que el correo acaba en spam o no sale.
_remitente = os.getenv("DEFAULT_FROM_EMAIL", "").strip()

if CORREO_CONFIGURADO and EMAIL_HOST_USER not in _remitente:
    _remitente = f"FILEY <{EMAIL_HOST_USER}>"

DEFAULT_FROM_EMAIL = _remitente or "FILEY <noreply@filey.org>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# La caída silenciosa a consola es la causa nº1 de "el OTP no
# llega": el envío parece exitoso pero el código solo se imprime
# en esta terminal. Avisarlo en voz alta al levantar el servidor.
if not CORREO_CONFIGURADO and "runserver" in sys.argv:
    print(
        "\n"
        "  ┌─────────────────────────────────────────────────────────────┐\n"
        "  │  CORREO EN MODO CONSOLA — el OTP NO se envía por correo.    │\n"
        "  │  El código aparece impreso aquí abajo, en esta terminal.    │\n"
        "  │                                                             │\n"
        "  │  Para enviarlo de verdad, llena en filey/.env:              │\n"
        "  │     EMAIL_HOST_USER / EMAIL_HOST_PASSWORD                   │\n"
        "  │  y comprueba con:  python manage.py probar_correo <destino> │\n"
        "  └─────────────────────────────────────────────────────────────┘\n",
        file=sys.stderr,
    )


# ── Logging ───────────────────────────────────────────────────
# Sin esto, el motivo real de un fallo de envío (credenciales,
# remitente rechazado, timeout) se pierde: la vista solo muestra
# un mensaje genérico a la persona.

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"consola": {"class": "logging.StreamHandler"}},
    "loggers": {
        "apps.registros": {"handlers": ["consola"], "level": "INFO"},
    },
}


# ── Parámetros del OTP (CU-REG-002) ───────────────────────────

OTP_VIGENCIA_MINUTOS = 15   # paso 4: expira_en = ahora + 15 min
OTP_INTENTOS_MAX = 3        # E1: máximo 3 intentos por código emitido
OTP_REENVIO_COOLDOWN_SEG = 60  # A1: reenvío disponible tras 60 s

# Límites por cuenta destino (defensa contra abuso distribuido, que
# el límite por IP no cubre). Ver services/otp.py.
OTP_VENTANA_MINUTOS = 15          # ventana móvil de conteo
OTP_EMISIONES_MAX_VENTANA = 5     # máx. códigos emitidos por cuenta/ventana
OTP_FALLOS_MAX_VENTANA = 10       # fallos acumulados que disparan el lockout
OTP_LOCKOUT_MINUTOS = 15          # duración del lockout de verificación


# ── Límite de peticiones por IP (comun/limites.py) ────────────
# Sustituye al throttling de DRF, que se fue con la API REST. Es la
# capa por IP; la capa por cuenta destino vive en services/otp.py.

LIMITES_PETICIONES = {
    "auth-identificar": "20/min",
    "auth-otp": "10/min",
}


# ── Anti-enumeración del acceso administrativo ────────────────
# El acceso admin responde igual exista o no el correo (ver
# services/senuelo.py). Para que el TIEMPO tampoco delate quién es
# administrador, las respuestas se retienen hasta un mínimo: el
# camino real hashea el código y habla con el SMTP, y sin este piso
# esa latencia extra vuelve a distinguir las cuentas reales.
# Si el SMTP de producción resulta más lento, subir el piso de OTP.

ADMIN_PISO_IDENTIFICAR_SEG = float(os.getenv("ADMIN_PISO_IDENTIFICAR_SEG", "0.3"))
ADMIN_PISO_OTP_SEG = float(os.getenv("ADMIN_PISO_OTP_SEG", "1.5"))


# ── Internacionalización ──────────────────────────────────────

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Merida"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ── Endurecimiento HTTP (solo con DEBUG=False) ────────────────
# En desarrollo se sirve por http://localhost, así que estos
# candados se activan únicamente en producción para no romper el
# entorno local. Todos pueden afinarse por variable de entorno.

if not DEBUG:
    # Redirige http→https y confía en la cabecera del proxy de
    # Render/Cloudflare (que terminan TLS antes de Django).
    SECURE_SSL_REDIRECT = os.getenv("DJANGO_SSL_REDIRECT", "true").lower() == "true"
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # HSTS: el navegador recuerda usar HTTPS. Se empieza con un año.
    SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_HSTS_SECONDS", str(60 * 60 * 24 * 365)))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Las cookies (sesión, CSRF) solo por HTTPS.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Defensa en profundidad de cabeceras.
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "same-origin"

    # Orígenes de confianza para el CSRF detrás del dominio real
    # (coma-separado en la variable).
    _csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "").strip()
    if _csrf:
        CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf.split(",") if o.strip()]
