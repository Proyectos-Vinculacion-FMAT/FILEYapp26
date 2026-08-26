"""
Cómo se pinta cada tipo de convocatoria.

Esto es presentación, así que no sale de la vista: el contrato del
proyecto dice que una vista expone nombres de dominio —``tipo``,
``estado``— y nunca ``clase_css`` ni ``texto_boton`` (skill
`filey-render` §5). La traducción de `EVT` a un degradado verde se
decide aquí, que es la capa de plantillas.

Los nombres de clase son los del prototipo (`banner-eventos`,
`banner-stand`, `banner-visitas`) y ya existen en `filey.css`: esta
pantalla no añade CSS.
"""

from django import template

from ..models import TipoConvocatoria

register = template.Library()

# `TAL` no está porque `TipoConvocatoria` tampoco lo tiene: falta
# decidir si es un cuarto tipo o una convocatoria `EVT` con otro público
# (ver el índice de `FER`). Cuando se decida, el banner `banner-infantil`
# ya existe en la hoja, esperando.
PRESENTACION = {
    TipoConvocatoria.EVT: {"icono": "🎤", "banner": "banner-eventos"},
    TipoConvocatoria.STD: {"icono": "🏬", "banner": "banner-stand"},
    TipoConvocatoria.VIS: {"icono": "🚌", "banner": "banner-visitas"},
}

POR_DEFECTO = {"icono": "📄", "banner": "banner-eventos"}


@register.filter
def icono_de(tipo: str) -> str:
    """El emoji del banner. Un tipo desconocido cae en uno neutro."""
    return PRESENTACION.get(tipo, POR_DEFECTO)["icono"]


@register.filter
def banner_de(tipo: str) -> str:
    """La clase de degradado del banner, del mismo modo."""
    return PRESENTACION.get(tipo, POR_DEFECTO)["banner"]
