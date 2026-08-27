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

from comun.admin_feria import admin_feria

from .models import Convocatoria
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
