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
#
# Desde ADR-0003 la lista está partida en dos, y la partición **es** la
# arquitectura: `django-tenants` decide dónde crea las tablas de una app
# según en cuál de las dos esté.
#
#   SHARED_APPS  → schema `public`. Una sola copia para todo el sistema.
#   TENANT_APPS  → schema `feria_<slug>`. Una copia por edición.
#
# Una app que esté en las dos duplica *todas* sus tablas en *todos* los
# schemas. Por eso `FER` está partido en dos apps de Django
# (`apps.ferias` global, `apps.convocatorias` por feria) en vez de ser
# una sola con modelos de las dos capas.

SHARED_APPS = [
    # Obligatoria y primera: aporta el backend, el middleware y
    # `migrate_schemas`.
    "django_tenants",
    # Tiene que ir en `public` porque es donde vive el modelo tenant.
    "apps.ferias",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # La identidad es global: la misma Persona con el mismo correo
    # participa en FILEY 2027 y administra FILEY 2028 (ADR-0003).
    "apps.registros",
    "apps.notificaciones",
    # Sin modelos: está aquí porque Django solo descubre `templatetags/`
    # dentro de las apps instaladas, y en `comun/templatetags/chasis.py`
    # vive la barra superior de todo el sistema.
    "comun",
]

TENANT_APPS = [
    "apps.convocatorias",
    # Cada dominio vertical es **su propia app**, con sus tablas y su
    # namespace de URLs: no comparten modelos entre sí ni con
    # `apps.convocatorias`, que es la mitad por feria de `FER`. La
    # dependencia va en una sola dirección (`ADR-0006`).
    "apps.stands",
    # Aquí se añaden EVT, VIS, PRG y SAL conforme se construyan: todos
    # son contenido de una feria.
]

INSTALLED_APPS = SHARED_APPS + [a for a in TENANT_APPS if a not in SHARED_APPS]

TENANT_MODEL = "ferias.Feria"
TENANT_DOMAIN_MODEL = "ferias.Domain"

# `/f/<slug>/…` — el prefijo por feria que fija ADR-0003. Se eligió
# sobre el subdominio porque no exige configurar DNS ni un certificado
# por edición.
TENANT_SUBFOLDER_PREFIX = "f"

MIDDLEWARE = [
    # PRIMERO, antes que nada: resuelve la feria del prefijo de la URL y
    # fija el `search_path` de la conexión. Empieza cada petición con un
    # `set_schema_to_public()`, que es lo que impide que el schema de una
    # petición se filtre a la siguiente sobre una conexión reutilizada.
    #
    # Correr aquí tiene una consecuencia que hay que tener presente: es
    # ANTES de `AuthenticationMiddleware`, así que no hay `request.user`
    # y este middleware **no puede comprobar permisos**. Eso lo hacen los
    # decoradores de `apps/ferias/permisos.py`. Enmienda a ADR-0003, que
    # describía el middleware como el sitio de esa comprobación.
    "django_tenants.middleware.TenantSubfolderMiddleware",
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

# Dos urlconfs, porque la librería usa uno u otro según el schema:
# `ROOT_URLCONF` es lo que cuelga de `/f/<slug>/` y `PUBLIC_SCHEMA_URLCONF`
# lo que se sirve fuera de toda feria (acceso, django-admin).
ROOT_URLCONF = "config.urls_feria"
PUBLIC_SCHEMA_URLCONF = "config.urls_publicas"

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


import dj_database_url

# ── Base de datos ─────────────────────────────────────────────
# PostgreSQL, y no como preferencia: ADR-0003 aísla cada feria en su
# propio schema, y SQLite no tiene schemas. Ya no hay respaldo a
# SQLite ni en desarrollo — el entorno local dejaría fuera justo la
# parte del sistema que más falta probar.

DATABASES = {
    "default": dj_database_url.config(
        # El default es el Postgres de `docker-compose.yml`. Quien use
        # una instancia propia (otro puerto, otro usuario) lo declara en
        # su `.env`; ver `.env.example`.
        default="postgres://filey_user:filey_password@localhost:5432/filey_db",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

if not DATABASES["default"].get("ENGINE", "").endswith("postgresql"):
    raise ImproperlyConfigured(
        "FILEY requiere PostgreSQL: cada feria vive en su propio schema "
        "(ADR-0003) y SQLite no los soporta. Revisa DATABASE_URL."
    )

# `dj_database_url` devuelve el backend estándar de Django; se sustituye
# por el de `django-tenants`, que es el mismo más la gestión del
# `search_path` por petición.
DATABASES["default"]["ENGINE"] = "django_tenants.postgresql_backend"

# Decide en qué schema se crea la tabla de cada app al migrar, según esté
# en SHARED_APPS o en TENANT_APPS.
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)


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
# La usa el limitador de peticiones por IP (comun/limites.py), y de ella
# depende que ese límite signifique algo.
#
# Con LocMemCache cada proceso lleva su propio contador, así que el
# límite real se multiplica por el número de workers: `start.sh` levanta
# gunicorn con 3, o sea 60 peticiones/min donde la configuración dice 20.
# Por eso, en producción, LocMem no es una configuración válida y el
# `check` de abajo lo impide (CU-REG-003, "Requisito de despliegue").
REDIS_URL = os.getenv("REDIS_URL", "")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
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

# ── Archivos que sube la gente ────────────────────────────────
# Distintos de los estáticos y en casi todo lo contrario: los
# estáticos son parte del despliegue, públicos y cacheables para
# siempre; esto son actas constitutivas, RFC y comprobantes de pago
# de personas concretas (`ADR-0007`).
#
# **Nada de esto se sirve por una URL.** No hay ruta para `MEDIA_URL`
# en ningún urlconf, y es deliberado: cada módulo entrega sus archivos
# por una vista que comprueba quién pregunta. `MEDIA_URL` existe
# porque `FileField.url` la usa para componer, no porque algo la
# resuelva.

MEDIA_URL = "medios/"

# Dónde caen los archivos con el almacenamiento local. Se saca del
# entorno para que en Render apunte al disco montado y no al sistema de
# archivos del contenedor, que se borra en cada despliegue.
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", BASE_DIR / "medios"))

# `local` (por omisión) o `s3`. Cambiar de uno a otro es cambiar esta
# variable y las cuatro de abajo: no se toca código. Ver `ADR-0007`.
ALMACENAMIENTO = os.getenv("ALMACENAMIENTO", "local").lower()

if ALMACENAMIENTO == "s3":
    # Sirve para cualquier almacén compatible con S3 —Supabase Storage,
    # Cloudflare R2, AWS— porque lo único que los distingue es el
    # endpoint. Requiere `django-storages[s3]` en requirements.txt, que
    # no está instalado mientras nadie use esta rama.
    _opciones_s3 = {
        "bucket_name": os.getenv("S3_BUCKET"),
        "endpoint_url": os.getenv("S3_ENDPOINT_URL"),
        "access_key": os.getenv("S3_ACCESS_KEY"),
        "secret_key": os.getenv("S3_SECRET_KEY"),
    }
    _VARIABLE_DE = {
        "bucket_name": "S3_BUCKET",
        "endpoint_url": "S3_ENDPOINT_URL",
        "access_key": "S3_ACCESS_KEY",
        "secret_key": "S3_SECRET_KEY",
    }
    _faltantes = sorted(_VARIABLE_DE[k] for k, v in _opciones_s3.items() if not v)
    if _faltantes:
        raise ImproperlyConfigured(
            "ALMACENAMIENTO=s3 pero faltan estas variables: "
            + ", ".join(_faltantes)
            + ". Abortar es lo correcto: sin ellas el sistema arrancaría y "
            "perdería en silencio todo lo que alguien subiera."
        )
    _almacen_por_defecto = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            **_opciones_s3,
            # Privado, y con URL firmada de vida corta. Aun así, quien
            # entrega el archivo sigue siendo la vista del módulo: el
            # bucket no es la puerta.
            "default_acl": "private",
            "querystring_auth": True,
            # Nunca pisar un archivo existente. Con nombres aleatorios no
            # debería pasar, y si pasara sería un choque de UUID que
            # preferimos ver como archivo nuevo y no como uno perdido.
            "file_overwrite": False,
        },
    }
else:
    _almacen_por_defecto = {"BACKEND": "django.core.files.storage.FileSystemStorage"}


# ── Los dos almacenes ─────────────────────────────────────────

STORAGES = {
    "default": _almacen_por_defecto,
    "staticfiles": {
        # En producción se comprime y se versiona por hash: el navegador
        # puede cachear para siempre y aun así ver el CSS nuevo tras cada
        # despliegue. Eso exige haber corrido `collectstatic`, que en
        # desarrollo no se corre — de ahí las dos ramas.
        # `comun.estaticos.EstaticosFiley` y no el de whitenoise a secas:
        # deja el build de Godot del mapa fuera del manifiesto. Su
        # `index.js` pide el `.wasm` por su nombre literal, así que
        # hashearlo rompe el mapa **solo en producción**.
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "comun.estaticos.EstaticosFiley"
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


# ── Correo (Notificaciones vía Resend) ────────────────────────
# TODO el correo del proyecto sale por `django.core.mail`; quién lo
# entrega lo decide este ajuste. Antes el OTP hablaba con Resend por su
# cuenta, sin pasar por aquí: las pruebas no lo veían y, con la clave
# configurada, la suite mandaba correos reales. Ver
# apps/notificaciones/backends.py.
#
# Django sustituye este backend por `locmem` durante los tests, así que
# ninguna prueba puede salir a la red por accidente.
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "apps.notificaciones.backends.ResendBackend"
)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "FILEY <noreply@filey.org>")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

if not RESEND_API_KEY and "runserver" in sys.argv:
    print(
        "\n"
        "  ┌─────────────────────────────────────────────────────────────┐\n"
        "  │  CORREO SIN RESEND_API_KEY — el OTP NO se enviará.          │\n"
        "  │  El sistema lanzará un error al intentar enviar correos.    │\n"
        "  │                                                             │\n"
        "  │  Para enviarlo de verdad, llena en filey/.env:              │\n"
        "  │     RESEND_API_KEY                                          │\n"
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
