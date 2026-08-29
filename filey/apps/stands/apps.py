from django.apps import AppConfig


class StandsConfig(AppConfig):
    """`STD` — venta de stands del showfloor.

    Va en ``TENANT_APPS``: sus tablas viven en el schema de cada feria
    (`ADR-0003`). Y es una app propia, con sus modelos y su namespace de
    URLs: no comparte tablas con `EVT` ni con `apps.convocatorias`, que
    es la mitad por feria de `FER`.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.stands"
    verbose_name = "Stands (venta de espacios)"

    def ready(self):
        """Se inscribe como el módulo que sirve las convocatorias `STD`.

        Es el patrón de `ADR-0006`, y la dirección importa: **`stands`
        nombra a `convocatorias`, nunca al revés**. `FER` no sabe que
        existimos; lo único que sabe es que alguien reclamó el tipo.

        Los imports van dentro y no arriba porque ``ready()`` corre
        cuando el registro de apps ya está poblado; a nivel de módulo,
        importar modelos revienta.
        """
        from apps.convocatorias.models import TipoConvocatoria
        from apps.convocatorias.modulos import Modulo, registrar

        from .servicios import configuracion

        registrar(
            Modulo(
                tipo=TipoConvocatoria.STD,
                etiqueta="Venta de stands",
                url_aplicar="stands:solicitud",
                url_panel="stands:solicitudes",
                crear_configuracion=configuracion.crear_por_defecto,
            )
        )
