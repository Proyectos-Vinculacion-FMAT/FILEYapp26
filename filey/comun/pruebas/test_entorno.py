"""
Una variable de entorno vacía es una que no está (`config/settings.py`).

Salió de un 404 real (2026-09-03): con ``MEDIA_ROOT=`` en el `.env` —que
es como se deja una variable "en blanco"— `os.getenv` devolvía la cadena
vacía en vez del valor por omisión, `Path("")` resolvía al directorio de
trabajo, y los adjuntos ya subidos dejaban de encontrarse.

Lo que se vigila es que el defecto no vuelva por la puerta de atrás: en
Render una variable **declarada y sin valor** llega igual de vacía, y ahí
el síntoma habría sido escribir los archivos en el disco efímero del
contenedor sin un solo error en el log.
"""

import pytest

from config.settings import _del_entorno


def test_una_clave_ausente_cae_al_defecto(monkeypatch):
    monkeypatch.delenv("PRUEBA_FILEY", raising=False)
    assert _del_entorno("PRUEBA_FILEY", "medios") == "medios"


@pytest.mark.parametrize("vacia", ["", "   ", "\t"])
def test_una_clave_vacia_tambien(monkeypatch, vacia):
    """Es el caso que costó el 404: `KEY=` en un `.env`.

    Los espacios cuentan como vacío: un `.env` editado a mano deja un
    espacio detrás del `=` con facilidad, y un `MEDIA_ROOT=" "` sería el
    mismo desastre con peor rastro.
    """
    monkeypatch.setenv("PRUEBA_FILEY", vacia)
    assert _del_entorno("PRUEBA_FILEY", "medios") == "medios"


def test_un_valor_de_verdad_manda(monkeypatch):
    monkeypatch.setenv("PRUEBA_FILEY", "/discos/filey")
    assert _del_entorno("PRUEBA_FILEY", "medios") == "/discos/filey"


def test_el_defecto_puede_no_ser_una_cadena(monkeypatch):
    """`MEDIA_ROOT` pasa un `Path`, y tiene que salir intacto.

    Convertirlo a texto aquí funcionaría por accidente —`Path` lo acepta
    de vuelta— pero rompería cualquier otro defecto que no sea una ruta.
    """
    from pathlib import Path

    monkeypatch.delenv("PRUEBA_FILEY", raising=False)
    defecto = Path("/base/medios")
    assert _del_entorno("PRUEBA_FILEY", defecto) is defecto
