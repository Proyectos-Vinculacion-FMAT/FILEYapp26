"""
Límite de peticiones por IP (``comun/limites.py``).

Es la defensa que sustituyó al throttling de DRF cuando se retiró la
API REST. Se prueba aquí porque es fácil que una migración se lleve por
delante una protección sin que nada falle de forma visible.
"""

import pytest
from django.http import HttpResponse
from django.test import RequestFactory

from comun import limites

pytestmark = pytest.mark.django_db


def _vista(peticion):
    return HttpResponse("ok")


def _peticion(ip="203.0.113.7", metodo="post"):
    fabrica = RequestFactory()
    hacer = getattr(fabrica, metodo)
    return hacer("/acceso/", REMOTE_ADDR=ip)


def test_deja_pasar_hasta_el_tope_y_luego_corta(settings):
    settings.LIMITES_PETICIONES = {"prueba": "3/min"}
    protegida = limites.limitar("prueba")(_vista)

    for _ in range(3):
        assert protegida(_peticion()).status_code == 200

    respuesta = protegida(_peticion())
    assert respuesta.status_code == 429
    assert int(respuesta["Retry-After"]) > 0


def test_el_limite_es_por_ip(settings):
    settings.LIMITES_PETICIONES = {"prueba": "1/min"}
    protegida = limites.limitar("prueba")(_vista)

    assert protegida(_peticion(ip="198.51.100.1")).status_code == 200
    assert protegida(_peticion(ip="198.51.100.1")).status_code == 429
    # Otra IP arranca con su propia cuota.
    assert protegida(_peticion(ip="198.51.100.2")).status_code == 200


def test_los_get_no_consumen_cuota(settings):
    """Recargar la pantalla no debe gastar los intentos de nadie."""
    settings.LIMITES_PETICIONES = {"prueba": "1/min"}
    protegida = limites.limitar("prueba")(_vista)

    for _ in range(5):
        assert protegida(_peticion(metodo="get")).status_code == 200

    assert protegida(_peticion()).status_code == 200


def test_la_respuesta_de_corte_no_dice_nada_del_correo(settings):
    """El limitador no puede volverse un oráculo de cuentas existentes."""
    settings.LIMITES_PETICIONES = {"prueba": "0/min"}
    protegida = limites.limitar("prueba")(_vista)

    respuesta = protegida(_peticion())

    assert respuesta.status_code == 429
    assert respuesta.content == b""


def test_respeta_la_ip_reenviada_por_el_proxy(settings):
    settings.LIMITES_PETICIONES = {"prueba": "1/min"}
    protegida = limites.limitar("prueba")(_vista)
    fabrica = RequestFactory()

    def con_proxy(ip_real):
        return fabrica.post(
            "/acceso/", REMOTE_ADDR="10.0.0.1", HTTP_X_FORWARDED_FOR=f"{ip_real}, 10.0.0.1"
        )

    assert protegida(con_proxy("203.0.113.10")).status_code == 200
    assert protegida(con_proxy("203.0.113.10")).status_code == 429
    assert protegida(con_proxy("203.0.113.11")).status_code == 200


def test_los_ambitos_reales_estan_configurados(settings):
    """Si alguien borra un ámbito, la vista que lo usa revienta al arrancar."""
    assert "auth-identificar" in settings.LIMITES_PETICIONES
    assert "auth-otp" in settings.LIMITES_PETICIONES
