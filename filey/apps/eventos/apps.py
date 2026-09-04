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

        El import de ``senales`` no se usa: está por su efecto. Es como
        se conecta el receptor que descarta los adjuntos a medio subir
        cuando alguien vuelve al catálogo (`CU-EVT-002`), y va aquí por
        lo mismo que el registro de módulos — `convocatorias` anuncia y
        no sabe quién escucha.

        ``url_aplicar`` apunta al **seguimiento** y no al formulario. El
        catálogo dice "Continuar" a quien ya tiene registro (`CU-FER-006`)
        y eso llevaba a un formulario en blanco a quien ya había mandado
        tres propuestas. La puerta de un módulo es el sitio desde el que
        se ve en qué va el trámite —lo mismo que `stands:inicio` en
        `STD`—, y quien no ha mandado ninguna cae en `E1` de
        `CU-EVT-003`, que es un botón para empezar.

        No confundir con ``url_panel``, que es la puerta de quien
        administra: ésa sí lleva a la cola de propuestas.
        """
        from apps.convocatorias.models import TipoConvocatoria
        from apps.convocatorias.modulos import Modulo, SeccionPanel, registrar

        from . import senales  # noqa: F401  — conecta al importarse
        from .servicios import configuracion

        registrar(
            Modulo(
                tipo=TipoConvocatoria.EVT,
                etiqueta="Actividades del programa",
                url_aplicar="eventos:mis_propuestas",
                # El panel **es** la cola de propuestas, y no una portada
                # aparte con números que enlazan a ella. `STD` sí tiene las
                # dos cosas porque su panel resume tres colas distintas y
                # el estado del mapa; aquí solo hay una cola, así que una
                # portada intermedia sería una pantalla de paso que
                # obligaría a un clic más para llegar al trabajo. Los
                # conteos de `CU-EVT-011` van arriba de la propia lista,
                # que es donde el prototipo los pone.
                url_panel="eventos:propuestas",
                # Las cinco del prototipo (`admin-evt-propuestas.html`),
                # en su orden. Las cuatro sin ruta están en el plan y no
                # construidas: se pintan apagadas para que el menú enseñe
                # la forma completa del módulo, que es lo que evita la
                # pregunta "¿y dónde se mandan los resultados?".
                secciones_panel=(
                    SeccionPanel(
                        "Propuestas", "📄", "eventos:propuestas",
                        tambien=("eventos:detalle_propuesta",),
                    ),
                    SeccionPanel("Notificaciones", "🔔"),
                    SeccionPanel("Programa", "📅"),
                    SeccionPanel("Seguimiento", "📊"),
                    SeccionPanel("Configuración", "⚙️"),
                ),
                crear_configuracion=configuracion.crear_por_defecto,
            )
        )
