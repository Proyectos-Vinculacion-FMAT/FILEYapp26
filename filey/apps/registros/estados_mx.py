"""
Catálogo de las entidades federativas de México (ISO 3166-2:MX).

Se guarda el **código de tres letras**, no el nombre, por lo mismo que
`paises.py` guarda «MX» y no «México»: el nombre se escribe de varias
formas —«Ciudad de México», «CDMX», «Distrito Federal», «Edo. de
México», «Estado de México»— y un catálogo libre acaba con cuatro filas
para la misma entidad en el mismo informe.

Los códigos son los de ISO 3166-2:MX sin el prefijo `MX-`. Dos merecen
una nota porque su nombre oficial cambió y el código no, que es
exactamente la razón de guardar el código:

- ``CMX`` es la Ciudad de México, antes Distrito Federal (``DIF``).
- ``VER`` es Veracruz de Ignacio de la Llave; ``MIC``, Michoacán de
  Ocampo; ``COA``, Coahuila de Zaragoza. Se listan por el nombre de uso
  corriente, que es el que la gente busca en un desplegable.

Solo aplica cuando el país es México (`CU-REG-001`): fuera de México
esto no se pregunta, porque un catálogo de 32 entidades mexicanas no
describe una dirección en Bogotá ni en Madrid.
"""

#: Yucatán primero y marcado por omisión: FILEY es la feria de Yucatán y
#: de ahí viene la mayoría de quien se registra. El resto va en orden
#: alfabético.
#:
#: .. note:: Es la misma decisión que «México primero» en `paises.py`
#:
#:    Ahorrar el desplazamiento a la mayoría es la diferencia entre un
#:    campo que se llena bien y uno que se llena con lo primero que
#:    quede a mano.
ESTADO_POR_DEFECTO = "YUC"

ESTADOS_MX = [
    ("YUC", "Yucatán"),
    ("AGU", "Aguascalientes"),
    ("BCN", "Baja California"),
    ("BCS", "Baja California Sur"),
    ("CAM", "Campeche"),
    ("CHP", "Chiapas"),
    ("CHH", "Chihuahua"),
    ("CMX", "Ciudad de México"),
    ("COA", "Coahuila"),
    ("COL", "Colima"),
    ("DUR", "Durango"),
    ("MEX", "Estado de México"),
    ("GUA", "Guanajuato"),
    ("GRO", "Guerrero"),
    ("HID", "Hidalgo"),
    ("JAL", "Jalisco"),
    ("MIC", "Michoacán"),
    ("MOR", "Morelos"),
    ("NAY", "Nayarit"),
    ("NLE", "Nuevo León"),
    ("OAX", "Oaxaca"),
    ("PUE", "Puebla"),
    ("QUE", "Querétaro"),
    ("ROO", "Quintana Roo"),
    ("SLP", "San Luis Potosí"),
    ("SIN", "Sinaloa"),
    ("SON", "Sonora"),
    ("TAB", "Tabasco"),
    ("TAM", "Tamaulipas"),
    ("TLA", "Tlaxcala"),
    ("VER", "Veracruz"),
    ("ZAC", "Zacatecas"),
]

NOMBRES_POR_CODIGO = dict(ESTADOS_MX)


def nombre_de(codigo: str) -> str:
    """Etiqueta legible de un código, o el propio código si no está.

    No lanza, igual que `paises.nombre_de`: un código que ya no esté en
    el catálogo no debe reventar la ficha de quien se registró cuando sí
    estaba.
    """
    return NOMBRES_POR_CODIGO.get(codigo or "", codigo or "")
