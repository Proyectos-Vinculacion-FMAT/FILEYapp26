"""
Servir el mapa al componente que lo dibuja (`CU-STD-037`, `CU-STD-038`).

El showfloor lo pinta `event-stand-map` —un canvas de Godot embebido en un
`<iframe>`— y Django le manda los datos por `postMessage` (`ADR-0008`).
Aquí se produce **exactamente** el objeto que su contrato describe en
`docs/bridge_protocol.md`: `grid`, `stands` y `decorations`.

.. important:: El recorte de `RN-09` ocurre **aquí**, antes de enviar

   El contrato del componente lo dice con todas las letras: *"el mapa
   nunca decide qué esconder"*. Los tres estados viajan distintos para
   quien administra (`RN-18`) y colapsados en `ocupado` para quien
   aplica (`RN-09`).

   Que el recorte sea del servidor no es una preferencia de diseño: si el
   estado real viajara al navegador —aunque el canvas no lo pintara—
   cualquiera con las herramientas de desarrollo abiertas vería qué
   editorial tiene apartado qué espacio.

.. note:: `price` sí viaja, y `estado` no se traduce

   El precio se manda calculado porque el detalle del espacio lo pinta la
   página con lo que el canvas le devuelve en `openStand`. Y los estados
   del componente **ya son los del dominio** desde el 2026-08-27
   —`disponible`, `reservado`, `ocupado`—, así que no hay tabla de
   traducción: mandar los de antes daría tres espacios grises y tres
   mensajes de `error`.
"""

from decimal import ROUND_HALF_UP, Decimal

from ..models import DecoracionMapa, MapaShowfloor, Stand

#: Lo que se manda cuando quien mira no puede distinguir (`RN-09`).
OCUPADO = Stand.Estado.OCUPADO


def _forma(stand: Stand) -> dict:
    """La forma del espacio, en las claves del contrato.

    Un rectángulo va con `col`/`row`/`w`/`h`; uno irregular con `rects`,
    que el componente admite para las L y las T. El mapa de 2026 tiene
    tres.
    """
    if stand.rectangulos:
        return {
            "rects": [
                {
                    "col": r["col"],
                    "row": r["fila"],
                    "w": r["ancho_celdas"],
                    "h": r["alto_celdas"],
                }
                for r in stand.rectangulos
            ]
        }
    return {
        "col": stand.col,
        "row": stand.fila,
        "w": stand.ancho_celdas,
        "h": stand.alto_celdas,
    }


def _estado(stand: Stand, con_detalle: bool, mios: frozenset) -> str:
    """El estado con el que viaja un espacio. La línea que decide quién ve qué.

    Tres lecturas del mismo mapa:

    - **Quien administra** (`con_detalle`) ve los tres estados de
      `RN-10`, sin colapsar (`RN-18`).
    - **Quien aplica** ve `disponible` u `ocupado`: `reservado` y
      `ocupado` llegan colapsados (`RN-09`), porque distinguirlos diría
      cómo va el reparto del recinto.
    - **Sus propios espacios** viajan como `reservado`, que es el
      tercer color del componente. No rompe `RN-09`: lo que esa regla
      protege es lo de **los demás**, y de los suyos ya sabe todo — es
      justo lo que viene a ver en el mapa de su reserva. El componente
      solo admite tres estados (`bridge_protocol.md`), así que "el mío"
      se pinta con el que sobra, y la leyenda de la pantalla lo dice.
    """
    if con_detalle:
        return stand.estado
    if stand.clave in mios:
        return Stand.Estado.RESERVADO
    return stand.estado if stand.esta_libre else OCUPADO


def _stand(
    stand: Stand, costo_m2: Decimal, con_detalle: bool, mios: frozenset
) -> dict:
    datos = {
        "id": stand.clave,
        "label": stand.etiqueta,
        "status": _estado(stand, con_detalle, mios),
        # Redondeado, no truncado. `int()` de un `Decimal` corta hacia
        # cero, así que con un `costo_m2` con centavos la tarjeta del
        # mapa diría un peso menos que la pantalla de detalle —que sí
        # redondea— y las dos estarían hablando del mismo espacio.
        "price": int(stand.precio(costo_m2).quantize(Decimal("1"), ROUND_HALF_UP)),
        **_forma(stand),
    }
    if stand.zona:
        datos["zone"] = stand.zona
    return datos


def _decoracion(deco: DecoracionMapa) -> dict:
    if deco.tipo == DecoracionMapa.Tipo.TEXTO:
        return {"type": "text", "col": deco.col, "row": deco.fila, "text": deco.etiqueta}
    datos = {
        "type": "rect",
        "col": deco.col,
        "row": deco.fila,
        "w": deco.ancho_celdas,
        "h": deco.alto_celdas,
        "label": deco.etiqueta,
    }
    if deco.color:
        datos["color"] = deco.color
    return datos


def para_el_canvas(
    mapa: MapaShowfloor,
    *,
    costo_m2: Decimal,
    con_detalle: bool = False,
    mios: frozenset | set | tuple = (),
) -> dict:
    """El mapa en el formato de `bridge_protocol.md`.

    :param con_detalle: ``True`` para quien administra la feria
        (`CU-STD-038`: los tres estados de `RN-10`); ``False`` para quien
        aplica (`CU-STD-037`: `reservado` y `ocupado` colapsados).
    :param mios: las claves de los espacios de quien pregunta, para que
        pueda distinguirlos en el mapa de su reserva (`CU-STD-013`). Solo
        se usa cuando no hay `con_detalle`.

    `dimensions_text` **no se manda**: el componente lo deriva de la
    forma y de `meters_per_cell`, y mandarlo sería una segunda fuente
    para la misma cifra — la misma razón por la que `metros_cuadrados`
    no es una columna.
    """
    # `select_related("mapa")`: `Stand.precio` mide la superficie, que
    # sale de `metros_por_celda`. Sin esto son 151 consultas.
    stands = mapa.stands.select_related("mapa")
    return {
        "grid": {
            "cell_size": mapa.tamano_celda,
            "cols": mapa.columnas,
            "rows": mapa.filas,
            "meters_per_cell": float(mapa.metros_por_celda),
        },
        "stands": [
            _stand(s, costo_m2, con_detalle, frozenset(mios)) for s in stands
        ],
        "decorations": [_decoracion(d) for d in mapa.decoraciones.all()],
    }
