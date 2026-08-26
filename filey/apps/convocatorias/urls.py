"""
Rutas de las convocatorias — **dentro** de una feria.

Se montan en la raíz de `config/urls_feria.py`, así que el catálogo es
la portada de `/f/<slug>/`. No llevan el prefijo escrito: lo antepone
`django-tenants` (ver ese módulo).
"""

from django.urls import path

from . import views

app_name = "convocatorias"

urlpatterns = [
    path("", views.catalogo_de_la_feria, name="catalogo"),
]
