"""
La barra de estados de una cola del panel, para cualquier módulo.

Es la mitad en Python de `plantillas/componentes/filtros.html`: una arma
los chips y la otra los pinta. Subieron juntas desde `apps/stands` cuando
`EVT` necesitó la misma cola de revisión — una app vertical no puede
importar de otra (regla 4 de `CLAUDE.md`), y dos copias de un filtro se
separan a la primera corrección.

Nada de aquí sabe de qué dominio es la cola: recibe conteos y opciones, y
devuelve una lista de diccionarios.
"""

from django.utils.http import urlencode


def chips_de_estado(
    conteos: dict,
    opciones,
    activo: str,
    busqueda: str,
    *,
    total: int | None = None,
    etiqueta_vacio: str = "Todas",
    otros: dict | None = None,
) -> list:
    """La barra de estados de una cola, con cuántas hay en cada uno.

    Sustituye al `<select>` que había: son pocas opciones excluyentes y
    conocidas, y con la lista desplegada **se ve el vocabulario entero
    sin abrir nada** (ley de Hick, tope de siete). Además cada una dice
    su número, que es lo que quien revisa viene a saber —"¿qué necesita
    de mí hoy?"— sin tener que filtrar para averiguarlo.

    Elegir un estado **es** filtrar: cada chip es un enlace, no un
    control que después haya que enviar. Un clic en vez de dos, y el
    filtro sigue siendo compartible por GET.

    :param conteos: ``{valor_del_estado: cuántas}``. Las que no aparecen
        salen en cero, y eso es información: "Rechazadas 0" dice algo
        distinto de que la fila no exista.
    :param opciones: pares ``(valor, etiqueta)``, incluida cualquier
        pseudo-columna como las reservas vencidas de `STD`.
    :param busqueda: se arrastra en el enlace. Cambiar de estado no debe
        borrar en silencio lo que alguien tecleó.
    :param total: cuántas hay en «Todas», si no es la suma de los
        conteos. Hace falta cuando alguna opción no es un estado sino un
        recorte de otro —las reservas vencidas son `por_confirmar` con el
        plazo pasado (`RN-12`)—: sumarla contaría dos veces las mismas.
    :param etiqueta_vacio: cómo se llama el primer chip, el que no lleva
        parámetro. Es «Todas» en las colas que no filtran de entrada, y
        la cola de pagos lo cambia porque **entrar ahí ya es filtrar**:
        su estado natural es «por validar», que es el trabajo del día.
    :param otros: los demás filtros puestos, que también viajan en el
        enlace. Es lo mismo que hace ``busqueda`` y por la misma razón: la
        cola de `EVT` filtra además por tipo de actividad y categoría, y
        cambiar de estado no debe borrar en silencio lo que ya estaba
        elegido. Los valores vacíos se descartan, para que la dirección no
        se llene de parámetros que no filtran nada.
    """
    filtro = {"q": busqueda} if busqueda else {}
    filtro.update({clave: valor for clave, valor in (otros or {}).items() if valor})
    chips = [
        {
            "etiqueta": etiqueta_vacio,
            "cuantas": sum(conteos.values()) if total is None else total,
            "activo": not activo,
            "parametros": urlencode(filtro),
        }
    ]
    for valor, etiqueta in opciones:
        chips.append(
            {
                "etiqueta": etiqueta,
                "cuantas": conteos.get(valor, 0),
                "activo": valor == activo,
                "parametros": urlencode({**filtro, "estado": valor}),
            }
        )
    return chips
