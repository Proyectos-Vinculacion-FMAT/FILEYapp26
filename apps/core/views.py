from django.views.generic import TemplateView


class InicioView(TemplateView):
    """Portada. Existe para que el scaffold sea verificable con `runserver`."""

    template_name = "core/inicio.html"
