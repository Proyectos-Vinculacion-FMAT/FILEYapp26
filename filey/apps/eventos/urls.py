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
    # A1 · la cola de revisión y el panel del módulo (`CU-EVT-007`,
    # `CU-EVT-011`). Es a donde apunta `url_panel` del registro de
    # módulos: `EVT` no tiene una portada aparte de su cola, porque la
    # pregunta que trae a quien administra —«¿qué necesita de mí hoy?»— la
    # contesta la propia lista con sus conteos arriba.
    path(
        "eventos/<int:convocatoria_id>/propuestas/",
        views.propuestas,
        name="propuestas",
    ),
    # A2 · el expediente de una propuesta y su dictamen (`CU-EVT-008`,
    # `CU-EVT-009`). Sin la convocatoria en la ruta: la propuesta ya sabe
    # de cuál cuelga, y repetirla daría dos fuentes para lo mismo.
    path(
        "eventos/propuesta/<int:solicitud_id>/",
        views.detalle_propuesta,
        name="detalle_propuesta",
    ),
    # La entrega de adjuntos. Es la única forma de alcanzar un archivo:
    # `MEDIA_URL` no está montada en ningún urlconf (`ADR-0007`).
    path(
        "eventos/documento/<int:documento_id>/",
        views.documento,
        name="documento",
    ),
]
