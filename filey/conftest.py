"""
Fixtures que valen para **todas** las apps.

Lo que vive aquí y no en `apps/<dom>/pruebas/conftest.py` es lo que no
es de ningún dominio: condiciones del entorno de pruebas que cualquier
app nueva necesitaría igual, y que si se olvidan fallan de una forma que
no señala a su causa.
"""

import pytest


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
