"""
Comprobaciones de despliegue que Django ejecuta con `manage.py check`.

Aquí vive lo que no se puede dejar en un comentario y esperar que alguien
lo lea: configuraciones que en desarrollo funcionan igual de bien y en
producción desactivan una defensa **sin dar ningún síntoma**.
"""

import os

from django.conf import settings
from django.core.checks import Error, Warning, register

LOCMEM = "django.core.cache.backends.locmem.LocMemCache"
SISTEMA_DE_ARCHIVOS = "django.core.files.storage.FileSystemStorage"


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


@register(deploy=True)
def almacenamiento_persistente_en_produccion(app_configs, **kwargs):
    """Guardar en el contenedor pierde los archivos en cada despliegue.

    Es un aviso y no un error a propósito: el equipo decidió el
    2026-08-27 arrancar con el sistema de archivos local mientras no
    haya un almacén de objetos contratado (`ADR-0007`), y bloquear el
    despliegue por una decisión tomada sería estorbar.

    Lo que no puede pasar es que se olvide. Lo que se pierde no da
    ningún síntoma —la fila de la base sigue ahí, con su ruta, y el
    archivo ya no está detrás—: el expediente de un expositor se ve
    completo hasta que alguien intenta abrir su acta constitutiva.

    El aviso se calla solo de dos formas, y las dos son correctas:
    apuntando ``MEDIA_ROOT`` a un disco montado que sobreviva al
    despliegue, o poniendo ``ALMACENAMIENTO=s3``.
    """
    if settings.DEBUG:
        return []

    backend = settings.STORAGES.get("default", {}).get("BACKEND", "")
    if backend != SISTEMA_DE_ARCHIVOS:
        return []

    if os.getenv("MEDIA_ROOT"):
        # Se declaró a dónde van: se asume que ese disco persiste. Este
        # check no puede saber si el volumen está montado de verdad.
        return []

    return [
        Warning(
            "Los archivos que sube la gente se guardan dentro del contenedor.",
            hint=(
                "MEDIA_ROOT no está declarada, así que los archivos caen en el "
                "sistema de archivos del contenedor y se pierden en cada "
                "despliegue. Apunta MEDIA_ROOT a un disco montado, o configura "
                "ALMACENAMIENTO=s3 con sus credenciales. Ver ADR-0007."
            ),
            id="comun.W001",
        )
    ]
