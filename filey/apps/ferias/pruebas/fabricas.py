"""
Fábricas de ferias para las pruebas que **no** necesitan un schema.

Crear una feria de verdad dispara las migraciones de todos los dominios
de contenido y tarda segundos. La mayoría de las pruebas —permisos,
listados, redirecciones— solo necesitan la fila en `public`, así que
pagan eso sin ganar nada.

Las que sí prueban el aislamiento usan las fixtures de `conftest.py`,
que crean el schema de verdad. La diferencia es deliberada: si una
prueba de aislamiento se apoyara en esto, comprobaría nada.

Vive aquí y no en un `conftest.py` porque lo usan dos paquetes de
pruebas —`ferias` y `registros`—, y un `conftest.py` no se importa desde
otro.
"""

from ..models import Feria


def feria_sin_schema(nombre, slug, estado=Feria.Estado.ACTIVA) -> Feria:
    """Una `Feria` que NO crea su schema.

    ``auto_create_schema`` se pone en la instancia y no se pasa al
    constructor porque es un **atributo de clase** de ``TenantMixin``,
    no una columna: como kwarg, ``Model.__init__`` lo rechaza.
    """
    feria = Feria(
        nombre=nombre, slug=slug, schema_name=f"feria_{slug}", estado=estado
    )
    feria.auto_create_schema = False
    feria.save()
    return feria
