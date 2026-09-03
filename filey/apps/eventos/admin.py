"""
`EVT` en el admin de la edición.

> [!warning] Se registra en `admin_feria`, **nunca** en `admin.site`
> `apps.eventos` está en `TENANT_APPS`: sus tablas existen en
> `feria_2027`, `feria_2028`… y en ninguna parte de `public`. Registrar
> aquí en el admin de siempre no falla al arrancar —la entrada se ve bien
> en el índice— y revienta con `relation "eventos_solicitud" does not
> exist` la primera vez que alguien la abre.

Esto es para consultar y para desatascar, no para operar: dictaminar es
`CU-EVT-009` y tiene su propia pantalla, donde se avisa a quien propuso.
Por eso el estado no se edita desde aquí.
"""

from django.contrib import admin

from comun.admin_feria import admin_feria

from .models import CatalogoActividades, ConfiguracionConvocatoria, Solicitud


@admin.register(CatalogoActividades, site=admin_feria)
class CatalogoActividadesAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden")
    ordering = ("orden",)


@admin.register(ConfiguracionConvocatoria, site=admin_feria)
class ConfiguracionConvocatoriaAdmin(admin.ModelAdmin):
    list_display = ("convocatoria", "prefijo_folio")


@admin.register(Solicitud, site=admin_feria)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = (
        "folio",
        "titulo_actividad",
        "institucion",
        "estado",
        "fecha_de_solicitud",
    )
    list_filter = ("estado", "es_uady")
    search_fields = ("titulo_actividad", "institucion")
    # El dictamen es de `CU-EVT-009`: cambiar el estado desde aquí se
    # saltaría el aviso a quien propuso y la comprobación de que la
    # solicitud siga pendiente.
    readonly_fields = ("estado", "fecha_de_solicitud")
