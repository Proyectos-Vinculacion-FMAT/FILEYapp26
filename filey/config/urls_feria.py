"""
Rutas de **dentro de una feria** — `/f/<slug>/…` (`ROOT_URLCONF`).

`django-tenants` no las monta tal cual: envuelve estos patrones en un
resolver que antepone `f/<slug>/`, así que aquí se escriben **sin** el
prefijo. La contrapartida buena es que `{% url %}` y `reverse()`
normales ya devuelven la URL con su feria; no hay que pasar el slug a
mano por ninguna plantilla.

Aquí se montarán los dominios de contenido (`eventos/`, `talleres/`,
`stands/`, `visitas/`) conforme se construyan: todos son contenido de
una edición, y ninguno vive fuera de una.
"""

from django.urls import path

from apps.ferias import views

urlpatterns = [
    path("", views.portada, name="feria_portada"),
]

# Estos cuatro parecen redundantes —son los de fábrica de Django— y no lo
# son: sin ellos, **cualquier error dentro de una feria llega disfrazado**.
#
# `django-tenants` no monta este módulo tal cual: lo envuelve en un
# `LazyURLConfModule` que resuelve los atributos por `import_string`. Ese
# envoltorio, ante un atributo que no existe, **lanza `ImportError` en vez
# de devolver `None`**, que es lo que Django espera al preguntar
# `getattr(urlconf, "handler500", None)`.
#
# El resultado: una vista de feria que revienta produce su excepción real,
# Django va a buscar el manejador de error, y lo que sale por el log es
# `ImportError: Module "config.urls_feria" does not define a "handler500"`.
# La causa verdadera desaparece. Declararlos hace que el envoltorio los
# encuentre y el error real vuelva a verse.
handler400 = "django.views.defaults.bad_request"
handler403 = "django.views.defaults.permission_denied"
handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"
