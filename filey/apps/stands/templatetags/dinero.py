"""El importe de `comun.formatos`, como filtro de plantilla.

Solo registra: la regla de cómo se escribe una cifra vive en un sitio, y
las vistas la usan desde ahí para sus avisos.
"""

from django import template

from comun.formatos import pesos as _pesos

register = template.Library()

register.filter("pesos", _pesos)
