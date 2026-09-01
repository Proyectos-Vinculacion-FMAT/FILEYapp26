"""
Las comprobaciones de despliegue (`comun/checks.py`).

No prueban código de producción: prueban **la alarma**. Las dos vigilan
configuraciones que en desarrollo funcionan igual de bien y en producción
desactivan algo sin dar ningún síntoma, así que si la alarma se rompe no
lo nota nadie hasta que ya pasó lo que venía a evitar.
"""

from ..checks import (
    almacenamiento_persistente_en_produccion,
    cache_compartida_en_produccion,
)

LOCAL = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
S3 = {"BACKEND": "storages.backends.s3.S3Storage"}


def _ids(avisos):
    return [a.id for a in avisos]


# ── comun.E001 · la caché por proceso ─────────────────────────


def test_locmem_en_produccion_se_rechaza(settings):
    settings.DEBUG = False
    settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

    assert _ids(cache_compartida_en_produccion(None)) == ["comun.E001"]


def test_en_desarrollo_locmem_esta_bien(settings):
    settings.DEBUG = True
    settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

    assert cache_compartida_en_produccion(None) == []


# ── comun.W001 · el almacenamiento efímero ────────────────────


def test_avisa_si_los_archivos_caen_en_el_contenedor(settings, monkeypatch):
    """La decisión del 2026-08-27 es legítima; olvidarla no.

    Lo que se pierde no da síntoma: la fila de la base sigue ahí con su
    ruta y el archivo ya no está detrás.
    """
    settings.DEBUG = False
    settings.STORAGES = {**settings.STORAGES, "default": LOCAL}
    monkeypatch.delenv("MEDIA_ROOT", raising=False)

    avisos = almacenamiento_persistente_en_produccion(None)

    assert _ids(avisos) == ["comun.W001"]
    # Aviso, no error: el despliegue no se bloquea por una decisión que
    # el equipo tomó a sabiendas.
    assert avisos[0].level < 40


def test_un_disco_montado_calla_el_aviso(settings, monkeypatch):
    settings.DEBUG = False
    settings.STORAGES = {**settings.STORAGES, "default": LOCAL}
    monkeypatch.setenv("MEDIA_ROOT", "/var/data/medios")

    assert almacenamiento_persistente_en_produccion(None) == []


def test_el_almacen_de_objetos_calla_el_aviso(settings, monkeypatch):
    """El día que haya bucket, esta comprobación deja de hablar sola."""
    settings.DEBUG = False
    settings.STORAGES = {**settings.STORAGES, "default": S3}
    monkeypatch.delenv("MEDIA_ROOT", raising=False)

    assert almacenamiento_persistente_en_produccion(None) == []


def test_en_desarrollo_no_molesta(settings, monkeypatch):
    settings.DEBUG = True
    settings.STORAGES = {**settings.STORAGES, "default": LOCAL}
    monkeypatch.delenv("MEDIA_ROOT", raising=False)

    assert almacenamiento_persistente_en_produccion(None) == []
