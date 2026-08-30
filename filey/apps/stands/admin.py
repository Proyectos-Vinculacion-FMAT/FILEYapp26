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


class ConfiguracionConMapaForm(forms.ModelForm):
    """La configuración de la convocatoria, con su mapa al lado.

    `mapa_json` **no es un campo del modelo**: el mapa no se guarda como
    archivo, se traduce a `MapaShowfloor`, `Stand` y `DecoracionMapa`
    (`CU-STD-039`). Es un campo del formulario, y lo que hace al guardar
    lo decide el admin.

    .. note:: Por qué aquí y no en el admin de `Convocatoria`

       `apps/convocatorias` **nunca nombra a un vertical** (`ADR-0006`),
       así que su pantalla no puede tener un campo de mapa de stands.
       Ésta es la configuración *de esta convocatoria* para este módulo
       —su nombre en pantalla es literalmente «configuración de la
       convocatoria»— y es donde ya se pone el precio. Con esto, montar
       una edición es una sola pantalla.
    """

    mapa_json = forms.FileField(
        required=False,
        label="Cargar el mapa del showfloor",
        help_text=(
            "JSON en el formato de event-stand-map (grid / stands / "
            "decorations). Ver docs/requisitos/STD/README.md."
        ),
    )
    reemplazar_mapa = forms.BooleanField(
        required=False,
        label="Reemplazar el mapa que ya exista",
        help_text=(
            "Borra todos sus espacios. Sin marcar, una convocatoria que ya "
            "tiene mapa se rechaza."
        ),
    )

    class Meta:
        model = ConfiguracionSistema
        fields = "__all__"

    def clean_mapa_json(self):
        """Se lee y se valida **antes de guardar nada**.

        Así un archivo que no es JSON —el PDF del plano, por ejemplo—
        sale como error de este campo y no como un 500 a medio guardar.
        """
        archivo = self.cleaned_data.get("mapa_json")
        if not archivo:
            return None
        try:
            return json.loads(archivo.read().decode("utf-8"))
        except UnicodeDecodeError:
            raise forms.ValidationError("El archivo no es texto UTF-8.") from None
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(f"No es JSON válido: {exc}") from None


@admin.register(ConfiguracionSistema, site=admin_feria)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    """Precios, plazos y el mapa de una convocatoria (`CU-STD-034`, `039`).

    **La pantalla de verdad es A10** —`stands:configuracion`, del panel—
    y es la que usa quien administra la feria. Esto sigue existiendo por
    lo que A10 no puede tener: la **importación del mapa**, que reemplaza
    el showfloor entero y es del operador de la plataforma (`ADR-0005`).

    **El alta no se ofrece**: la fila la crea el alta de la convocatoria
    (`CU-FER-005` paso 6), y crear una a mano dejaría dos para la misma
    convocatoria o una huérfana.

    .. important:: El mapa solo lo carga el operador de la plataforma

       Esta pantalla la abre cualquiera con `is_staff`, porque poner un
       precio es operación diaria. **Importar un mapa no**: reemplaza el
       showfloor entero (`ADR-0005`). Por eso los dos campos del mapa
       solo se le enseñan al superusuario **y el guardado lo vuelve a
       comprobar** — esconder un campo no es una comprobación, y el
       formulario admite lo que se le mande.
    """

    form = ConfiguracionConMapaForm
    list_display = (
        "convocatoria",
        "costo_m2",
        "porcentaje_anticipo",
        "plazo_reserva_dias",
        "descuento_pronto_pago",
        "fecha_limite_pronto_pago",
        "cuenta_publicada",
    )
    list_select_related = ("convocatoria",)
    readonly_fields = ("resumen_del_mapa",)
    def has_add_permission(self, peticion):
        return False

    @admin.display(description="Cuenta publicada", boolean=True)
    def cuenta_publicada(self, obj):
        """Si ya hay dónde pagar. Sin esto, quien reserva no puede.

        Va en la lista y no como filtro: un `list_filter` sobre la CLABE
        pondría cada número de cuenta en la barra lateral, que es
        exactamente lo que no se enseña de una cuenta bancaria.
        """
        return obj.tiene_datos_bancarios

    def get_fieldsets(self, peticion, obj=None):
        economicas = (
            None,
            {
                "fields": (
                    "convocatoria",
                    "costo_m2",
                    "porcentaje_anticipo",
                    "plazo_reserva_dias",
                    "descuento_pronto_pago",
                    "fecha_limite_pronto_pago",
                )
            },
        )
        # `CU-STD-015`: es lo que el expositor copia frente a la app de su
        # banco, así que va en su propio bloque y no mezclado con los
        # precios. Mientras no esté puesto, su pantalla dice que todavía
        # no publicamos la cuenta, en vez de enseñar una ficha vacía.
        bancarias = (
            "Datos bancarios",
            {
                "fields": (
                    "banco_titular",
                    "banco_nombre",
                    "banco_cuenta",
                    "banco_clabe",
                    "banco_sucursal",
                    "banco_referencia",
                    "instrucciones_pago",
                ),
                "description": (
                    "Se le enseñan tal cual a quien tiene una reserva. Sin "
                    "cuenta ni CLABE no se publica nada."
                ),
            },
        )
        if not peticion.user.is_superuser:
            return (economicas, bancarias)
        return (
            economicas,
            bancarias,
            (
                "Mapa del showfloor",
                {
                    "fields": ("resumen_del_mapa", "mapa_json", "reemplazar_mapa"),
                    "description": (
                        "El mapa se traduce a espacios al guardar; no se "
                        "guarda como archivo."
                    ),
                },
            ),
        )

    @admin.display(description="Mapa actual")
    def resumen_del_mapa(self, obj):
        """Qué hay cargado hoy, antes de decidir si se reemplaza.

        Sin esto hay que ir a otra pantalla a averiguar si la convocatoria
        ya tiene mapa, que es justo lo que decide si hace falta marcar la
        casilla de reemplazo.
        """
        if obj is None or obj.pk is None:
            return "—"
        mapa = MapaShowfloor.objects.filter(convocatoria=obj.convocatoria).first()
        if mapa is None:
            return "Sin mapa. Carga uno para que se pueda reservar."
        return (
            f"{mapa.salon} · {mapa.stands.count()} espacios · "
            f"{mapa.metros_cuadrados_vendibles:.0f} m² vendibles · "
            f"retícula de {mapa.columnas}×{mapa.filas} m"
        )

    def save_model(self, peticion, obj, form, change):
        """Guarda la configuración y, si vino un mapa, lo importa.

        En este orden y **no en una sola transacción, a propósito**: el
        precio y el mapa son dos cosas independientes, y que un archivo
        malo tire también el cambio de `costo_m2` sería castigar dos veces
        por un error.
        """
        super().save_model(peticion, obj, form, change)

        datos = form.cleaned_data.get("mapa_json")
        if not datos:
            return
        if not peticion.user.is_superuser:
            raise PermissionDenied(
                "Importar un mapa reemplaza el showfloor entero de una "
                "convocatoria: lo hace el operador de la plataforma."
            )
        try:
            resumen = mapas.importar(
                convocatoria=obj.convocatoria,
                datos=datos,
                confirmado=form.cleaned_data.get("reemplazar_mapa", False),
            )
        except mapas.ImportacionRechazada as exc:
            # Como aviso y no como excepción: la configuración **sí** se
            # guardó, y un 500 haría creer que no.
            self.message_user(peticion, f"El mapa no se cargó: {exc}", messages.ERROR)
        else:
            self.message_user(peticion, str(resumen), messages.SUCCESS)


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
