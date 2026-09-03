"""
Alta de convocatorias desde el admin de Django (`CU-FER-005`, provisional).

> [!warning] Se registra en `admin_feria`, **nunca** en `admin.site`
> `apps.convocatorias` está en `TENANT_APPS`, así que su tabla existe en
> `feria_2027`, `feria_2028`… y en ninguna parte de `public`. El admin de
> `/django-admin/` corre sobre `public`: registrar ahí este modelo no
> falla al arrancar —da una entrada que se ve bien en el índice— y
> revienta con `relation "convocatorias_convocatoria" does not exist` la
> primera vez que alguien la abre. Ver `comun/admin_feria.py`.

Esto es una **medida provisional**, y conviene que se lea como tal: el
caso de uso pone el alta en el panel de la feria y en manos de su dueño,
mientras que aquí la ejecuta el equipo técnico con `is_staff`. Lo que sí
se respeta es la lógica: esta pantalla no escribe la fila, llama a
`servicios/altas.py` —el mismo sitio al que llamará la pantalla del
panel cuando exista, y el mismo reparto que ya usa `FeriaAdmin`—.

> [!note] El formulario de edición también abre y cierra
> Que se pueda cambiar `estado` desde aquí no es CU-FER-008: es lo que
> un `ModelAdmin` hace. Sin ello una convocatoria nacería en `borrador`
> para siempre y el catálogo del participante no llegaría a tener nunca
> nada, que es justo lo que este alta viene a desbloquear.
"""

from django import forms
from django.contrib import admin
from django.shortcuts import redirect

from comun.admin_feria import admin_feria

from .models import Convocatoria, RegistroConvocatoria
from .servicios import altas


class ConvocatoriaForm(forms.ModelForm):
    """El formulario del alta y el de la edición.

    Su único trabajo propio es adelantar E2 al formulario. Podría vivir
    solo en `has_add_permission`, pero entre que se pinta el botón y se
    envía el formulario la feria puede haberse archivado, y entonces el
    fallo saldría como un 500 en vez de como un error legible.
    """

    class Meta:
        model = Convocatoria
        fields = ["tipo", "nombre", "fecha_apertura", "fecha_cierre", "estado"]

    def clean(self):
        datos = super().clean()
        if self.instance.pk is None:
            # No hace falta la petición para saber en qué feria estamos:
            # la conexión ya lo sabe (`ADR-0003`), y preguntárselo a ella
            # es lo que impide que el formulario y el servicio comprueben
            # ferias distintas.
            try:
                altas.feria_que_admite_convocatorias()
            except altas.AltaRechazada as exc:
                raise forms.ValidationError(str(exc)) from exc
        return datos


@admin.register(Convocatoria, site=admin_feria)
class ConvocatoriaAdmin(admin.ModelAdmin):
    form = ConvocatoriaForm
    list_display = ("nombre", "tipo", "estado", "fecha_apertura", "fecha_cierre")
    list_filter = ("tipo", "estado")
    search_fields = ("nombre",)
    ordering = ("tipo", "nombre")

    def has_add_permission(self, peticion):
        """Oculta «añadir» en una feria archivada (E2).

        Vetarlo aquí es lo que evita ofrecer un formulario que no se
        puede enviar. Que la edición se **consulte** sigue estando
        permitido: es el motivo por el que este veto está en el botón y
        no en `AdminDeFeria.has_permission`.
        """
        if not super().has_add_permission(peticion):
            return False
        try:
            altas.feria_que_admite_convocatorias()
        except altas.AltaRechazada:
            return False
        return True

    def add_view(self, peticion, form_url="", extra_context=None):
        """Convierte el fallo de E1 en un mensaje, no en un 500.

        `CU-FER-005` E1 pide dos cosas cuando el módulo no puede crear su
        configuración: que no quede nada, y que el sistema lo informe. Lo
        primero lo garantiza la transacción del servicio; lo segundo no
        lo da el admin por su cuenta, porque `save_model` no tiene forma
        de abortar el guardado y volver al formulario con un error.

        Se captura aquí, fuera del `atomic` con el que el admin envuelve
        `changeform_view`, así que para cuando llega el mensaje la
        transacción ya se deshizo.
        """
        try:
            return super().add_view(peticion, form_url, extra_context)
        except altas.ConfiguracionDelModuloFallo as exc:
            self.message_user(peticion, str(exc), level="ERROR")
            return redirect(peticion.path)

    def get_fields(self, peticion, obj=None):
        """En el alta no se elige el estado: nace en `borrador`.

        Abrirla es un acto aparte y deliberado (CU-FER-008): una
        convocatoria recién creada no tiene revisada su configuración, y
        poder marcarla «abierta» en el mismo formulario que la crea
        convierte ese segundo acto en un descuido de un clic.
        """
        campos = ["tipo", "nombre", "fecha_apertura", "fecha_cierre"]
        if obj is None:
            return campos
        return campos + ["estado"]

    def save_model(self, peticion, obj, form, change):
        """En el alta manda el servicio; en la edición, el modelo.

        El alta no hace `obj.save()` por la misma razón que no lo hace
        `FeriaAdmin`: si esta pantalla escribiera la fila por su cuenta,
        crear una convocatoria desde aquí y crearla desde la pantalla del
        panel —cuando exista— harían cosas distintas, y una de las dos se
        saltaría la configuración del módulo y la bitácora.
        """
        if change:
            obj.save()
            return

        resultado = altas.crear_convocatoria(
            tipo=form.cleaned_data["tipo"],
            nombre=form.cleaned_data["nombre"],
            fecha_apertura=form.cleaned_data.get("fecha_apertura"),
            fecha_cierre=form.cleaned_data.get("fecha_cierre"),
        )

        # El admin sigue trabajando con `obj` después de esto —el log,
        # el redirect, el mensaje de éxito—, y quien tiene la clave
        # primaria real es la fila que creó el servicio. Mismo apaño y
        # mismo motivo que en `FeriaAdmin.save_model`: la firma de
        # `save_model` no permite devolver otra instancia.
        obj.__dict__.update(resultado.convocatoria.__dict__)

        # A2: no es un error y no bloquea nada, pero un alta duplicada
        # por descuido tiene que notarse ahora y no cuando el
        # participante vea dos tarjetas iguales en el catálogo.
        if resultado.otras_del_mismo_tipo:
            nombres = ", ".join(f"«{c.nombre}»" for c in resultado.otras_del_mismo_tipo)
            self.message_user(
                peticion,
                f"Esta edición ya tenía otra convocatoria de tipo "
                f"{obj.get_tipo_display()}: {nombres}. Se creó igualmente —caben "
                "varias del mismo tipo—, pero el nombre es lo único que las "
                "distingue en el catálogo.",
                level="WARNING",
            )


@admin.register(RegistroConvocatoria, site=admin_feria)
class RegistroConvocatoriaAdmin(admin.ModelAdmin):
    """Quién se inscribió a qué, en solo lectura.

    **No se puede crear ni editar desde aquí, y es deliberado.** Un
    registro nace al guardarse el expediente del módulo, dentro de la
    misma transacción y pasando por
    ``servicios/registros.py::obtener_o_crear_registro`` — que es el
    único sitio donde se comprueba que el módulo corresponda al tipo de
    la convocatoria, invariante que la base no puede sostener
    (`ADR-0006`). Un alta a mano desde el admin se saltaría esa
    comprobación y dejaría un registro huérfano, sin expediente, contando
    en los totales de la convocatoria.

    Está para consultar: hoy es la única forma de ver quién entró por qué
    puerta, mientras el panel de la feria no exista.
    """

    list_display = ("persona", "convocatoria", "estado", "fecha_registro")
    list_filter = ("estado", "convocatoria")
    search_fields = ("persona__correo", "convocatoria__nombre")
    ordering = ("-fecha_registro",)
    list_select_related = ("convocatoria", "persona")

    def has_add_permission(self, peticion):
        return False

    def has_change_permission(self, peticion, obj=None):
        return False
