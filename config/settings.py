"""
Configuración de FILEY 2027 — monolito Django que sirve front y back.

Separación modular:
    apps/        Python puro (models, services, views, urls). Sin templates ni static.
    frontend/    templates/ y static/. Todo lo que el navegador ve.

Ver el skill `filey-render` para la justificación de esta separación y para el
procedimiento de portar una pantalla del prototipo.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-cambiar-en-produccion")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Dominios. Uno por prefijo de caso de uso; se añaden conforme se implementan.
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# Templates centralizados en frontend/, NO dentro de cada app: el frontend es un
# módulo, no un anexo de cada app de backend. APP_DIRS queda en False a propósito.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend" / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Merida"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------------------------------------------------------------------
# TRANSITORIO — fuente única de CSS
#
# El prototipo sigue siendo la fuente de verdad de las capas CSS. En vez de
# copiarlas a frontend/static/ (lo que crearía dos versiones que divergen), se
# sirve prototipo/ como directorio de estáticos. Así `{% static 'VIS/styles.css' %}`
# resuelve al archivo real, y su `@import '../common/styles-base.css'` sigue
# funcionando porque la ruta relativa se conserva.
#
# Condición de salida: cuando la última pantalla del prototipo esté portada,
# `git mv prototipo/common prototipo/{DOM}/styles.css` → frontend/static/css/ y
# se borra la segunda entrada de esta lista. Un solo cambio, sin migración de CSS.
# ---------------------------------------------------------------------------
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "static",
    BASE_DIR / "prototipo",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
