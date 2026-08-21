"""
Piezas compartidas por las pruebas del Core Registros.

Dos cosas hay que domar para poder probar el OTP:

1. **El código no se puede leer de la base** — se guarda hasheado, que
   es justo el punto. Se fija con ``codigo_fijo`` monkeypatcheando el
   generador, igual que se haría con un reloj falso para probar fechas.
2. **El correo sale en un hilo aparte** — bien en producción, porque
   hablar con el proveedor tarda segundos, e incómodo en pruebas, donde
   ese hilo abriría su propia conexión a la base de pruebas.
   ``sin_hilo_de_correo`` lo vuelve síncrono, así que el buzón de Django
   queda consultable.

El correo en sí no hay que domarlo: sale por ``django.core.mail``, y
Django sustituye el backend por ``locmem`` durante los tests. Ninguna
prueba puede alcanzar la red aunque haya una ``RESEND_API_KEY`` en el
entorno (ver ``apps/notificaciones/backends.py``).
"""

import pytest
from django.core.cache import cache

from apps.registros.models import Modulo, NivelPermiso, Persona, RolPermiso
from apps.registros.services import otp as otp_service

CODIGO = "123456"


@pytest.fixture(autouse=True)
def cache_limpia():
    """El señuelo y el limitador viven en caché: aislarlos entre pruebas.

    Sin esto, el límite por IP consumido en una prueba haría fallar a la
    siguiente por motivos que no tienen nada que ver con lo que prueba.
    """
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def estaticos_sin_manifiesto(settings):
    """Sirve los estáticos sin el manifiesto de hashes.

    Django corre las pruebas con DEBUG=False, que en producción activa
    el almacenamiento versionado por hash — y ese exige un
    `collectstatic` previo. Sin esta línea, cualquier plantilla con
    `{% static %}` reventaría en pruebas por un motivo de despliegue.
    """
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }


@pytest.fixture(autouse=True)
def sin_hilo_de_correo(monkeypatch):
    """Envía el correo en el mismo hilo, para poder revisar el buzón."""
    monkeypatch.setattr(
        otp_service,
        "_despachar_correo",
        lambda correo, nombre, codigo, sesion_id: otp_service._tarea_envio(
            correo, nombre, codigo, sesion_id
        ),
    )


@pytest.fixture
def codigo_fijo(monkeypatch):
    """Hace que todo OTP emitido sea ``123456``."""
    monkeypatch.setattr(otp_service, "_generar_codigo", lambda: CODIGO)
    return CODIGO


@pytest.fixture
def participante(db):
    return Persona.objects.create_user(
        correo="ana@ejemplo.com",
        nombre_completo="Ana María Pech",
        telefono="9990000001",
    )


@pytest.fixture
def admin_general(db):
    """Administrador con el rol ``*``: puede con todos los módulos."""
    persona = Persona.objects.create_user(
        correo="hipolito@filey.org",
        nombre_completo="Hipólito Canto",
        telefono="9990000002",
    )
    RolPermiso.objects.create(
        persona=persona, modulo=Modulo.TODOS, nivel=NivelPermiso.EDICION
    )
    return persona


@pytest.fixture
def admin_evt(db):
    """Administrador de un solo módulo, con permiso de solo lectura."""
    persona = Persona.objects.create_user(
        correo="revisor@filey.org",
        nombre_completo="Rita Uc",
        telefono="9990000003",
    )
    RolPermiso.objects.create(
        persona=persona, modulo=Modulo.EVT, nivel=NivelPermiso.LECTURA
    )
    return persona
