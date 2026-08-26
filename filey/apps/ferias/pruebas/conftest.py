"""
Fixtures de las pruebas que necesitan **schemas de verdad**.

A diferencia de las de `apps/registros/pruebas/`, que crean ferias sin
schema porque solo miran permisos, aquí el schema es lo que se prueba:
sin crearlo no hay nada que aislar. Cada una cuesta una tanda de
migraciones, así que son pocas y a propósito.
"""

import pytest
from django.db import connection

from apps.ferias.servicios import altas


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
    """Una feria completa: fila, schema migrado, slug de ruteo y dueña."""
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
