"""
Fixtures que valen para **todas** las apps.

Lo que vive aquí y no en `apps/<dom>/pruebas/conftest.py` es lo que no
es de ningún dominio: condiciones del entorno de pruebas que cualquier
app nueva necesitaría igual, y que si se olvidan fallan de una forma que
no señala a su causa.

Las ferias con schema de verdad están aquí por lo segundo. Las pide más
de un paquete de pruebas —`ferias` prueba el aislamiento, `convocatorias`
prueba el catálogo que vive dentro—, y un `conftest.py` no se importa
desde otro.
"""

import pytest
from django.db import connection

from apps.ferias.servicios import altas


@pytest.fixture(autouse=True)
def estaticos_sin_manifiesto(settings):
    """Sirve los estáticos sin el manifiesto de hashes.

    Django corre las pruebas con `DEBUG=False`, y con eso `settings.py`
    activa el almacenamiento versionado por hash — que exige un
    `collectstatic` previo. Sin esta línea, **cualquier plantilla con
    `{% static %}` revienta en pruebas** por un motivo de despliegue.

    Vive en la raíz porque no es de `registros`, que es donde estaba
    hasta el 2026-08-25: la primera plantilla de `ferias` que extendió
    `base.html` volvió a tropezar con lo mismo. Y no se notó en local
    —donde el `.env` trae `DJANGO_DEBUG=true` y el almacenamiento es el
    plano— sino en CI, que prueba con la configuración endurecida.

    El fallo, además, llega disfrazado: el `ValueError` del manifiesto
    dispara el manejador de error 500, y el urlconf dinámico de
    `django-tenants` responde a `handler500` con un `ImportError` que
    tapa la causa real.
    """
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }


@pytest.fixture(autouse=True)
def empezar_en_public():
    """Deja la conexión en `public` antes de cada prueba.

    No es higiene de pruebas: es la contrapartida de cómo funciona
    `TenantSubfolderMiddleware`, y conviene tenerla presente.

    El middleware **no restaura** el `search_path` al terminar una
    petición; lo que hace es empezar cada una con
    `set_schema_to_public()`. Para las peticiones eso basta y sobra —una
    no puede heredar el schema de la anterior—, pero deja la conexión
    apuntando a la última feria visitada.

    En producción no llega a importar: lo único que corre fuera de una
    petición es el hilo del OTP, que abre su propia conexión (y hay una
    prueba de eso), y los comandos de `manage.py`, que son otro proceso.
    En las pruebas sí importa, porque todo comparte una conexión y una
    prueba que visita `/f/2027/` haría fallar a la siguiente que intente
    crear una feria — `TenantMixin.save()` se niega a crear un tenant
    desde fuera de `public`.
    """
    connection.set_schema_to_public()
    yield
    connection.set_schema_to_public()


@pytest.fixture
def feria_2027(db):
    """Una feria completa: fila, schema migrado, slug de ruteo y dueña.

    Cuesta una tanda de migraciones, así que se pide solo cuando el
    schema es lo que se prueba. Para lo demás está
    `apps/ferias/pruebas/fabricas.py::feria_sin_schema`.
    """
    return altas.crear_feria(
        nombre="FILEY 2027",
        slug="2027",
        correo_dueno="ana@uady.mx",
        nombre_dueno="Ana",
        primer_apellido_dueno="Pech",
        enviar_aviso=False,
        verbosity=0,
    ).feria


@pytest.fixture
def feria_2028(db):
    """Una segunda feria, que es contra la que se comprueba el aislamiento."""
    return altas.crear_feria(
        nombre="FILEY 2028",
        slug="2028",
        correo_dueno="beto@uady.mx",
        nombre_dueno="Beto",
        primer_apellido_dueno="Chan",
        enviar_aviso=False,
        verbosity=0,
    ).feria
