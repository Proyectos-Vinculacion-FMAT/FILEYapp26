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

#: Cuántos dígitos hace falta reconocer para dar algo por teléfono. Sale
#: de `CU-REG-001`: *"al menos 10 dígitos"*, que es clave lada más número
#: en México.
#:
#: .. warning:: Deja fuera formatos extranjeros legítimos
#:
#:    Un móvil español son nueve dígitos. La misma pantalla que exige
#:    diez pide también el país, así que la regla y el catálogo de países
#:    se contradicen para quien escribe desde fuera de Norteamérica. Es
#:    una regla escrita —`CU-REG-001`, "Datos relevantes"— y por eso se
#:    respeta tal cual; corregirla es decisión del equipo, no de aquí.
MINIMO_DIGITOS_TELEFONO = 10


def solo_digitos(valor: str) -> str:
    """El teléfono con solo sus dígitos.

    Es lo que se guarda, para que "999 000 0000" y "9990000000" sean el
    mismo teléfono al comparar. Sin esto, buscar un duplicado obliga a
    normalizar en cada consulta — y a acordarse de hacerlo.
    """
    return re.sub(r"\D", "", valor or "")


def telefono(valor: str) -> None:
    """Que lo escrito se parezca a un número al que se pueda llamar.

    Cuenta **dígitos** en vez de casar un formato completo porque la
    gente escribe el suyo de cinco maneras —con lada entre paréntesis,
    con guiones, con `+52`— y todas son correctas. Lo que se rechaza es
    lo que no tiene números suficientes para ser un teléfono.

    :raises ValidationError: con el mínimo dicho en voz alta.
    """
    if len(solo_digitos(valor)) < MINIMO_DIGITOS_TELEFONO:
        raise ValidationError(
            f"El teléfono debe tener al menos {MINIMO_DIGITOS_TELEFONO} dígitos, "
            "con clave lada (por ejemplo, 999 123 4567)."
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
