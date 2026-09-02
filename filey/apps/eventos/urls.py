"""
Rutas de `EVT` — **dentro** de una feria.

Cuelgan de `config/urls_feria.py`, así que no llevan escrito el prefijo
`/f/<slug>/`: lo antepone `django-tenants`. Namespace propio (`eventos:`),
como manda que cada vertical sea su propia app.

`propuesta` recibe el id de la convocatoria porque una feria puede tener
más de una convocatoria de eventos, y cada una lleva su folio y su
configuración por separado. La confirmación no lo lleva: una propuesta ya
sabe de qué convocatoria es, y repetirlo en la URL abriría la puerta a que
las dos partes no coincidan.
"""

from django.urls import path

from . import views

app_name = "eventos"

urlpatterns = [
    # U1 · la pantalla de captura y envío (`CU-EVT-002`). Es a donde
    # apunta el "Registrarme" del catálogo (`ADR-0006`).
    path(
        "eventos/<int:convocatoria_id>/propuesta/",
        views.propuesta,
        name="propuesta",
    ),
    # El acuse con el folio, paso 14 del CU.
    path(
        "eventos/propuesta/<int:solicitud_id>/enviada/",
        views.confirmacion,
        name="confirmacion",
    ),
]
