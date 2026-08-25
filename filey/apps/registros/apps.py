from django.apps import AppConfig


class RegistrosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.registros"
    label = "registros"
    verbose_name = "Core Registros (REG)"

    def ready(self):
        # Registra las comprobaciones de despliegue de `comun`. Van
        # colgadas de esta app porque `comun` no es una app instalada
        # (es un paquete transversal, sin modelos ni migraciones) y algo
        # tiene que importarlas para que Django las conozca.
        from comun import checks  # noqa: F401
