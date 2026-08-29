"""
El carrito de stands (`CU-STD-011`).

Es una **selección de trabajo**: no aparta ni bloquea nada. Los espacios
se protegen solo al confirmar la reserva (`CU-STD-012`), y eso es lo que
hace que "primero en confirmar gana" sea la regla y no "primero en meter
al carrito".

Vive en la sesión de Django (`ADR-0002`), no en una tabla. Un carrito es
un borrador que la mayoría de la gente abandona: guardarlo llenaría la
base de selecciones muertas que nadie limpia, y no compra nada — nada
depende de que sobreviva a cerrar el navegador.

Se guarda **una clave por convocatoria**: una feria puede tener una
convocatoria general y otra de pabellón, y mezclar sus carritos daría una
reserva con stands de dos mapas distintos.
"""

from dataclasses import dataclass
from decimal import Decimal

from ..models import Stand

#: Prefijo de la clave en la sesión. La convocatoria va detrás.
CLAVE = "stands:carrito"


def _clave(convocatoria) -> str:
    return f"{CLAVE}:{convocatoria.pk}"


@dataclass(frozen=True)
class Linea:
    """Un stand del carrito, con lo que cuesta hoy."""

    stand: Stand
    metros_cuadrados: Decimal
    precio: Decimal

    @property
    def disponible(self) -> bool:
        return self.stand.esta_libre


@dataclass(frozen=True)
class Contenido:
    """El carrito ya resuelto contra el mapa."""

    lineas: list[Linea]
    subtotal: Decimal
    #: Los que alguien reservó mientras esta persona decidía (`E1`).
    #: Se enseñan, no se tiran en silencio: quien armó una selección de
    #: ocho espacios tiene que ver **cuál** perdió.
    no_disponibles: list[Linea]

    @property
    def vacio(self) -> bool:
        return not self.lineas

    @property
    def metros_cuadrados(self) -> Decimal:
        """La superficie de lo **tomable**, no de todo lo elegido.

        Igual que el subtotal: contar lo que alguien ya reservó daría
        unos metros que no se pueden comprar.
        """
        return sum(
            (linea.metros_cuadrados for linea in self.lineas if linea.disponible),
            start=Decimal("0"),
        )

    @property
    def claves(self) -> list[str]:
        return [linea.stand.clave for linea in self.lineas]


def claves_en(sesion, convocatoria) -> list[str]:
    """Lo guardado, tal cual. Puede nombrar stands que ya no existen."""
    return list(sesion.get(_clave(convocatoria), []))


def _guardar(sesion, convocatoria, claves) -> None:
    sesion[_clave(convocatoria)] = list(dict.fromkeys(claves))
    # La sesión no detecta que una lista mutó por dentro; sin esto, un
    # carrito modificado se pierde al terminar la petición.
    sesion.modified = True


def agregar(sesion, convocatoria, clave: str) -> None:
    """Mete un stand. Repetirlo no lo duplica.

    **No comprueba disponibilidad aquí.** La comprobación que vale es la
    de `CU-STD-012` paso 5, con los stands bloqueados; la de ahora se
    quedaría vieja en el tiempo que la persona tarda en decidir. Lo que
    sí hace `contenido()` es enseñar cuáles dejaron de estar libres.
    """
    _guardar(sesion, convocatoria, [*claves_en(sesion, convocatoria), clave])


def quitar(sesion, convocatoria, clave: str) -> None:
    """`A1`. Quitar algo que no está no es un error."""
    _guardar(
        sesion,
        convocatoria,
        [c for c in claves_en(sesion, convocatoria) if c != clave],
    )


def vaciar(sesion, convocatoria) -> None:
    sesion.pop(_clave(convocatoria), None)
    sesion.modified = True


def contenido(sesion, convocatoria, mapa, costo_m2: Decimal) -> Contenido:
    """El carrito resuelto contra el mapa de ahora mismo.

    Las claves que ya no existen —porque se reimportó el mapa— se
    descartan sin decir nada: no son una pérdida del expositor, es que
    ese espacio dejó de existir en el recinto.
    """
    guardadas = claves_en(sesion, convocatoria)
    if not guardadas:
        return Contenido(lineas=[], subtotal=Decimal("0.00"), no_disponibles=[])

    por_clave = {
        s.clave: s
        for s in mapa.stands.select_related("mapa").filter(clave__in=guardadas)
    }
    libres, tomados = [], []
    for clave in guardadas:
        stand = por_clave.get(clave)
        if stand is None:
            continue
        linea = Linea(
            stand=stand,
            metros_cuadrados=stand.metros_cuadrados,
            precio=stand.precio(costo_m2),
        )
        (libres if stand.esta_libre else tomados).append(linea)

    return Contenido(
        lineas=libres + tomados,
        # El subtotal cuenta **solo lo que todavía se puede tomar**:
        # sumar lo perdido daría una cifra que nadie va a pagar.
        subtotal=sum((linea.precio for linea in libres), start=Decimal("0.00")),
        no_disponibles=tomados,
    )
