"""
Cómo se lee una propuesta ya enviada (`CU-EVT-003`, paso 4).

El gemelo de solo lectura de `formularios.py`. El paso 4 pide «todos los
datos enviados», y son distintos en cada uno de los ocho tipos: entre una
charla y una presentación de libro hay veinticinco columnas de
diferencia. Esto compone esos datos en bloques que la plantilla solo
recorre.

.. note:: El orden sale del formulario, no se vuelve a escribir

   Cada formulario declara su ``orden`` —calcado del diagrama del
   modelo— y aquí se reutiliza tal cual. Así el detalle enseña los campos
   en el mismo orden en que se capturaron, que es lo que hace posible
   comparar la pantalla con lo que uno recuerda haber escrito, y no hay
   una segunda lista que se pueda separar de la primera.

.. note:: Por qué no está en `servicios/`

   Aquí no se decide nada: no hay regla que un comando de `manage.py`
   tenga que poder llamar sin pasar por HTTP. Es composición para pintar,
   igual que `formularios.py`, y por eso vive a su lado y no una carpeta
   más adentro.
"""

from .formularios import FORMULARIO_POR_TIPO, Campo, Personas

#: Lo que se enseña cuando un campo opcional se quedó vacío. Un hueco en
#: blanco no distingue «no lo llenó» de «la pantalla se rompió».
VACIO = "—"


def bloques_del_tipo(actividad):
    """Los datos propios del tipo, en el orden en que se capturaron.

    :param actividad: la `Actividad` de la solicitud. Se baja a la fila
        hija con ``.detalle``, que es quien tiene las columnas.
    :returns: lista de ``{"clase": "campo"|"personas", …}``.
    """
    hija = actividad.detalle
    orden = FORMULARIO_POR_TIPO[actividad.tipo.nombre].orden

    bloques = []
    for pieza in orden:
        if isinstance(pieza, Campo):
            bloques.append(_campo(hija, pieza.nombre))
        else:
            bloques.append(_personas(hija, pieza))
    return bloques


def _campo(hija, nombre: str) -> dict:
    """Un campo suelto, con su rótulo y su valor ya legible."""
    campo = hija._meta.get_field(nombre)
    if campo.choices:
        # «Autor/a», no «autor». El valor de la columna es un código.
        valor = getattr(hija, f"get_{nombre}_display")()
    else:
        valor = getattr(hija, nombre)
    return {
        "clase": "campo",
        "etiqueta": campo.verbose_name,
        "valor": valor or VACIO,
    }


def _personas(hija, lista: Personas) -> dict:
    """Una lista de personas, **sin las filas que nadie llenó**.

    El formulario pinta las cinco de un libro porque hay que poder
    escribir en ellas; aquí se pintan las que tienen a alguien dentro.
    Enseñar «Autor 4: —» tres veces seguidas no informa de nada y empuja
    hacia abajo lo que sí se llenó.

    `validar_personas` garantiza que las capturadas son 1..n seguidas, así
    que cortar en la primera vacía sería equivalente; se filtra igual
    porque una fila con hueco escrita a mano en la base no debería
    esconder a las de después.
    """
    filas = []
    for n in range(1, lista.maximo + 1):
        nombre = (getattr(hija, f"nombre_{lista.prefijo}_{n}") or "").strip()
        if not nombre:
            continue
        participa = getattr(hija, f"{lista.prefijo}_{n}_participa", None)
        filas.append(
            {
                "etiqueta": f"{lista.etiqueta} {n}".capitalize(),
                "nombre": nombre,
                "semblanza": getattr(hija, f"semblanza_{lista.prefijo}_{n}", ""),
                # `None` en los seis tipos que no preguntan si asiste, y
                # entonces la plantilla no pinta nada. `False` sí se
                # pinta: que un autor no vaya a estar es un dato.
                "participa": participa,
            }
        )
    return {
        "clase": "personas",
        # «Los autores» a partir de «el autor», que es lo que declara el
        # formulario para el rótulo de una fila.
        "titulo": _plural(lista.etiqueta),
        "filas": filas,
    }


def _plural(etiqueta: str) -> str:
    """«el autor» → «Autores». Solo para el encabezado de un grupo.

    Los seis rótulos que hay hoy son «el participante», «quien imparte»,
    «el autor», «el editor» y «el presentador». Los que empiezan por
    artículo se pluralizan; «quien imparte» no tiene plural que valga la
    pena inventar y se queda como está, con mayúscula.
    """
    for articulo in ("el ", "la ", "los ", "las "):
        if etiqueta.startswith(articulo):
            palabra = etiqueta[len(articulo) :]
            return (palabra + ("es" if palabra.endswith("r") else "s")).capitalize()
    return etiqueta.capitalize()
