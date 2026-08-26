"""
Rutas del Core Ferias que viven **fuera** de una feria.

Solo la lista de "mis ferias" (`CU-FER-002`): es lo que se ve antes de
haber elegido una, así que no puede colgar de `/f/<slug>/`. Lo que sí es
de una feria concreta se monta en `config/urls_feria.py`.
"""

from django.urls import path

from . import views

app_name = "ferias"

urlpatterns = [
    path("admin/ferias/", views.mis_ferias, name="mis_ferias"),
]
