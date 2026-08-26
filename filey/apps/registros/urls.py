"""
Rutas del Core Registros — montadas en la raíz del sitio.

Mismo mapa de pantallas que traía el prototipo REG y que tenía el
frontend Angular, para que ningún enlace ya compartido se rompa:

    Participante:  /acceso → /acceso/registro → /acceso/codigo → /convocatorias
    Administrador: /admin/acceso → /admin/acceso/codigo → /admin/modulos
"""

from django.urls import path

from . import views

app_name = "registros"

urlpatterns = [
    path("", views.raiz, name="raiz"),
    # ── Participante ──
    path("acceso/", views.acceso, name="acceso"),
    path("acceso/registro/", views.registro, name="registro"),
    path("acceso/codigo/", views.codigo, name="codigo"),
    path("acceso/codigo/reenviar/", views.reenviar, name="reenviar"),
    path("convocatorias/", views.convocatorias, name="convocatorias"),
    # ── Administrador ──
    path("admin/acceso/", views.admin_acceso, name="admin_acceso"),
    path("admin/acceso/codigo/", views.admin_codigo, name="admin_codigo"),
    path(
        "admin/acceso/codigo/reenviar/",
        views.admin_reenviar,
        name="admin_reenviar",
    ),
    # ── Común ──
    path("salir/", views.salir, name="salir"),
]
