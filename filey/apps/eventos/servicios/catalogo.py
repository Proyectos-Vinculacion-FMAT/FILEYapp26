"""
Los ocho tipos de actividad, para quien tiene que enseñarlos.

Existe para que ni la vista ni la plantilla hagan la consulta: el orden
es del dominio —el del selector que la Coordinación lee de arriba abajo,
no el alfabético— y se decide en un solo sitio.
"""

from ..models import MODELO_POR_TIPO, TIPOS_DE_PUBLICACION, CatalogoActividades


def tipos():
    """Los ocho, en el orden en que se enseñan."""
    return CatalogoActividades.objects.all()


def tipo_por_nombre(nombre: str) -> CatalogoActividades | None:
    """El tipo con ese nombre, o ``None`` si no existe.

    ``None`` y no excepción: el nombre llega de la barra de direcciones
    (`?tipo=…`), así que un valor inventado es entrada de usuario, no un
    error del sistema. Quien llama decide si eso es un 404 o simplemente
    no pintar la sección.
    """
    if nombre not in MODELO_POR_TIPO:
        return None
    return CatalogoActividades.objects.filter(nombre=nombre).first()


def es_publicacion(nombre: str) -> bool:
    """Si ese tipo es presentación de libro o de revista (`A1`).

    Son los dos que además piden archivos, ejemplar físico y una sinopsis
    más larga. Se pregunta por aquí y no comparando cadenas sueltas en
    tres pantallas distintas.
    """
    return nombre in TIPOS_DE_PUBLICACION
