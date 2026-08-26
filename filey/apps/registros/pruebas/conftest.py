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

from apps.ferias.models import AdminFeria
from apps.ferias.pruebas.fabricas import feria_sin_schema
from apps.registros.models import Persona
from apps.registros.services import otp as otp_service

CODIGO = "123456"


@pytest.fixture(autouse=True)
def urlconf_publico(settings):
    """Resuelve nombres de URL contra el urlconf de **fuera** de una feria.

    `ROOT_URLCONF` apunta al urlconf de dentro de una feria porque es de
    donde `django-tenants` saca los patrones que prefija con
    `/f/<slug>/`. Fuera de una petición —que es donde estas pruebas
    llaman a `reverse()`— Django resuelve contra `ROOT_URLCONF`, y ahí
    `registros:` no existe.

    Todo lo que se prueba en este paquete es la zona pública, así que se
    apunta al urlconf que de verdad la sirve. Las pruebas de dentro de
    una feria viven en `apps/ferias/pruebas/`.
    """
    settings.ROOT_URLCONF = settings.PUBLIC_SCHEMA_URLCONF


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
        nombre="Ana María",
        primer_apellido="Pech",
        segundo_apellido="Uc",
        telefono="9990000001",
        pais="MX",
    )


@pytest.fixture
def feria(db):
    return feria_sin_schema("FILEY 2027", "2027")


@pytest.fixture
def otra_feria(db):
    """Una segunda feria, para comprobar que el acceso no se contagia."""
    return feria_sin_schema("FILEY 2028", "2028")


@pytest.fixture
def dueno_feria(db, feria):
    """Dueña de una feria: administra su contenido **y** sus accesos."""
    persona = Persona.objects.create_user(
        correo="hipolito@filey.org",
        nombre="Hipólito",
        primer_apellido="Canto",
        telefono="9990000002",
    )
    AdminFeria.objects.create(feria=feria, persona=persona, es_dueno=True)
    return persona


@pytest.fixture
def admin_feria(db, feria, dueno_feria):
    """Administradora de la misma feria, sin ser su dueña."""
    persona = Persona.objects.create_user(
        correo="revisor@filey.org",
        nombre="Rita",
        primer_apellido="Uc",
        telefono="9990000003",
    )
    AdminFeria.objects.create(
        feria=feria, persona=persona, es_dueno=False, creado_por=dueno_feria
    )
    return persona
