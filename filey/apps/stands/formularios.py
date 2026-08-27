"""
Los formularios de `STD`.

Aquí solo vive lo que es de un formulario: qué campos se piden, cómo se
pintan y qué se rechaza antes de tocar la base. **Ninguna regla de
negocio** — si la convocatoria admite solicitudes, si ya hay una viva, si
se puede dictaminar — vive en `servicios/`, que es a quien llaman estos
formularios y también un comando de `manage.py`.
"""

from django import forms

from .models import MATERIALES, TEMATICAS, Documento, Editorial


class SubidaMultiple(forms.FileInput):
    """Un `<input type="file" multiple>`.

    Django retiró el soporte de `multiple` de sus widgets de archivo en
    la 5.0 —el `ClearableFileInput` lo rechaza en tiempo de import— y
    documenta este subclaseo como la forma de recuperarlo. Hace falta
    para las cartas de representación: son varias, una por editorial
    representada (`RN-17`).
    """

    allow_multiple_selected = True


class ArchivosMultiples(forms.FileField):
    """El campo que acompaña a `SubidaMultiple`.

    ``FileField.clean`` valida **un** archivo; aquí llegan varios, así
    que se valida cada uno. Sin esto, subir tres cartas guardaría una.
    """

    widget = SubidaMultiple

    def clean(self, data, initial=None):
        limpiar = super().clean
        if isinstance(data, (list, tuple)):
            return [limpiar(archivo, initial) for archivo in data]
        return limpiar(data, initial)

#: Cuántas cajas de sello se pintan de más sobre las que ya hay. Sin
#: JavaScript no se pueden añadir filas, así que el formulario tiene que
#: traer hueco de sobra: es la regla 6 de `CLAUDE.md`.
SELLOS_EN_BLANCO = 4


class EditorialForm(forms.ModelForm):
    """La Ficha de Registro para Expositores (`CU-STD-001` paso 2).

    Es larga porque la ficha lo es. Lo que sí se decide aquí es **qué es
    obligatorio**: el director general y el celular sí; los otros tres
    cargos no, porque una editorial pequeña no los tiene y exigirlos
    dejaría fuera a quien puede exponer perfectamente.
    """

    materiales = forms.MultipleChoiceField(
        choices=[(m, m) for m in MATERIALES],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Materiales que exhibe",
    )
    tematicas = forms.MultipleChoiceField(
        choices=[(t, t) for t in TEMATICAS],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Temáticas",
    )

    class Meta:
        model = Editorial
        exclude = ["persona", "total_sellos", "creada_en", "actualizada_en"]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Razón social o nombre comercial"}),
            "nombre_antepecho": forms.TextInput(
                attrs={"placeholder": "Lo que se rotula en el stand"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # `total_sellos` no se pide: se deriva de cuántos sellos se
        # declaren (ver `servicios/solicitudes.py::guardar_editorial`).
        # Preguntarlo daría dos fuentes para el mismo número.
        for campo in ("director_comercial_email", "director_editorial_email",
                      "director_promocion_email", "telefono_oficina"):
            self.fields[campo].required = False


class SellosForm(forms.Form):
    """Los sellos que la editorial representa (`RN-17`).

    Un formulario suelto y no un `formset` porque un sello es un nombre:
    el `formset` traería gestión de `DELETE`, de orden y de `id` para
    guardar una lista de cadenas. Lo que llega es una lista de nombres y
    `guardar_editorial` la sustituye entera.
    """

    def __init__(self, *args, sellos_actuales=None, **kwargs):
        super().__init__(*args, **kwargs)
        actuales = list(sellos_actuales or [])
        for i in range(len(actuales) + SELLOS_EN_BLANCO):
            self.fields[f"sello_{i}"] = forms.CharField(
                required=False,
                max_length=200,
                label=f"Sello {i + 1}",
                initial=actuales[i] if i < len(actuales) else "",
            )

    def nombres(self) -> list[str]:
        """Los sellos escritos, sin vacíos y sin repetir."""
        escritos = (
            (self.cleaned_data.get(nombre) or "").strip() for nombre in self.fields
        )
        return list(dict.fromkeys(s for s in escritos if s))


class DocumentoForm(forms.Form):
    """Los adjuntos de la solicitud (`CU-STD-001` paso 3).

    La constancia fiscal y la lista de títulos son obligatorias la
    primera vez; al reenviar tras una petición de cambios no, porque las
    que ya se subieron siguen ahí y volver a pedirlas obligaría a
    recargar todo por corregir un teléfono (`CU-STD-002` A1).
    """

    constancia_fiscal = forms.FileField(
        required=True, label="Constancia de situación fiscal"
    )
    lista_titulos = forms.FileField(required=True, label="Lista de títulos")
    cartas_representacion = ArchivosMultiples(
        required=False,
        label="Cartas de representación",
        help_text=(
            "Una por cada editorial representada, con membrete del "
            "representado y firma de un ejecutivo facultado (RN-17)."
        ),
    )

    def __init__(self, *args, ya_hay_documentos=False, **kwargs):
        super().__init__(*args, **kwargs)
        if ya_hay_documentos:
            self.fields["constancia_fiscal"].required = False
            self.fields["lista_titulos"].required = False

    #: Qué tipo de `Documento` es cada campo.
    TIPOS = {
        "constancia_fiscal": Documento.Tipo.CONSTANCIA_FISCAL,
        "lista_titulos": Documento.Tipo.LISTA_TITULOS,
        "cartas_representacion": Documento.Tipo.CARTA_REPRESENTACION,
    }


class DictamenForm(forms.Form):
    """Aceptar, rechazar o pedir cambios (`CU-STD-006`, `CU-STD-007`).

    Un solo formulario para las tres acciones porque las tres salen del
    mismo botón del detalle y comparten el motivo. Cuál se ejecuta lo
    decide `accion`, y que el motivo sea obligatorio al pedir cambios lo
    decide el servicio — no este formulario, para que un comando de
    `manage.py` no se salte la regla.
    """

    accion = forms.ChoiceField(
        choices=[
            ("aceptar", "Aceptar"),
            ("rechazar", "Rechazar"),
            ("cambios", "Solicitar cambios"),
        ]
    )
    motivo = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        label="Motivo o cambios que hacen falta",
        help_text="Es lo que el aplicante recibe por correo.",
    )
