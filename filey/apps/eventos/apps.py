from django.apps import AppConfig


class EventosConfig(AppConfig):
    """`EVT` — el programa general de la feria.

    Va en ``TENANT_APPS``: sus tablas viven en el schema de cada feria
    (`ADR-0003`). Es una app propia, con sus modelos y su namespace de
    URLs; no comparte tablas con `STD` ni con `apps.convocatorias`, que
    es la mitad por feria de `FER`.

    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.eventos"
    verbose_name = "Eventos (programa general)"

    def ready(self):
        """Se inscribe como el módulo que sirve las convocatorias `EVT`.

        Es el patrón de `ADR-0006`, y la dirección importa: **`eventos`
        nombra a `convocatorias`, nunca al revés**. `FER` no sabe que
        existimos; lo único que sabe es que alguien reclamó el tipo.

        Los imports van dentro y no arriba porque ``ready()`` corre
        cuando el registro de apps ya está poblado; a nivel de módulo,
        importar modelos revienta.

        Sin ``url_panel`` ni secciones: el panel del administrador es
        `CU-EVT-007` en adelante y todavía no existe. Que falte no es un
        olvido — un módulo puede existir para el participante antes de
        tener panel, y el contrato lo admite.
        """
        from apps.convocatorias.models import TipoConvocatoria
        from apps.convocatorias.modulos import Modulo, registrar

        from .servicios import configuracion

        registrar(
            Modulo(
                tipo=TipoConvocatoria.EVT,
                etiqueta="Actividades del programa",
                url_aplicar="eventos:propuesta",
                crear_configuracion=configuracion.crear_por_defecto,
            )
        )
