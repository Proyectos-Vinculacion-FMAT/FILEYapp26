"""
Rutas de los accesos de una feria — **dentro** de `/f/<slug>/`.

Namespace propio (`accesos:`) y no `ferias:`, que es el de las pantallas
de fuera de toda feria (`urls.py`). Que sean dos nombres distintos es lo
que hace imposible confundirlos: `{% url 'accesos:panel' %}` solo
resuelve dentro de una feria y `{% url_publica 'ferias:elegir' %}` solo
fuera. Con un namespace compartido, el mismo prefijo significaría cosas
distintas según el urlconf activo — que es justo la trampa que describe
`comun/urls.py`.

Aquí no se escribe el prefijo `f/<slug>/`: lo antepone `django-tenants`
(ver `config/urls_feria.py`).
"""

from django.urls import path

from . import views_accesos

app_name = "accesos"

urlpatterns = [
    path("", views_accesos.panel_accesos, name="panel"),
    path("<int:acceso_id>/retirar/", views_accesos.retirar_acceso, name="retirar"),
]
