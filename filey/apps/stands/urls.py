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
    # La puerta del módulo: es a donde apunta el "Registrarme" del
    # catálogo (`ADR-0006`) y no lleva a ninguna pantalla propia — mira
    # en qué paso va cada quien y lo manda ahí (`CU-STD-003`).
    path(
        "stands/<int:convocatoria_id>/expositor/",
        views.inicio,
        name="inicio",
    ),
    # U1 · lo que ve el aplicante.
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
    # A5 · la cola de pagos por validar (`CU-STD-018`). Es transversal:
    # cruza todas las reservas de la convocatoria.
    path(
        "stands/<int:convocatoria_id>/pagos/",
        views.pagos_por_validar,
        name="pagos",
    ),
    # El detalle de un abono. Sin la convocatoria en la ruta: el
    # movimiento ya sabe de qué reserva cuelga, y repetirla daría dos
    # fuentes para lo mismo.
    path(
        "stands/movimiento/<int:movimiento_id>/",
        views.movimiento,
        name="movimiento",
    ),
    # A10 · lo que cuesta un espacio y dónde se paga (`CU-STD-034`).
    path(
        "stands/<int:convocatoria_id>/configuracion/",
        views.ajustes_de_la_convocatoria,
        name="configuracion",
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
    # Los datos que consume el canvas (`CU-STD-037` y `CU-STD-038`). Son
    # dos rutas y no una con un parámetro: el recorte de `RN-09` lo decide
    # el decorador de cada una, y una sola vista con un `if` pondría esa
    # decisión donde es fácil equivocarse.
    path(
        "stands/<int:convocatoria_id>/mapa/datos/",
        views.mapa_datos,
        name="mapa_datos",
    ),
    path(
        "stands/<int:convocatoria_id>/showfloor/datos/",
        views.mapa_datos_completo,
        name="mapa_datos_completo",
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
    # El mismo carrito, servido suelto para que htmx lo intercambie al
    # lado del mapa sin recargar la página — recargar costaría volver a
    # bajar los 39 MB del canvas.
    path(
        "stands/<int:convocatoria_id>/carrito/lateral/",
        views.carrito_lateral,
        name="carrito_lateral",
    ),
    path(
        "stands/<int:convocatoria_id>/reservar/",
        views.reservar,
        name="reservar",
    ),
    # El último paso: la cuenta por pagar y sus abonos (`CU-STD-013`,
    # `016`, `017`). En singular porque una editorial lleva una sola
    # reserva viva (`RN-23`).
    path(
        "stands/<int:convocatoria_id>/mi-reserva/",
        views.cuenta,
        name="cuenta",
    ),
    path(
        "stands/<int:convocatoria_id>/mi-reserva/abonar/",
        views.registrar_abono,
        name="registrar_abono",
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
