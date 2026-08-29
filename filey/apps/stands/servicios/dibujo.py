"""
Convertir un mapa en algo que una plantilla pueda pintar.

El showfloor se dibuja en **SVG servido por el servidor**, no por un
componente de JavaScript. Es la regla 6 de `CLAUDE.md`: toda pantalla
funciona sin JavaScript. Un mapa hecho con `<path>` y `<a>` se navega con
el teclado, se imprime, y sigue ahí si el script no carga; lo que
JavaScript añade encima —el zoom, el resaltado— es mejora, no requisito.

Aquí no se decide **quién ve qué**. Eso lo hace `vista_para`, que recibe
si quien mira administra la feria, y es lo único que separa `CU-STD-009`
(el aplicante ve `disponible` / `ocupado`) de `CU-STD-032` (quien
administra ve los tres estados de `RN-10`).
"""

from dataclasses import dataclass
from decimal import Decimal

from ..models import DecoracionMapa, MapaShowfloor, Stand


@dataclass(frozen=True)
class Pieza:
    """Una caja ya lista para el `<svg>`, sin nada que decidir."""

    clave: str
    etiqueta: str
    contorno: str
    #: Dónde va el rótulo y de qué tamaño, en unidades de celda.
    x: float
    y: float
    tamano_texto: float
    estado: str
    #: Lo que se le enseña a quien mira: `disponible` u `ocupado` para el
    #: aplicante (`RN-09`), el estado real para quien administra.
    aspecto: str
    metros_cuadrados: Decimal
    precio: Decimal
    libre: bool

    @property
    def aspecto_texto(self) -> str:
        """El estado en palabras, para el `<title>` del SVG.

        Es lo que lee un lector de pantalla y lo que sale en el globo del
        ratón, así que dice `Ocupado` y no `ocupado`.
        """
        return dict(Stand.Estado.choices).get(self.aspecto, self.aspecto).capitalize()


@dataclass(frozen=True)
class Vista:
    """Todo lo que la plantilla necesita para pintar un mapa."""

    columnas: int
    filas: int
    salon: str
    piezas: list[Pieza]
    decoraciones: list[Pieza]
    libres: int
    total: int

    @property
    def proporcion(self) -> str:
        """Para que el `<svg>` reserve su sitio antes de pintarse."""
        return f"{self.columnas} / {self.filas}"


def contorno(celdas: set[tuple[int, int]]) -> str:
    """El perímetro de un conjunto de celdas, como un `d` de SVG.

    Se juntan las cuatro aristas de cada celda y se tiran las que
    aparecen dos veces —las interiores—; las que quedan se encadenan en
    bucles.

    Hace falta porque un stand irregular son varios rectángulos, y
    dibujarlos por separado deja una costura por dentro: se vería como
    dos stands pegados en vez de uno en L.
    """
    aristas = {}
    for c, f in celdas:
        for a, b in (
            ((c, f), (c + 1, f)),
            ((c + 1, f), (c + 1, f + 1)),
            ((c + 1, f + 1), (c, f + 1)),
            ((c, f + 1), (c, f)),
        ):
            if (b, a) in aristas:
                del aristas[(b, a)]
            else:
                aristas[(a, b)] = True

    salientes: dict = {}
    for a, b in aristas:
        salientes.setdefault(a, []).append(b)

    partes = []
    while salientes:
        inicio = next(iter(salientes))
        bucle, actual = [inicio], inicio
        while True:
            siguiente = salientes[actual].pop()
            if not salientes[actual]:
                del salientes[actual]
            if siguiente == inicio:
                break
            bucle.append(siguiente)
            actual = siguiente
        # Fuera los vértices en línea recta: mismo dibujo, menos bytes.
        # Un mapa de 151 stands se sirve en cada visita.
        limpio = [
            p
            for i, p in enumerate(bucle)
            if not (
                (bucle[i - 1][0] == p[0] == bucle[(i + 1) % len(bucle)][0])
                or (bucle[i - 1][1] == p[1] == bucle[(i + 1) % len(bucle)][1])
            )
        ]
        partes.append("M" + " L".join(f"{x} {y}" for x, y in limpio) + " Z")
    return " ".join(partes)


def _rotulo(formas: list[dict]) -> tuple[float, float, float]:
    """Dónde cabe el rótulo: en medio del rectángulo más grande.

    En un stand en L, el centro de la envolvente cae en el hueco —encima
    del vecino—, así que se usa el trozo más ancho y no el conjunto.
    """
    mayor = max(formas, key=lambda r: r["ancho_celdas"] * r["alto_celdas"])
    menor_lado = min(mayor["ancho_celdas"], mayor["alto_celdas"])
    return (
        mayor["col"] + mayor["ancho_celdas"] / 2,
        mayor["fila"] + mayor["alto_celdas"] / 2,
        round(min(2.2, menor_lado * 0.85), 2),
    )


def _pieza_de(stand: Stand, costo_m2: Decimal, con_detalle: bool) -> Pieza:
    x, y, tamano = _rotulo(stand.formas)
    return Pieza(
        clave=stand.clave,
        etiqueta=stand.etiqueta,
        contorno=contorno(stand.celdas),
        x=x,
        y=y,
        tamano_texto=tamano,
        estado=stand.estado,
        # `RN-09`: quien aplica no distingue `reservado` de `ocupado`.
        # Saber cuál es no le sirve de nada y sí dice quién va ganando el
        # reparto del recinto, así que los dos llegan colapsados.
        aspecto=stand.estado if con_detalle else (
            Stand.Estado.DISPONIBLE if stand.esta_libre else Stand.Estado.OCUPADO
        ),
        metros_cuadrados=stand.metros_cuadrados,
        precio=stand.precio(costo_m2),
        libre=stand.esta_libre,
    )


def _pieza_de_decoracion(deco: DecoracionMapa) -> Pieza:
    if deco.tipo == DecoracionMapa.Tipo.TEXTO:
        celdas, formas = set(), [
            {"col": deco.col, "fila": deco.fila, "ancho_celdas": 1, "alto_celdas": 1}
        ]
    else:
        formas = [
            {
                "col": deco.col,
                "fila": deco.fila,
                "ancho_celdas": deco.ancho_celdas,
                "alto_celdas": deco.alto_celdas,
            }
        ]
        celdas = {
            (c, f)
            for c in range(deco.col, deco.col + deco.ancho_celdas)
            for f in range(deco.fila, deco.fila + deco.alto_celdas)
        }
    x, y, tamano = _rotulo(formas)
    return Pieza(
        clave="",
        etiqueta=deco.etiqueta,
        contorno=contorno(celdas) if celdas else "",
        x=x,
        y=y,
        # Los rótulos de las salas son largos: se pintan más chicos que
        # el número de un stand o no caben en su caja.
        tamano_texto=round(min(2.0, tamano * 0.55), 2),
        estado=deco.tipo,
        aspecto=deco.tipo,
        metros_cuadrados=Decimal("0"),
        precio=Decimal("0"),
        libre=False,
    )


def vista_para(
    mapa: MapaShowfloor, *, costo_m2: Decimal, con_detalle: bool = False
) -> Vista:
    """El mapa listo para pintar.

    :param con_detalle: ``True`` para quien administra la feria
        (`CU-STD-032`: ve los tres estados de `RN-10`); ``False`` para
        quien aplica (`CU-STD-009`: solo si puede reservarlo o no).
    """
    # `select_related("mapa")` y no `.all()`: `Stand.metros_cuadrados`
    # pregunta por `metros_por_celda`, que vive en el mapa. Sin esto son
    # 151 consultas —una por espacio— para un dato que ya tenemos en la
    # mano, y el mapa se pinta en cada visita.
    stands = list(mapa.stands.select_related("mapa"))
    piezas = [_pieza_de(s, costo_m2, con_detalle) for s in stands]
    return Vista(
        columnas=mapa.columnas,
        filas=mapa.filas,
        salon=mapa.salon,
        piezas=piezas,
        decoraciones=[_pieza_de_decoracion(d) for d in mapa.decoraciones.all()],
        libres=sum(1 for p in piezas if p.libre),
        total=len(piezas),
    )
