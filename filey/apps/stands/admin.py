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

import json

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import path, reverse

from apps.convocatorias.models import Convocatoria, TipoConvocatoria
from comun.admin_feria import admin_feria

from .servicios import mapas

from .models import (
    ConfiguracionSistema,
    DecoracionMapa,
    DescuentoAplicado,
    Documento,
    Editorial,
    MapaShowfloor,
    Notificacion,
    Reserva,
    ReservaStand,
    SelloEditorial,
    Solicitud,
    Stand,
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


# ── El mapa del showfloor ─────────────────────────────────────


class ImportarMapaForm(forms.Form):
    """El archivo y la confirmación de `CU-STD-039`."""

    convocatoria = forms.ModelChoiceField(
        queryset=Convocatoria.objects.none(),
        label="Convocatoria de stands",
        help_text="El mapa es de una convocatoria, no de la feria (RN-19).",
    )
    archivo = forms.FileField(
        label="Archivo del mapa",
        help_text="JSON en formato «filey-mapa/1». Ver scripts/derivar-mapa/.",
    )
    confirmar = forms.BooleanField(
        required=False,
        label="Reemplazar el mapa que ya exista",
        help_text=(
            "Borra todos sus espacios. Sin marcar, una convocatoria que ya "
            "tiene mapa se rechaza."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["convocatoria"].queryset = Convocatoria.objects.filter(
            tipo=TipoConvocatoria.STD
        )

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        try:
            return json.loads(archivo.read().decode("utf-8"))
        except UnicodeDecodeError:
            raise forms.ValidationError("El archivo no es texto UTF-8.") from None
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(f"No es JSON válido: {exc}") from None


@admin.register(MapaShowfloor, site=admin_feria)
class MapaShowfloorAdmin(admin.ModelAdmin):
    """El showfloor de cada convocatoria, y la pantalla que lo carga.

    **No se da de alta a mano ni se edita aquí.** Un mapa son cientos de
    filas con una geometría que tiene que cuadrar entre sí; teclearla en
    un formulario es imposible en la práctica y garantiza dejarla a
    medias. Se importa entera o no se importa (`CU-STD-039`).
    """

    list_display = ("convocatoria", "salon", "columnas", "filas", "importado_en")
    list_select_related = ("convocatoria",)

    def has_add_permission(self, peticion):
        return False

    def has_change_permission(self, peticion, obj=None):
        return False

    def get_urls(self):
        return [
            path(
                "importar/",
                self.admin_site.admin_view(self.importar),
                name="stands_mapashowfloor_importar",
            ),
            *super().get_urls(),
        ]

    def _url_listado(self) -> str:
        """El listado de mapas, en **este** sitio de admin.

        Se arma con `admin_site.name` y no con el prefijo `admin:` de
        siempre: hay dos sitios de admin, y el de la edición se llama
        `admin_feria`. Escribir `admin:` aquí resuelve al otro —el que
        corre sobre `public`— o revienta con `NoReverseMatch`.
        """
        return reverse(
            f"{self.admin_site.name}:stands_mapashowfloor_changelist"
        )

    def importar(self, peticion):
        """`CU-STD-039`. Solo el operador de la plataforma.

        `is_staff` abre este admin entero, así que no basta: importar
        reemplaza el showfloor de una convocatoria y es una operación de
        montaje, no de operación diaria. Hasta que exista un editor con
        vista previa, el sitio correcto es la herramienta del equipo
        técnico (`ADR-0005`).
        """
        if not peticion.user.is_superuser:
            raise PermissionDenied(
                "Importar un mapa reemplaza el showfloor entero de una "
                "convocatoria: lo hace el operador de la plataforma."
            )

        formulario = ImportarMapaForm(peticion.POST or None, peticion.FILES or None)
        if peticion.method == "POST" and formulario.is_valid():
            try:
                resumen = mapas.importar(
                    convocatoria=formulario.cleaned_data["convocatoria"],
                    datos=formulario.cleaned_data["archivo"],
                    confirmado=formulario.cleaned_data["confirmar"],
                )
            except mapas.ImportacionRechazada as exc:
                # Como error del formulario y no como `messages.error`: se
                # queda con lo capturado y el archivo se vuelve a elegir
                # en el mismo sitio donde se dice qué falló.
                formulario.add_error(None, str(exc))
            else:
                self.message_user(peticion, str(resumen), messages.SUCCESS)
                return redirect(self._url_listado())

        return render(
            peticion,
            "admin/stands/importar_mapa.html",
            {
                **self.admin_site.each_context(peticion),
                "title": "Importar el mapa del showfloor",
                "form": formulario,
                "opts": self.model._meta,
                "url_listado": self._url_listado(),
            },
        )


@admin.register(Stand, site=admin_feria)
class StandAdmin(admin.ModelAdmin):
    """Consulta y desatasco. La corrección con vista previa es `CU-STD-033`.

    `estado` sí se puede tocar aquí, a propósito: mientras no exista
    `Reserva`, es la única forma de desbloquear un espacio que quedó
    marcado. Cuando la reserva exista, esto tendrá que pasar a solo
    lectura — moverlo a mano dejaría un stand libre con una reserva
    apuntándolo.
    """

    list_display = ("clave", "etiqueta", "zona", "estado", "col", "fila")
    list_filter = ("estado", "zona", "mapa__convocatoria")
    search_fields = ("clave", "etiqueta")
    list_select_related = ("mapa",)
    readonly_fields = ("mapa", "clave", "col", "fila", "ancho_celdas",
                       "alto_celdas", "rectangulos")

    def has_add_permission(self, peticion):
        return False


@admin.register(DecoracionMapa, site=admin_feria)
class DecoracionMapaAdmin(admin.ModelAdmin):
    list_display = ("etiqueta", "tipo", "col", "fila")
    list_filter = ("tipo", "mapa__convocatoria")
    list_select_related = ("mapa",)


# ── La reserva ────────────────────────────────────────────────


class LineaInline(admin.TabularInline):
    model = ReservaStand
    extra = 0
    autocomplete_fields = ("stand",)


class DescuentoInline(admin.TabularInline):
    model = DescuentoAplicado
    extra = 0


@admin.register(Reserva, site=admin_feria)
class ReservaAdmin(admin.ModelAdmin):
    """Consulta y desatasco, no operación.

    `monto_total` y `estado` son de solo lectura a propósito: los mueve
    el cobro (`RN-13`, `RN-14`) y tocarlos aquí dejaría una reserva
    diciendo «pagada» sin un peso detrás. Cancelar o prorrogar es
    `CU-STD-035`, con su pantalla y su bitácora.
    """

    list_display = (
        "editorial", "estado", "monto_total", "fecha_creacion",
        "fecha_vencimiento_anticipo",
    )
    list_filter = ("estado",)
    search_fields = ("editorial__nombre",)
    list_select_related = ("editorial",)
    readonly_fields = ("registro", "editorial", "estado", "monto_total",
                       "fecha_creacion")
    inlines = [LineaInline, DescuentoInline]

    def has_add_permission(self, peticion):
        return False


@admin.register(DescuentoAplicado, site=admin_feria)
class DescuentoAplicadoAdmin(admin.ModelAdmin):
    list_display = ("reserva", "tipo", "porcentaje", "aplicado_por", "fecha")
    list_filter = ("tipo",)
    list_select_related = ("reserva__editorial", "aplicado_por")
