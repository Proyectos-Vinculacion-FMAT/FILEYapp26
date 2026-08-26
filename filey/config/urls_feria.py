"""
Rutas de **dentro de una feria** — `/f/<slug>/…` (`ROOT_URLCONF`).

`django-tenants` no las monta tal cual: envuelve estos patrones en un
resolver que antepone `f/<slug>/`, así que aquí se escriben **sin** el
prefijo. La contrapartida buena es que `{% url %}` y `reverse()`
normales ya devuelven la URL con su feria; no hay que pasar el slug a
mano por ninguna plantilla.

Aquí se montarán los dominios de contenido (`eventos/`, `talleres/`,
`stands/`, `visitas/`) conforme se construyan: todos son contenido de
una edición, y ninguno vive fuera de una.
"""

from django.urls import path

from apps.ferias import views

urlpatterns = [
    path("", views.portada, name="feria_portada"),
]
