"""
Rutas de `EVT` — **dentro** de una feria.

Cuelgan de `config/urls_feria.py`, así que no llevan escrito el prefijo
`/f/<slug>/`: lo antepone `django-tenants`. Namespace propio (`eventos:`),
como manda que cada vertical sea su propia app.

Casi todas reciben el id de la convocatoria porque una feria puede tener
más de una convocatoria de eventos, y cada una lleva su folio y su
configuración por separado. La confirmación no lo lleva: una propuesta ya
sabe de qué convocatoria es, y repetirlo en la URL abriría la puerta a que
las dos partes no coincidan.

`detalle` sí lo lleva, y no por lo mismo: no es para saber de qué
convocatoria es la propuesta —eso ya lo sabe— sino porque **es parte de
la consulta**. La propuesta se busca entre las de esa persona *en esa
convocatoria*, así que un id de otra edición no devuelve una propuesta
que luego haya que rechazar: no devuelve ninguna.
"""

from django.urls import path

from . import views

app_name = "eventos"

urlpatterns = [
    # La puerta del módulo: es a donde apunta el "Registrarme" del
    # catálogo (`ADR-0006`). Sin propuestas es `E1` y ofrece el
    # formulario; con ellas es el seguimiento (`CU-EVT-003`).
    path(
        "eventos/<int:convocatoria_id>/mis-propuestas/",
        views.mis_propuestas,
        name="mis_propuestas",
    ),
    # El detalle de una, en solo lectura (`CU-EVT-003` paso 4).
    path(
        "eventos/<int:convocatoria_id>/propuesta/<int:solicitud_id>/",
        views.detalle,
        name="detalle",
    ),
    # U1 · la pantalla de captura y envío (`CU-EVT-002`).
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
    # `MEDIA_URL` no está montada en ningún urlconf (`ADR-0007`). La usan
    # las dos caras: quien administra desde A2 y quien propuso desde el
    # detalle de `CU-EVT-003`.
    path(
        "eventos/documento/<int:documento_id>/",
        views.documento,
        name="documento",
    ),
]
