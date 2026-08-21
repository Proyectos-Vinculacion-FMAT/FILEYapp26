"""
Rutas raíz del monolito.

Cada módulo de dominio se monta aquí bajo su propio prefijo conforme se
construya (`eventos/`, `talleres/`, `stands/`, `visitas/`). `registros`
va en la raíz porque es la puerta de entrada del sistema: el acceso, el
código y las convocatorias no cuelgan de ningún dominio.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin interno de Django (inspección de datos del equipo), bajo un
    # prefijo propio para no chocar con /admin/ del panel FILEY.
    path("django-admin/", admin.site.urls),
    path("", include("apps.registros.urls")),
]
