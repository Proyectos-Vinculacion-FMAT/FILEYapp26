"""
Comprobaciones de despliegue que Django ejecuta con `manage.py check`.

Aquí vive lo que no se puede dejar en un comentario y esperar que alguien
lo lea: configuraciones que en desarrollo funcionan igual de bien y en
producción desactivan una defensa **sin dar ningún síntoma**.
"""

from django.conf import settings
from django.core.checks import Error, register

LOCMEM = "django.core.cache.backends.locmem.LocMemCache"


@register(deploy=True)
def cache_compartida_en_produccion(app_configs, **kwargs):
    """El límite por IP no significa nada con una caché por proceso.

    `comun/limites.py` cuenta las peticiones de cada IP en la caché. Con
    `LocMemCache` cada worker lleva su propia cuenta, así que el límite
    efectivo se multiplica por el número de procesos: con los 3 workers
    de `start.sh`, "20/min" son en realidad 60/min. No falla nada, no se
    registra nada, y la defensa simplemente vale un tercio de lo que
    dice — que es la peor forma de estar roto.

    Es el "Requisito de despliegue" de CU-REG-003. Se comprueba en vez de
    documentarse porque un requisito que solo vive en un documento se
    incumple sin que nadie se entere.
    """
    if settings.DEBUG:
        return []

    backend = settings.CACHES.get("default", {}).get("BACKEND", "")
    if backend != LOCMEM:
        return []

    return [
        Error(
            "La caché por defecto es LocMemCache y DEBUG está desactivado.",
            hint=(
                "Cada proceso tendría su propio contador y el límite de "
                "peticiones por IP de comun/limites.py se multiplicaría por el "
                "número de workers. Configura REDIS_URL para usar una caché "
                "compartida entre procesos."
            ),
            id="comun.E001",
        )
    ]
