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
        from apps.convocatorias.modulos import Modulo, SeccionPanel, registrar

        from .servicios import configuracion

        registrar(
            Modulo(
                tipo=TipoConvocatoria.STD,
                etiqueta="Venta de stands",
                url_aplicar="stands:inicio",
                url_panel="stands:panel",
                # Las seis del prototipo de STD (`admin-layout.component`),
                # en su orden, más el resumen. Las tres sin ruta están en
                # el plan y no construidas: se pintan apagadas para que el
                # menú enseñe la forma completa del módulo.
                #
                # El prototipo llama "Aplicaciones" a lo que aquí es
                # "Solicitudes". Se conserva el nombre de los casos de uso
                # y del modelo: cambiarlo dejaría la pantalla diciendo una
                # palabra y `Solicitud` otra.
                secciones_panel=(
                    SeccionPanel("Resumen", "📊", "stands:panel"),
                    SeccionPanel(
                        "Solicitudes", "📄", "stands:solicitudes",
                        tambien=("stands:detalle_solicitud",),
                    ),
                    SeccionPanel(
                        "Reservas", "🎟️", "stands:reservas",
                        tambien=("stands:detalle_reserva",),
                    ),
                    SeccionPanel(
                        "Pagos por validar", "🧾", "stands:pagos",
                        tambien=("stands:movimiento",),
                    ),
                    SeccionPanel("Expositores", "👥"),
                    SeccionPanel("Mapa del salón", "🗺️", "stands:mapa_completo"),
                    SeccionPanel("Configuración", "⚙️", "stands:configuracion"),
                ),
                crear_configuracion=configuracion.crear_por_defecto,
            )
        )
