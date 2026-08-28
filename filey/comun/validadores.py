"""
Validadores de formato que van a repetirse entre dominios.

Un teléfono y un código postal se piden en `STD` hoy, y se van a pedir en
`EVT` y en `VIS` en cuanto tengan formulario. Viven aquí y no en un
dominio para que la regla sea una sola: dos regex parecidas en dos apps
divergen en cuanto alguien arregla una.

.. note:: Qué se valida y qué no

   El objetivo es **cortar lo que claramente no es un teléfono ni un
   código postal**, no certificar que existan. Un validador demasiado
   estricto rechaza a un expositor de un país cuyo formato nadie previó,
   y eso cuesta más que un dato imperfecto que una persona va a leer de
   todas formas.
"""

import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

#: Dígitos, espacios, guiones, puntos, paréntesis y un `+` inicial. Con
#: al menos ocho dígitos: en México son diez —clave lada más número, como
#: pide la ficha—, y ocho deja pasar los formatos cortos de otros países
#: sin dejar pasar "1234".
telefono = RegexValidator(
    regex=r"^\+?[\d\s().-]{8,}$",
    message=(
        "Escribe el teléfono con clave lada, solo números "
        "(por ejemplo, 999 123 4567)."
    ),
)

#: Cinco dígitos exactos. Es el formato mexicano, y solo se aplica cuando
#: el domicilio es de México.
_CP_MEXICO = re.compile(r"^\d{5}$")

#: Fuera de México se admite casi cualquier cosa razonable: hay países
#: con letras (Canadá, Reino Unido) y con longitudes de tres a diez.
_CP_EXTRANJERO = re.compile(r"^[\w\s-]{3,10}$", re.UNICODE)


def validar_cp(codigo: str, pais: str) -> None:
    """El código postal, con el rigor que el país permite.

    Se valida **contra el país** y no con una sola regla porque los dos
    errores posibles cuestan cosas distintas: aceptar `"abc"` en un
    domicilio mexicano ensucia el dato sin que nadie se entere, y exigir
    cinco dígitos a una editorial de Toronto la deja fuera.

    :raises ValidationError: con un mensaje que dice el formato esperado.
    """
    codigo = (codigo or "").strip()
    if not codigo:
        return  # Que sea obligatorio lo decide el campo, no esto.

    if pais == "MX":
        if not _CP_MEXICO.match(codigo):
            raise ValidationError("En México el código postal son 5 dígitos.")
    elif not _CP_EXTRANJERO.match(codigo):
        raise ValidationError("Escribe un código postal válido.")
