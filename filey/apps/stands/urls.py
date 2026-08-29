"""
Rutas de `STD` — **dentro** de una feria.

Cuelgan de `config/urls_feria.py`, así que no llevan escrito el prefijo
`/f/<slug>/`: lo antepone `django-tenants`. Namespace propio (`stands:`),
como manda que cada vertical sea su propia app.

Las dos que el registro de módulos nombra —``solicitud`` y ``panel``—
reciben el id de la convocatoria, porque una feria puede tener varias
convocatorias de stands y cada una tiene su propio expediente, su propio
mapa y su propio precio.
"""

from django.urls import path

from . import views

app_name = "stands"

urlpatterns = [
    # U1 · lo que ve el aplicante. Es a donde apunta el "Registrarme" del
    # catálogo de convocatorias (`ADR-0006`).
    path(
        "stands/<int:convocatoria_id>/solicitud/",
        views.solicitud,
        name="solicitud",
    ),
    # A1 y el panel del módulo.
    path(
        "stands/<int:convocatoria_id>/",
        views.panel,
        name="panel",
    ),
    path(
        "stands/<int:convocatoria_id>/solicitudes/",
        views.solicitudes_de_la_convocatoria,
        name="solicitudes",
    ),
    # A2 · no lleva la convocatoria en la ruta: la solicitud ya sabe de
    # cuál cuelga, y repetirla daría dos fuentes para lo mismo y una URL
    # que puede mentir.
    path(
        "stands/solicitud/<int:solicitud_id>/",
        views.detalle_solicitud,
        name="detalle_solicitud",
    ),
    # El showfloor. La clave del stand va en la URL y no su id: es lo
    # que la gente dice en voz alta ("el 24B"), y sobrevive a reimportar
    # el mapa, que borra las filas y las vuelve a crear con ids nuevos.
    path(
        "stands/<int:convocatoria_id>/mapa/",
        views.mapa,
        name="mapa",
    ),
    path(
        "stands/<int:convocatoria_id>/mapa/<str:clave>/",
        views.detalle_stand,
        name="detalle_stand",
    ),
    # `CU-STD-032`: el mismo mapa sin colapsar los estados (`RN-18`).
    path(
        "stands/<int:convocatoria_id>/showfloor/",
        views.mapa_completo,
        name="mapa_completo",
    ),
    # La reserva. El carrito vive en la sesión, así que no lleva id.
    path(
        "stands/<int:convocatoria_id>/carrito/",
        views.carrito_de_stands,
        name="carrito",
    ),
    path(
        "stands/<int:convocatoria_id>/reservar/",
        views.reservar,
        name="reservar",
    ),
    path(
        "stands/<int:convocatoria_id>/mis-reservas/",
        views.mis_reservas,
        name="mis_reservas",
    ),
    # A · la cola de reservas y su detalle (`CU-STD-028`, `029`).
    path(
        "stands/<int:convocatoria_id>/reservas/",
        views.reservas_de_la_convocatoria,
        name="reservas",
    ),
    path(
        "stands/reserva/<int:reserva_id>/",
        views.detalle_reserva,
        name="detalle_reserva",
    ),
    # La entrega de adjuntos. Es la única forma de alcanzar un archivo:
    # `MEDIA_URL` no está montada en ningún urlconf (`ADR-0007`).
    path(
        "stands/documento/<int:documento_id>/",
        views.documento,
        name="documento",
    ),
]
