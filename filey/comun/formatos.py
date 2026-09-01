"""Cómo se escriben las cifras que ve la gente.

Vive en `comun` y no en un dominio porque el mismo importe sale por dos
puertas —la plantilla y el aviso que deja una vista— y escribirlo de dos
formas en la misma pantalla es un error que nadie reporta y todo el mundo
nota: el saldo dice `$27,000.00` y el mensaje de encima `$27000.00`.

Los dominios lo alcanzan por el filtro `{% load dinero %}{{ x|pesos }}`
(`apps/stands/templatetags/dinero.py`), que solo lo registra.
"""

from decimal import Decimal, InvalidOperation


def pesos(valor) -> str:
    """Un importe como se escribe en una factura: `$27,000.00`.

    El separador de millares no es adorno: el saldo de la cuenta del
    expositor se lee a 32 px (`CU-STD-013`), y a ese tamaño `$27000.00`
    hay que contarlo con el dedo para saber si son veintisiete mil o
    doscientos setenta mil.

    Con `None` devuelve una raya y no `$0.00`: un importe que no existe y
    uno que vale cero son cosas distintas, y confundirlas en una cuenta
    por pagar sale caro.
    """
    if valor is None or valor == "":
        return "—"
    try:
        cantidad = Decimal(valor)
    except (InvalidOperation, TypeError, ValueError):
        return "—"
    # El signo delante del peso y no entre los dos (`-$3,000.00`, nunca
    # `$-3,000.00`): así se escribe un descuento en el desglose, y es
    # donde el ojo lo busca al recorrer la columna.
    signo = "-" if cantidad < 0 else ""
    return f"{signo}${abs(cantidad):,.2f}"
