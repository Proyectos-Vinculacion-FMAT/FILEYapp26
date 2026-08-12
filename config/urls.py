"""
URLs raíz. Cada dominio se monta con su propio namespace, espejando la estructura
de prototipo/{DOM}/ y los prefijos de caso de uso de docs/requisitos/.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("apps.core.urls", "core"), namespace="core")),
    # Conforme se implementen:
    # path("acceso/",    include(("apps.reg.urls", "reg"), namespace="reg")),
    # path("eventos/",   include(("apps.evt.urls", "evt"), namespace="evt")),
    # path("visitas/",   include(("apps.vis.urls", "vis"), namespace="vis")),
]
