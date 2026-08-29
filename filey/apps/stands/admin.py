"""
`STD` en el admin de la edición.

> [!warning] Se registra en `admin_feria`, **nunca** en `admin.site`
> `apps.stands` está en `TENANT_APPS`: sus tablas existen en
> `feria_2027`, `feria_2028`… y en ninguna parte de `public`. Registrar
> aquí en el admin de siempre no falla al arrancar —la entrada se ve bien
> en el índice— y revienta con `relation "stands_editorial" does not
> exist` la primera vez que alguien la abre.

Esto es para consultar y para desatascar, no para operar: quien dictamina
lo hace en A2, que es donde se avisa al aplicante y se comprueba que la
solicitud siga pendiente. Por eso `Solicitud` no deja cambiar el estado
desde aquí.
"""

from django.contrib import admin

from comun.admin_feria import admin_feria

from .models import (
    ConfiguracionSistema,
    Documento,
    Editorial,
    Notificacion,
    SelloEditorial,
    Solicitud,
)


class SelloInline(admin.TabularInline):
    model = SelloEditorial
    extra = 0


@admin.register(Editorial, site=admin_feria)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ("nombre", "persona", "giro", "responsable_stand")
    list_filter = ("giro",)
    search_fields = ("nombre", "persona__correo", "nombre_antepecho")
    inlines = [SelloInline]
    list_select_related = ("persona",)


@admin.register(Solicitud, site=admin_feria)
class SolicitudAdmin(admin.ModelAdmin):
    """Solo lectura, y es lo importante de esta clase.

    Cambiar `estado` a mano se saltaría todo lo que hace un dictamen de
    verdad: la comprobación de que siga pendiente (`CU-STD-006` E1), el
    registro de quién y cuándo, y el correo al aplicante. La solicitud
    quedaría aceptada sin que nadie se enterara.
    """

    list_display = ("editorial", "estado", "fecha_envio", "fecha_revision", "revisado_por")
    list_filter = ("estado",)
    search_fields = ("editorial__nombre",)
    list_select_related = ("editorial", "revisado_por")

    def has_add_permission(self, peticion):
        return False

    def has_change_permission(self, peticion, obj=None):
        return False


@admin.register(ConfiguracionSistema, site=admin_feria)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    """Precios y plazos de una convocatoria (`CU-STD-034`, provisional).

    La pantalla propia es A10 y no existe todavía; mientras tanto es
    desde aquí. **El alta no se ofrece**: la fila la crea el alta de la
    convocatoria (`CU-FER-005` paso 6), y crear una a mano dejaría dos
    para la misma convocatoria o una huérfana.
    """

    list_display = (
        "convocatoria",
        "costo_m2",
        "porcentaje_anticipo",
        "plazo_reserva_dias",
        "descuento_pronto_pago",
        "fecha_limite_pronto_pago",
    )
    list_select_related = ("convocatoria",)

    def has_add_permission(self, peticion):
        return False


@admin.register(Documento, site=admin_feria)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "nombre_original", "editorial", "fecha_carga")
    list_filter = ("tipo",)
    list_select_related = ("editorial",)


@admin.register(Notificacion, site=admin_feria)
class NotificacionAdmin(admin.ModelAdmin):
    """El registro de avisos. Sirve sobre todo para ver los que fallaron.

    Solo lectura: una notificación dice lo que pasó. Editarla a mano
    convertiría un correo que no salió en uno que sí, sin que nadie lo
    reciba.
    """

    list_display = ("tipo", "destinatario", "estado", "fecha_envio")
    list_filter = ("estado", "tipo")
    list_select_related = ("destinatario",)

    def has_add_permission(self, peticion):
        return False

    def has_change_permission(self, peticion, obj=None):
        return False
