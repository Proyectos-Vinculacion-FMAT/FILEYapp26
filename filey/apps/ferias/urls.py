"""
Rutas del Core Ferias que viven **fuera** de una feria.

Las dos pantallas de selección: la del participante (`CU-FER-010`) y la
del administrador (`CU-FER-002`). Es lo que se ve antes de haber
elegido, así que no puede colgar de `/f/<slug>/`. Lo que sí es de una
feria concreta se monta en `config/urls_feria.py`.
"""

from django.urls import path

from . import views

app_name = "ferias"

urlpatterns = [
    path("ferias/", views.elegir_feria, name="elegir"),
    path("admin/ferias/", views.mis_ferias, name="mis_ferias"),
    # Cambiar de cara sin volver a identificarse. Vive fuera de toda
    # feria —la barra superior sale también donde no hay ninguna— y
    # recibe el slug para saber a dónde devolver a quien la pulsa.
    path("modo/", views.cambiar_modo, name="modo"),
]
