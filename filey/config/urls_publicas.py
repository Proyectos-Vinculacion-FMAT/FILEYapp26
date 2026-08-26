"""
Rutas de **fuera de toda feria** — schema `public` (`PUBLIC_SCHEMA_URLCONF`).

Es lo que se sirve cuando la URL no empieza por `/f/<slug>/`: la puerta
de entrada al sistema (acceso, código, alta de cuenta) y el admin
interno de Django. Nada de aquí depende de una edición concreta.

Lo que sí es de una feria vive en `urls_feria.py`.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin interno de Django (inspección de datos del equipo), bajo un
    # prefijo propio para no chocar con /admin/ del panel FILEY. Es
    # también donde se dan de alta las ferias (CU-FER-001).
    path("django-admin/", admin.site.urls),
    # Antes de elegir feria: la lista de las que administro (CU-FER-002).
    path("", include("apps.ferias.urls")),
    path("", include("apps.registros.urls")),
]
