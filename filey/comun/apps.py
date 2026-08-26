from django.apps import AppConfig


class ComunConfig(AppConfig):
    """`comun` es una app de Django, aunque no tenga modelos.

    Lo es por dos motivos concretos, no por simetría:

    - Django solo descubre ``templatetags/`` dentro de las apps
      instaladas, y ``comun/templatetags/chasis.py`` es lo que dibuja la
      barra superior de todas las pantallas.
    - Las comprobaciones de ``checks.py`` se registran aquí, que es su
      sitio. Hasta el 2026-08-26 colgaban del ``ready()`` de
      ``registros``, que no tiene nada que ver con ellas.

    Va en ``SHARED_APPS`` y no en ``TENANT_APPS``: sin modelos no crea
    ninguna tabla, así que duplicarla por feria no significaría nada.
    """

    name = "comun"
    label = "comun"
    verbose_name = "Transversal"

    def ready(self):
        from . import checks  # noqa: F401
